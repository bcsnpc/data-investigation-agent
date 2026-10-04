"""An application edge requires the job's exact, approved connection evidence."""
import copy
import json
import unittest
from uuid import uuid4

import test_enterprise_discovery as fixtures


class SourceConnectionTests(unittest.TestCase):
    scan=fixtures.DiscoveryTests.scan
    sql=fixtures.DiscoveryTests.sql
    def setUp(self):
        fixtures.DiscoveryTests.setUp(self)
        self.lake,self.job,self.connection=(str(uuid4()) for _ in range(3))
        self.items += [{'id':self.lake,'type':'Lakehouse','displayName':'Destination'},
                       {'id':self.job,'type':'CopyJob','displayName':'Application load'}]
        self.parts[self.job]={'copyjob-content.json':json.dumps({
            'properties':{'source':{'connectionSettings':{'typeProperties':{'database':'source'},
                'externalReferences':{'connection':self.connection}}},
                'destination':{'connectionSettings':{'typeProperties':{'workspaceId':self.ws,'artifactId':self.lake}}}},
            'activities':[{'id':'copy','properties':{'source':{'datasetSettings':{'schema':'business','table':'events'}},
                'destination':{'datasetSettings':{'schema':'dbo','table':'new_fact'}}}}]})}
        self.connection_body={'id':self.connection,'connectionDetails':{
            'type':'SQL','path':'approved.database.windows.net;source'},
            'credentialDetails':{'password':'must-not-enter-context'}}
        self.connection_calls=0

    def transport(self,endpoint,*args,**kwargs):
        if endpoint=='connections/'+self.connection:
            self.connection_calls+=1
            if endpoint in self.denied:raise PermissionError('connection unavailable')
            return {'status_code':200,'text':copy.deepcopy(self.connection_body)}
        return fixtures.DiscoveryTests.transport(self,endpoint,*args,**kwargs)

    def edge(self,body):
        return [e for e in body['graph']['edges'] if e['relation']=='DERIVED_FROM'
                and e['source'].endswith('/table/dbo.new_fact')]

    def test_exact_declared_connection_binds_source_and_strips_credentials(self):
        body=self.scan()['body']
        edges=self.edge(body)
        self.assertEqual(len(edges),1)
        self.assertTrue(edges[0]['target'].startswith('sql://approved.database.windows.net/source/'))
        self.assertNotIn('must-not-enter-context',json.dumps(body))
        self.assertEqual(self.connection_calls,1)
        before={(a['id'],a['kind']) for a in body['assets'] if a['kind']!='SourceConnection'}
        self.denied.add('connections/'+self.connection)
        after=self.scan()['body']
        self.assertEqual(before,{(a['id'],a['kind']) for a in after['assets'] if a['kind']!='SourceConnection'})
        self.assertEqual(self.edge(after),[])

    def test_other_server_database_or_connector_never_binds_by_name(self):
        for details in ({'type':'SQL','path':'other.database.windows.net;source'},
                        {'type':'SQL','path':'approved.database.windows.net;other'},
                        {'type':'Other','path':'approved.database.windows.net;source'}):
            with self.subTest(details=details):
                self.connection_body['connectionDetails']=details
                body=self.scan()['body']
                self.assertEqual(self.edge(body),[])
                scope='fabric://'+self.ws+'/connection/'+self.connection
                self.assertEqual(body['coverage'][scope]['status'],'UNAVAILABLE')

    def test_connection_response_identity_must_match_reference(self):
        self.connection_body['id']=str(uuid4())
        self.assertEqual(self.edge(self.scan()['body']),[])

    def test_connection_evidence_does_not_displace_planner_directory_or_sql_objects(self):
        from pathlib import Path
        from types import SimpleNamespace
        from unittest.mock import patch
        from investigator import dynamic_reasoning
        from investigator.onboarding import encoded
        case=json.loads((Path(__file__).parent/'fixtures/planner-view/directory-coverage.json').read_text(encoding='utf8'))
        store=SimpleNamespace(get=lambda _: {'context':{'model_assets':[]}})
        state={'model_id':'model','observations':[],'decisions':[],
            'discovery_version':'synthetic','planner_calls':0,'input_characters':0,
            'envelope':{'measure_id':'measure','dimension_ids':[],
                'limits':{'planner_calls':12,'input_characters':384000}}}
        def project(context):
            with patch.object(dynamic_reasoning.context_search,'latest',return_value={**context,'version':'synthetic'}):
                return dynamic_reasoning.enrich(store,state,{'observations':[]})
        before=project(case)
        after_context=copy.deepcopy(case)
        after_context['assets'] += [{'id':'connection/'+str(i),'name':'source','kind':'SourceConnection',
            'availability':'CURRENT','metadata':{'connectionDetails':{'type':'SQL','path':'host;database'}}}
            for i in range(50)]
        after=project(after_context)
        self.assertEqual(before['context_entry_points'],after['context_entry_points'])
        self.assertEqual(sum(e['kind']=='SqlObject' for e in before['context_entry_points']),
                         sum(e['kind']=='SqlObject' for e in after['context_entry_points']))
        self.assertEqual(encoded(before),encoded(after))


if __name__=='__main__':unittest.main()
