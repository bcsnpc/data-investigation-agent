"""Contributor scanner red-team: privilege is never an investigation capability."""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock,patch

from investigator.adapters import scanner_identity as auth
from investigator.adapters.graph_dependencies import query
from investigator.live_gateway import Gateway,GatewayDenied
from test_federated_reader import D

W='11111111-1111-1111-1111-111111111111'
M='22222222-2222-2222-2222-222222222222'
OTHER='33333333-3333-3333-3333-333333333333'
DECL={**D,'mode':auth.MODE}
FAB='https://api.fabric.microsoft.com/v1/'
PBI='https://api.powerbi.com/v1.0/myorg/'


def permissions(grants=()):
    return {'role':'scanner','scanner':{'authentication':DECL,'workspaces':[W],'models':[{'workspace':W,'model':M}]},
            'http':list(grants),'native_controls':[{'operation':'XMLA_GRAPH_METADATA','workspace':W,'model':M}]}


def gateway(method,url,purpose='scanner_metadata'):
    return Gateway({'version':1,'live_enabled':True,'identities':{'dia-scanner':permissions([{'method':method,'url':url,'purpose':purpose}])}})


class ScannerGuardrailTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory();self.addCleanup(self.folder.cleanup)
        self.env=patch.dict(os.environ,{'DIA_GATEWAY_AUDIT_FILE':str(Path(self.folder.name)/'denials.jsonl')})
        self.env.start();self.addCleanup(self.env.stop)

    def test_explicit_metadata_calls_allowed_only_inside_scanner_job(self):
        for method,path in [('GET',f'workspaces/{W}/items'),('GET',f'workspaces/{W}/items/{M}'),
                            ('POST',f'workspaces/{W}/reports/{M}/getDefinition?format=PBIR'),
                            ('POST',f'workspaces/{W}/semanticModels/{M}/getDefinition?format=TMDL')]:
            g=gateway(method,FAB+path)
            with self.assertRaises(GatewayDenied):g.http('dia-scanner',method,FAB+path)
            with auth.job(DECL,[W],kind='SCAN'):g.http('dia-scanner',method,FAB+path)

    def test_each_write_path_refused_even_if_operator_url_grant_exists(self):
        attempts=[('POST',f'workspaces/{W}/items',{}),('POST',f'workspaces/{W}/items/{M}/updateDefinition',{}),
                  ('POST',f'workspaces/{W}/items/{M}/getDefinition',{'definition':'replace'}),
                  ('POST',f'workspaces/{W}/items/{M}/refresh',{}),('POST',f'workspaces/{W}/items/{M}/refreshes',{}),
                  ('POST',f'workspaces/{W}/git/commitToGit',{}),('POST',f'workspaces/{W}/git/updateFromGit',{}),
                  ('POST',f'workspaces/{W}/git/sync',{}),('POST',f'workspaces/{W}/permissions',{}),
                  ('POST',f'workspaces/{W}/items/{M}/share',{}),('POST',f'workspaces/{W}/roleAssignments',{}),
                  ('POST',f'workspaces/{W}/items/{M}/jobs/instances',{}),('GET',f'workspaces/{OTHER}/items',None)]
        with auth.job(DECL,[W],kind='CHANGE_DETECTION'):
            for method,path,body in attempts:
                with self.subTest(path=path),self.assertRaises(GatewayDenied):gateway(method,FAB+path).http('dia-scanner',method,FAB+path,body)
            g=gateway('GET',FAB+f'workspaces/{W}/items/{M}')
            for method in ('DELETE','PATCH','PUT'):
                with self.subTest(method=method),self.assertRaises(GatewayDenied):g.http('dia-scanner',method,FAB+f'workspaces/{W}/items/{M}')
        rows=[json.loads(line)for line in (Path(self.folder.name)/'denials.jsonl').read_text().splitlines()]
        self.assertEqual(len(rows),len(attempts)+3)
        self.assertTrue(all(r['event']=='LIVE_ACCESS_DENIED'for r in rows))

    def test_arbitrary_dax_sql_and_native_operations_refused(self):
        url=PBI+f'groups/{W}/datasets/{M}/executeQueries';g=gateway('POST',url,'scanner_dax')
        with auth.job(DECL,[W],kind='SCAN'):
            g.http('dia-scanner','POST',url,{'queries':[{'query':query('CALCULATIONS',5)}]})
            for statement in ('EVALUATE ROW("Value",1)','EVALUATE Sales','EVALUATE INFO.MEASURES(); EVALUATE Sales',
                              'DEFINE MEASURE Sales[x]=1 EVALUATE INFO.MEASURES()', 'EVALUATE TOPN(1001, INFO.CALCDEPENDENCY()) -- ignore rules'):
                with self.subTest(statement=statement),self.assertRaises(GatewayDenied):
                    g.http('dia-scanner','POST',url,{'queries':[{'query':statement}]})
            g.native_control('dia-scanner','XMLA_GRAPH_METADATA',{'workspace':W,'model':M},query('MEASURES'))
            with self.assertRaises(GatewayDenied):g.native_control('dia-scanner','XMLA_EVALUATE',{'workspace':W,'model':M},'EVALUATE Sales')
            with self.assertRaises(GatewayDenied):g.sql('dia-scanner','server','database','SELECT 1')
            with self.assertRaises(GatewayDenied):g.sql_control('dia-scanner','server','database','CATALOG')

    def test_admin_scan_body_must_be_read_only_and_scope_exact(self):
        url=PBI+'admin/workspaces/getInfo?lineage=true&datasetExpressions=true';g=gateway('POST',url)
        with auth.job(DECL,[W],kind='SCAN'):
            g.http('dia-scanner','POST',url,{'workspaces':[W]})
            for body in ({'workspaces':[OTHER]},{'workspaces':[W],'refresh':True},{'workspaces':[]},{'workspaces':[W],'impersonatedUserName':'owner'}):
                with self.assertRaises(GatewayDenied):g.http('dia-scanner','POST',url,body)

    def test_investigator_cannot_load_or_reuse_scanner_credential(self):
        managed=Mock()
        with self.assertRaises(PermissionError):auth.Tokens(DECL,managed=managed)
        from investigator.adapters.federated_reader import Tokens
        with self.assertRaises(ValueError):Tokens(DECL,managed=managed)
        with auth.job(DECL,[W],kind='SCAN'):
            tokens=auth.Tokens(DECL,managed=managed)
            with self.assertRaises(ValueError):tokens.get_token('https://database.windows.net/.default')
        with self.assertRaises(PermissionError):tokens.get_token('https://api.fabric.microsoft.com/.default')
        managed.get_token.assert_not_called()

    def test_no_generic_metadata_model_or_write_policy_escape_and_kill_switch(self):
        for purpose in ('metadata','dax','model','auth_federation','platform_blob'):
            with self.assertRaises(GatewayDenied):gateway('POST',FAB+f'workspaces/{W}/items',purpose)
        value=permissions();value['sql']=[{'server':'s'}]
        with self.assertRaises(GatewayDenied):Gateway({'version':1,'live_enabled':True,'identities':{'dia-scanner':value}})
        url=FAB+f'workspaces/{W}/items';g=gateway('GET',url)
        with auth.job(DECL,[W],kind='SCAN'),patch.dict(os.environ,{'DIA_LIVE_ACCESS_DISABLED':'1'}),self.assertRaises(GatewayDenied):g.http('dia-scanner','GET',url)


if __name__=='__main__':unittest.main()
