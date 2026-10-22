"""A real compiler/receipt/resolver/repository success path, plus hostile bindings."""
import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import test_declared_predicate_adapter as sample
from cloud_value_execution import _compile
from cloud_value_verifier import execute
from investigator import estate_graph_contract as c
from investigator.estate_graph_repository import GraphRepository
from investigator.graph_value_bridge import attach,build_bundle,graph_hash,capability
from investigator.shared_state import SharedState,TRANSACTION_ACTIVE,encoded

T0='2026-10-13T00:00:00Z';T1='2026-10-13T01:00:00Z';T2='2026-10-13T02:00:00Z'


class ValueBridgeTests(unittest.TestCase):
    def setUp(self):
        h=sample.DeclaredPredicateAdapterTests();h.setUp();self.addCleanup(h.doCleanups)
        h.parts[:]=[h.report_doc,h.page,h.visual]
        for part in h.parts:
            h.modify(part,lambda d:d.pop('filterConfig',None));part['metadata']['path']=part['name']
        column='resolved/sales/value'
        h.model['context']['model_assets'].append({'id':column,'kind':'SemanticColumn','name':'Value','parent_id':h.table['id'],'metadata':{'dataType':'int64'}})
        self.model=copy.deepcopy(h.model);self.model['environment']='synthetic'
        self.mapping={'layer_id':'GOLD','endpoint':{'surface':'FABRIC_SQL','server':'synthetic.example.invalid','database':'catalog'},
            'objects':{'physical-table':{'schema':'dbo','table':'facts','columns':['Value']}},
            'columns':{column:{'object_id':'physical-table','column':'Value'}},'relationships':[]}
        self.options={'measure_id':h.measure['id'],'target_id':h.visual['id'],'tolerance':{'kind':'ABSOLUTE','value':'0','source':'owner exact'}}
        self.plan=_compile(self.model,[self.mapping],self.options)
        proof={'source':'STATIC_DEFINITION','source_id':'part','definition_hash':'a'*64,'observed_at':T0,'span':{'kind':'METADATA','path':'sourceColumn'}}
        nodes=[c.node('semantic-column','owner','COLUMN','Value',proof,properties={'asset_id':column}),
            c.node('physical-table-node','owner','TABLE','facts',proof,properties={'asset_id':'physical-table'}),
            c.node('physical-column','owner','COLUMN','Value',proof)]
        edges=[c.edge('contains','owner','CONTAINS','physical-table-node','physical-column',proof),
            c.edge('bridge','owner','COMPUTED_FROM','semantic-column','physical-column',proof)]
        self.graph={'estate':'synthetic','owner':'owner','definition_hash':'a'*64,'observed_at':T0,'nodes':nodes,'edges':edges}
        self.binding={'version':'compiled-value-attachments-v1','estate':'synthetic','graph_hash':graph_hash(self.graph),'model_hash':c.digest(self.model),
            'boundaries':[{'edge_id':'bridge','source_layer':'SEMANTIC','target_layer':'GOLD'}]}
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.state=SharedState.offline(Path(self.temp.name)/'state.sqlite');self.repo=GraphRepository(self.state);self.repo.migrate();self.repo.replace(self.graph)
        row=copy.deepcopy(self.model);context=row.pop('context')
        self.state.put('catalog_model',encoded(['synthetic',row['id']]),row)
        self.state.put('catalog_context',encoded(['synthetic',row['id'],row['context_id']]),{'body':context,'hash':c.digest(context)})
        self.native={'status':'SUCCEEDED','value':42,'provider_response':json.dumps({'results':[{'tables':[{'rows':[{'[quantity]':42,'[surface_identity]':'reader'}]}]}]}),
            'request':{'query':self.plan['native_statement'],'workspace':self.model['workspace'],'native_model_id':self.model['native_id']},
            'attestation':{'declared':{'identity':'reader','engine':'OLAP','connection':self.model['workspace'],'object':self.model['native_id']},
                'reported':{'identity':'reader'},'reportable':['identity'],'binding':'VALUE_QUERY'},'snapshot':{'query_bound':False},'observed_at':T1}
        declared={'identity':'reader','engine':'SQL','connection':'server','object':'catalog'}
        self.lower={'status':'SUCCEEDED','value':'42','duplicate_lookup_keys':0,'request':{'query':self.plan['layers'][0]['statement']},
            'provider_response':{'rows':[{'quantity':'42','duplicate_lookup_keys':0}],'read_only_verified':True,'surface_report_binding':'VALUE_QUERY','surface_report':declared},
            'attestation':{'declared':declared,'reported':declared,'reportable':['identity','engine','object'],'binding':'VALUE_QUERY'},'snapshot':{'query_bound':False},'observed_at':T1}
        self.result=execute(self.plan,lambda q:copy.deepcopy(self.native),lambda q:copy.deepcopy(self.lower),lambda r:None)

    def test_successful_exact_edge_uses_real_resolver_and_persists_separate_grade_after_durable_bundle(self):
        retained=[]
        def retain(kind,body):
            self.assertFalse(TRANSACTION_ACTIVE.get());retained.append((kind,body))
            self.assertEqual('DECLARED',next(e for e in self.repo.records('synthetic')['edges']if e['id']=='bridge')['confidence'])
        result=attach(state=self.state,environment='synthetic',model=self.model,plan=self.plan,result=self.result,binding=self.binding,retain=retain,observed_at=T2)
        self.assertTrue(result['confidence_awarded']);self.assertEqual('VALUE_VERIFIED',result['status']);self.assertFalse(result['complete_path_claimed'])
        stored=next(e for e in self.repo.records('synthetic')['edges']if e['id']=='bridge')
        self.assertEqual('VALUE_VERIFIED',stored['confidence']);self.assertIn('individual rows',stored['properties']['value_verification']['qualification'])
        self.assertEqual('SNAPSHOT_UNVERIFIED',stored['properties']['value_verification']['snapshot'])
        self.assertEqual(1,len(retained));self.assertEqual(self.native['provider_response'],retained[0][1]['originals'][0]['receipt']['provider_response'])

    def test_typed_route_can_award_from_optional_hashed_existing_graph_binding(self):
        from types import SimpleNamespace
        from cloud_value_execution import run
        from test_cloud_dax_authorization import FakeMeter
        folder=Path(self.temp.name);records=[]
        def save(name,body):
            path=folder/name;path.write_text(json.dumps(body))
            import hashlib
            return {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        options={**self.options,'model':save('model.json',self.model),'mappings':save('mappings.json',[self.mapping]),
            'graph_binding':save('graph-binding.json',self.binding),'budget':{'environment':'synthetic'},'max_requests':12}
        context=SimpleNamespace(root=folder,record=lambda k,v:records.append((k,v)))
        with patch('investigator.estate_manifest.load',return_value={'environment':'synthetic'}), \
             patch('investigator.adapters.estate_installation.configuration',return_value={}), \
             patch('investigator.shared_state.configured_state',return_value=self.state), \
             patch('scan_estate_graph.Meter',FakeMeter), \
             patch('cloud_value_execution._native',return_value=copy.deepcopy(self.native)), \
             patch('cloud_value_execution._lower',return_value=copy.deepcopy(self.lower)):
            result=run({'manifest':'synthetic.json','options':options},context)
        self.assertTrue(result['confidence_awarded']);self.assertEqual('VALUE_VERIFIED',result['grade'])
        self.assertIn('NOT_INCLUDED',result['graph_proof_replay_coverage'])
        self.assertTrue(any(k=='mapped-value-proof-bundle'for k,v in records))
        self.assertEqual('VALUE_VERIFIED',next(e for e in self.repo.records('synthetic')['edges']if e['id']=='bridge')['confidence'])

    def test_changed_actual_provider_value_forged_query_or_edge_refuses(self):
        for change,reason in [('value','ORIGINAL_RESULT'),('query','RECOMPILED_PLAN'),('edge','EXISTING_GRAPH_EDGE')]:
            plan=copy.deepcopy(self.plan);result=copy.deepcopy(self.result);binding=copy.deepcopy(self.binding)
            if change=='value':result['reads'][0]['receipt']['value']=43
            elif change=='query':plan['native_statement']='EVALUATE ROW("quantity",43)'
            else:binding['boundaries'][0]['edge_id']='invented-edge'
            with self.subTest(change=change),self.assertRaisesRegex(ValueError,reason):
                build_bundle(model=self.model,plan=plan,result=result,binding=binding,graph=self.graph)

    def test_wrong_existing_endpoint_or_current_pins_refuses(self):
        wrong=copy.deepcopy(self.graph);wrong['edges'][1]['target']='semantic-column';binding=copy.deepcopy(self.binding);binding['graph_hash']=graph_hash(wrong)
        with self.assertRaisesRegex(ValueError,'QUANTITY_ENDPOINTS'):
            build_bundle(model=self.model,plan=self.plan,result=self.result,binding=binding,graph=wrong)
        binding['graph_hash']='f'*64
        with self.assertRaisesRegex(ValueError,'CURRENT_GRAPH'):
            build_bundle(model=self.model,plan=self.plan,result=self.result,binding=binding,graph=self.graph)

    def test_failed_retention_or_model_change_during_publication_never_awards(self):
        with self.assertRaisesRegex(RuntimeError,'upload failed'):
            attach(state=self.state,environment='synthetic',model=self.model,plan=self.plan,result=self.result,binding=self.binding,
                retain=lambda *a:(_ for _ in ()).throw(RuntimeError('upload failed')),observed_at=T2)
        def changed(*unused):
            row=copy.deepcopy(self.model);row.pop('context');row['enabled']=False
            key=encoded(['synthetic',row['id']]);prior=self.state.get('catalog_model',key)
            self.state.put('catalog_model',key,row,revision=prior['revision'])
        with self.assertRaisesRegex(ValueError,'CURRENT_PUBLISHED_MODEL'):
            attach(state=self.state,environment='synthetic',model=self.model,plan=self.plan,result=self.result,binding=self.binding,retain=changed,observed_at=T2)
        self.assertEqual('DECLARED',next(e for e in self.repo.records('synthetic')['edges']if e['id']=='bridge')['confidence'])

    def test_sumx_attachment_gap_is_explicit_even_when_query_path_cannot_run(self):
        plan=copy.deepcopy(self.plan);plan['program']['kind']='SUMX_RELATED'
        self.assertEqual('SUMX_RELATED_GRAPH_ATTACHMENT_NOT_IMPLEMENTED',capability(plan)['reason'])
        with self.assertRaisesRegex(ValueError,'SUMX_RELATED_GRAPH_ATTACHMENT_NOT_IMPLEMENTED'):
            build_bundle(model=self.model,plan=plan,result=self.result,binding=self.binding,graph=self.graph)


if __name__=='__main__':unittest.main()
