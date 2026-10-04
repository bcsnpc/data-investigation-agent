import copy
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from investigator import record_presence as presence
from investigator.adapters.record_presence import plan
from investigator.process_debugging import vertical
from investigator import process_outcomes
from test_system_of_record import SourceAdapter

REQUEST=[{'value':'900099','source':{'start':0,'end':6,'quote':'900099'}}]


def observation(layer,count=0):
    return {'id':'presence-'+layer,'tool':'bounded_sql','check_kind':'EXPECTED_RECORD_PRESENCE',
        'status':'COMPLETED','completeness':'COMPLETE_RESPONSE',
        'read_address':presence.address(layer,copy.deepcopy(REQUEST)),
        'record_presence':{'layer':layer,'requested':copy.deepcopy(REQUEST),'presence':{'900099':count>0}},
        'values':[{'presence_0':{'value':count}}], 'surface_report_binding':'VALUE_QUERY',
        'surface_attestation':{'consistency':'MATCHED','missing_required_fields':[]}}


class PresenceAdapter(SourceAdapter):
    def __init__(self,states,**kwargs):
        super().__init__(list(states),dict.fromkeys(states,12),**kwargs)
        self.states=states;self.presence_reads=[]
    def capabilities(self):return super().capabilities()|{'expected_record_presence'}
    def record_presence(self,path,layer,requested,scope):
        self.presence_reads.append(layer['id'])
        if self.states[layer['id']] is None:return {'status':'UNAVAILABLE','reason':'No faithful key mapping.'}
        return {'status':'OBSERVED','evidence':observation(layer['id'],self.states[layer['id']])}


class PresenceTests(unittest.TestCase):
    def test_presence_is_attested_per_layer_and_all_absent_or_present_earns_source_consistency(self):
        for count in (0,1):
            a=PresenceAdapter(dict(report=count,delivery=count,application=count))
            result=vertical(a,'m',{'expected_records':REQUEST})
            self.assertEqual(a.presence_reads,['report','delivery','application'])
            self.assertEqual(result['classification'],'CONSISTENT_TO_SOURCE')
            process_outcomes.validate(result,{o['id']:o for o in result['_observations']})
            self.assertIn('absent' if count==0 else 'present',result['business_output']['delivery_accounts'][-1])
    def test_missing_or_disagreeing_presence_never_becomes_source_consistency(self):
        for value in (None,1):
            result=vertical(PresenceAdapter(dict(report=0,delivery=0,application=value)),'m',{'expected_records':REQUEST})
            self.assertEqual(result['classification'],'NO_KNOWN_PATTERN')
            self.assertIn('membership',result['support']['process']['missing_capability'])
    def test_outcome_validation_recomputes_original_membership_and_rejects_tampering(self):
        result=vertical(PresenceAdapter(dict(report=0,delivery=0,application=0)),'m',{'expected_records':REQUEST})
        for change in ('missing','null','count','address','attestation'):
            obs=copy.deepcopy({o['id']:o for o in result['_observations']})
            o=obs['presence-application']
            if change=='missing':del obs[o['id']]
            elif change=='null':o['values'][0]['presence_0']['value']=None
            elif change=='count':o['values'][0]['presence_0']['value']=1
            elif change=='address':o['read_address']['layer']='delivery'
            else:o['surface_attestation']['consistency']='MISMATCHED'
            with self.subTest(change=change),self.assertRaises(ValueError):process_outcomes.validate(result,obs)
    def test_absence_is_zero_count_never_blank_failed_query_or_missing_value(self):
        self.assertEqual(presence.counts([{'[presence_0]':{'value':0}}],REQUEST),{'900099':False})
        for rows in ([],[{}],[{'presence_0':{'value':None}}],[{'presence_0':{'value':-1}}],
                     [{'presence_0':{'value':0.5}}],[{'presence_0':{'value':float('nan')}}]):
            with self.assertRaises(ValueError):presence.counts(rows,REQUEST)
    def test_unreachable_source_is_not_read(self):
        a=PresenceAdapter(dict(report=0,delivery=0,application=0))
        original=a.resolve_path
        def path(m):
            p=original(m);p['system_of_record']['reachable']=False;return p
        a.resolve_path=path
        result=vertical(a,'m',{'expected_records':REQUEST})
        self.assertEqual(result['classification'],'CONSISTENT_TO_BOUNDARY')
        self.assertNotIn('application',a.presence_reads)

    def test_source_present_landing_absent_feeds_validated_gap_even_when_aggregates_agree(self):
        from test_source_delivery import DeliveryAdapter
        class GapAdapter(PresenceAdapter,DeliveryAdapter):pass
        a=GapAdapter(dict(report=0,delivery=0,application=1));a.modified='2026-10-04T01:59:59Z'
        result=vertical(a,'m',{'expected_records':REQUEST})
        self.assertEqual(result['classification'],'INGESTION_GAP')
        process_outcomes.validate(result,{o['id']:o for o in result['_observations']})


