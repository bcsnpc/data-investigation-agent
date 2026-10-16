import copy
import hashlib
import unittest
from test_estate_graph_static import asset,part,NOW
from investigator.adapters.estate_graph_static import extract


class DependencyIntegrationTests(unittest.TestCase):
    def assets(self):
        self.model='fabric://00000000-0000-0000-0000-000000000001/00000000-0000-0000-0000-000000000002'
        raw='{"model":{"tables":[]}}'
        rows=[{'DATABASE_NAME':'Selected model','OBJECT_TYPE':'MEASURE','TABLE':'T','OBJECT':'M',
               'REFERENCED_OBJECT_TYPE':'COLUMN','REFERENCED_TABLE':'T','REFERENCED_OBJECT':'V'}]
        result={'status':'COLLECTED','request':{'kind':'CALCULATIONS','target':{
            'workspace':self.model.split('/')[-2],'model':self.model.split('/')[-1]}},'rows':rows,
            'unknown':None,'receipt':{'status':'SUCCEEDED','rows':rows,'error':None,'receipt_id':'sealed-metadata'}}
        self.observation=asset('metadata','EngineDependencyMetadata','CALCULATIONS',self.model,{
            'result':result,'model_name':'Selected model','model_definition_hash':hashlib.sha256(raw.encode()).hexdigest()})
        return [asset(self.model,'SemanticModel','Selected model'),asset('t','SemanticTable','T',self.model),
            asset('m','Measure','M','t',{'expression':'SUM(T[V])'}),asset('v','SemanticColumn','V','t'),
            part('bim',self.model,'model.bim',raw),self.observation]

    def build(self,assets):
        def sink(raw):
            digest=hashlib.sha256(raw).hexdigest()
            return {'sha256':digest,'bytes':len(raw),'uri':'cas://definitions/'+digest}
        return extract('estate',assets,sink,observed_at=NOW)

    def test_exact_engine_rows_cover_measure_without_promoting_to_verified(self):
        graph=self.build(self.assets())
        nodes={n['properties'].get('asset_id'):n['id'] for n in graph['nodes']}
        edge=next(e for e in graph['edges'] if e['source']==nodes['m'] and e['target']==nodes['v'])
        self.assertEqual(edge['confidence'],'DECLARED');self.assertEqual(edge['provenance']['source'],'ENGINE_DEPENDENCY')
        self.assertFalse(any(e['source']==nodes['m'] and e['confidence']=='UNKNOWN' for e in graph['edges']))

    def test_one_unresolved_dependency_keeps_producer_gap_even_with_valid_row(self):
        assets=self.assets();result=self.observation['metadata']['result']
        result['rows'].append({**result['rows'][0],'REFERENCED_OBJECT':'Missing'})
        graph=self.build(assets);m=next(n['id'] for n in graph['nodes'] if n['properties'].get('asset_id')=='m')
        self.assertTrue(any(e['source']==m and e['confidence']=='UNKNOWN' for e in graph['edges']))

    def test_changed_definition_or_wrong_model_never_covers_producer(self):
        for mutation in ('pin','model','target'):
            assets=self.assets();meta=self.observation['metadata']
            if mutation=='pin':meta['model_definition_hash']='a'*64
            if mutation=='model':meta['model_name']='Other model'
            if mutation=='target':meta['result']['request']['target']['model']='other'
            graph=self.build(assets)
            self.assertFalse(any(e['provenance']['source']=='ENGINE_DEPENDENCY' for e in graph['edges']))
            self.assertTrue(any('does not bind' in n['label'] for n in graph['nodes']))

    def test_empty_metadata_does_not_claim_dependency_free_measure(self):
        assets=self.assets();self.observation['metadata']['result']['rows']=[]
        graph=self.build(assets)
        self.assertTrue(any('Engine-resolved expression' in n['label'] for n in graph['nodes']))


if __name__=='__main__':unittest.main()
