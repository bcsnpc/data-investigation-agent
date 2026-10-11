"""Exclude only retained human-reply intervals from active agent wall time."""
from datetime import datetime
import math
from .onboarding import Conflict


def timestamp(value):
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            raise ValueError('timezone required')
        result = parsed.timestamp()
        if not math.isfinite(result):
            raise ValueError('finite timestamp required')
        return result
    except (TypeError, ValueError, OverflowError) as exc:
        raise Conflict('Agent human wait requires original timestamp evidence') from exc


def interval(ticket, loop, comment_id, journal, *, now):
    if loop.get('status') != 'WAITING_FOR_USER':
        raise Conflict('Only a real waiting-for-user interval can pause active wall time')
    waiting = [e for e in loop.get('transcript', []) if e.get('event') == 'TOOL_RESULT'
               and e.get('result', {}).get('status') == 'WAITING_FOR_USER']
    if not waiting:
        raise Conflict('Agent human wait lacks retained question evidence')
    event = waiting[-1]; question_id = event['result'].get('comment_id')
    records = [r for r in journal if r.get('id') == event.get('receipt_id')
               and r.get('event') == 'TOOL_RESULT' and r.get('detail', {}).get('result') == event['result']]
    questions = [c for c in ticket.get('comments', []) if c.get('id') == question_id and c.get('actor') == 'AGENT']
    replies = [c for c in ticket.get('comments', []) if c.get('id') == comment_id and c.get('actor') == 'USER']
    if len(records) != 1 or len(questions) != 1 or len(replies) != 1:
        raise Conflict('Agent human wait lacks original question/reply receipts')
    if ticket['comments'].index(replies[0]) <= ticket['comments'].index(questions[0]):
        raise Conflict('Agent human wait reply precedes its question')
    start = records[0]['at']; asked = timestamp(questions[0].get('created')); end = timestamp(replies[0].get('created'))
    if not isinstance(start, (int, float)) or not math.isfinite(start) or not asked <= start <= end <= now:
        raise Conflict('Agent human wait timestamp order differs')
    return {'question_id': question_id, 'comment_id': comment_id,
            'waiting_receipt_id': event['receipt_id'], 'asked_at': questions[0]['created'],
            'waiting_started_at': start, 'replied_at': replies[0]['created'],
            'seconds': end - start}


def total(ticket, journal, *, now):
    """Recompute every pause from original evidence, never trust saved seconds."""
    seconds = 0; last = float('-inf'); used = set()
    loops = ticket.get('agent_loop_history', [])
    for saved in ticket.get('agent_wait_pauses', []):
        if saved['comment_id'] in used:
            raise Conflict('Agent human wait reply was counted twice')
        matching = [l for l in loops if any(e.get('receipt_id') == saved.get('waiting_receipt_id')
                    for e in l.get('transcript', []))]
        if len(matching) != 1:
            raise Conflict('Agent human wait history evidence differs')
        checked = interval(ticket, matching[0], saved['comment_id'], journal, now=now)
        if checked != saved or checked['waiting_started_at'] < last:
            raise Conflict('Agent human wait interval changed or overlaps')
        seconds += checked['seconds']; last = timestamp(checked['replied_at']); used.add(saved['comment_id'])
    return seconds
