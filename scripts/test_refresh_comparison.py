import copy
import unittest
from unittest.mock import patch
from investigator import process_outcomes,refresh_comparison
from investigator.process_debugging import vertical
from investigator.adapters.direct_source import connection_proof,quantity_proof
from investigator.synthesis_digest import _context_evidence
from test_process_debugging import Adapter


def proof():
    return {'version':1,'basis':'UNCHANGED_DECLARED_SOURCE','presentation_layer':'top',
            'source_layer':'lower','measure_id':'measure','source_column':'units','aggregate':'SUM',
            'scope':'WHOLE_ENTITY','intervening_operations':[],'provenance':'DECLARED_BY_DEFINITION',
            'definition_asset_id':'def','definition_hash':'a'*64}

class Direct(Adapter):
    def __init__(self,*,transforms=False,timing=None):
        super().__init__(['top','lower'],{'top':10,'lower':11},explain=transforms)
        self.transforms=transforms;self.timing=timing
    def capabilities(self):
        return (super().capabilities()-{'presentation_freshness'})|{'declared_source_comparison'}|({'refresh_timing'} if self.timing else set())
    def direct_source_comparison(self,boundary,scope):
        return None if self.transforms else proof()
    def refresh_timing(self,path):
        if isinstance(self.timing,Exception):raise self.timing
        return self.timing

