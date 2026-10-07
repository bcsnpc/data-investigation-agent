"""Strict known-domain acceptance gate; missing replay evidence is not a pass."""
import argparse,json,re,sys,socket
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'acceptance/unknown_domain'),str(Path(__file__).parent)]
from contract import project,compare,answer_matches,ANSWER_CATEGORIES
INVARIANTS=frozenset(('both_outputs','no_serialized_structure','no_business_identifier_form','timing_hedge_once','valid_mechanism_layer_tokens','layer_names_by_declared_role'))


def validate_case(case):
    from investigator.acceptance_context import validate_case_state,state_definition
    state_definition(fixture_configuration(),validate_case_state(case))
    if not case.get('reference_session_id') or not case.get('model_id') or not re.fullmatch('[0-9a-f]{64}',case.get('ticket_hash','')):
        raise ValueError('Acceptance reference/ticket identity is incomplete')
    expected=case.get('expected',{})
    if (case.get('version')!=4 or set(case['invariants'])!=INVARIANTS
            or len(case['invariants'])!=len(INVARIANTS)
            or expected.get('answer_category') not in ANSWER_CATEGORIES
            or not case.get('acceptance_change_reason','').strip()
            or any(k not in ('status','outcome','answer_category','resolutions','boundaries','layers_reached','reproduction') for k in expected)):
        raise ValueError('Acceptance contract is incomplete or unsupported')
    if not {'status','answer_category','resolutions','boundaries','layers_reached','reproduction'}<=set(expected):
        raise ValueError('Acceptance structure is incomplete')


def fixture_configuration():
    return json.loads((ROOT/'infra/estates/fixture.json').read_text(encoding='utf-8'))


