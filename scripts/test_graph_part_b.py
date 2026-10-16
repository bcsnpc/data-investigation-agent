import copy
import hashlib
import unittest
from investigator.adapters.graph_dependencies import collect,dependency_edges,query
from investigator.graph_interpreter import propose
from investigator.graph_verification import VerificationResolver,verify_path,QUALIFICATION
from investigator.live_gateway import Gateway,GatewayDenied
from test_estate_graph import graph,T0,T1


def verification_fixture(edge_id='vm',scope='b'*64):
    edge=next(e for e in graph()['edges'] if e['id']==edge_id)
    common={'estate':'estate','edge_id':edge_id,'source':edge['source'],'target':edge['target'],
            'scope_hash':scope,'definition_hash':'a'*64}
    binding={'id':'binding','producer':'LINEAGE_EDGE_COMPILER',**common,
        'source_statement_hash':'d'*64,'target_statement_hash':'e'*64,
        'dependency_witness':{'kind':'DECLARED_DEFINITION','definition_hash':'a'*64,
            'source':edge['source'],'target':edge['target'],'span':{'kind':'JSON_POINTER','path':'/visual'}}}
    check={'id':'q','producer':'LINEAGE_QUERY_CHECK',**common,'binding_id':'binding',
           'source_read':'s','target_read':'t','observed_at':T0}
    reads={key:{'id':key,'producer':'QUERY_READ','status':'SUCCEEDED','estate':'estate','object_id':edge[side],
           'scope_hash':scope,'definition_hash':'a'*64,'statement_hash':binding[side+'_statement_hash'],
           'value':{'state':'VALUE','typed_value':{'type':'integer','value':'42'}},
           'attestation':{'identity':'MATCHED','engine':'MATCHED','connection':'MATCHED','object':'MATCHED'},
           'snapshot':None,'observed_at':T0} for key,side in [('s','source'),('t','target')]}
    resolver=VerificationResolver(lambda key:copy.deepcopy(check) if key=='q' else None,
        lambda key:copy.deepcopy(binding) if key=='binding' else None,lambda key:copy.deepcopy(reads[key]))
    return resolver,check,binding,reads


