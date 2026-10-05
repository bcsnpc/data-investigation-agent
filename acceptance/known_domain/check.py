"""Strict known-domain acceptance gate; missing replay evidence is not a pass."""
import argparse,json,re,sys,socket
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'acceptance/unknown_domain'),str(Path(__file__).parent)]
from contract import project,compare,answer_matches,ANSWER_CATEGORIES
INVARIANTS=frozenset(('both_outputs','no_serialized_structure','no_business_identifier_form','timing_hedge_once','valid_mechanism_layer_tokens','layer_names_by_declared_role'))


def validate_case(case):
    from investigator.acceptance_context import validate_case_pin
    validate_case_pin(case)
    expected=case.get('expected',{})
    if (case.get('version')!=3 or set(case['invariants'])!=INVARIANTS
            or len(case['invariants'])!=len(INVARIANTS)
            or expected.get('answer_category') not in ANSWER_CATEGORIES
            or not case.get('acceptance_change_reason','').strip()
            or any(k not in ('status','outcome','answer_category','resolutions','boundaries','layers_reached','reproduction') for k in expected)):
        raise ValueError('Acceptance contract is incomplete or unsupported')
    if not {'status','answer_category','resolutions','boundaries','layers_reached','reproduction'}<=set(expected):
        raise ValueError('Acceptance structure is incomplete')


def output_checks(case,state,*,provider_mechanism=None,pinned_context=None,local_payload=None):
    errors=[]
    try:
        actual=project(state,(case.get('expected',{}).get('reproduction') or {}).get('cell_id'))
        errors += ['STRUCTURE:'+row['invariant'] for row in compare(case['expected'],actual)]
    except (ValueError,KeyError):errors.append('STRUCTURED_RESULT_MISSING')
    pin=case.get('context_pin')
    if pin:
        if state.get('envelope',{}).get('context_id')!=pin['context_id']:errors.append('CONTEXT_ID_CHANGED')
        if pinned_context!=pin:errors.append('CONTEXT_HASH_NOT_ESTABLISHED')
    outputs=(state.get('synthesis') or {}).get('outputs',{})
    for kind in ('business_output','technical_output'):
        text=outputs.get(kind,{}).get('explanation',{}).get('text')
        if not isinstance(text,str) or not text:errors.append(kind+':MISSING_OUTPUT');continue
        if not answer_matches(case['expected']['answer_category'],text):errors.append(kind+':ANSWER_CATEGORY_CHANGED')
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
            boundaries=[o for o in state.get('observations',[]) if o.get('comparison_status')=='CROSS_SURFACE_VERIFIED']
            labels=(local_payload or {}).get('layer_labels') or (state.get('assessment') or {}).get('technical_output',{}).get('layer_labels',{})
            for boundary in boundaries:
                for side in ('upper_layer','lower_layer'):
                    if not labels.get(boundary.get(side),{}).get('role'):
                        errors.append('technical_output:UNDECLARED_LAYER_ROLE')
            mechanism=outputs[kind].get('model_mechanism',provider_mechanism)
            if mechanism is None and (state.get('synthesis') or {}).get('provenance') in ('DETERMINISTIC_REFUSAL_RENDERING','DETERMINISTIC_BOUNDED_SPINE_RENDERING'):
                mechanism={'text':'','provenance':'ENGINE_ONLY_RENDERING'}
            if mechanism is None:errors.append('technical_output:MISSING_MODEL_MECHANISM_PROVENANCE')
            elif mechanism.get('provenance') not in ('PROVIDER_MECHANISM','SEALED_PROVIDER_MECHANISM','ENGINE_ONLY_RENDERING'):
                errors.append('technical_output:INVALID_MECHANISM_PROVENANCE')
            elif mechanism.get('text'):
                payload=local_payload or {'layer_labels':labels,'evidence':[{'id':o['id'],'tool':o.get('tool'),'result':o}
                    for o in state.get('observations',[])]}
                try:validate_layer_references(mechanism['text'],payload)
                except ValueError as exc:errors.append('technical_output:LAYER_REFERENCE:'+str(exc))
    return sorted(set(errors))


def reproduction_verdict(state,cell_id):
    facts=[o for o in state.get('observations',[]) if o.get('check_kind')=='DECLARED_CONTEXT_REPRODUCTION'
           and o.get('cell',{}).get('id')==cell_id]
    if len(facts)!=1:return None
    fact=facts[0];figure=fact.get('reported_figure') or {}
    return {'cell_id':cell_id,'label':fact.get('label'),'reproduced_value':fact.get('reproduced_value'),
            'reported_state':figure.get('state'),'reported_value':figure.get('value')}


