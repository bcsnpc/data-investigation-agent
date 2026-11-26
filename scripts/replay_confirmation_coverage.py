"""Offline counterfactual replay of saved queries and delivery boundaries.

This uses saved responses, not a replacement model. A newly required query or
evaluator response is reported as missing, never generated from an expectation.
Original captures, evidence IDs, outcomes and grades are never overwritten.
"""
import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import socket
from unittest.mock import patch

from investigator.delivery_coverage import candidate_resolution,canonical_selected_target
from investigator.delivery_references import calculation_measure, reformat
from investigator.conclusion_contract import validate
from investigator.estate_graph_contract import digest
from investigator.grounded_answers import finding
from investigator.intake_candidates import select_unique
from investigator.investigative_queries import Queries


def replay_queries(case):
    """Compile each saved query with the current read-only compiler, no port."""
    rows=[]
    for prior in case.get('queries', []):
        calls=[]
        def execute(layer, bound, **kwargs):
            if (bound.get('query')!=prior.get('executed_text')
                    or bound.get('parameters',[])!=prior.get('parameters',[])
                    or bound.get('asset_ids',[])!=prior.get('asset_ids',[])):
                raise RuntimeError('SAVED_QUERY_BINDING_DIFFERS_NO_RESULT_SUBSTITUTION')
            calls.append(bound)
            if prior['status']!='SUCCEEDED':
                raise RuntimeError('SAVED_NATIVE_ERROR')
            return deepcopy(prior['result'])
        queries=Queries(deepcopy(case['context']['layers']), execute=execute,
                        reserve=lambda *a:None, save=lambda *a:None)
        try:
            observed=queries.run(prior['layer'],prior['text'],
                kind='dax' if case['context']['layers'][prior['layer']]['dialect']=='DAX' else 'sql',
                purpose=prior['purpose'])
            observed=observed.get('record',observed)
            rows.append({'id':prior['id'],'before':prior['status'],
                         'after':observed.get('status'),'saved_result_used':bool(calls),
                         'reason':observed.get('error')})
        except (ValueError,RuntimeError,KeyError) as error:
            rows.append({'id':prior['id'],'before':prior['status'],'after':'REFUSED',
                         'reason':str(error)[:300],'saved_result_used':bool(calls)})
    return rows


def current_candidates(case, assets):
    """New derived evidence gets new IDs; never relabel a sealed old result."""
    from investigator.adapters.native_literal_visual import nonmatching_literal
    context=case['context'];inventory=context.get('candidate_inventory')
    if not inventory:return {}
    by_id={a['id']:a for a in assets}
    excluded=[]
    for candidate in inventory['candidates']:
        identity=candidate['id']
        if identity==candidate.get('explicit',{}).get('visual'):continue
        asset=by_id.get(candidate.get('retained_scope',{}).get('properties',{}).get('asset_id'))
        if asset and nonmatching_literal(asset,case['intake'].get('reported_figure')):
            excluded.append(identity)
    inventory['candidates']=[c for c in inventory['candidates']if c['id']not in excluded]
    inventory['total_candidates']=inventory.get('total_candidates',len(inventory['candidates'])+len(excluded))-len(excluded)
    identities={c['id']for c in inventory['candidates']};remap={}
    for old,record in list(case['evidence'].items()):
        if record.get('tool')!='check_target_candidates':continue
        observations=[o for o in record['result']['observations']if o['candidate']in identities]
        result=select_unique(inventory,observations,case['intake'].get('reported_figure'))
        if result==record['result']:continue
        derived={**deepcopy(record),'result':result}
        identity='case-evidence:'+digest(derived)
        case['evidence'].pop(old);case['evidence'][identity]=derived;remap[old]=identity
    return {'excluded_static_candidates':excluded,'derived_evidence_remap':remap}


def replay_file(path, assets):
    raw=path.read_bytes();saved=json.loads(raw);outcome=saved.get('result',saved)
    row={'ticket':path.stem.removesuffix('-result'),'saved_sha256':sha256(raw).hexdigest(),
         'saved_status':outcome.get('status'),'capture_seal':saved.get('capture_seal'),
         'estate_reads':0,'model_calls':0}
    original=outcome.get('case')
    if not original:
        row.update(classification='NO_INVESTIGATION_CASE',drafts=[],query_replay=[])
        return row
    case=deepcopy(original)
    row['query_replay']=replay_queries(case)
    adjustment=current_candidates(case,assets)
    row.update(adjustment)
    drafts=[]
    for record in original.get('evidence',{}).values():
        if record.get('kind')!='MODEL_RESPONSE':continue
        for call in record['response'].get('content',[]):
            if call.get('type')!='tool_use' or call.get('name')!='submit_finding':continue
            args=deepcopy(call['input'])
            args['evidence_ids']=[adjustment.get('derived_evidence_remap',{}).get(i,i)for i in args.get('evidence_ids',[])]
            item={'saved_tool_id':call.get('id'),'verdict':args.get('verdict'),
                  'verdict_class':args.get('verdict_class')}
            try:
                context=case['context'];path_nodes=context.get('path',{}).get('nodes',[])
                args,changes=reformat(args,queries=case['queries'],evidence=case['evidence'],
                    layers=context['layers'],nodes=path_nodes,
                    definition_measure=calculation_measure(context,args))
                args,selection=canonical_selected_target(args,case)
                if selection:item['code_selected_from_unique_cited_match']=selection
                candidate_resolution(args,case)
                validate(args,case)
                finding(args,case)
                item.update(code_boundary='ACCEPTED',reference_reformats=len(changes))
            except (ValueError,KeyError,TypeError,__import__('jsonschema').ValidationError) as error:
                item.update(code_boundary='REFUSED',reason=str(error)[:650])
            drafts.append(item)
    row.update(classification='SAVED_BOUNDARIES_REPLAYED',drafts=drafts,
               any_supported_draft=any(d['code_boundary']=='ACCEPTED' for d in drafts),
               fresh_evaluator_required_for_changed_draft=True,
               limitation='Boundary counterfactual, not a generated continuation or new independent grade. Saved model replies cannot supply a newly required source read, target choice, or evaluator response.')
    return row


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path);parser.add_argument('--assets',type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    assets=json.loads(args.assets.read_bytes())['assets'] if args.assets else []
    report={'scope':'OFFLINE_SAVED_NATIVE_QUERY_AND_DELIVERY_BOUNDARIES',
            'estate_reads':0,'model_calls':0,'official_scores_changed':False,'rows':[]}
    with patch.object(socket.socket,'connect',side_effect=RuntimeError('OFFLINE_REPLAY_NETWORK_FORBIDDEN')):
        for path in sorted(args.directory.glob('*-result.json')):
            saved=json.loads(path.read_bytes())
            if saved.get('capture_seal') and 'execution'in saved:
                report['rows'].append(replay_file(path,assets))
    report['counts']=dict(Counter(r['classification']for r in report['rows']))
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'tickets':len(report['rows']),'counts':report['counts'],
                      'code_eligible':sum(r.get('any_supported_draft',False)for r in report['rows'])}))


if __name__=='__main__':main()
