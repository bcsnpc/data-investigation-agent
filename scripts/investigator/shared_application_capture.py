"""Opt-in exact row deltas for repeated shared application table snapshots.

Authority is still read every time; only the capture representation is smaller.
Archived tapes without the explicit marker keep their full-snapshot grammar.
"""
import copy
from .process_tape import ACTIVE,value,TapeError
from .shared_state import sha

VERSION='EXACT_TABLE_DELTAS_V1'


def enabled(tape):
    return tape is not None and tape.bootstrap.get('state',{}).get('shared_application_capture')==VERSION


def validate_marker(state):
    if state.get('shared_application_capture')!=VERSION or 'shared_application' not in state:
        raise TapeError('TAPE_APPLICATION_CAPTURE_VERSION')


def validate_saved(table,saved):
    from .shared_application import validate_table
    if (not isinstance(saved,dict) or set(saved)!={'revision','body'}
            or saved['revision'] is not None and type(saved['revision'])is not int):
        raise TapeError('TAPE_APPLICATION_DELTA_SNAPSHOT')
    validate_table(table,saved['body'])


def build(previous,saved):
    if previous is None:return {'format':VERSION,'mode':'BASELINE','saved':saved}
    before,previous_hash=previous
    body=before['body'];after=saved['body']
    if body is None or after is None or any(body[k]!=after[k] for k in ('schema','columns')):
        return {'format':VERSION,'mode':'REPLACE','before_sha256':previous_hash,'saved':saved}
    old={r[0]:r for r in body['rows']};new={r[0]:r for r in after['rows']}
    changes=[{'rowid':k,'before':old.get(k),'after':new.get(k)} for k in sorted(old.keys()|new.keys()) if old.get(k)!=new.get(k)]
    return {'format':VERSION,'mode':'DELTA','before_sha256':previous_hash,'after_sha256':sha(saved),
            'revision':saved['revision'],'changes':changes}


def apply(table,previous,recorded):
    if not isinstance(recorded,dict) or recorded.get('format')!=VERSION:raise TapeError('TAPE_APPLICATION_DELTA_FORMAT')
    mode=recorded.get('mode')
    if mode=='BASELINE':
        if previous is not None or set(recorded)!={'format','mode','saved'}:raise TapeError('TAPE_APPLICATION_DELTA_BASELINE')
        result=recorded['saved']
    elif mode=='REPLACE':
        if (previous is None or set(recorded)!={'format','mode','before_sha256','saved'}
                or recorded['before_sha256']!=previous[1]):raise TapeError('TAPE_APPLICATION_DELTA_PARENT')
        result=recorded['saved']
    elif mode=='DELTA':
        if (previous is None or set(recorded)!={'format','mode','before_sha256','after_sha256','revision','changes'}
                or recorded['before_sha256']!=previous[1] or previous[0]['body'] is None
                or not isinstance(recorded['changes'],list)):
            raise TapeError('TAPE_APPLICATION_DELTA_PARENT')
        result=copy.deepcopy(previous[0]);rows={r[0]:r for r in result['body']['rows']};last=0
        for change in recorded['changes']:
            if (not isinstance(change,dict) or set(change)!={'rowid','before','after'} or type(change['rowid'])is not int
                    or change['rowid']<=last or change['before']==change['after'] or rows.get(change['rowid'])!=change['before']):
                raise TapeError('TAPE_APPLICATION_DELTA_BEFORE')
            last=change['rowid'];after=change['after']
            if after is None:rows.pop(last)
            elif not isinstance(after,list) or not after or after[0]!=last:raise TapeError('TAPE_APPLICATION_DELTA_ROW')
            else:rows[last]=after
        result['body']['rows']=[rows[k] for k in sorted(rows)];result['revision']=recorded['revision']
        if sha(result)!=recorded['after_sha256']:raise TapeError('TAPE_APPLICATION_DELTA_HASH')
    else:raise TapeError('TAPE_APPLICATION_DELTA_MODE')
    validate_saved(table,result)
    return result


def read(table,producer):
    tape=ACTIVE.get();name='shared_application:'+table
    if tape is not None and 'shared_application_capture' in tape.bootstrap.get('state',{}):validate_marker(tape.bootstrap['state'])
    if not enabled(tape):return value('CONFIGURATION',name,producer)
    cache=getattr(tape,'application_capture_snapshots',None)
    if cache is None:cache={};tape.application_capture_snapshots=cache
    previous=cache.get(table)
    def capture():
        saved=producer();validate_saved(table,saved)
        return build(previous,saved)
    recorded=value('CONFIGURATION',name,capture)
    saved=apply(table,previous,recorded)
    cache[table]=(copy.deepcopy(saved),sha(saved))
    return saved
