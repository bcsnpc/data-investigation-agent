"""Prepare private, explicitly simulated examples from hash-checked graph exports.

This operator command performs no network, provider, shared-state or estate read.
Its deliberately minimal output is a harness stub, never model enrichment.
"""
import argparse
import hashlib
import json
from pathlib import Path
from enrich_estate import recorded_stub
from investigator.enrichment import task


def sources_from_export(export, definitions):
    result=[]
    for entry in export['subjects']:
        node=entry['node']; reference=node['properties']['definition']
        raw=(Path(definitions)/reference['sha256']).read_bytes()
        if len(raw)!=reference['bytes'] or hashlib.sha256(raw).hexdigest()!=reference['sha256']:
            raise ValueError('ENRICHMENT_RETAINED_DEFINITION_HASH_DIFFERS')
        result.append(task({'estate':entry['estate'],'subject':node['id'],'kind':node['kind'],
            'definition_hash':node['provenance']['definition_hash'],'definition':raw.decode('utf8'),
            'neighbours':[], 'evidence_ids':[node['provenance']['source_id']]}))
    return result


def stub_outputs(sources, labels):
    return {s['subject']:{'business_meaning':'RECORDED_STUB: '+labels[s['subject']]+'. Meaning has not been model-enriched or human-confirmed.',
        'synonyms':[], 'calculation_explanation':'RECORDED_STUB: retained '+s['kind']+' definition; no semantic interpretation is claimed.',
        'hidden_logic':[], 'proposed_links':[]} for s in sources}


def prepare(export, definitions, output, at):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    sources=sources_from_export(export,definitions)
    labels={e['node']['id']:e['node']['label'] for e in export['subjects']}
    results=[]
    for estate in sorted({s['estate'] for s in sources}):
        selected=[s for s in sources if s['estate']==estate]
        response=recorded_stub(selected,stub_outputs(selected,labels),database=str(output/(estate+'.sqlite')),
            batch_key='round21-retained-stub-'+estate,at=at)
        if response['live_model_calls'] or response['live_enrichment_spend_microdollars']:
            raise AssertionError('STUB_MUST_NOT_CLAIM_LIVE_SPEND')
        (output/(estate+'-tasks.json')).write_text(json.dumps(selected,indent=2),encoding='utf8')
        (output/(estate+'-result.json')).write_text(json.dumps(response,indent=2),encoding='utf8')
        results.append({'estate':estate,'selected_objects':len(selected),'recording_class':'RECORDED_STUB',
            'live_model_calls':0,'live_enrichment_spend_microdollars':0,
            'examples':[{'subject':s['subject'],'label':labels[s['subject']],'kind':s['kind'],
                'definition_sha256':hashlib.sha256(s['definition'].encode()).hexdigest(),
                'business_meaning':response['examples'][i]['business_meaning'],
                'status':response['examples'][i]['status']} for i,s in enumerate(selected)]})
    return {'simulation_at':at,'source':export.get('source'),'status':'RECORDED_STUB_ONLY_NOT_LIVE_ENRICHMENT',
        'estate_reads':0,'live_model_calls':0,'live_spend_microdollars':0,'estates':results,
        'scope':'Five selected retained objects per estate, not full-estate coverage; no links proposed or promoted.'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--export',required=True);p.add_argument('--definitions',required=True)
    p.add_argument('--output',required=True);p.add_argument('--summary',required=True);p.add_argument('--at',required=True)
    a=p.parse_args()
    summary=prepare(json.loads(Path(a.export).read_text(encoding='utf8')),a.definitions,a.output,a.at)
    Path(a.summary).write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8')
