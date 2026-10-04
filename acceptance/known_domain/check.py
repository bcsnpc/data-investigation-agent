"""Strict known-domain acceptance gate; missing replay evidence is not a pass."""
import argparse,json,re,sys,socket
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'acceptance/unknown_domain')]
INVARIANTS=frozenset(('both_outputs','no_serialized_structure','no_business_identifier_form','timing_hedge_once','valid_mechanism_layer_tokens','layer_names_by_declared_role'))


def validate_case(case):
    from investigator.process_outcomes import OUTCOMES
    if (set(case['invariants'])!=INVARIANTS or len(case['invariants'])!=len(INVARIANTS)
            or case['expected_outcome'] not in tuple(OUTCOMES)+(None,)
            or not case.get('acceptance_change_reason','').strip()
            or not case['expected_answer_line'].startswith('Answer to your question: ')):
        raise ValueError('Acceptance contract is incomplete or has an unsupported invariant/outcome')


def output_checks(case,state):
    errors=[]
    if state.get('status')!=case['expected_status']:errors.append('STATUS_CHANGED')
    if (state.get('assessment') or {}).get('classification')!=case['expected_outcome']:errors.append('OUTCOME_CHANGED')
    outputs=(state.get('synthesis') or {}).get('outputs',{})
    for kind in ('business_output','technical_output'):
        text=outputs.get(kind,{}).get('explanation',{}).get('text')
        if not isinstance(text,str) or not text:errors.append(kind+':MISSING_OUTPUT');continue
        if case['expected_answer_line'] not in text:errors.append(kind+':ANSWER_CHANGED')
        body=text.split('\n\n',1)[-1]
        from investigator.narrative_form import validate
        try:validate(body,kind=='business_output')
        except ValueError as exc:errors.append(kind+':FORM:'+str(exc))
        timing=[s for s in re.split(r'(?<=[.!?])\s+',body) if re.search(
            r'same moment|different update times|update timing|matching data versions|SNAPSHOT_UNVERIFIED',s,re.I)]
        if len(timing)>1:errors.append(kind+':REPEATED_TIMING_LIMIT')
        if kind=='technical_output':
            from investigator.path_narrative import validate_layer_references
            # Only the model paragraph uses this vocabulary: engine-rendered
            # legends and limits deliberately state role names and identities.
            commentary=body.split('\n\n')
            boundaries=[o for o in state.get('observations',[]) if o.get('comparison_status')=='CROSS_SURFACE_VERIFIED']
            labels=(state.get('assessment') or {}).get('technical_output',{}).get('layer_labels',{})
            for boundary in boundaries:
                for side in ('upper_layer','lower_layer'):
                    if not labels.get(boundary.get(side),{}).get('role'):
                        errors.append('technical_output:UNDECLARED_LAYER_ROLE')
            if len(commentary)>1 and commentary[1].strip():
                # Complete replay is required to validate against its receipt
                # digest; never infer labels from words in this output.
                if labels and not re.search(r'\bL\d+ \([A-Z]+\)',body):errors.append('technical_output:MISSING_LAYER_ROLE')
                payload={'layer_labels':labels,'evidence':[{'id':o['id'],'tool':o.get('tool'),'result':o}
                    for o in state.get('observations',[])]}
                try:validate_layer_references(commentary[1],payload)
                except ValueError as exc:errors.append('technical_output:LAYER_REFERENCE:'+str(exc))
        for required in case.get('required_output_terms',[]):
            if required not in text:errors.append(kind+':MISSING_REQUIRED_TERM:'+required)
    return sorted(set(errors))


def run_case(case,fixture_root,output):
    result={'ticket':case['ticket'],'source_session_id':case['source_session_id'],
            'status':'BLOCKED','network_calls':0,'physical_requests':0,'errors':[]}
    folder=fixture_root/'unknown-domain-v4'
    if not all((folder/name).exists() for name in ('catalog.sqlite','config.json')):
        result['reason']='MISSING_PRIVATE_REPLAY_INPUTS';return result
    from metadata_config import load_config
    from session_replay import replay,ReplayError
    config=load_config(folder/'config.json')
    def no_network(*args,**kwargs):raise ReplayError('NETWORK_FORBIDDEN')
    try:
        with patch.object(socket,'create_connection',side_effect=no_network),patch.object(socket.socket,'connect',side_effect=no_network):
            replayed=replay(case['source_session_id'],fixture_root/'planner-recordings',folder/'catalog.sqlite',
                config['storage']['database'],config,output,allow_engine_drift=True)
        if replayed['status']!='MATCHED':result['reason']='BYTE_EXACT_RUNTIME_REPLAY_DID_NOT_MATCH'
        else:
            result['errors']=output_checks(case,replayed['session'])
            result['status']='FAILED' if result['errors'] else 'PASSED'
            result['reason']='OUTPUT_INVARIANT_FAILED' if result['errors'] else None
    except Exception as exc:
        result['reason']=str(exc) if type(exc).__name__ in ('ReplayError','RecordingError') else type(exc).__name__
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--fixture-root',type=Path,default=ROOT/'.local')
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--ledger',type=Path)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    cases=[json.loads(p.read_text()) for p in sorted((Path(__file__).parent/'cases').glob('*.json'))]
    if len(cases)!=15 or len({c['ticket'] for c in cases})!=15:raise ValueError('Acceptance roster must conserve all fifteen tickets')
    results=[]
    for case in cases:
        validate_case(case)
        result=run_case(case,args.fixture_root,args.output/case['ticket']);results.append(result)
        print(json.dumps(result),flush=True)
        if args.ledger:
            from datetime import datetime,timezone
            row={'experiment':'ROUND_FOUR_OFFLINE_ACCEPTANCE','mode':'offline','run_key':case['ticket'],
                 'session_id':'round-four-offline-'+case['ticket'],'source_session_id':case['source_session_id'],
                 'date_utc':datetime.now(timezone.utc).isoformat(),'status':result['status'],
                 'stop_reason':result.get('reason'),'physical_requests':0,'diagnostic_reads':0,'planner_calls':0,
                 'notes_doc':'docs/round-four-acceptance-gaps.md'}
            with args.ledger.open('a',encoding='utf8',newline='\n') as f:f.write(json.dumps(row,separators=(',',':'))+'\n')
    (args.output/'summary.json').write_text(json.dumps(results,indent=2)+'\n')
    return 0 if all(r['status']=='PASSED' for r in results) else 1


if __name__=='__main__':raise SystemExit(main())