def sealed_mechanism(path):
    """Read the explicit provider response field, never infer paragraphs in prose.

    This is a grading view of historical bytes, not a change to their receipts
    or outputs. New outputs carry the same role directly in model_mechanism.
    """
    import base64
    from investigator.process_tape import Tape,validate_event
    tape=Tape(path);operation=None;found=[]
    for event in tape.events:
        if event['kind']=='OPERATION_START':operation=json.loads(validate_event(event,event['ordinal']))['name']
        if event['kind']!='PROVIDER_RESPONSE' or operation!='synthesize':continue
        wrapper=json.loads(validate_event(event,event['ordinal']))
        body=json.loads(base64.b64decode(wrapper['body'],validate=True))
        for call in body.get('output',[]):
            if call.get('type')!='function_call':continue
            args=json.loads(call['arguments'])
            if 'technical_output' in args:
                found.append({'text':args['technical_output']['text'],'provenance':'SEALED_PROVIDER_MECHANISM',
                              'provider_event_sha256':event['sha256']})
    if not found:return None
    return found[-1]


def run_case(case,fixture_root,output):
    result={'ticket':case['ticket'],'source_session_id':case['source_session_id'],
            'status':'BLOCKED','network_calls':0,'physical_requests':0,'errors':[]}
    input_path=fixture_root/'known-domain-runs'/(case['ticket']+'.json')
    if not input_path.is_file():
        result['reason']='MISSING_PRIVATE_REPLAY_INPUTS';return result
    from process_replay import replay
    from investigator.process_tape import Tape,TapeError
    from investigator.onboarding import digest
    import sqlite3
    def no_network(*args,**kwargs):raise TapeError('NETWORK_FORBIDDEN')
    try:
        run=json.loads(input_path.read_text(encoding='utf-8'))
        if (run.get('session') or {}).get('id')!=case['source_session_id']:
            raise TapeError('ACCEPTANCE_RUN_ID_DIFFERS')
        path=Path(run['tape_path'])
        if not path.is_absolute():path=fixture_root/path
        tape=Tape(path)
        # Select from the sealed bootstrap, including a recorded operator pin.
        # Never install the case's requested context into an existing tape.
        model_id=run['session']['model_id']
        with sqlite3.connect(path.parent/'catalog.sqlite') as db:
            recorded_pin=tape.bootstrap['state'].get('context_pins',{}).get(model_id)
            cid=(recorded_pin or {}).get('context_id') or db.execute('SELECT context_id FROM models WHERE id=?',(model_id,)).fetchone()[0]
            context=json.loads(db.execute('SELECT body FROM model_contexts WHERE id=? AND model_id=?',(cid,model_id)).fetchone()[0])
        established={'context_id':cid,'hash':digest(context)}
        from investigator.acceptance_context import require_context
        require_context(case,established)
        with patch.object(socket,'create_connection',side_effect=no_network),patch.object(socket.socket,'connect',side_effect=no_network):
            replayed=replay(path,output,allow_engine_drift=True)
        if not replayed['matched']:result['reason']='BYTE_EXACT_RUNTIME_REPLAY_DID_NOT_MATCH'
        else:
            result['walk_outcome']=replayed['outcome']
            result['reproduction_verdict']=reproduction_verdict(replayed['session'],case['expected']['reproduction']['cell_id']) if case.get('grade_kind')=='reproduction' else None
            from investigator.synthesis_digest import build
            with sqlite3.connect(output/'catalog.sqlite') as db:
                db.row_factory=sqlite3.Row
                payload=build(replayed['session'],db)
            result['errors']=output_checks(case,replayed['session'],provider_mechanism=sealed_mechanism(path),pinned_context=established,local_payload=payload)
            result['status']='FAILED' if result['errors'] else 'PASSED'
            result['reason']='OUTPUT_INVARIANT_FAILED' if result['errors'] else None
    except Exception as exc:
        result['reason']=str(exc) if type(exc).__name__ in ('TapeError','RecordingError') else type(exc).__name__

    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--fixture-root',type=Path,default=ROOT/'.local')
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--ledger',type=Path)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    cases=[json.loads(p.read_text(encoding='utf-8')) for p in sorted((Path(__file__).parent/'cases').glob('*.json'))]
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
