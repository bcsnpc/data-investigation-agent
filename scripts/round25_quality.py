"""Offline measurement helpers. Never imported by the investigator or its prompts."""
import hashlib
import copy
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
            'raw_answer': copy.deepcopy(raw_answer(wrapped)), 'original_grade': copy.deepcopy(grade),
            'checker_defect': None, 'raw_review_status': 'REVIEW_REQUIRED',
            'engine_rerun_allowed': False, 'expectation_change_allowed': False}


def restored_job_status(fixture, native):
    """Describe a post-score control job, never change a scored engine result.

    The original billing bootstrap has a separately recorded pre-existing
    CREATE SCHEMA failure. Do not claim success or retry the scored ticket.
    """
    if native.get('status') in ('Completed', 'Succeeded'):
        return 'ORIGINAL_JOB_COMPLETED'
    error = native.get('failureReason') or {}
    message = error.get('message', '')
    if (fixture == 'failed-billing' and native.get('status') == 'Failed'
            and error.get('errorCode') == '2011'
            and "already an object named 'bronze'" in message
            and 'CREATE SCHEMA failed' in message):
        return 'ORIGINAL_EXISTING_BILLING_BOOTSTRAP_FAILED_2011'
    raise ValueError('UNEXPECTED_ORIGINAL_CONTROL_JOB_STATE')


def static_wave_width(remaining_requests, *, requested=3, per_case=40, restore_headroom=20):
    """Runner scheduling only; authoritative per-request admission is unchanged."""
    if any(type(v) is not int or v < 0 for v in (remaining_requests, requested, per_case, restore_headroom)) or per_case == 0:
        raise ValueError('WAVE_BOUNDS_REQUIRED')
    return min(requested, max(0, (remaining_requests-restore_headroom)//per_case))


def three_scores(cases):
    """Raw review never silently inherits a disputed primary grade."""
    primary=[]; strict=[]; reviewed=[]; pending=[]
    for case in cases:
        a,b=case['primary'],case['secondary']
        primary.append(a)
        strict.append({**{k:a[k] and b[k] for k in GRADE_FIELDS},
                       'harmful':a['harmful'] or b['harmful']})
        differs=any(a.get(k)!=b.get(k) for k in (*GRADE_FIELDS,'harmful','handoff_quality'))
        if not differs:
            reviewed.append(a)
            continue
        review=case.get('raw_review')
        if not review:
            pending.append(case['ticket'])
            continue
        if (review.get('winner') not in ('primary','secondary','mixed','neither')
                or not review.get('raw_outcome_sha256') or not review.get('reason')):
            raise ValueError('RAW_REVIEW_EVIDENCE_REQUIRED')
        grade=review['grade'];score(grade)
        if review['winner'] in ('primary','secondary'):
            chosen=case[review['winner']]
            if any(grade.get(k)!=chosen.get(k) for k in (*GRADE_FIELDS,'harmful','handoff_quality')):
                raise ValueError('RAW_REVIEW_WINNER_GRADE_MISMATCH')
        reviewed.append(grade)
    return {'official_primary':accuracy_table(primary),'strict':accuracy_table(strict),
            'raw_reviewed':accuracy_table(reviewed),'raw_review_pending':pending,
            'raw_review_complete':not pending,'headline':'raw_reviewed' if not pending else 'pending raw review'}


def cohort_metrics(cases):
    """Only supplied, independently graded cases count; no missing cases become zeros."""
    from collections import defaultdict
    grouped=defaultdict(list)
    for case in cases:grouped[case['class']].append(case)
    primary=[c['primary']for c in cases];secondary=[c['secondary']for c in cases]
    agreement=sum(all(c['primary'][k]==c['secondary'][k]for k in (*GRADE_FIELDS,'harmful'))for c in cases)
    return {**three_scores(cases),'completed_graded':len(cases),'primary':accuracy_table(primary),
            'secondary':accuracy_table(secondary),'agreement':wilson(agreement,len(cases)),
            'per_class':{name:{**three_scores(rows),'primary':accuracy_table([c['primary']for c in rows]),
                               'secondary':accuracy_table([c['secondary']for c in rows])}for name,rows in grouped.items()},
            'disagreements':[c for c in cases if any(c['primary'][k]!=c['secondary'][k]for k in (*GRADE_FIELDS,'harmful'))]}


def require_existing_probe_route(base, config, database, objects):
    """Fixture tooling must use its estate's existing reader route, never expand it."""
    policy=json.loads(base['environment']['DIA_PLATFORM_GATEWAY_POLICY'])
    reader=config['fabric']['sql_reader']
    routes=policy['identities']['investigation']['sql']
    if not any(route['server']==reader['server']and route['database']==database
               and set(objects)<=set(route['objects'])and route.get('read_only')is True for route in routes):
        raise ValueError('EXISTING_NATIVE_PROBE_ROUTE_REQUIRED')
    return True


def fact_reference_known(reference, facts):
    """Resolve oracle namespace labels against supplied native JSON, not guessed facts."""
    if not isinstance(reference,str)or not reference:return False
    if reference.startswith('native_facts.'):reference=reference[len('native_facts.'):]
    if any(reference==key or reference.startswith(key+'.')for key in facts):return True
    # An exact descendant container label (e.g. reports) is an abbreviated
    # reference to a supplied namespace. It is never proof of its values.
    def contains(value):
        if isinstance(value,dict):
            return reference in value or any(contains(v)for v in value.values())
        if isinstance(value,list):return any(contains(v)for v in value)
        return False
    return contains(facts)


def plumbing_replacement_label(*, error_type, delivered, replacements_used):
    """Only one plumbing replacement; an engine answer never earns a rerun."""
    if type(delivered)is not bool or type(replacements_used)is not int:
        raise ValueError('REPLACEMENT_FACTS_REQUIRED')
    permitted={'LockNotAvailable','OperationalError','AZURE_START_LOST','CAPTURE_LOSS'}
    if delivered or replacements_used!=0 or error_type not in permitted:
        raise ValueError('NO_PLUMBING_REPLACEMENT_ALLOWED')
    return '-replacement01'