class RefreshComparisonTests(unittest.TestCase):
    def test_direct_divergence_without_timestamps_validates(self):
        result=vertical(Direct(),'measure',{})
        self.assertEqual(result['classification'],'REFRESH_LATENCY')
        process_outcomes.validate(result,{o['id']:o for o in result['_observations']})
        for key in ('business_output','technical_output'):
            self.assertIn(refresh_comparison.LIMIT,result[key]['mandatory_limits'])
        o=next(o for o in result['_observations'] if 'direct_source_proof' in o)
        projected=_context_evidence(o)['result']
        for field in ('direct_source_proof','comparison_id','reader_timing_unavailable','refresh_timing'):
            self.assertEqual(projected[field],o[field])

    def test_full_support_and_narrative_assembly_preserve_comparison_basis(self):
        from investigator import synthesis_narrative as narrative,assessment_support
        r=vertical(Direct(),'measure',{});observations=r.pop('_observations')
        next(o for o in observations if o['id']=='read-top')['test_purpose']='ESTABLISH_BASELINE'
        assessment_support.validate(r,{o['id']:o for o in observations})
        entries=[{'id':o['id'],'tool':o['tool'],'process_roles':o['process_roles']} for o in observations]
        for e in entries:
            if e['id'] in ('read-top','read-lower'):
                e.update(provenance={'receipt_seal':'TEST_ONLY'},verified_quantity={'quantity':'10' if e['id']=='read-top' else '11'})
            if e['id']=='read-top':e['test_purpose']='ESTABLISH_BASELINE'
            if e['id']=='boundary-1-comparison':e['result']={'comparison_status':'CROSS_SURFACE_VERIFIED','upper_layer':'top','lower_layer':'lower','values_equal':False,'referenced_evidence_ids':['read-top','read-lower']}
            if e['id']=='declared-source-freshness':e.update(_context_evidence(next(o for o in observations if o['id']==e['id'])))
        for e in entries:
            original=next(o for o in observations if o['id']==e['id'])
            if 'snapshot_attestation' in original:e.setdefault('result',{})['snapshot_attestation']=original['snapshot_attestation']
        payload={'evidence':entries,'deterministic_process_finding':{'classification':r['classification']}}
        refs=[e['id'] for e in entries]
        response={'business_output':{'text':narrative.business_text(r['classification'],payload),'evidence_ids':refs},
                  'technical_output':{'text':narrative.path_narrative.summary(payload),'evidence_ids':refs}}
        _,outputs=narrative.assemble(narrative.Response(response),payload,{'assessment':r,'observations':observations})
        for key in ('business_output','technical_output'):
            self.assertIn(refresh_comparison.LIMIT,outputs[key]['mandatory_limits'])
            self.assertIn('unavailable',outputs[key]['explanation']['text'])

    def test_transformation_never_reclassified_as_freshness(self):
        self.assertEqual(vertical(Direct(transforms=True),'measure',{})['classification'],'TRANSFORMATION_LOGIC')

    def test_missing_timing_limitation_is_rejected(self):
        r=vertical(Direct(),'measure',{});r['limits'].remove(refresh_comparison.LIMIT)
        with self.assertRaisesRegex(ValueError,'missing-timestamp'):
            process_outcomes.validate(r,{o['id']:o for o in r['_observations']})

    def test_no_proof_or_wrong_boundary_does_not_fire(self):
        for change in ({'source_layer':'other'},{'intervening_operations':['FILTER']},{'provenance':'INFERRED_FROM_CODE'},{'measure_id':'other'}):
            a=Direct();a.direct_source_comparison=lambda *args:dict(proof(),**change)
            self.assertNotEqual(vertical(a,'measure',{})['classification'],'REFRESH_LATENCY')

    def test_refusals_are_not_weakened(self):
        a=Direct();a.not_comparable={'lower'}
        self.assertEqual(vertical(a,'measure',{})['classification'],'NO_COMPARABLE_PATH')
        a=Direct();a.reports['lower']={'identity':'wrong','object':'lower'}
        self.assertEqual(vertical(a,'measure',{})['classification'],'NO_COMPARABLE_PATH')

    def test_timing_is_enrichment_not_admission_or_classification(self):
        for timing in (None,{'status':'AVAILABLE','identity_provenance':{'account':'metadata@example.com'},'history':[{'status':'Completed'}]},RuntimeError('denied')):
            r=vertical(Direct(timing=timing),'measure',{})
            self.assertEqual(r['classification'],'REFRESH_LATENCY')
        a=Direct(timing={'status':'LATENT'});a.values['lower']=10
        self.assertEqual(vertical(a,'measure',{})['classification'],'CONSISTENT_TO_BOUNDARY')
        a=Direct();a.presentation_freshness=lambda *args:self.fail('legacy timing path called')
        vertical(a,'measure',{})

    def test_connection_requires_full_pass_through(self):
        source={'type':'entity','schemaName':'dbo','entityName':'T','expressionSource':'Source'}
        definition={'id':'def','metadata':{'content':'{}'}}
        valid='let db = Sql.Database("host", "endpoint") in db'
        def check(expr,doc=None,src=None):
            return connection_proof(doc or {},expr,src or source,{'mode':'directLake'},definition)
        self.assertIsNotNone(check(valid))
        for expr in (valid+' extra','let db = Sql.Database("host", "endpoint"), x = Table.SelectRows(db, each true) in x','Sql.Database("host", "endpoint", [Query="SELECT 1"])'):
            self.assertIsNone(check(expr))
        self.assertIsNone(check(valid,{'roles':[{'name':'R'}]}))
        self.assertIsNone(check(valid,{'tables':[{'calculationGroup':{}}]}))
        self.assertIsNone(check(valid,src=dict(source,expression='transform')))

    def test_output_contains_two_values_basis_missing_timing_and_action(self):
        from investigator.output_contract import business_text
        from investigator.business_vocabulary import validate_text
        from investigator.path_narrative import summary
        entries=[{'id':'a','test_purpose':'ESTABLISH_BASELINE','provenance':{'receipt_seal':'x'},'verified_quantity':{'quantity':'10'}},
                 {'id':'b','provenance':{'receipt_seal':'y'},'verified_quantity':{'quantity':'11'}},
                 {'id':'c','tool':'process','result':{'comparison_status':'CROSS_SURFACE_VERIFIED','values_equal':False,'referenced_evidence_ids':['a','b']}}]
        payload={'evidence':entries,'deterministic_process_finding':{'classification':'REFRESH_LATENCY'}}
        text=business_text('REFRESH_LATENCY',payload);validate_text(text,text)
        for fragment in ('10','11','No processing','refresh time','read access','Recommended action'):
            self.assertIn(fragment,text)
        self.assertNotIn('unavailable',summary(payload))  # Timing belongs to engine-rendered limits.

