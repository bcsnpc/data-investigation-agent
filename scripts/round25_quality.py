"""Offline measurement helpers. Never imported by the investigator or its prompts."""
import hashlib
import json
import math
import subprocess
from pathlib import Path

GRADE_FIELDS = ('verdict_match', 'layer_match', 'cause_match')


def wilson(correct, total):
    """Two-sided 95% Wilson interval; an empty sample is not measurable."""
    if type(correct) is not int or type(total) is not int or not 0 <= correct <= total:
        raise ValueError('INVALID_BINOMIAL_COUNTS')
    if total == 0:
        return {'correct': 0, 'total': 0, 'accuracy': None, 'lower': None,
                'upper': None, 'confidence': .95, 'method': 'Wilson'}
    z = 1.959963984540054
    p = correct / total
    divisor = 1 + z*z/total
    center = (p + z*z/(2*total)) / divisor
    radius = z * math.sqrt(p*(1-p)/total + z*z/(4*total*total)) / divisor
    return {'correct': correct, 'total': total, 'accuracy': p,
            'lower': max(0., center-radius), 'upper': min(1., center+radius),
            'confidence': .95, 'method': 'Wilson'}


def score(grade):
    if any(type(grade.get(k)) is not bool for k in (*GRADE_FIELDS, 'harmful')):
        raise ValueError('GRADING_BOOLEANS_REQUIRED')
    return int(all(grade[k] for k in GRADE_FIELDS))


def accuracy_table(records):
    """Same all-three rule as Round24; separate dimensions are never averaged."""
    return {'all_three': wilson(sum(score(r) for r in records), len(records)),
            **{k: wilson(sum(r[k] for r in records), len(records)) for k in GRADE_FIELDS},
            'harmful': wilson(sum(r['harmful'] for r in records), len(records))}


def verify_freeze(receipt, root=None):
    """Git applies working-tree filters in batch, avoiding false CRLF changes."""
    root = Path(root or Path(__file__).resolve().parents[1])
    names = sorted(receipt['engine_files'])
    actual = subprocess.check_output(['git', 'hash-object', '--stdin-paths'],
                                    input='\n'.join(names)+'\n', text=True, cwd=root).splitlines()
    if len(actual) != len(names):
        raise ValueError('INCOMPLETE_ENGINE_FILE_CHECK')
    changed = [name for name, blob in zip(names, actual)
               if blob != receipt['engine_files'][name]['git_canonical_blob']]
    if changed:
        raise ValueError('FROZEN_ENGINE_CHANGED: '+','.join(changed))
    return {'files_checked': len(names), 'runtime_unchanged': True,
            'frozen_commit': receipt['commit'], 'worker_image': receipt['worker_image']}


def raw_answer(wrapped):
    answer = wrapped.get('result', wrapped)
    outputs = answer.get('outputs') or {}
    return {'status': answer.get('status'), 'stop': answer.get('stop'),
            'business': outputs.get('business', answer.get('business')),
            'technical': outputs.get('technical'), 'handoff': answer.get('handoff')}


def audit_failure(wrapped, grade, *,outcome_bytes):
    """Bind every zero to full raw prose/structure, never just a header mapping.

    This is an audit record, not an automatic override of either grader.
    A semantic disagreement requires explicit review against the raw answer.
    """
    if score(grade):
        raise ValueError('FAIL_AUDIT_REQUIRES_ZERO')
    return {'raw_outcome_sha256': hashlib.sha256(outcome_bytes).hexdigest(),
            'raw_answer': raw_answer(wrapped), 'original_grade': grade,
            'checker_defect': None, 'raw_review_status': 'REVIEW_REQUIRED',
            'engine_rerun_allowed': False, 'expectation_change_allowed': False}
