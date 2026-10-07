"""File-only OTLP traces from sealed events; no transport, query or new clock.

Missing historic attribution remains UNRECORDED. Legacy top-level `run` is
WALK (inclusive of its nested checks); finer stage timing is never invented.
"""
import base64
import copy
from datetime import datetime
from decimal import Decimal
import hashlib
import json
import re
from .process_tape import Tape, validate_event

STAGES = ('intake', 'context', 'reproduce', 'walk', 'source', 'compose')
OPERATIONS = {'intake': 'intake', 'preview': 'context', 'create': 'context', 'run': 'walk', 'synthesize': 'compose'}


def nanos(seconds):
    return str(int(Decimal(str(seconds)) * 1000000000))


def attributes(values):
    result = []
    for key, value in sorted(values.items()):
        if value is None: continue
        if type(value) is bool: typed = {'boolValue': value}
        elif type(value) is int: typed = {'intValue': str(value)}
        elif type(value) is float: typed = {'doubleValue': value}
        elif isinstance(value, str): typed = {'stringValue': value}
        else: raise ValueError('Trace attributes must be scalar, never serialized evidence')
        result.append({'key': key, 'value': typed})
    return result


def validate(value):
    """Validate with the official generated OTLP protobuf, plus tree invariants.

    OTLP JSON encodes IDs as hex, unlike generic protobuf JSON's base64 bytes.
    Convert only those three fields before parsing; unknown schema fields fail.
    """
    from google.protobuf.json_format import ParseDict
    from opentelemetry.proto.trace.v1.trace_pb2 import TracesData
    candidate = copy.deepcopy(value); all_spans = []
    for resource in candidate['resourceSpans']:
        for scope in resource['scopeSpans']:
            for span in scope['spans']:
                all_spans.append(span)
                for field, size in [('traceId', 32), ('spanId', 16), ('parentSpanId', 16)]:
                    if field not in span: continue
                    text = span[field]
                    if not isinstance(text, str) or not re.fullmatch('[0-9a-f]{' + str(size) + '}', text) or int(text, 16) == 0:
                        raise ValueError('Invalid OTLP hexadecimal identifier')
                    span[field] = base64.b64encode(bytes.fromhex(text)).decode()
    ParseDict(candidate, TracesData(), ignore_unknown_fields=False)
    spans = [s for r in value['resourceSpans'] for scope in r['scopeSpans'] for s in scope['spans']]
    ids = {(s['traceId'], s['spanId']): s for s in spans}
    if len(ids) != len(spans): raise ValueError('Duplicate trace span identity')
    for trace in {s['traceId'] for s in spans}:
        if sum('parentSpanId' not in s for s in spans if s['traceId'] == trace) != 1:
            raise ValueError('Trace must have one root')
    for s in spans:
        start, end = int(s['startTimeUnixNano']), int(s['endTimeUnixNano'])
        if start > end: raise ValueError('Recorded span ends before it starts')
        if 'parentSpanId' not in s: continue
        parent = ids.get((s['traceId'], s['parentSpanId']))
        if parent is None: raise ValueError('Trace parent is missing')
        if not int(parent['startTimeUnixNano']) <= start <= end <= int(parent['endTimeUnixNano']):
            raise ValueError('Child interval leaves its recorded parent')
        visited = {s['spanId']}
        while parent is not None:
            if parent['spanId'] in visited: raise ValueError('Trace tree contains a cycle')
            visited.add(parent['spanId'])
            parent = ids.get((parent['traceId'], parent['parentSpanId'])) if 'parentSpanId' in parent else None
    return value