class OptionalTimingTests(unittest.TestCase):
    def config(self):
        return {'fabric':{'workspace_id':'00000000-0000-0000-0000-000000000001',
            'auth':{'tenant_id':'00000000-0000-0000-0000-000000000002'},
            'refresh_timing_reader':{'account':'metadata@example.com','profile':'.local/metadata-test'}}}

    def test_configuration_is_optional_secret_free_and_separate(self):
        import json,tempfile
        from pathlib import Path
        from metadata_config import ROOT,load_config
        config=json.loads((ROOT/'infra/metadata/development.json').read_text(encoding='utf-8-sig'))
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'config.json';path.write_text(json.dumps(config),encoding='utf-8')
            self.assertNotIn('refresh_timing_reader',load_config(path)['fabric'])
            config['fabric']['refresh_timing_reader']={'account':'metadata@example.com','profile':'.local/metadata-test'}
            path.write_text(json.dumps(config),encoding='utf-8')
            self.assertEqual(load_config(path)['fabric']['refresh_timing_reader'],config['fabric']['refresh_timing_reader'])
            config['fabric']['sql_reader']={'account':'metadata@example.com','profile':'.local/other','server':'host'}
            path.write_text(json.dumps(config),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'distinct'):load_config(path)
            del config['fabric']['sql_reader']
            config['fabric']['refresh_timing_reader']['password']='forbidden'
            path.write_text(json.dumps(config),encoding='utf-8')
            with self.assertRaises(ValueError):load_config(path)

    def test_no_profile_fallback(self):
        import refresh_timing_reader as timing
        with patch.object(timing,'session_status',return_value={'status':'SIGN_IN_REQUIRED'}),patch.object(timing,'cli') as cli:
            r=timing.read(self.config(),{})
        cli.assert_not_called()
        self.assertEqual(r['status'],'UNAVAILABLE')
        self.assertEqual(r['identity_provenance']['account'],'metadata@example.com')
        self.assertFalse(r['identity_provenance']['execution_reader'])

    def test_served_metadata_retains_distinct_authenticated_identity(self):
        import refresh_timing_reader as timing
        import base64,json
        claims={'tid':self.config()['fabric']['auth']['tenant_id'],'aud':timing.RESOURCE,'upn':'metadata@example.com','oid':'identity-object'}
        token='h.'+base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip('=')+'.s'
        response=unittest.mock.MagicMock();response.__enter__.return_value=response
        response.read.return_value=json.dumps({'value':[{'status':'Completed','endTime':'2026-09-27T00:00:00Z','refreshType':'ViaApi'}]}).encode()
        response.headers.get.return_value='request-id'
        model={'workspace':self.config()['fabric']['workspace_id'],'native_id':'00000000-0000-0000-0000-000000000003'}
        with patch.object(timing,'session_status',return_value={'status':'READY'}),patch.object(timing,'cli',return_value={'accessToken':token}),patch.object(timing,'urlopen',return_value=response) as http:
            r=timing.read(self.config(),model)
        self.assertEqual(r['status'],'AVAILABLE');http.assert_called_once()
        self.assertEqual(r['identity_provenance']['token_identity'],'metadata@example.com')
        self.assertEqual(r['history'][0]['refreshType'],'ViaApi')
        self.assertFalse(r['causal_explanation_established'])

    def test_quantity_proof_refuses_calculation_and_cross_table_reference(self):
        metadata={'measure':{'id':'m','parent_id':'t'},'assets':[
            {'id':'t','kind':'SemanticTable','name':'Sales'},
            {'id':'c','parent_id':'t','kind':'SemanticColumn','name':'Amount','metadata':{'dataType':'int64','sourceColumn':'amount'}}]}
        layer={'id':'source','semantic_table':'Sales','semantic_column':'Amount','binding':{
            'provenance':'DECLARED_BY_DEFINITION','unchanged_connection':{'server':'host','definition_asset_id':'d','definition_hash':'h','semantic_table_id':'t'}}}
        config={'fabric':{'sql_reader':{'server':'host'}}}
        self.assertIsNotNone(quantity_proof(metadata,layer,config))
        for key,value in (('dataType','double'),('expression','1+1'),('type','calculated')):
            changed=copy.deepcopy(metadata);changed['assets'][1]['metadata'][key]=value
            self.assertIsNone(quantity_proof(changed,layer,config))
        changed=copy.deepcopy(layer);changed['binding']['unchanged_connection']['semantic_table_id']='wrong'
        self.assertIsNone(quantity_proof(metadata,changed,config))
        metadata['assets'][1]['parent_id']='other'
        self.assertIsNone(quantity_proof(metadata,layer,config))

if __name__=='__main__':unittest.main()
