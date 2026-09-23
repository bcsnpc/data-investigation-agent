"""Content-free, append-only evaluation telemetry; receipts remain the evidence."""
from datetime import datetime, timezone
import json
from trajectory_metrics import metrics
from pathlib import Path
from uuid import uuid4


def row(result, calls, family='engineering'):
    state = result['session']
    observations = state.get('observations', [])
    decisions = [d['decision'] for d in state.get('decisions', [])]
    lookups = [o for o in observations if o.get('lookup')]
    reads = [o for o in observations if o.get('tool') != 'context' and o.get('status') == 'COMPLETED']
    retrievals = sum(d.get('action') == 'LOOKUP' for d in decisions)
    tests = sum(d.get('action') in ('RUN', 'QUERY') for d in decisions)
    rejected = dict.fromkeys(('schema', 'prerequisite', 'redundancy', 'complexity', 'other'), 0)
    for observation in observations:
        if observation.get('status') != 'REJECTED':
            continue
        metadata = observation.get('metadata', {})
        reason = metadata.get('reason', '')
        category = ('prerequisite' if metadata.get('recovery_assets') else
                    'schema' if reason.startswith('Decision contract rejected:') else
                    'redundancy' if observation.get('duplicate_of') or reason.startswith('Scalar diagnostics already observed') else
                    'complexity' if reason.startswith('Relational complexity budget exceeded') else 'other')
        rejected[category] += 1
    errors = dict.fromkeys(('rate_limit', 'timeout', 'other'), 0)
    repairs = dict.fromkeys(('hypothesis_id', 'text_bound', 'schema_prefetch', 'other'), 0)
    for event in state.get('events', []):
        if event.get('kind') == 'PROPOSAL_REPAIRED':
            category = event.get('detail', {}).get('repair_kind', 'other')
            repairs[category if category in repairs else 'other'] += 1
        if event.get('kind') == 'PLANNER_ERROR':
            detail = event.get('payload', event.get('detail', {}))
            name = detail.get('error_type', '')
            errors['rate_limit' if name == 'RateLimitError' else 'timeout' if name == 'APITimeoutError' else 'other'] += 1
    count = state.get('planner_calls', 0)
    sql = sum(o.get('tool') in ('bounded_sql', 'source', 'source_records') for o in reads)
    dax = sum(o.get('tool') in ('bounded_dax', 'native', 'native_records') for o in reads)
    return dict(**metrics(state),session_id=result['replay_id'], date_utc=datetime.now(timezone.utc).isoformat(),
        mode='replay', family=family, engine_tag='unfrozen-'+state['engine_hash'][:12], manifest_sha_short='NONE',
        model_deployment=json.loads(calls[0]['bodies']['request.body'])['model'],
        settings_hash=state['planner_profile_hash'], planner_calls=count,
        reads_sql=sql, reads_dax=dax, reads_other=len(reads)-sql-dax,
        context_lookups=len(lookups), distinct_context_lookups=len({json.dumps(o['lookup'], sort_keys=True) for o in lookups}),
        retrieval_calls=retrievals, test_calls=tests, retrieval_test_ratio=retrievals/tests if tests else None,
        rejections=rejected, repairs=repairs,
        provider_errors=errors, cumulative_input_chars=state.get('input_characters', 0),
        output_tokens_reserved=sum(c['context']['reservation']['output_tokens'] for c in calls[:count]),
        wall_seconds=result['wall_seconds'], stop_reason=state.get('stop_reason') or result['status'],
        outcome_label=state.get('outcome', {}).get('classification', 'NOT_GRADED'),
        intent_unknown=state.get('assessment', {}).get('support', {}).get('intent_dependency', 'UNKNOWN') == 'UNKNOWN',
        graded='NOT_GRADED', notes_doc='docs/offline-session-replay.md')


def append(path, entry):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(entry, separators=(',', ':'))+'\n')


def failed(error_type, wall_seconds):
    """A preflight failure has no reconstructed calls; never log exception text."""
    return dict(**metrics({}),session_id=str(uuid4()), date_utc=datetime.now(timezone.utc).isoformat(),
        mode='replay', family='engineering', engine_tag='unfrozen-item-3',
        manifest_sha_short='NONE', model_deployment='NOT_RECONSTRUCTED',
        settings_hash='NOT_RECONSTRUCTED', planner_calls=0, reads_sql=0, reads_dax=0,
        reads_other=0, context_lookups=0, distinct_context_lookups=0, retrieval_calls=0,
        test_calls=0, retrieval_test_ratio=None,
        rejections=dict.fromkeys(('schema', 'prerequisite', 'redundancy', 'complexity', 'other'), 0),
        repairs=dict.fromkeys(('hypothesis_id', 'text_bound', 'schema_prefetch', 'other'), 0),
        provider_errors=dict.fromkeys(('rate_limit', 'timeout', 'other'), 0),
        cumulative_input_chars=0, output_tokens_reserved=0, wall_seconds=wall_seconds,
        stop_reason='REPLAY_PREFLIGHT_'+error_type, outcome_label='NOT_GRADED',
        intent_unknown=True, graded='NOT_GRADED', notes_doc='docs/offline-session-replay.md')