class CompilerTests(unittest.TestCase):
    def setUp(self):
        self.source={'id':'app','name':'Events','availability':'CURRENT','kind':'SqlObject',
            'metadata':{'schema_name':'source','name':'Events','type_desc':'USER_TABLE','columns':[{'name':'event_key','data_type':'bigint'}]}}
        key={'id':'key','name':'event_key','parent_id':'app','kind':'SqlColumn','availability':'CURRENT','metadata':{'data_type':'bigint'}}
        endpoint={'id':'endpoint','name':'landing-db','kind':'SQLEndpoint','availability':'CURRENT','metadata':{'properties':{'connectionString':'approved.example'}}}
        self.context={'assets':[self.source,key,endpoint]}
        self.proof={'source':self.source,'server':'app.example','database':'application-db',
            'mapping':{'translator':{'mappings':[{'source':{'name':'event_key'},'destination':{'name':'copied_key'}}]}},
            'destination_columns':{'copied_key':{'data_type':'bigint'}}}
        self.layers=[{'id':'semantic','kind':'presentation'},
            {'id':'landing','kind':'declared_source','binding':{'declared_partition':{'schema_name':'dbo','entity_name':'Events'},
               'declared_connection_asset_id':'endpoint','unchanged_connection':True,'declared_role_count':0}},
            {'id':'app','copy_mapping_proof':self.proof}]
        self.adapter=SimpleNamespace(store=None,config={'source_delivery':{'source_asset_id':'app','key_column_id':'key'},
            'sql':{'server':'app.example','database':'application-db'},'fabric':{'sql_reader':{'server':'approved.example'}}},
            model={'context':{'model_assets':[{'id':'semantic','name':'Events','kind':'SemanticTable'},
                {'id':'member','parent_id':'semantic','name':'Event key','kind':'SemanticColumn',
                 'metadata':{'sourceColumn':'copied_key','dataType':'int64'}}]}})
        self.patch=patch('investigator.adapters.record_presence.context_search.latest',return_value=self.context)
        self.patch.start();self.addCleanup(self.patch.stop)
    def compile(self,index,scope=None):return plan(self.adapter,{'layers':self.layers},self.layers[index],REQUEST,scope or {})
    def test_compiles_from_declared_mapping_not_names_on_each_surface(self):
        self.assertIn('[event_key] = 900099',self.compile(2)['query'])
        self.assertIn('[copied_key] = 900099',self.compile(1)['query'])
        self.assertIn("'Events'[Event key] = 900099",self.compile(0)['query'])
        from investigator.query_sql import compile_query as sql
        from investigator.query_dax import compile_query as dax
        for index in (1,2):
            compiled=self.compile(index);sql(compiled['query'],compiled['catalog'],max_rows=2)
        dax(self.compile(0)['query'],self.adapter.model['context']['model_assets'],max_rows=2)
    def test_unknown_mapping_scope_transform_or_connection_never_guessed(self):
        for scope in ({'filters':[{'x':'y'}]},{'dimension_ids':['dimension']}):
            with self.assertRaisesRegex(ValueError,'filtered scope'):self.compile(1,scope)
        self.context['assets'][-1]['metadata']['properties']['connectionString']='other.example'
        with self.assertRaisesRegex(ValueError,'approved lower'):self.compile(1)
        self.layers[1]['kind']='transform'
        with self.assertRaisesRegex(ValueError,'intervening transformation'):self.compile(1)
        self.proof['mapping']['translator']['mappings']=[]
        with self.assertRaisesRegex(ValueError,'exact mapping'):self.compile(2)
    def test_bounded_integral_keys_only_and_unreachable_source_refuses(self):
        self.adapter.config['system_of_record']={'reachable':False}
        with self.assertRaisesRegex(ValueError,'unreachable'):self.compile(2)
        for value in ('1 OR 1=1','1.5','9007199254740992'):
            request=copy.deepcopy(REQUEST);request[0]['value']=value
            with self.assertRaisesRegex(ValueError,'exact integral'):plan(self.adapter,{'layers':self.layers},self.layers[1],request,{})


if __name__=='__main__':unittest.main()
