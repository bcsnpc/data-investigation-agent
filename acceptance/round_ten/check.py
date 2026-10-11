"""Grade independently sealed tickets, then replay only earned additions offline.

The authored ticket index remains the outcome oracle. The selected evidence
roster pins artifacts; it cannot replace an expectation with an observed answer.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'acceptance/known_domain'),
               str(ROOT / 'acceptance/unknown_domain')]
from contract import answer_category, answer_matches


def corrected_case(case, sealed_bytes, corrections):
    """Apply explicit human corrections without replacing the original byte seal."""
    result = copy.deepcopy(case)
    for change in corrections:
        if change['id'] != case.get('id'):
            continue
        if hashlib.sha256(sealed_bytes).hexdigest() != change['original_sha256']:
            raise ValueError('EXPECTATION_CORRECTION_SOURCE_HASH_DIFFERS')
        column = change['column']
        if result['expectation_columns'][column] != change['before']:
            raise ValueError('EXPECTATION_CORRECTION_BEFORE_DIFFERS')
        if not change.get('authority') or not change.get('reason'):
            raise ValueError('EXPECTATION_CORRECTION_REQUIRES_HUMAN_REASON')
        result['expectation_columns'][column] = copy.deepcopy(change['after'])
    return result


def grade(case, column, run):
    expected = case['expectation_columns'][column]
    state = run.get('session') or {}
    intake = run.get('intake') or {}
    synthesis = state.get('synthesis') or {}
    actual = {'status': state.get('status') or intake.get('status'),
              'outcome': (state.get('assessment') or {}).get('classification'),
              'answer_category': None}
    errors = []
    if state:
        try:
            actual['answer_category'] = answer_category(state)
        except (ValueError, KeyError):
            errors.append('QUESTION_ACCOUNT_MISSING')
    if 'accepted_dispositions' in expected:
        disposition = actual['status']
        if (disposition == 'COMPLETED'
                and actual['outcome'] in ('NO_COMPARABLE_PATH', 'NO_KNOWN_PATTERN')
                and actual['answer_category'] in ('NOT_ANSWERED', 'NO_REPORTED_FIGURE')):
            disposition = 'CAPABILITY_REFUSAL'
        if disposition not in expected['accepted_dispositions']:
            errors.append('REQUEST_NOT_REFUSED')
    else:
        errors.extend(key.upper() + '_CHANGED' for key, value in expected.items()
                      if actual.get(key) != value)
    if run.get('error'):
        errors.append('RUN_ERROR')
    if state and synthesis.get('status') != 'COMPLETED':
        errors.append('SYNTHESIS_NOT_COMPLETED')
    outputs = synthesis.get('outputs') if state else intake.get('refusal_outputs')
    outputs = outputs or {}
    from investigator.narrative_form import validate
    from investigator.path_narrative import validate_mechanism
    for kind in ('business_output', 'technical_output'):
        output = outputs.get(kind) or {}
        text = output.get('explanation', {}).get('text')
        if not isinstance(text, str) or not text:
            errors.append(kind + ':MISSING_OUTPUT')
            continue
        if state and actual['answer_category'] and not answer_matches(actual['answer_category'], text):
            errors.append(kind + ':ANSWER_HEADER_DIFFERS')
        try:
            # The exact quoted question is provenance, not narrative prose.
            validate(text.split('\n\n', 1)[-1], kind == 'business_output')
            mechanism = output.get('model_mechanism') or {}
            if kind == 'technical_output' and mechanism.get('text'):
                validate_mechanism(mechanism['text'])
        except ValueError as exc:
            errors.append(kind + ':FORM:' + str(exc))
    reproduction = case.get('expected_reproduction')
    if reproduction and state:
        from decimal import Decimal, InvalidOperation
        from investigator.reproduction_composition import select
        lead = select(state.get('observations', []))
        if lead is None or lead.get('label') != reproduction['label']:
            errors.append('REPRODUCTION_LABEL_CHANGED')
        if lead is not None:
            try:
                if Decimal(str((lead.get('reported_figure') or {}).get('value'))) != Decimal(reproduction['value']):
                    errors.append('AUTHORED_FIGURE_CHANGED')
                if (reproduction['label'] == 'REPRODUCED'
                        and Decimal(str(lead.get('reproduced_value'))) != Decimal(reproduction['value'])):
                    errors.append('REPRODUCED_VALUE_CHANGED')
            except (InvalidOperation, ValueError, KeyError):
                errors.append('REPRODUCTION_VALUE_UNAVAILABLE')
    return {'actual': actual, 'errors': sorted(set(errors)), 'passed': not errors}


def run(roster_path, fixture_root, output):
    from private_bundle import tape_path, estate_manifest
    from investigator.process_tape import Tape
    from recorded_engine import replay_revision
    roster = json.loads(Path(roster_path).read_text())
    index = json.loads((ROOT / 'acceptance/tickets/round-ten/index.json').read_text())
    entries = {row['id']: row for row in index['entries']}
    corrections = json.loads((ROOT / 'acceptance/tickets/round-ten/expectation-corrections.json').read_text())['corrections']
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    results = []
    for selected in roster['entries']:
        row = {'id': selected['id'], 'column': selected['column'], 'passed': False,
               'network_requests': 0, 'physical_requests': 0}
        try:
            entry = entries[row['id']]
            case_bytes = (ROOT / entry['path']).read_bytes()
            if hashlib.sha256(case_bytes).hexdigest() != entry['sha256']:
                raise ValueError('AUTHORED_EXPECTATION_HASH_DIFFERS')
            raw = (Path(fixture_root) / selected['run_path']).read_bytes()
            if hashlib.sha256(raw).hexdigest() != selected['run_sha256']:
                raise ValueError('EARNED_SOURCE_HASH_DIFFERS')
            original = json.loads(raw)
            case = corrected_case(json.loads(case_bytes), case_bytes, corrections)
            from investigator.onboarding import digest
            if (original.get('family') != row['id']
                    or digest((original.get('intake') or {}).get('text')) != case['ticket_hash']
                    or (original.get('fixture_state') or {}).get('name') != case['fixture_state']):
                raise ValueError('EARNED_TICKET_OR_FIXTURE_IDENTITY_DIFFERS')
            if original.get('session') and original['session'].get('model_id') != case['model_id']:
                raise ValueError('EARNED_MODEL_IDENTITY_DIFFERS')
            path = tape_path(original, fixture_root)
            if hashlib.sha256(path.read_bytes()).hexdigest() != selected['tape_sha256']:
                raise ValueError('EARNED_TAPE_HASH_DIFFERS')
            tape = Tape(path)
            tape.validate()
            native_state = tape.bootstrap['state'].get('fixture_state')
            if native_state != original.get('fixture_state'):
                raise ValueError('EARNED_TAPE_FIXTURE_STATE_DIFFERS')
            row['tape_class'] = tape.tape_class
            replayed = replay_revision(path, output / (row['column'] + '-' + row['id']),
                tape.engine_revision, estate_manifest=estate_manifest(tape, fixture_root))
            state = replayed['session']
            reconstructed = {'error': None}
            reconstructed['session' if original.get('session') else 'intake'] = state
            current = grade(case, row['column'], reconstructed)
            row['current_policy_audit'] = current
            from historical_policy import select, grade as historical_grade
            policy = select(roster_path, selected)
            # Run/tape byte seals were checked above. The cohort pin additionally
            # binds the whole roster and each exact selected run/tape hash.
            if policy is not None:
                row.update(historical_grade(policy, case, row['column'], reconstructed))
                row['historical_policy'] = {key: policy[key] for key in
                    ('revision', 'archive_sha256', 'checker_sha256', 'module_sha256')}
            else:
                row.update(current)
                row['historical_policy'] = None
            row['replay_matched'] = replayed['matched']
            row['passed'] = row['passed'] and replayed['matched']
        except Exception as exc:
            row['reason'] = type(exc).__name__ + ':' + str(exc)
        results.append(row)
    result = {'count': len(results), 'passed': sum(r['passed'] for r in results),
              'network_requests': 0, 'physical_requests': 0, 'rows': results,
              'current_policy_audit': {'count': len(results),
                  'passed': sum((r.get('current_policy_audit') or {}).get('passed', False) for r in results),
                  'failures': [{'id': r['id'], 'column': r['column'],
                      'errors': (r.get('current_policy_audit') or {}).get('errors', []),
                      'reason': r.get('reason')}
                      for r in results if not (r.get('current_policy_audit') or {}).get('passed', False)]},
              'claim': 'Historical producer replay against independently authored synthetic expectations; not general or unfamiliar-domain acceptance.'}
    (output / 'scores.json').write_text(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--roster', required=True, type=Path)
    parser.add_argument('--fixture-root', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    result = run(args.roster, args.fixture_root, args.output)
    print(json.dumps({key: result[key] for key in ('count', 'passed', 'network_requests', 'physical_requests')}))
    print(json.dumps({'CURRENT_POLICY_AUDIT': result['current_policy_audit']}))
    raise SystemExit(0 if result['count'] == result['passed'] else 1)
