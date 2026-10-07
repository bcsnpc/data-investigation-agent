"""Verify a separate model-only tape before grading its superseding sentence.

Historical runtime replay and its rendered outputs remain byte-exact. The
current mechanism invariant grades the explicitly authorised new provider
sentence, never silently takes a sentence from a different column.
"""
import base64
import hashlib
import json
from pathlib import Path
from investigator.mechanism_revision import effective_records,REASON
from investigator.process_tape import Tape,validate_event


def select_pools(path,source,*,root,pools):
    """Select by sealed source identity, never by family or column labels."""
    original_hash=hashlib.sha256(Path(path).read_bytes()).hexdigest()
    matching=[(records,revisions) for records,revisions in pools
              if any(r['source_tape_sha256']==original_hash for r in revisions['revisions'])]
    if len(matching)>1:raise ValueError('MECHANISM_SUPERSESSION_AMBIGUOUS_SOURCE_POOL')
    if not matching:return None
    records,revisions=matching[0]
    return select(path,source,root=root,records=records,revisions=revisions)


def select(path,source,*,root,records,revisions):
    original_hash=hashlib.sha256(Path(path).read_bytes()).hexdigest()
    matches=[r for r in revisions['revisions'] if r['source_tape_sha256']==original_hash]
    if not matches:return None
    if root is None:raise ValueError('MECHANISM_SUPERSESSION_PRIVATE_TAPE_REQUIRED')
    if len(matches)!=1:raise ValueError('MECHANISM_SUPERSESSION_AMBIGUOUS')
    revision=matches[0]
    if source is None or source['provider_event_sha256']!=revision['source_provider_event_sha256']:
        raise ValueError('MECHANISM_SUPERSESSION_SOURCE_EVENT_DIFFERS')
    original=next(r for r in records if r['tape_sha256']==original_hash)['attempts'][-1]
    if original['response']!=source['response']:
        raise ValueError('MECHANISM_SUPERSESSION_ORIGINAL_RESPONSE_DIFFERS')
    # Enforces every structured field, including future fields, against the
    # unchanged published extract of this exact sealed original response.
    effective_records(records,revisions)
    member=Path(revision['revision_tape_member']);root=Path(root).resolve()
    amended=(root/member).resolve()
    if member.is_absolute() or not amended.is_relative_to(root):raise ValueError('MECHANISM_SUPERSESSION_PATH')
    if hashlib.sha256(amended.read_bytes()).hexdigest()!=revision['revision_tape_sha256']:
        raise ValueError('MECHANISM_SUPERSESSION_TAPE_HASH_DIFFERS')
    tape=Tape(amended);state=tape.bootstrap['state']
    if (state['supersedes_tape_sha256']!=original_hash or state['reason']!=REASON
            or state['supersedes_provider_event_sha256']!=source['provider_event_sha256']):
        raise ValueError('MECHANISM_SUPERSESSION_BOOTSTRAP_DIFFERS')
    final=json.loads(validate_event(tape.events[-1],tape.events[-1]['ordinal']))
    if final['status']!='ACCEPTED' or final['result']['response']!=revision['response']:
        raise ValueError('MECHANISM_SUPERSESSION_NOT_ACCEPTED')
    event=next(e for e in reversed(tape.events) if e['kind']=='PROVIDER_RESPONSE')
    if event['sha256']!=revision['revision_provider_event_sha256']:
        raise ValueError('MECHANISM_SUPERSESSION_PROVIDER_EVENT_DIFFERS')
    request_event=next(e for e in reversed(tape.events) if e['kind']=='PROVIDER_REQUEST' and e['ordinal']<event['ordinal'])
    request=json.loads(validate_event(request_event,request_event['ordinal']))
    submitted=json.loads(request['input'])['mechanism']
    if (submitted['spine']!=source['payload'] or submitted['previous_mechanism']!=source['text']
            or submitted['reason']!=REASON):
        raise ValueError('MECHANISM_SUPERSESSION_PROVIDER_CONTEXT_DIFFERS')
    wrapper=json.loads(validate_event(event,event['ordinal']))
    response=json.loads(base64.b64decode(wrapper['body'],validate=True))
    answer=json.loads(''.join(c['text'] for o in response['output'] if o['type']=='message'
                             for c in o['content'] if c['type']=='output_text'))
    if answer!={'text':revision['response']['technical_output']['text']}:
        raise ValueError('MECHANISM_SUPERSESSION_PROVIDER_BODY_DIFFERS')
    return {'text':answer['text'],'provenance':'SEALED_PROVIDER_MECHANISM',
            'provider_event_sha256':event['sha256'],'source_tape_sha256':original_hash,
            'revision_tape_sha256':revision['revision_tape_sha256'],
            'structured_fields_byte_identical':True,'original_rendered_outputs_unchanged':True,'reason':REASON}
