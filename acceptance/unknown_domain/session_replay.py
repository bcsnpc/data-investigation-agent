"""Offline runtime replay over isolated database copies and recorded HTTP responses.

No publisher truth is read. Missing context/receipts are gaps, never fabricated.
"""
from contextlib import closing
import copy
from datetime import datetime
import json
import os
from pathlib import Path
import sqlite3
import sys
import time
from unittest.mock import patch
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from investigator.adaptive_planner import azure_plan
from investigator.adaptive_runtime import AdaptiveRuntime
from investigator import adaptive_runtime, dynamic_reasoning, planner_recording
from investigator.onboarding import ModelStore, digest, encoded
from investigator.runtime import Runtime, fingerprint


class ReplayError(ValueError):
    pass


def backup(source, destination):
    with closing(sqlite3.connect(Path(source).resolve().as_uri() + '?mode=ro', uri=True)) as original:
        with closing(sqlite3.connect(destination)) as cloned:
            original.backup(cloned)


def replay(session_id, recordings, database, inventory, config, output, *, inject_at=None,
           injection=None, allow_engine_drift=False):
    """Replay a complete session; injection probes stop after the modified response.

    Raw responses are copied in memory for explicit fault injection only. Canonical
    records, receipts and databases are never opened for writing.
    """
    import httpx
    from openai import DefaultHttpxClient
    started = time.monotonic()
    calls = planner_recording.load_session(session_id, recordings)
    if not calls or [c['context'].get('planner_call') for c in calls] != list(range(1, len(calls)+1)):
        raise ReplayError('INCOMPLETE_SESSION_RECORDINGS')
    for call in calls:
        recorded_failure = (not call['manifest'].get('exclusion') and
                            call['manifest'].get('error_type') in ('APITimeoutError', 'APIConnectionError'))
        required = {'request.body', 'runtime-return.json'}
        if not recorded_failure:
            required |= {'response.body', 'response-status.json'}
        if not required <= set(call['bodies']):
            raise ReplayError('MISSING_RESPONSE_OR_RUNTIME_TIMING')
    first = calls[0]['context']
    if 'state' not in first or 'planner_profile' not in first or 'environment' not in first:
        raise ReplayError('MISSING_RUNTIME_BOOTSTRAP')
    if digest(config) != first['state']['config_hash']:
        raise ReplayError('CONFIGURATION_MISMATCH')
    engine_changed = first['state']['engine_hash'] != fingerprint()
    if engine_changed and not allow_engine_drift:
        raise ReplayError('ENGINE_VERSION_MISMATCH')
    if inject_at is not None and (type(inject_at) is not int or not 1 <= inject_at <= len(calls) or injection is None):
        raise ReplayError('INVALID_INJECTION')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    backup(database, output / 'catalog.sqlite')
    backup(inventory, output / 'inventory.sqlite')
    store = ModelStore(output / 'catalog.sqlite', output / 'inventory.sqlite', first['environment'])
    unrecorded_tools = []
    def forbidden_read(request):
        unrecorded_tools.append(True)
        raise ReplayError('UNRECORDED_TOOL_READ')
    clock = [first['state']['deadline'] - first['payload']['remaining_wall_seconds']]
    runtime = Runtime(store, config, forbidden_read, forbidden_read)
    profile = first['planner_profile']
    if digest(profile) != first['state']['planner_profile_hash']:
        raise ReplayError('PLANNER_PROFILE_MISMATCH')
    index = [0]
    comparisons = []
    def transport(request):
        if index[0] >= len(calls):
            raise ReplayError('RECORDED_PROVIDER_EXHAUSTED')
        call = calls[index[0]]
        matches = request.content == call['bodies']['request.body']
        comparisons.append({'planner_call': index[0]+1, 'request_bytes_match': matches})
        if not matches:
            raise ReplayError('PLANNER_INPUT_MISMATCH')
        clock[0] = json.loads(call['bodies']['runtime-return.json'])['clock']
        if 'response.body' not in call['bodies']:
            error = httpx.ReadTimeout if call['manifest']['error_type'] == 'APITimeoutError' else httpx.ConnectError
            raise error('Recorded provider transport failure (offline)', request=request)
        response = call['bodies']['response.body']
        if inject_at == index[0]+1:
            body = json.loads(response)
            function = next((item for item in body.get('output', []) if item.get('type') == 'function_call'), None)
            if function is None:
                raise ReplayError('INJECTION_NEEDS_FUNCTION_RESPONSE')
            function['arguments'] = json.dumps(injection)
            response = json.dumps(body).encode()
        return httpx.Response(json.loads(call['bodies']['response-status.json'])['status_code'], content=response)

    agent = AdaptiveRuntime(runtime, azure_plan, clock=lambda: clock[0], planner_profile=profile,
                            usage_policy=first.get('usage_policy'))
    with runtime.db() as db:
        row = db.execute('SELECT state FROM adaptive_sessions WHERE id=?', (session_id,)).fetchone()
        if row is None:
            raise ReplayError('SESSION_NOT_IN_CATALOG')
        expected = json.loads(row['state'])
        initial = copy.deepcopy(first['state'])
        initial.update(status='READY', token=None, planner_calls=0, engine_hash=fingerprint())
        initial['input_characters'] -= first['reservation']['input_characters']
        db.execute('UPDATE adaptive_sessions SET state=?,state_hash=? WHERE id=?',
                   (encoded(initial), digest(initial), session_id))
        db.execute('DELETE FROM adaptive_events WHERE session_id=?', (session_id,))
        if agent.governor:
            # Roll back reservations only in this disposable replay copy, preserving
            # the original prior-day/prior-session allowance and all source evidence.
            db.execute('DELETE FROM adaptive_usage WHERE session_id=?', (session_id,))
            cutoff = datetime.fromisoformat(first['created_utc']).timestamp()
            db.execute('DELETE FROM adaptive_usage WHERE created>?', (cutoff,))
    if agent.governor:
        expected_usage = dict(first['budget']['reserved_today'])
        expected_usage['planner_calls'] -= 1
        expected_usage['input_characters'] -= first['reservation']['input_characters']
        expected_usage['output_tokens'] -= first['reservation']['output_tokens']
        if agent.governor.snapshot()['reserved_today'] != expected_usage:
            raise ReplayError('PRIOR_USAGE_CANNOT_BE_RECONSTRUCTED')
    model = json.loads(calls[0]['bodies']['request.body'])['model']
    state = agent.get(session_id)
    failure = None
    with patch.dict(os.environ, {'INVESTIGATOR_RECORD_PLANNER': '0',
            'AZURE_OPENAI_ENDPOINT': 'https://offline.openai.azure.com',
            'AZURE_OPENAI_DEPLOYMENT': model, 'AZURE_OPENAI_API_KEY': 'offline-placeholder-credential'}), \
            patch.object(planner_recording, 'http_options', side_effect=lambda: {
                'http_client': DefaultHttpxClient(transport=httpx.MockTransport(transport))}), \
            patch('socket.create_connection', side_effect=ReplayError('NETWORK_FORBIDDEN')), \
            patch('socket.socket.connect', side_effect=ReplayError('NETWORK_FORBIDDEN')):
        for ordinal in range(len(calls)+1):
            if state['status'] != 'READY':
                break
            index[0] = ordinal
            if ordinal < len(calls):
                call = calls[ordinal]
                clock[0] = state['deadline'] - call['context']['payload']['remaining_wall_seconds']
                after = calls[ordinal+1]['context']['state'] if ordinal+1 < len(calls) else expected
                prior_ids = {o['id'] for o in call['context']['state']['observations']}
                new_ids = [o['id'] for o in after['observations'] if o['id'] not in prior_ids]
            else:
                new_ids = []
            # Preserve recorded observation identities while executing the actual
            # lookup and rejection paths. Lease tokens never enter model input.
            generated = iter([str(uuid4())] + new_ids)
            def runtime_id():
                return next(generated, str(uuid4()))
            with patch.object(adaptive_runtime, 'uuid4', side_effect=runtime_id), \
                    patch.object(dynamic_reasoning, 'uuid4', side_effect=lambda: new_ids[0] if new_ids else str(uuid4())):
                try:
                    state = agent.step(session_id)
                except Exception as exc:
                    failure = type(exc).__name__
                    state = agent.get(session_id)
                    break
            if inject_at == ordinal+1:
                break
    fields = ('status', 'stop_reason', 'planner_calls', 'cloud_calls', 'input_characters',
              'hypotheses', 'assessment', 'question', 'no_progress', 'observations')
    differences = [key for key in fields if state.get(key) != expected.get(key)]
    matched = (not failure and not unrecorded_tools and not differences and len(comparisons) == len(calls)
               and all(c['request_bytes_match'] for c in comparisons))
    result = {'replay_id': str(uuid4()), 'source_session_id': session_id, 'mode': 'replay',
        'status': ('INJECTION_PROBE' if inject_at and len(comparisons) == inject_at
                   and all(c['request_bytes_match'] for c in comparisons)
                   and not failure and not unrecorded_tools else 'MATCHED' if matched else 'MISMATCH'),
        'engine_changed': engine_changed, 'comparisons': comparisons, 'differences': differences,
        'failure_type': failure, 'unrecorded_tool_attempts': len(unrecorded_tools),
        'network_calls': 0, 'injected_planner_call': inject_at, 'session': state,
        'wall_seconds': round(time.monotonic()-started, 3), 'business_correctness': 'NOT_GRADED'}
    with (output / 'result.json').open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
    return result
