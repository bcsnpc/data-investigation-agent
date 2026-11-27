"""Synthetic factory/scorer contracts. No estate I/O or AI calls."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
if not(ROOT/'fixtures/scan_benchmark').exists():
    raise unittest.SkipTest('Owner fixture factory is checkout-only, excluded from worker image')
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'scripts'))
from fixtures.scan_benchmark.factory import build,domain_plan,quoted
from fixtures.scan_benchmark.score import score
from investigator.adapters.sql_catalog_scope import project
from metadata_connectors import FabricMetadataConnector
from investigator.adapters.metadata_error import MetadataUnavailable
from investigator.adapters.sql_catalog_lineage import extract


class FactoryTests(unittest.TestCase):
    def spec(self,key):
        return next(s for s in json.loads((ROOT/'fixtures/scan_benchmark/specs.json').read_text())['estates']if s['id']==key)

    def test_insurance_amendment(self):
        p=domain_plan(self.spec('B'));names={o['address']for o in p.objects}
        self.assertTrue({'src.TBL_PLCY_VER','src.TBL_PRM_TRN','src.TBL_CVRG','src.TBL_CLM_RSV','src.TBL_CLM_PMT','src.TBL_AGT','src.TBL_CUST'}<=names)
        self.assertEqual(4,len([n for n in names if n.rsplit('.',1)[1].startswith('V_PRM_X')]))
        self.assertEqual(2,len([o for o in p.objects if o['kind']=='procedure']))
        self.assertTrue(any(t['kind']=='dynamic_sql'for t in p.traps))
        self.assertNotIn('Berka',json.dumps(p.spec));self.assertNotIn('Banking',json.dumps(p.spec))

    def test_separate_truth_and_deterministic_artifacts(self):
        with tempfile.TemporaryDirectory()as d:
            a=Path(d)/'inputs';s=Path(d)/'scores';spec=self.spec('B')
            first=build(spec,a,s);before=(a/'B/build.json').read_bytes()
            self.assertEqual(first,build(spec,a,s));self.assertEqual(before,(a/'B/build.json').read_bytes())
            self.assertNotIn('expected',before.decode());self.assertNotIn('traps',before.decode())
            self.assertEqual('PLANNED_NOT_OBSERVED',json.loads((s/'B-manifest.json').read_text())['status'])
            with self.assertRaises(ValueError):build(spec,a,a/'scoring')

    def test_reject_existing_estate_and_oversized_population(self):
        with tempfile.TemporaryDirectory()as d:
            for key,value in [('database','ordersops'),('rows',100000)]:
                spec=self.spec('B');spec[key]=value
                with self.assertRaises(ValueError):build(spec,Path(d)/'a',Path(d)/'b')
        with self.assertRaises(ValueError):quoted('x]; DROP TABLE x;--')

    def test_no_silent_toy_wholesale(self):
        with self.assertRaisesRegex(ValueError,'Pinned MIT'):domain_plan(self.spec('A'))


class ScoreTests(unittest.TestCase):
    def pair(self):
        obj=dict(address='s.t',columns=[dict(name='id')],layer='source',source_of_truth='candidate')
        truth=dict(estate='synthetic',status='DEPLOYED_VERIFIED',objects=[obj],edges=[],traps=[])
        observation=dict(origin='DIA_NATIVE_DISCOVERY',objects=[copy.deepcopy(obj)],edges=[])
        return truth,observation

    def test_no_credit_for_unbuilt_plan_or_owner_receipt(self):
        t,o=self.pair();t['status']='PLANNED_NOT_OBSERVED'
        with self.assertRaises(ValueError):score(t,o)
        t['status']='DEPLOYED_VERIFIED';o['origin']='OWNER_READBACK'
        with self.assertRaises(ValueError):score(t,o)

    def test_exact_match_and_miss(self):
        t,o=self.pair();self.assertEqual('PASS',score(t,o)['status'])
        o['objects'][0]['columns']=[]
        self.assertEqual('COLUMN_MISSING',score(t,o)['non_permission_misses'][0]['kind'])

    def test_nonpermission_failure_cannot_excuse_missing_objects(self):
        t,o=self.pair();o['objects']=[]
        o['permission_gaps']=[dict(object='s',scope='schema',status_code=500,missing_grant='read')]
        self.assertTrue(any(g['kind']=='OBJECT_MISSING'for g in score(t,o)['non_permission_misses']))
        o['permission_gaps'][0]['status_code']=403
        self.assertFalse(score(t,o)['non_permission_misses'])

    def test_inferred_edge_needs_uncertainty_not_invention(self):
        t,o=self.pair();t['edges']=[dict(source='s.t',target='s.original',relation='COPY_OF',knowledge='inferable_only')]
        self.assertEqual('SCAN_DEFECTS',score(t,o)['status'])
        o['uncertain_objects']=['s.t'];self.assertEqual('PASS',score(t,o)['status'])
        o['edges']=[dict(source='s.t',target='s.other',relation='COPY_OF',knowledge='declared')]
        self.assertTrue(any(g['kind']=='LINEAGE_FALSE_POSITIVE'for g in score(t,o)['non_permission_misses']))


class CatalogScopeTests(unittest.TestCase):
    def snapshot(self):
        return dict(objects=[dict(object_id=1,schema_name='alpha'),dict(object_id=2,schema_name='beta')],
            columns=[dict(object_id=1),dict(object_id=2)],definitions=[dict(object_id=1),dict(object_id=2)],
            keys=[],checks=[],foreign_keys=[])

    def test_connection_only_scope_keeps_every_visible_schema(self):
        for requested in(None,'*'):
            with self.subTest(requested=requested):
                raw=self.snapshot();r,schemas=project(raw,requested)
                self.assertEqual(['alpha','beta'],schemas);self.assertEqual(2,len(r['objects']))
                self.assertEqual(2,len(r['columns']));self.assertEqual(2,len(raw['columns']))

    def test_explicit_legacy_scope_stays_narrow(self):
        raw=self.snapshot();r,schemas=project(raw,'alpha')
        self.assertEqual(['alpha'],schemas);self.assertEqual([dict(object_id=1)],r['columns'])
        self.assertEqual(2,len(raw['objects']))

    def test_empty_authorized_schema_is_retained_without_inventing_objects(self):
        r,schemas=project(self.snapshot(),'empty')
        self.assertEqual(['empty'],schemas);self.assertEqual([],r['objects']);self.assertEqual([],r['definitions'])


class DefinitionRouteTests(unittest.TestCase):
    def test_native_404_uses_typed_route_without_escalation(self):
        calls=[]
        def transport(endpoint,method='get'):
            calls.append((endpoint,method))
            if '/items/'in endpoint:raise MetadataUnavailable(404)
            return {'status_code':200,'text':{'definition':{'parts':[]}}}
        reader=FabricMetadataConnector('workspace',transport,None)
        self.assertEqual({},reader.get_definition({'id':'model','type':'SemanticModel'}))
        self.assertEqual([('workspaces/workspace/items/model/getDefinition?format=TMSL','post'),
                          ('workspaces/workspace/semanticModels/model/getDefinition?format=TMSL','post')],calls)

    def test_no_retry_or_permission_fallback_on_403_or_429(self):
        for code in(403,429):
            calls=[]
            def transport(endpoint,method='get'):
                calls.append(endpoint);raise MetadataUnavailable(code)
            with self.assertRaises(MetadataUnavailable):FabricMetadataConnector('workspace',transport,None).get_definition({'id':'model','type':'SemanticModel'})
            self.assertEqual(1,len(calls))


class SqlLineageTests(unittest.TestCase):
    def assets(self,text):
        return [dict(id='source',kind='SqlObject',name='raw.T',parent='database',meta={}),
            dict(id='view',kind='SqlObject',name='mart.V',parent='database',meta={'definitions':[{'definition':text}]}),
            dict(id='scol',kind='SqlColumn',name='value',parent='source',meta={}),
            dict(id='vcol',kind='SqlColumn',name='value',parent='view',meta={})]

    def test_view_and_column_edges_use_exact_database_and_schema(self):
        result=extract(self.assets('CREATE VIEW mart.V AS SELECT value FROM raw.T'))
        self.assertEqual({('source','view','data'),('scol','vcol','data')},
            {(e['source'],e['target'],e['kind'])for e in result['edges']})
        self.assertEqual([],result['gaps'])

    def test_similar_name_and_missing_schema_are_not_bindings(self):
        for reference in('other.T','T','another_database.raw.T'):
            r=extract(self.assets('CREATE VIEW mart.V AS SELECT value FROM '+reference))
            self.assertEqual([],r['edges']);self.assertTrue(r['gaps'])

    def test_string_literal_never_becomes_lineage(self):
        r=extract(self.assets("CREATE VIEW mart.V AS SELECT 'raw.T' AS value"))
        self.assertEqual([],r['edges'])

    def test_dynamic_procedure_is_explicitly_incomplete(self):
        r=extract(self.assets("CREATE PROCEDURE mart.V AS BEGIN EXEC sp_executesql N'SELECT value FROM raw.T'; END"))
        self.assertEqual([],r['edges']);self.assertTrue(r['gaps'])


if __name__=='__main__':unittest.main()
