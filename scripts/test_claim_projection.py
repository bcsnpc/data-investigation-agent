import copy
import json
import sqlite3
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from investigator import claim_projection as neutral
from investigator.adapters import claim_projection as producer
from investigator.adapters.microsoft_process import MicrosoftProcessAdapter
from investigator.native_identity import make, KEY
from investigator.onboarding import Conflict

UUID = '11111111-1111-1111-1111-111111111111'


class Store:
    def __init__(self, database, model): self.database, self.model = database, model
    def get(self, identity):
        if identity != self.model['id']: raise KeyError(identity)
        return self.model
    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.database)
        try:
            with db: yield db
        finally: db.close()


class ProjectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        source_columns = [{'name': name, 'data_type': typ, 'computed_definition': None}
                          for name, typ in [('event_key','bigint'),('amount','bigint'),('category','int'),('memo','nvarchar')]]
        self.source = {'id':'app','kind':'SqlObject','name':'Events','availability':'CURRENT',
                       'metadata':{'schema_name':'source','name':'Events','type_desc':'USER_TABLE','columns':source_columns}}
        columns = [{'id': identity,'kind':'SemanticColumn','parent_id':'semantic','name': label,
                    'metadata':{'sourceColumn': target,'dataType':typ}}
                   for identity,label,target,typ in [('member','Event key','copied_key','int64'),('amount','Amount','copied_amount','int64'),
                                                    ('category','Category','copied_category','int64'),('memo','Memo','copied_memo','string')]]
        self.measure = {'id':'quantity','kind':'Measure','parent_id':'semantic','name':'Quantity','metadata':{'expression':"SUM('Events'[Amount])"}}
        self.model = {'id':'model','enabled':True,'revision':1,'context_id':'context','workspace':UUID,'native_id':UUID,
                      'context':{'model_assets':[{'id':'semantic','kind':'SemanticTable','name':'Events'},self.measure,*columns]}}
        self.store = Store(Path(self.temp.name)/'store.sqlite',self.model)
        reader = {'mode':'isolated_reader','tenant_id':UUID,'principal_id':UUID,'account':'reader@example.com','model_ids':[UUID]}
        self.config = {'source_delivery':{'source_asset_id':'app','key_column_id':'key'},
                       'sql':{'server':'app.example','database':'application-db','auth':{'account':'sql-reader'}},
                       'fabric':{'workspace_id':UUID,'native_reader':reader,'sql_reader':{'server':'approved.example','account':'reader@example.com'}}}
        mappings = [{'source':{'name':col['name']},'destination':{'name':columns[i]['metadata']['sourceColumn']}} for i,col in enumerate(source_columns)]
        self.proof = {'source':self.source,'server':'app.example','database':'application-db',
                      'mapping':{'translator':{'mappings':mappings}},
                      'destination_columns':{m['destination']['name']:c for m,c in zip(mappings,source_columns)}}
        self.layers = [{'id':'semantic','kind':'presentation','measure':self.measure},
                       {'id':'landing','kind':'declared_source','semantic_column':'Amount',
                        'declared_columns':[dict(c['metadata'],name=c['name']) for c in columns],
                        'binding':{'status':'RESOLVED','declared_partition':{'schema_name':'dbo','entity_name':'Events','source_type':'entity','partition_count':1},
                                   'declared_connection_asset_id':'endpoint','unchanged_connection':{'server':'approved.example','endpoint':'endpoint'},'declared_role_count':0}},
                       {'id':'app','copy_mapping_proof':self.proof}]
        self.path = {'layers':self.layers}
        self.context = {'assets':[self.source,{'id':'key','name':'event_key','kind':'SqlColumn','parent_id':'app','availability':'CURRENT','metadata':{'data_type':'bigint'}},
                                  {'id':'endpoint','name':'landing-db','kind':'SQLEndpoint','availability':'CURRENT'}]}
        self.patches = [patch('investigator.context_search.latest',return_value=self.context),
                        patch('investigator.source_diagnostics.snapshot',return_value=({'app':self.source},{})),
                        patch('application_sql_surface.read',side_effect=lambda config,req:self.transport('app',req))]
        for item in self.patches: item.start(); self.addCleanup(item.stop)
        self.calls = []; self.meters = []; self.rows = {}; self.bad_identity = False; self.partial = False
        self.adapter = MicrosoftProcessAdapter(self.store,self.config,self.model,
            lambda req:self.transport('semantic',req),None,execute_lower=lambda db,req:self.transport('landing',req),
            meter_read=lambda tool,execute:self.meter(tool,execute))
    def meter(self,tool,execute): self.meters.append(tool); return execute()
    def transport(self,layer,request):
        self.calls.append((layer,copy.deepcopy(request)))
        rows = copy.deepcopy(self.rows.get(layer,[{'count_0':1}]))
        if request['read_address']['projection']['kind'] == 'MULTIPLICITY':
            for row in rows:
                row.setdefault('all_rows', 3); row.setdefault('distinct_keys', 2); row.setdefault('null_keys', 0)
        if self.partial: rows *= request['max_rows']
        surface = request['read_address']['surface']
        report = {k:surface[k] for k in ('identity','engine','object')}
        if self.bad_identity: report['identity'] = 'other@example.com'
        if layer == 'semantic':
            for row in rows: row.update({'surface_'+k:v for k,v in report.items()})
            response = {'results':[{'tables':[{'rows':rows}]}]}
            response[KEY] = make(response,request,self.config['fabric']['native_reader'])
            return response
        return {'rows':rows,'read_only_verified':True,'surface_report':report,'surface_report_binding':'VALUE_QUERY'}
    def request(self,kind='SET_RECONCILIATION',**kwargs): return {'kind':kind,'keys':['123'],**kwargs}
    def probe(self,request,index): return self.adapter.claim_probe(self.path,self.layers[index],request,{})
    def run_all(self,request):
        output = [self.probe(request,index) for index in range(3)]
        for result in output: self.assertEqual(result['status'],'OBSERVED',result)
        return [result['evidence'] for result in output]
    def assess(self,request,observations,unavailable=()):
        expected = {layer['id']: self.adapter.claim_probe_contract(self.path, layer, request, {}) for layer in self.layers}
        return neutral.reduce(self.store,'model',self.path,request,observations,list(unavailable), expected_requests=expected)

    def test_real_compilers_transports_seals_and_source_to_presentation_order(self):
        request = self.request(); self.rows['landing'] = self.rows['semantic'] = [{'count_0':0}]
        observed = self.run_all(request); result = self.assess(request,observed)
        self.assertEqual(result['status'],'OBSERVED_DIFFERENCE')
        self.assertEqual(result['layer_order'],['app','landing','semantic'])
        self.assertTrue(result['boundaries'][0]['first_change_established'])
        self.assertEqual(result['boundaries'][0]['input'],'app')
        self.assertEqual(result['coverage'],'EXPLICIT_EXAMPLE_KEYS_ONLY')
        self.assertEqual(len(self.calls),3); self.assertEqual(len(self.meters),3)
        self.assertFalse(result['defect_established']); self.assertEqual(result['snapshot_status'],'SNAPSHOT_UNVERIFIED')
        self.assertIn('timing was not excluded',result['limits'][0])
        self.assertIn('event_key',self.calls[-1][1]['query'])
        self.assertIn('copied_key',self.calls[1][1]['query'])
        self.assertIn('Event key',self.calls[0][1]['query'])

    def test_missing_preceding_source_never_establishes_first_change(self):
        request = self.request('MULTIPLICITY'); self.rows['semantic']=[{'count_0':2}]
        observed=[self.probe(request,i)['evidence'] for i in (0,1)]
        result=self.assess(request,observed,[{'layer':'app','reason':'Unreachable'}])
        self.assertEqual(result['status'],'NOT_COMPARABLE')
        self.assertFalse(result['boundaries'][0]['first_change_established'])
        self.assertEqual(result['missing_layers'],[{'layer':'app','reason':'Unreachable'}])
        self.assertTrue(any('Global counts' in line for line in result['limits']))

    def test_record_blank_absence_duplicate_and_numeric_string_are_distinct(self):
        request=self.request('RECORD_VALUE',field_id='memo')
        self.rows={'semantic':[{'count_0':1,'value_0':None}], 'landing':[{'count_0':0,'value_0':None}],
                   'app':[{'count_0':2,'value_0':'arbitrary maximum'}]}
        observed=self.run_all(request); result=self.assess(request,observed)
        self.assertEqual(result['status'],'NOT_COMPARABLE')
        self.assertEqual(result['comparison_gaps'][0]['layer'],'app')
        self.assertIsNone(result['boundaries'][0]['agrees'])
        records=[item['facts']['records'][0] for item in result['observations']]
        self.assertEqual(records[0]['value_state'],'AMBIGUOUS_DUPLICATE_KEY');self.assertIsNone(records[0]['value'])
        self.assertEqual(records[1]['value_state'],'NO_RECORD')
        self.assertEqual(records[2]['value'],{'type':'blank','value':None})
        self.assertNotEqual(neutral.cell({'x':{'type':'string','value':'1'}},'x'),neutral.cell({'x':{'type':'decimal','value':'1'}},'x'))

    def test_attestation_mismatch_partial_and_query_failure_never_become_absence(self):
        request=self.request();self.bad_identity=True
        self.assertEqual(self.probe(request,0)['status'],'UNAVAILABLE')
        self.bad_identity=False;self.partial=True
        self.assertEqual(self.probe(request,1)['status'],'UNAVAILABLE')
        self.partial=False
        with patch.object(self.adapter,'execute_lower',side_effect=RuntimeError('transport failed')):
            result=self.probe(request,1)
        self.assertEqual(result['status'],'UNAVAILABLE');self.assertIn('receipt_id',result)

    def test_tampering_with_derived_fact_or_sealed_receipt_refuses(self):
        request=self.request();observed=self.run_all(request)
        changed=copy.deepcopy(observed);changed[0]['claim_projection']['records'][0]['count']=99
        with self.assertRaisesRegex(ValueError,'FACTS_DIFFER'):self.assess(request,changed)
        with self.store.connect() as db:
            db.execute('UPDATE flexible_diagnostics SET status=? WHERE id=?',('FAILED',observed[0]['id']))
        with self.assertRaises(Conflict):self.assess(request,observed)

    def test_unsealed_and_stale_context_are_not_accepted(self):
        request=self.request();observed=self.run_all(request)
        with self.store.connect() as db:db.execute('DELETE FROM aggregate_receipt_seals WHERE id=?',(observed[0]['id'],))
        with self.assertRaisesRegex(ValueError,'UNSEALED'):self.assess(request,observed)
        self.model['revision']=2
        with self.assertRaisesRegex(ValueError,'ORIGINAL_RECEIPT_DIFFERS'):neutral.validate(observed[1],self.store,'model')

    def test_unknown_field_transform_scope_and_unreachable_source_refuse_before_dispatch(self):
        for request in (self.request('RECORD_VALUE',field_id='invented'),self.request('DECOMPOSITION',dimension_id='memo',measure_id='quantity')):
            self.assertEqual(self.probe(request,0)['status'],'UNAVAILABLE')
        self.assertEqual(self.adapter.claim_probe(self.path,self.layers[0],self.request(),{'filters':[{'x':1}]})['status'],'UNAVAILABLE')
        self.layers.insert(1,{'id':'transformed','kind':'transformation'})
        self.assertEqual(self.probe(self.request(),0)['status'],'UNAVAILABLE')
        self.layers.pop(1);self.config['system_of_record']={'reachable':False}
        self.assertEqual(self.probe(self.request(),2)['status'],'UNAVAILABLE')
        self.assertEqual(self.calls,[])

    def test_decomposition_compiles_actual_sum_and_empty_native_sentinel(self):
        request={'kind':'DECOMPOSITION','keys':[],'dimension_id':'category','measure_id':'quantity'}
        self.rows={'semantic':[{'marker':1,'group_value':None,'quantity':None,'row_count':None}], 'landing':[], 'app':[]}
        observed=self.run_all(request);result=self.assess(request,observed)
        self.assertEqual(result['status'],'OBSERVED_EQUAL')
        self.assertTrue(all(o['facts']=={'groups':[]} for o in result['observations']))
        self.assertIn('SELECTCOLUMNS',self.calls[0][1]['query']);self.assertIn('GROUP BY',self.calls[1][1]['query'])
        self.measure['metadata']['expression']="SUM('Events'[Amount]) + 1"
        self.assertEqual(self.probe(request,0)['status'],'UNAVAILABLE')

    def test_integral_decomposition_values_match_without_decimal_format_drift(self):
        request={'kind':'DECOMPOSITION','keys':['123'],'dimension_id':'category','measure_id':'quantity'}
        self.rows={layer:[{'marker':0,'group_value':2,'quantity':10,'row_count':1}] for layer in ('semantic','landing','app')}
        observed=self.run_all(request);self.assertEqual(self.assess(request,observed)['status'],'OBSERVED_EQUAL')
        self.assertEqual(neutral.cell({'x':{'type':'decimal','value':'1.00'}},'x'),neutral.cell({'x':{'type':'decimal','value':'1'}},'x'))

    def test_closed_registry_recomputes_projection_instead_of_accepting_boolean(self):
        from investigator.process_receipts import validate_for_synthesis
        observed=self.run_all(self.request())[0]
        self.assertEqual(validate_for_synthesis(observed)[0],'CLAIM_PROJECTION')
        observed['surface_attestation']['consistency']='CONTRADICTED'
        with self.assertRaises(Conflict):validate_for_synthesis(observed)

    def test_global_multiplicity_includes_null_rows_without_counting_null_as_a_key(self):
        request = {'kind': 'MULTIPLICITY', 'keys': []}
        self.rows = {layer: [{'all_rows': 6, 'distinct_keys': 3, 'null_keys': 1}]
                     for layer in ('semantic', 'landing', 'app')}
        observed = self.run_all(request)
        result = self.assess(request, observed)
        self.assertEqual(result['status'], 'OBSERVED_EQUAL')
        self.assertEqual(result['coverage'], 'DECLARED_UNFILTERED_ENTITY_KEY_COUNTS')
        for item in result['observations']:
            self.assertEqual(item['facts']['global_counts'], {'row_count': 6, 'distinct_nonnull_keys': 3,
                              'null_key_rows': 1, 'duplicate_nonnull_rows': 2})
        self.assertIn('ISBLANK', self.calls[0][1]['query'])
        self.assertIn('DISTINCT', self.calls[1][1]['query'])
        self.rows['landing'][0]['distinct_keys'] = 8
        self.assertEqual(self.probe(request, 1)['status'], 'UNAVAILABLE')

    def test_native_decomposition_saturated_inner_topn_cannot_claim_complete(self):
        request = {'kind': 'DECOMPOSITION', 'keys': [], 'dimension_id': 'category', 'measure_id': 'quantity'}
        # A provider with 201 or more groups yields its TOPN(200) plus the
        # sentinel. The outer bounded read must classify all 201 as PARTIAL.
        self.rows['semantic'] = [{'marker': 1, 'group_value': None, 'quantity': None, 'row_count': None}] + [
            {'marker': 0, 'group_value': i, 'quantity': 1, 'row_count': 1} for i in range(200)]
        result = self.probe(request, 0)
        self.assertEqual(result['status'], 'UNAVAILABLE')
        self.assertEqual(result['reason'], 'CLAIM_PROJECTION_INCOMPLETE_READ')
        self.assertIn('TOPN(200,', self.calls[0][1]['query'])
        self.assertEqual(self.calls[0][1]['max_rows'], 201)
        with self.store.connect() as db:
            saved = json.loads(db.execute('SELECT result FROM flexible_diagnostics WHERE id=?',
                                          (result['receipt_id'],)).fetchone()[0])
        self.assertEqual(saved['completeness'], 'PARTIAL')

    def test_zero_key_uses_strict_native_equality_not_blank_coercion(self):
        request = {'kind': 'SET_RECONCILIATION', 'keys': ['0']}
        self.run_all(request)
        self.assertIn('==0', self.calls[0][1]['query'].replace(' ', ''))
        self.assertNotIn('ISBLANK', self.calls[0][1]['query'])

    def test_first_record_field_change_is_located_without_causal_verdict(self):
        request = self.request('RECORD_VALUE', field_id='amount')
        self.rows = {'app':[{'count_0':1,'value_0':7}], 'landing':[{'count_0':1,'value_0':8}],
                     'semantic':[{'count_0':1,'value_0':8}]}
        result = self.assess(request, self.run_all(request))
        self.assertEqual(result['status'], 'OBSERVED_DIFFERENCE')
        self.assertTrue(result['boundaries'][0]['first_change_established'])
        self.assertTrue(result['boundaries'][1]['agrees'])
        self.assertFalse(result['cause_verified'])

    def test_native_field_type_or_declared_security_roles_cannot_be_silently_ignored(self):
        self.model['context']['model_assets'][-1]['metadata']['dataType'] = 'int64'
        result = self.probe(self.request('RECORD_VALUE', field_id='memo'), 0)
        self.assertEqual(result['status'], 'UNAVAILABLE')
        self.layers[1]['binding']['declared_role_count'] = 1
        self.assertEqual(self.probe(self.request(), 2)['status'], 'UNAVAILABLE')
        self.assertEqual(self.calls, [])

    def test_hostile_producer_sealed_wrong_query_with_correct_address_is_rejected(self):
        request = self.request()
        original = producer.plan
        def wrong_query(*args, **kwargs):
            compiled = original(*args, **kwargs)
            compiled['query'] = compiled['query'].replace('123', '124')
            return compiled
        with patch.object(producer, 'plan', side_effect=wrong_query):
            observed = self.run_all(request)
        # Every receipt really is sealed and its address claims key 123.
        # The consumer independently compiles key 123, so the altered query
        # cannot enter findings despite its valid seal and producer fields.
        with self.assertRaisesRegex(ValueError, 'COMPILED_REQUEST_DIFFERS'):
            self.assess(request, observed)

    def test_invalid_request_keys_do_not_reach_transport(self):
        for keys in ([],['123?'],['1 OR 1=1'],['1','1'],['01'],['-0'],['9007199254740992']):
            request={'kind':'SET_RECONCILIATION','keys':keys}
            self.assertEqual(self.probe(request,0)['status'],'UNAVAILABLE')
        self.assertEqual(self.calls,[])
        self.assertEqual(self.adapter.claim_probe(self.path, self.layers[0], self.request(), None)['status'], 'UNAVAILABLE')

    def test_each_key_has_its_own_first_disappearance_layer(self):
        request = {'kind': 'SET_RECONCILIATION', 'keys': ['123', '124']}
        self.rows = {'app': [{'count_0': 1, 'count_1': 1}],
                     'landing': [{'count_0': 0, 'count_1': 1}],
                     'semantic': [{'count_0': 0, 'count_1': 0}]}
        result = self.assess(request, self.run_all(request))
        changed = [row for row in result['key_transitions'] if row['kind'] == 'DISAPPEARED']
        self.assertEqual([(row['key'], row['first_layer']) for row in changed],
                         [('123', 'landing'), ('124', 'semantic')])
        self.assertTrue(all(row['first_presence_change_established'] for row in changed))
        self.assertTrue(all(len(row['evidence_ids']) == 2 for row in changed))
        # Historical whole-boundary first is only the first aggregate change;
        # it must not be used to hide the second key's later first disappearance.
        self.assertFalse(result['boundaries'][1]['first_change_established'])

    def test_each_key_has_its_own_first_multiplicity_and_value_change(self):
        for kind in ('MULTIPLICITY', 'RECORD_VALUE'):
            with self.subTest(kind=kind):
                request = {'kind': kind, 'keys': ['123', '124']}
                if kind == 'MULTIPLICITY':
                    self.rows = {'app': [{'count_0': 1, 'count_1': 1}],
                                 'landing': [{'count_0': 2, 'count_1': 1}],
                                 'semantic': [{'count_0': 2, 'count_1': 2}]}
                    flag = 'first_count_change_established'
                else:
                    request['field_id'] = 'amount'
                    self.rows = {'app': [{'count_0': 1, 'count_1': 1, 'value_0': 7, 'value_1': 9}],
                                 'landing': [{'count_0': 1, 'count_1': 1, 'value_0': 8, 'value_1': 9}],
                                 'semantic': [{'count_0': 1, 'count_1': 1, 'value_0': 8, 'value_1': 10}]}
                    flag = 'first_value_change_established'
                result = self.assess(request, self.run_all(request))
                firsts = [row for row in result['key_transitions'] if row[flag]]
                self.assertEqual([(row['key'], row['first_layer']) for row in firsts],
                                 [('123', 'landing'), ('124', 'semantic')])

    def test_missing_preceding_read_blocks_each_key_first_but_keeps_observed_change(self):
        request = {'kind': 'SET_RECONCILIATION', 'keys': ['123', '124']}
        self.rows = {'landing': [{'count_0': 1, 'count_1': 1}],
                     'semantic': [{'count_0': 0, 'count_1': 0}]}
        observed = [self.probe(request, index)['evidence'] for index in (0, 1)]
        result = self.assess(request, observed, [{'layer': 'app', 'reason': 'Unreachable'}])
        self.assertEqual(len(result['key_transitions']), 2)
        for row in result['key_transitions']:
            self.assertEqual(row['kind'], 'DISAPPEARED')
            self.assertFalse(row['first_change_established'])
            self.assertFalse(row['preceding_layers_complete'])
            self.assertIsNone(row['first_layer'])

    def test_duplicate_on_one_key_does_not_hide_another_keys_first_value_change(self):
        request = {'kind': 'RECORD_VALUE', 'keys': ['123', '124'], 'field_id': 'amount'}
        self.rows = {'app': [{'count_0': 2, 'count_1': 1, 'value_0': 99, 'value_1': 7}],
                     'landing': [{'count_0': 1, 'count_1': 1, 'value_0': 7, 'value_1': 7}],
                     'semantic': [{'count_0': 1, 'count_1': 1, 'value_0': 8, 'value_1': 8}]}
        result = self.assess(request, self.run_all(request))
        self.assertEqual(result['status'], 'NOT_COMPARABLE')
        later = {row['key']: row for row in result['key_transitions'] if row['output'] == 'semantic'}
        self.assertFalse(later['123']['first_value_change_established'])
        self.assertTrue(later['124']['first_value_change_established'])
        self.assertEqual(later['124']['first_layer'], 'semantic')

    def test_prior_count_change_does_not_hide_first_membership_change(self):
        request = self.request()
        self.rows = {'app': [{'count_0': 1}], 'landing': [{'count_0': 2}], 'semantic': [{'count_0': 0}]}
        result = self.assess(request, self.run_all(request))
        earlier, later = result['key_transitions']
        self.assertEqual(earlier['kind'], 'COUNT_CHANGED')
        self.assertFalse(earlier['first_change_established'])
        self.assertTrue(earlier['first_count_change_established'])
        self.assertTrue(later['first_presence_change_established'])
        self.assertTrue(later['first_change_established'])
        self.assertFalse(later['first_count_change_established'])

    def test_empty_path_or_no_adjacent_observations_cannot_claim_agreement(self):
        request = self.request()
        with self.assertRaisesRegex(ValueError, 'PATH_HAS_NO_LAYERS'):
            neutral.reduce(self.store, 'model', {'layers': []}, request, [], [])
        observed = self.run_all(request)
        expected = {layer['id']: self.adapter.claim_probe_contract(self.path, layer, request, {})
                    for layer in self.layers}
        single = neutral.reduce(self.store, 'model', {'layers': [self.layers[0]]}, request,
                                [observed[0]], [], expected_requests=expected)
        self.assertEqual(single['status'], 'NOT_COMPARABLE')
        self.assertEqual(single['boundaries'], [])
        self.assertEqual(len(single['observations']), 1)
        self.assertIn('No adjacent pair', single['comparison_gaps'][0]['reason'])
        separated = self.assess(request, [observed[0], observed[2]],
                                [{'layer': 'landing', 'reason': 'Unavailable'}])
        self.assertEqual(separated['status'], 'NOT_COMPARABLE')
        self.assertEqual(separated['boundaries'], [])
        self.assertEqual(separated['key_transitions'], [])


if __name__ == '__main__': unittest.main()