def output_checks(case,state,*,provider_mechanism=None,fixture_state=None,local_payload=None):
    errors=[]
    try:
        actual=project(state,(case.get('expected',{}).get('reproduction') or {}).get('cell_id'))
        errors += ['STRUCTURE:'+row['invariant'] for row in compare(case['expected'],actual)]
    except (ValueError,KeyError):errors.append('STRUCTURED_RESULT_MISSING')
    from investigator.acceptance_context import require_state,declared_role_view
    try:require_state(case,fixture_state or {},fixture_configuration())
    except ValueError as exc:errors.append('FIXTURE_STATE:'+str(exc))
    if local_payload is not None:local_payload=declared_role_view(local_payload,fixture_configuration())
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
            from investigator.path_narrative import validate_layer_references,validate_mechanism,RepeatedHedge
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
                try:validate_mechanism(mechanism['text'])
                except RepeatedHedge:errors.append('technical_output:HEDGE_TWICE')
                except ValueError as exc:errors.append('technical_output:MECHANISM_FORM:'+str(exc))
    from investigator.lineage_limits import validate_outputs
    errors.extend(validate_outputs(state.get('assessment') or {},outputs))
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
    result={'ticket':case['ticket'],'reference_session_id':case['reference_session_id'],
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
        state=run.get('session') or {}
        if state.get('model_id')!=case['model_id'] or digest(state.get('envelope',{}).get('symptom'))!=case['ticket_hash']:
            raise TapeError('ACCEPTANCE_TICKET_IDENTITY_DIFFERS')
        result['source_session_id']=state['id']
        from private_bundle import tape_path
        path=tape_path(run,fixture_root)
        tape=Tape(path)
        # Select from the sealed bootstrap, including a recorded operator pin.
        # Never install the case's requested context into an existing tape.
        model_id=run['session']['model_id']
        with sqlite3.connect(path.parent/'catalog.sqlite') as db:
            recorded_pin=tape.bootstrap['state'].get('context_pins',{}).get(model_id)
            cid=(recorded_pin or {}).get('context_id') or db.execute('SELECT context_id FROM models WHERE id=?',(model_id,)).fetchone()[0]
            context=json.loads(db.execute('SELECT body FROM model_contexts WHERE id=? AND model_id=?',(cid,model_id)).fetchone()[0])
        established={'context_id':cid,'hash':digest(context)}
        from investigator.acceptance_context import require_state
        binding=establish_fixture_state(case,run,input_path,tape,established)
        require_state(case,binding,fixture_configuration())
        with patch.object(socket,'create_connection',side_effect=no_network),patch.object(socket.socket,'connect',side_effect=no_network):
            from recorded_engine import replay_revision
            revision = tape.engine_revision if tape.engine_revision is not None else historical_replay_revision(run,input_path,tape)
            from private_bundle import estate_manifest
            replayed=replay_revision(path,output,revision,estate_manifest=estate_manifest(tape,fixture_root))
        result['tape_version']=tape.version
        result['replay_engine_revision']=revision
        result['recorded_engine_hash']=tape.bootstrap['engine_hash']
        if not replayed['matched']:result['reason']='BYTE_EXACT_RUNTIME_REPLAY_DID_NOT_MATCH'
        else:
            result['walk_outcome']=replayed['outcome']
            result['reproduction_verdict']=reproduction_verdict(replayed['session'],case['expected']['reproduction']['cell_id']) if case.get('grade_kind')=='reproduction' else None
            from investigator.synthesis_digest import build
            with sqlite3.connect(output/'catalog.sqlite') as db:
                db.row_factory=sqlite3.Row
                payload=build(replayed['session'],db)
            result['fixture_state']=binding['name'];result['context_used']=established
            result['fixture_state_provenance']=binding.get('provenance','RECORDED_NATIVE')
            result['errors']=output_checks(case,replayed['session'],provider_mechanism=sealed_mechanism(path),fixture_state=binding,local_payload=payload)
            result['status']='FAILED' if result['errors'] else 'PASSED'
            result['reason']='OUTPUT_INVARIANT_FAILED' if result['errors'] else None
    except Exception as exc:
        result['reason']=str(exc) if type(exc).__name__ in ('TapeError','RecordingError') else type(exc).__name__

    return result


def historical_replay_revision(run,input_path,tape):
    import hashlib
    bindings=json.loads((Path(__file__).parent/'historical-replay-bindings.json').read_text())
    matches=[b for b in bindings if b['session_id']==run['session']['id']
        and b['source_sha256']==hashlib.sha256(input_path.read_bytes()).hexdigest()
        and b['tape_sha256']==hashlib.sha256(tape.path.read_bytes()).hexdigest()]
    if len(matches)!=1:raise ValueError('Historical replay revision not established for this sealed run')
    return matches[0]['revision']


def establish_fixture_state(case,run,input_path,tape,context):
    """Native future declaration, or a separate sealed historical association.

    Never infer data state from context identity: gap and latency can share
    the same metadata context. Original tape bytes are never amended.
    """
    native=tape.bootstrap['state'].get('fixture_state')
    if native is not None:
        if native['context']!=context:raise ValueError('Recorded fixture context integrity differs')
        return native
    import hashlib
    bindings=json.loads((Path(__file__).parent/'historical-fixture-bindings.json').read_text())
    found=[b for b in bindings if b['session_id']==run['session']['id']
           and b['source_sha256']==hashlib.sha256(input_path.read_bytes()).hexdigest()
           and b['tape_sha256']==hashlib.sha256(tape.path.read_bytes()).hexdigest()
           and b['context']==context]
    if len(found)!=1:raise ValueError('Historical fixture state not established for this sealed run')
    return found[0]


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
            row={'experiment':'ROUND_FIVE_VERSIONED_OFFLINE_ACCEPTANCE','mode':'offline','run_key':case['ticket'],
                 'session_id':'round-four-offline-'+case['ticket'],'reference_session_id':case['reference_session_id'],
                 'date_utc':datetime.now(timezone.utc).isoformat(),'status':result['status'],
                 'stop_reason':result.get('reason'),'physical_requests':0,'diagnostic_reads':0,'planner_calls':0,
                 'notes_doc':'docs/versioned-recorded-engine-replay.md'}
            with args.ledger.open('a',encoding='utf8',newline='\n') as f:f.write(json.dumps(row,separators=(',',':'))+'\n')
    (args.output/'summary.json').write_text(json.dumps(results,indent=2)+'\n')
    return 0 if all(r['status']=='PASSED' for r in results) else 1


if __name__=='__main__':raise SystemExit(main())
