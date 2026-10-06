"""Control producers consume the response bounds the worker consumes."""
import json
from pathlib import Path

PATH=Path(__file__).resolve().parents[2]/'infra/scripts/WorkerResponseBounds.json'


def bounds(worker):
    values=json.loads(PATH.read_text(encoding='utf8'))
    if worker not in values:raise ValueError('Worker response contract undeclared: '+worker)
    value=values[worker]
    if (set(value)!={'minimum_rows','maximum_rows'} or
            any(type(v) is not int for v in value.values()) or
            not 1<=value['minimum_rows']<=value['maximum_rows']<=251):
        raise ValueError('Invalid worker response bounds')
    return value


def sql_request(worker,query,columns,objects):
    return {'query':query,'parameters':[],'response_mode':'records',
            'max_rows':bounds(worker)['minimum_rows'],'result_columns':list(columns),
            'require_read_only':True,'read_only_objects':list(objects)}


def finish(tape,result):
    # Tape owns this lifecycle, including validation. Never treat the absence
    # of an attribute as a value or default it with getattr.
    if type(tape.finished) is not bool:raise TypeError('Tape.finished must be boolean')
    if not tape.finished:tape.finish(result)
