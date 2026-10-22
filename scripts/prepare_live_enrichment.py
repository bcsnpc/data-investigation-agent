"""Offline full-retained-graph enrichment preparation; no network or credentials."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from investigator.enrichment import task,cache_key
from investigator.adapters.enrichment_anthropic import request_for,price

KINDS=frozenset({'REPORT','PAGE','VISUAL','SLICER','MEASURE','CALCULATED_COLUMN'})


def prepare(graphs,definitions,output,*,key_tables=None,cache=None):
    output=Path(output);output.mkdir(parents=True,exist_ok=True);definitions=Path(definitions)
    keys=key_tables or {};summaries=[];batches=[];needed={}
    for estate,graph in sorted(graphs.items()):
        nodes={node['id']:node for node in graph['nodes']}
        if not set(keys.get(estate,[]))<=nodes.keys():raise ValueError('ENRICHMENT_CONFIGURED_KEY_TABLE_ABSENT')
        if any(nodes[node]['kind']!='TABLE' for node in keys.get(estate,[])):raise ValueError('ENRICHMENT_CONFIGURED_KEY_TABLE_KIND')
        selected=[node for node in nodes.values() if node['kind'] in KINDS or node['id'] in keys.get(estate,[])]
        sources=[];gaps=[];cached=[]
        for node in sorted(selected,key=lambda value:value['id']):
            reference=node['properties'].get('definition');definition=reference
            if isinstance(reference,dict):
                path=definitions/str(reference.get('sha256'))
                if not path.exists():
                    needed[reference['sha256']]=reference;gaps.append({'subject':node['id'],'kind':node['kind'],'reason':'DEFINITION_BYTES_NOT_LOCAL','reference':reference});continue
                raw=path.read_bytes()
                if len(raw)!=reference['bytes'] or hashlib.sha256(raw).hexdigest()!=reference['sha256']:raise ValueError('ENRICHMENT_RETAINED_DEFINITION_HASH_DIFFERS')
                definition=raw.decode('utf8')
            if not isinstance(definition,str) or not definition:
                gaps.append({'subject':node['id'],'kind':node['kind'],'reason':'DEFINITION_NOT_RETAINED'});continue
            neighbours=set()
            for edge in graph['edges']:
                if edge['source']==node['id']:neighbours.add(edge['target'])
                if edge['target']==node['id']:neighbours.add(edge['source'])
            neighbours=[{'id':nodes[name]['id'],'kind':nodes[name]['kind'],'label':nodes[name]['label']} for name in sorted(neighbours) if name in nodes]
            source={'estate':estate,'subject':node['id'],'kind':node['kind'],'definition_hash':node['provenance']['definition_hash'],
                'definition':definition,'neighbours':neighbours,'evidence_ids':[node['provenance']['source_id']]}
            try:source=task(source)
            except ValueError as error:
                gaps.append({'subject':node['id'],'kind':node['kind'],'reason':str(error),'definition_characters':len(definition),'neighbours':len(neighbours)});continue
            prior=(cache or {}).get(cache_key(source))
            if prior and prior.get('recording_class')!='RECORDED_STUB':cached.append(node['id']);continue
            sources.append(source)
        batch_refs=[]
        for index in range(0,len(sources),50):
            chunk=sources[index:index+50];name=estate+'-tasks-'+str(index//50+1).zfill(2)+'.json'
            raw=json.dumps(chunk,sort_keys=True,ensure_ascii=False,indent=2).encode();(output/name).write_bytes(raw)
            requests=[request_for(source,cache_key(source)) for source in chunk]
            from investigator.shared_state import encoded
            upper=sum(price(len(encoded(request).encode())+4096,request['params']['max_tokens']) for request in requests)
            batch={'estate':estate,'index':index//50+1,'tasks':len(chunk),'task_file':name,'sha256':hashlib.sha256(raw).hexdigest(),
                'reservation_upper_microdollars':upper,'batch_key':'round21-live-'+estate+'-'+hashlib.sha256(raw).hexdigest()[:16]}
            batches.append(batch);batch_refs.append(batch)
        summaries.append({'estate':estate,'retained_nodes':len(nodes),'candidate_counts_by_kind':dict(Counter(node['kind'] for node in selected)),
            'candidate_count':len(selected),'configured_key_tables':keys.get(estate,[]),'ready_tasks':len(sources),
            'cache_skips':len(cached),'cache_checked':cache is not None,'cache_skip_subjects':cached,'gaps':gaps,'batches':batch_refs,
            'other_tables_not_selected':sum(node['kind']=='TABLE' and node['id'] not in keys.get(estate,[]) for node in nodes.values()),
            'raw_retained_graph_owner_health_not_established':True})
    result={'status':'PREPARED_WITH_GAPS' if any(summary['gaps'] for summary in summaries) else 'PREPARED_NOT_SUBMITTED',
        'estates':summaries,'batches':batches,'required_definitions':list(needed.values()),'estate_reads':0,'provider_calls':0,
        'reservation_upper_microdollars':sum(batch['reservation_upper_microdollars'] for batch in batches),
        'account':'enrichment:round-twenty-one','account_ceiling_microdollars':25000000,'recorded_stubs_count_as_live_enrichment':False}
    (output/'preparation.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf8')
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--graphs',required=True);parser.add_argument('--definitions',required=True)
    parser.add_argument('--output',required=True);parser.add_argument('--collector-runner');parser.add_argument('--cache')
    args=parser.parse_args();keys={}
    if args.collector_runner:
        runner=json.loads(Path(args.collector_runner).read_bytes())
        for check in runner['checks'].values():
            for config in check['options'].get('configs',[]):keys[config['estate']]=config.get('key_tables',[])
    result=prepare(json.loads(Path(args.graphs).read_bytes()),args.definitions,args.output,key_tables=keys,
        cache=json.loads(Path(args.cache).read_bytes()) if args.cache else None)
    print(json.dumps({'status':result['status'],'ready_tasks':sum(e['ready_tasks'] for e in result['estates']),
        'missing_unique_definitions':len(result['required_definitions']),'reservation_upper_microdollars':result['reservation_upper_microdollars']}))


if __name__=='__main__':main()