class MetadataTests(unittest.TestCase):
    def setUp(self):
        self.target={'workspace':'scope','model':'model'};self.calls=[];self.meters=[]
        self.gateway=Gateway({'version':1,'live_enabled':True,'identities':{'reader':{'native_controls':[
            {'operation':'XMLA_GRAPH_METADATA',**self.target}]}}})
    def run_query(self,**kw):
        def transport(request):
            self.calls.append(request);return kw.pop('response',{'status':'SUCCEEDED','rows':[], 'error':None,'receipt_id':'receipt'})
        def meter(request,fn):self.meters.append(request);return fn()
        response=kw.pop('response',None)
        if response is not None:
            def transport(request):self.calls.append(request);return response
        return collect(kind=kw.pop('kind','RELATIONSHIPS'),target=self.target,identity='reader',gateway=self.gateway,
            meter=meter,transport=transport,**kw)
    def test_known_permission_and_rest_restrictions_cost_no_requests(self):
        result=self.run_query(kind='CALCULATIONS');self.assertEqual(result['status'],'UNKNOWN')
        self.assertIn('write permission',result['unknown']['reason'])
        self.assertEqual(self.run_query(route='REST')['status'],'UNKNOWN');self.assertEqual(self.calls,[]);self.assertEqual(self.meters,[])
    def test_fixed_query_exact_scope_and_one_meter_per_attempt(self):
        result=self.run_query();self.assertEqual(result['status'],'COLLECTED');self.assertEqual(len(self.calls),1)
        self.assertEqual(len(self.meters),1);self.assertEqual(self.calls[0]['query'],query('RELATIONSHIPS'))
        with self.assertRaises(ValueError):self.gateway.native_control('reader','XMLA_GRAPH_METADATA',self.target,'EVALUATE ROW("x",1)')
        with self.assertRaises(GatewayDenied):self.gateway.native_control('reader','XMLA_GRAPH_METADATA',{'workspace':'other','model':'model'},query('RELATIONSHIPS'))
    def test_refusal_retained_and_truncation_never_complete(self):
        failure={'status':'PERMISSION_DENIED','rows':[],'error':{'code':'Denied','message':'Reader lacks metadata permission'},'receipt_id':'refused'}
        result=self.run_query(response=failure);self.assertEqual(result['receipt'],failure)
        result=self.run_query(row_cap=1,response={'status':'SUCCEEDED','rows':[{},{}],'error':None,'receipt_id':'large'})
        self.assertEqual(result['status'],'UNKNOWN');self.assertEqual(result['rows'],[])
    def test_unresolved_and_omitted_dependencies_are_gaps(self):
        result=self.run_query(kind='CALCULATIONS',semantic_write_permission=True,response={'status':'SUCCEEDED','rows':[
            {'DATABASE_NAME':'model','OBJECT_TYPE':'MEASURE','TABLE':'T','OBJECT':'M',
             'REFERENCED_OBJECT_TYPE':'COLUMN','REFERENCED_TABLE':'T','REFERENCED_OBJECT':'V'}], 'error':None,'receipt_id':'r'})
        args={'estate':'estate','owner':'dependencies','model':'model','bindings':{('MEASURE','T','M'):'m',('COLUMN','T','V'):'v'},
              'expected':[('MEASURE','T','M'),('MEASURE','T','Absent')],'definition_hash':'a'*64,'observed_at':T0,
              'definition_sink':lambda raw:{'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'uri':'cas://definition/reply'}}
        got=dependency_edges(result,**args);self.assertEqual(len(got['edges']),1);self.assertEqual(len(got['gaps']),1)
        self.assertEqual(got['edges'][0]['confidence'],'DECLARED')
        result['rows'][0]['REFERENCED_OBJECT']='not collected'
        self.assertEqual(len(dependency_edges(result,**args)['gaps']),3)


class InterpreterTests(unittest.TestCase):
    def run_proposal(self,change=None):
        code='target = source + 1';item={'source':'out','target':'in','kind':'COMPUTED_FROM','start':0,'end':len(code),'quote':code,'explanation':'Output uses the retained input expression.'}
        if change:item.update(change)
        calls=[]
        answer=propose(estate='estate',owner='code',code=code,definition_hash=hashlib.sha256(code.encode()).hexdigest(),
            source_id='codepart',observed_at=T0,nodes=[{'id':'out','kind':'COLUMN','label':'Output'},{'id':'in','kind':'COLUMN','label':'Input'}],
            producer=lambda request,schema:{'edges':[item]},model_call=lambda request,fn:(calls.append(request),fn())[1])
        self.assertEqual(len(calls),1);return answer
    def test_exact_span_only_inferred_and_no_completeness_claim(self):
        got=self.run_proposal();self.assertEqual(got['edges'][0]['confidence'],'INFERRED');self.assertEqual(got['coverage'],'INCOMPLETE')
    def test_bad_quote_unknown_id_or_extra_confidence_refused(self):
        for change in ({'quote':'invented'},{'target':'outside'},{'confidence':'VERIFIED'}):
            with self.assertRaises(Exception):self.run_proposal(change)


class VerificationTests(unittest.TestCase):
    def test_receipt_binds_every_edge_statement_scope_and_attestation(self):
        resolver,_,_,reads=verification_fixture();proof=resolver('q')
        self.assertEqual(proof['qualification'],QUALIFICATION);self.assertEqual(proof['snapshot'],'SNAPSHOT_UNVERIFIED')
        for key,value,error in [('statement_hash','f'*64,'BINDING'),('scope_hash','c'*64,'BINDING'),('object_id','other','BINDING')]:
            old=reads['s'][key];reads['s'][key]=value
            with self.assertRaisesRegex(ValueError,error):resolver('q')
            reads['s'][key]=old
        reads['s']['attestation']['engine']='UNATTESTED'
        with self.assertRaisesRegex(ValueError,'ATTESTATION'):resolver('q')
    def test_equal_values_without_dependency_witness_cannot_verify(self):
        resolver,_,binding,_=verification_fixture();binding['dependency_witness']['kind']='VALUES_EQUAL'
        with self.assertRaisesRegex(ValueError,'WITNESS'):resolver('q')
    def test_blank_is_value_not_zero_or_missing(self):
        resolver,_,_,reads=verification_fixture()
        for receipt in reads.values():receipt['value']={'state':'BLANK','typed_value':None}
        resolver('q');reads['s']['value']={'state':'VALUE','typed_value':{'type':'integer','value':'0'}}
        with self.assertRaisesRegex(ValueError,'DISAGREE'):resolver('q')
        reads['s']['status']='FAILED'
        with self.assertRaisesRegex(ValueError,'SUCCESSFUL'):resolver('q')
    def test_path_budget_and_disconnected_admitted_before_read(self):
        resolver,_,binding,_=verification_fixture();calls=[]
        kwargs={'estate':'estate','scope_hash':'b'*64,'compiler':lambda edge,scope:binding,
            'query_read':lambda binding,side:(calls.append(side),'s' if side=='source' else 't')[1],
            'record_check':lambda binding,s,t:'q','resolver':resolver}
        edge=graph()['edges'][2]
        with self.assertRaisesRegex(ValueError,'READ_CAP'):verify_path(edges=[edge],max_reads=1,**kwargs)
        self.assertEqual(calls,[])
        result=verify_path(edges=[edge],**kwargs);self.assertEqual(len(result['edges']),1);self.assertEqual(calls,['source','target'])


if __name__=='__main__':unittest.main()