def convert(path):
    tape = Tape(path)
    events = [(event, validate_event(event, index + 1)) for index, event in enumerate(tape.events)]
    def body(raw):
        try: return json.loads(raw)
        except (ValueError, UnicodeError): return None
    final = body(events[-1][1])
    if events[-1][0]['kind'] != 'FINAL' or not isinstance(final, dict):
        raise ValueError('Completed sealed tape required')
    state = final.get('result') or {}
    if not isinstance(state, dict): state = {}
    trace = hashlib.sha256(tape.path.read_bytes()).hexdigest()[:32]
    spans = []; summary = {stage: {'model_calls': 0, 'input_tokens': 0, 'output_tokens': 0,
        'physical_admissions': 0, 'wall_seconds': 0.0} for stage in STAGES}
    def span(name, start, end, parent, values, failed=False):
        identity = hashlib.sha256((trace + ':' + str(len(spans))).encode()).hexdigest()[:16]
        result = {'traceId': trace, 'spanId': identity, 'name': name, 'kind': 1,
            'startTimeUnixNano': nanos(start), 'endTimeUnixNano': nanos(end),
            'attributes': attributes(values), 'status': {'code': 2 if failed else 1}}
        if parent is not None: result['parentSpanId'] = parent
        spans.append(result); return result
    begin = min(e['at'] for e, _ in events); end = max(e['at'] for e, _ in events)
    root = span('investigation', begin, end, None, {'dia.tape.version': tape.version,
        'dia.tape.sha256': hashlib.sha256(tape.path.read_bytes()).hexdigest(),
        'dia.engine.revision': tape.engine_revision, 'dia.outcome': (state.get('assessment') or {}).get('classification'),
        'dia.physical.requests': state.get('physical_calls'), 'dia.diagnostic.reads': state.get('cloud_calls')}, bool(final.get('error')))
    # Top-level operations are recorded, not reconstructed from query contents.
    operations = []; opened = None
    for e, raw in events:
        b = body(raw)
        if e['kind'] == 'OPERATION_START':
            if opened is not None: raise ValueError('Nested top-level operations unsupported')
            opened = (e['at'], b['name'])
        elif e['kind'] == 'OPERATION_END':
            if opened is None or opened[1] != b['name']: raise ValueError('Recorded operation pairing differs')
            operations.append((opened[0], e['at'], OPERATIONS.get(b['name'], 'context'), bool(b.get('error')))); opened = None
    if opened is not None: raise ValueError('Unfinished operation cannot export a completed trace')
    # New tapes retain procedure-call stage events in the original FINAL state.
    # Attribute nested source/reproduction work from those events, not tool names.
    calls=[];pending_stage=None
    for event in state.get('events',[]):
        if event.get('kind') not in ('PROCESS_STAGE_STARTED','PROCESS_STAGE_FINISHED'):continue
        detail=event['detail'];stage=detail['stage']
        if stage not in STAGES:raise ValueError('Unknown recorded process stage')
        at=datetime.fromisoformat(event['created'].replace('Z','+00:00')).timestamp()
        if event['kind']=='PROCESS_STAGE_STARTED':
            if pending_stage is not None:raise ValueError('Nested recorded procedure stages')
            pending_stage=(at,stage,detail['operation'])
        else:
            if pending_stage is None or pending_stage[1:]!=(stage,detail['operation']):
                raise ValueError('Procedure stage pairing differs')
            calls.append((pending_stage[0],at,stage,bool(detail.get('error_type'))));pending_stage=None
    if pending_stage is not None:raise ValueError('Unfinished recorded procedure stage')
    timing=([o for o in operations if o[2]!='walk']+calls) if calls else operations
    stages = {}
    for stage in STAGES:
        intervals = [o for o in timing if o[2] == stage]
        if not intervals: continue
        stages[stage] = span(stage, min(o[0] for o in intervals), max(o[1] for o in intervals), root['spanId'],
                             {'dia.stage': stage, 'dia.stage.basis': 'RECORDED_PROCEDURE_CALL' if calls else 'RECORDED_OPERATION'}, any(o[3] for o in intervals))
        summary[stage]['wall_seconds'] = sum(float(Decimal(str(o[1])) - Decimal(str(o[0]))) for o in intervals)
    def stage_at(at):
        selected=next((c[2] for c in calls if c[0]<=at<=c[1]),None)
        if selected is not None:return selected
        # Unattributed gaps inside a modern walk are not invented stage spans.
        if calls:return next((o[2] for o in operations if o[2]!='walk' and o[0]<=at<=o[1]),None)
        return next((o[2] for o in operations if o[0] <= at <= o[1]), None)
    providers = []; budgets = {}
    for e, raw in events:
        b = body(raw); stage = stage_at(e['at'])
        if not stage or not isinstance(b, dict): continue
        if e['kind'] == 'PROVIDER_REQUEST': providers.append((e['at'], stage, b))
        elif e['kind'] in ('PROVIDER_RESPONSE', 'PROVIDER_FAILURE'):
            if not providers: raise ValueError('Provider response lacks recorded request')
            started, provider_stage, request = providers.pop(0)
            response = body(base64.b64decode(b['body'])) if e['kind'] == 'PROVIDER_RESPONSE' else {}
            response = response if isinstance(response, dict) else {}
            usage = response.get('usage') or {}
            fields = {'dia.stage': provider_stage, 'gen_ai.request.model': request.get('model'),
                'gen_ai.response.model': response.get('model'), 'dia.provider.status': b.get('status'),
                'gen_ai.usage.input_tokens': usage.get('input_tokens'), 'gen_ai.usage.output_tokens': usage.get('output_tokens')}
            span('model', started, e['at'], stages[provider_stage]['spanId'], fields, e['kind'] == 'PROVIDER_FAILURE')
            summary[provider_stage]['model_calls'] += 1
            for field in ('input_tokens', 'output_tokens'):
                if type(usage.get(field)) is int: summary[provider_stage][field] += usage[field]
        elif e['kind'] == 'BUDGET':
            request = b.get('request') or {}; key = (request.get('session_id'), request.get('key'))
            if b.get('phase') == 'BEFORE': budgets[key] = b
            elif (b.get('phase') == 'AFTER' and request.get('operation') == 'reserve'
                  and request.get('args', [])[:1] == ['cloud'] and not b.get('error')):
                before = budgets.get(key)
                if before and before['state'].get('reservation') is None and b['state'].get('reservation'):
                    summary[stage]['physical_admissions'] += 1
    # Receipt spans use engine-recorded admission/completion timestamps. SQL
    # guards and permission probes are retained separately, never discarded.
    observations = {o['id']: o for o in state.get('observations', []) if isinstance(o, dict) and 'id' in o}
    pending = []
    for event_index, event in enumerate(state.get('events', [])):
        if event.get('kind') not in ('PROCESS_READ_RESERVED', 'PROCESS_READ_RECORDED'): continue
        detail = event['detail']; at = datetime.fromisoformat(event['created'].replace('Z', '+00:00')).timestamp()
        if event['kind'] == 'PROCESS_READ_RESERVED': pending.append((detail.get('tool'), at)); continue
        logical = detail.get('logical_receipt') or {}
        receipt_id = detail.get('receipt_id') or logical.get('receipt_id')
        guard_id = detail.get('guard_receipt')
        reservation_tool = detail.get('logical_tool') or detail.get('tool')
        starts = [i for i, (tool, _) in enumerate(pending) if tool == reservation_tool]
        started = pending.pop(starts[-1])[1] if starts else at
        stage = stage_at(at)
        if stage is None: continue
        observation = observations.get(receipt_id) or {}; surface = observation.get('execution_surface') or {}
        attestation = observation.get('surface_attestation') or {}
        span('probe', started, at, stages[stage]['spanId'], {'dia.stage': stage,
            'dia.receipt.id': receipt_id or guard_id or 'UNRECORDED',
            'dia.guard.receipt.id': guard_id,
            'dia.evidence.pointer': 'FINAL.result.events[' + str(event_index) + ']',
            'dia.evidence.result_hash': detail.get('result_hash'),
            'dia.probe.tool': detail.get('tool'),
            'dia.probe.guard': bool(detail.get('guard_receipt')), 'dia.probe.status': detail.get('status'),
            'dia.execution.identity': surface.get('identity', 'UNRECORDED'),
            'dia.execution.engine': surface.get('engine', 'UNRECORDED'),
            'dia.layer.role': observation.get('layer_role', 'UNRECORDED'),
            'dia.attestation.grade': attestation.get('status', 'UNRECORDED')}, detail.get('status') not in ('COMPLETED', 'OBSERVED', 'AVAILABLE'))
    result = {'resourceSpans': [{'resource': {'attributes': attributes({'service.name': 'data-investigation-agent'})},
        'scopeSpans': [{'scope': {'name': 'dia.tape', 'version': '1'}, 'spans': spans}]}]}
    validate(result)
    if providers: raise ValueError('Provider request lacks recorded completion')
    physical = state.get('physical_calls')
    if physical is not None and sum(s['name'] == 'probe' for s in spans) != physical:
        raise ValueError('Recorded physical requests and exported probes differ')
    return result, {'stages': summary, 'basis': 'Recorded top-level operations; walk includes nested source/reproduction where finer historic phase timestamps are absent.',
                    'recorded_stages': sorted(stages), 'currency_cost': 'UNRECORDED',
                    'recorded_physical_requests': state.get('physical_calls'),
                    'recorded_diagnostic_reads': state.get('cloud_calls'),
                    'physical_requests': 0, 'network_calls': 0}


def footer(summary):
    """Same recorded totals as spans, without presenting absent timing as zero."""
    parts = []
    for name in STAGES:
        if name not in summary['recorded_stages']:
            parts.append(name + ': timing not recorded separately'); continue
        s = summary['stages'][name]
        parts.append(f"{name}: {s['wall_seconds']:.3f}s, {s['model_calls']} model calls, "
                     f"{s['input_tokens']}/{s['output_tokens']} input/output tokens, "
                     f"{s['physical_admissions']} physical admissions")
    return 'Recorded stage cost/time — ' + '; '.join(parts) + '; currency cost not recorded.'
