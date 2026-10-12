"""Exclude receipt-backed inactive waiting, including a queued real reply."""
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


def queued_reply(ticket, loop, comment_id, journal, *, now):
    """The worker remains inactive until it consumes the already saved reply."""
    human=interval(ticket,loop,comment_id,journal,now=now)
    end=timestamp(human['replied_at'])
    return {'version':'queued-agent-reply-v1','comment_id':comment_id,
        'waiting_receipt_id':human['waiting_receipt_id'],'replied_at':human['replied_at'],
        'consumed_at':now,'seconds':now-end}


def total(ticket, journal, *, now):
    """Recompute every pause from original evidence, never trust saved seconds."""
    seconds = 0; last = float('-inf'); used = set();segments=[];humans={}
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
        humans[checked['comment_id']]=checked
        segments.append((checked['waiting_started_at'],last))
    queued=set()
    for saved in ticket.get('agent_reply_queue_pauses',[]):
        identity=saved['comment_id'];human=humans.get(identity)
        if identity in queued or identity not in ticket.get('agent_consumed_replies',[]) or human is None:
            raise Conflict('Queued reply wait lacks a unique consumed human reply')
        start=timestamp(human['replied_at']);end=saved['consumed_at']
        if not isinstance(end,(int,float)) or not math.isfinite(end) or not start<=end<=now:
            raise Conflict('Queued reply wait timestamp order differs')
        expected={'version':'queued-agent-reply-v1','comment_id':identity,
            'waiting_receipt_id':human['waiting_receipt_id'],'replied_at':human['replied_at'],
            'consumed_at':end,'seconds':end-start}
        marker=[r for r in journal if r.get('id')==saved.get('receipt_id') and
                r.get('event')=='QUEUED_REPLY_WAIT_EXCLUDED' and r.get('detail',{}).get('pause')==expected]
        if saved!={**expected,'receipt_id':saved.get('receipt_id')} or len(marker)!=1 or marker[0]['at']<end:
            raise Conflict('Queued reply wait lacks its consumption receipt')
        if any(start<=r['at']<end and r.get('event') in ('DECISION','DECISION_REJECTED','TOOL_RESULT','ADMISSION_OR_PROVIDER_FAILED') for r in journal):
            raise Conflict('Queued reply wait overlaps active agent work')
        queued.add(identity);seconds+=end-start;segments.append((start,end))
    previous=float('-inf')
    for start,end in sorted(segments):
        if start<previous:raise Conflict('Inactive agent intervals overlap')
        previous=end
    return seconds
