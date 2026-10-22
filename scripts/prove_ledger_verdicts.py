"""Offline controlled-evidence proof through the real Investigator consumer.

These are synthetic contracts, not live estate findings or acceptance changes.
No provider, network, credential or database route is installed.
"""
import argparse
import json
from pathlib import Path
from types import SimpleNamespace

from investigator.evidence_verdicts import Evidence,VERDICTS
from investigator.ledger_investigator import Investigator

NOW='2026-10-22T11:00:00Z'


def read(subject,value,context=None):
    return {'subject':subject,'key':'record-1','state':'VALUE','value':value,'context':context or {'warehouse':'North'},
        'receipt_id':'synthetic-read:'+subject,'route_admitted':True,'read_only_verified':True,
        'expression_hash':'a'*64,'execution_surface':'synthetic-surface','warnings':['SNAPSHOT_UNVERIFIED']}


def scenario(verdict):
    events=[]
    def persist(value):events.append(value);return 'synthetic:'+str(len(events))
    registry=Evidence(['visual','down','up','job'],persist)
    target='visual';ids=[]
    def add(kind,subjects,value):
        identity=registry.add(kind,subjects,value);ids.append(identity);return identity
    def fact(subject,kind,value):
        return add('FACT',[subject],{'subject':subject,'kind':kind,'value':value,'state':'OBSERVED','freshness':'CURRENT',
            'collected_at':NOW,'observed_at':NOW,'source':'RUNTIME_OBSERVATION','reason':None,
            'provenance':{'evidence_ids':['synthetic-native-fact'],'collector':'synthetic-only','locator':subject}})
    if verdict=='as designed':
        # The fixture generates original native process receipts; the real
        # support validator consumes them twice, including the final verdict.
        from test_process_debugging import Adapter
        from investigator.process_debugging import vertical
        from investigator.native_verdict_support import design_witness
        native=vertical(Adapter(['down','up'],{'down':7,'up':8},explain=True),'measure',{})
        observations={entry['id']:entry for entry in native.pop('_observations')};target='down';refs=[]
        for subject,value in [('down',7),('up',8)]:
            original=observations['read-'+subject];original['declared_context']={'warehouse':'North'};original['test_purpose']='REPRODUCE_MEASURE'
            refs.append(add('READ',[subject],{**read(subject,value),'receipt_id':original['id'],
                'query':original['query'],'execution_surface':original['execution_surface']}))
        comparison=add('COMPARISON',['down','up'],{'left':refs[0],'right':refs[1],'support_ids':refs})
        witness=design_witness(native,observations);witness['support_ids']=[comparison]
        add('DESIGN_CHECK',['down','up'],witness)
    elif verdict=='access difference':
        refs=[]
        for principal,value in [('synthetic-a',7),('synthetic-b',8)]:
            refs.append(add('READ',['visual'],{**read('visual',value),'receipt_id':principal,
                'authenticated_identity':principal,'identity_verified':True,'query':'SELECT SUM(units) FROM dbo.records',
                'execution_surface':{'engine':'synthetic-sql','connection':'same','object':'same','identity':principal}}))
        comparison=add('COMPARISON',['visual'],{'left':refs[0],'right':refs[1],'support_ids':refs})
        add('ACCESS_CHECK',['visual'],{'checked':True,'mechanism':'Two separately authorized synthetic identities.',
            'impersonated':False,'support_ids':[comparison]})
    else:
        refs=[add('READ',[subject],read(subject,value)) for subject,value in [('visual',7),('down',7),('up',8)]]
        comparison=add('COMPARISON',['down','up'],{'left':refs[1],'right':refs[2],'support_ids':refs})
        add('BOUNDARY',['down','up','job'],{'downstream':'down','upstream':'up','job':'job','quantity_preserving':True,
            'kind':'MODEL_REFRESH' if verdict=='refresh stale' else 'LOAD'})
        fact('up','TABLE_LOAD',{'last_modified':'2026-10-22T10:00:00Z'})
        if verdict=='failed job':fact('job','JOB_RUN',{'status':'FAILED','run_id':'r','start':'2026-10-22T10:01:00Z','end':'2026-10-22T10:02:00Z','error':'synthetic copy failure'})
        elif verdict=='waiting on job':fact('job','JOB_RUN',{'status':'QUEUED','run_id':'r','start':'2026-10-22T10:01:00Z','end':None})
        elif verdict=='refresh stale':fact('job','REFRESH_RUN',{'status':'SUCCEEDED','run_id':'refresh','start':'2026-10-22T08:00:00Z','end':'2026-10-22T09:00:00Z'})
        elif verdict=='latency':
            fact('job','JOB_RUN',{'status':'SUCCEEDED','run_id':'r','start':'2026-10-22T08:00:00Z','end':'2026-10-22T09:00:00Z'})
            fact('job','SCHEDULE',{'next_due':'2026-10-22T12:00:00Z'});fact('job','TYPICAL_DURATION',{'median_seconds':60,'sample_count':3})
        elif verdict=='different question':
            other=add('READ',['down'],read('down',8,{'warehouse':'South'}))
            add('COMPARISON',['down'],{'left':refs[1],'right':other,'support_ids':[refs[1],other]})
        elif verdict=='source changed history':
            path=add('PATH',['up'],{'nodes':[{'id':'up','properties':{'system_of_record':True}}]})
            history={'subject':'up','receipt_id':'synthetic-history','read_only_verified':True,'route_admitted':True,
                'key':'record-1','context':{'warehouse':'North'},'query':'SELECT before_units,after_units FROM dbo.source_history',
                'read_only_objects':['[dbo].[source_history]'],'execution_surface':'synthetic-surface','before_quantity':7,'after_quantity':8,
                'changes':[{'key':'record-1','before':{'units':7},'after':{'units':8},'effective_at':'2026-10-21T00:00:00Z','changed_at':'2026-10-22T10:00:00Z'}]}
            add('HISTORY_CHECK',['up'],{'checked':True,'mechanism':'Synthetic retained back-dated source correction.',
                'native_history':history,'support_ids':[comparison,path]})
    path_id=add('PATH',[target],{'nodes':[{'id':node,'kind':'VISUAL' if node==target else 'TABLE','label':node} for node in registry.path],
                                      'edges':[],'stops':[],'truncated':False})
    tools=SimpleNamespace(evidence=registry,nodes={node:{'id':node,'label':node,'kind':'TABLE'} for node in registry.path},
        visual=target,key='record-1',context={'warehouse':'North'},comparison={'kind':'source','node':'up'},request_kind='COMPARE',
        depth={target:0,'up':1},now=NOW,path_id=path_id,boundary_ids=[],gap_ids=[],schemas={},
        reproduce=lambda:[identity for identity in ids if registry.get(identity)['kind']=='READ'],
        quick_checks=lambda:[identity for identity in ids if registry.get(identity)['kind']!='READ'])
    result=Investigator(tools,decide=None,persist=persist,admit=lambda *_:None,clock=lambda:1.0).run(
        {'visual':target,'text':'Synthetic controlled contract: '+verdict,'request':{'kind':'COMPARE'}})
    return {'expected':verdict,'actual':result['verdict'],'matched':result['verdict']==verdict,
        'support_ids':result['support']['evidence_ids'],'stop_reason':result['stop_reason'],
        'model_calls':result['cost']['model_calls'],'estate_reads':0,'event_count':len(events)}


def prove():
    rows=[scenario(verdict) for verdict in VERDICTS]
    return {'kind':'SYNTHETIC_CONTROLLED_EVIDENCE_NOT_LIVE','consumer':'Investigator.run','cases':rows,
        'passed':sum(row['matched'] for row in rows),'total':len(rows),'model_calls':0,'estate_reads':0}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    value=prove();Path(args.output).write_text(json.dumps(value,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'passed':value['passed'],'total':value['total'],'model_calls':0,'estate_reads':0}))
    return 0 if value['passed']==value['total'] else 1


if __name__=='__main__':raise SystemExit(main())
