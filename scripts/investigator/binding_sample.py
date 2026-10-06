"""Per-binding, typed sample comparisons; no ticket measure selects the profile.

A profile is a bounded witness, not a proof of global or rowwise equivalence.
The adapter establishes the target type and compiles both complete profiles.
"""
import copy
from decimal import Decimal
from datetime import date
from jsonschema import Draft202012Validator
from .code_sources import obj
from .lineage_binding import validate, seal, VerificationHold
from .usage_governance import UsageHold

PROFILES = {'NUMERIC': ('sum', 'count'),
            'STRING': ('count', 'distinct_count', 'hash_sum'),
            'TEMPORAL': ('min', 'max', 'count'),
            'BOOLEAN': ('true_count', 'count')}
TEXT = {'type': 'string', 'minLength': 1, 'maxLength': 500}
SAMPLE_SCHEMA = {'oneOf': [
    obj({'kind': {'const': 'KEY_RANGE'}, 'column': TEXT,
         'lower': {'type': 'integer'}, 'upper': {'type': 'integer'}, 'provenance': TEXT}),
    obj({'kind': {'const': 'DATE_WINDOW'}, 'column': TEXT,
         'lower': {'type': 'string', 'format': 'date'},
         'upper': {'type': 'string', 'format': 'date'}, 'provenance': TEXT})]}


def sample_address(proposal, sample, profile):
    validate(proposal)
    Draft202012Validator(SAMPLE_SCHEMA).validate(sample)
    if sample['kind'] == 'DATE_WINDOW':
        for key in ('lower', 'upper'):
            if date.fromisoformat(sample[key]).isoformat() != sample[key]:
                raise ValueError('Sample dates require canonical ISO dates')
    if sample['lower'] > sample['upper']:
        raise ValueError('Reversed sample key range')
    if profile not in PROFILES:
        raise ValueError('Unsupported target type profile')
    # Extraction provenance/confidence cannot change the identity of a read.
    binding={k:v for k,v in proposal.items() if k not in ('extractor','confidence')}
    value = {'kind': 'BINDING_SAMPLE', 'proposal_hash': seal(binding),
             'sample': copy.deepcopy(sample), 'profile': profile}
    value['id'] = seal(value)
    return value


def validate_address(address):
    if not isinstance(address, dict) or set(address) != {
            'kind', 'proposal_hash', 'sample', 'profile', 'id'}:
        raise ValueError('Binding sample address fields differ')
    if address['kind'] != 'BINDING_SAMPLE' or address['profile'] not in PROFILES:
        raise ValueError('Binding sample address kind/profile differs')
    Draft202012Validator(SAMPLE_SCHEMA).validate(address['sample'])
    if address['sample']['kind'] == 'DATE_WINDOW':
        for key in ('lower', 'upper'):
            if date.fromisoformat(address['sample'][key]).isoformat() != address['sample'][key]:
                raise ValueError('Sample dates require canonical ISO dates')
    if address['sample']['lower'] > address['sample']['upper']:
        raise ValueError('Reversed sample key range')
    if address['id'] != seal({k: v for k, v in address.items() if k != 'id'}):
        raise ValueError('Binding sample address identity differs')
    return address


def _quantities(value, profile):
    if not isinstance(value, dict) or set(value) != set(PROFILES[profile]):
        raise ValueError('Complete target-type quantity set was not obtained')
    result = {}
    for key, item in value.items():
        if item is None:
            if key not in ('sum', 'min', 'max', 'hash_sum'):
                raise ValueError('Count is not BLANK')
            result[key] = None
        elif profile == 'TEMPORAL' and key in ('min', 'max'):
            if not isinstance(item, str) or not item:
                raise ValueError('Temporal quantity lacks canonical text')
            result[key] = item
        else:
            if isinstance(item, bool):
                raise ValueError('Quantity must not coerce boolean to number')
            number = Decimal(str(item))
            if not number.is_finite():
                raise ValueError('Nonfinite sample quantity')
            if key in ('count', 'distinct_count', 'true_count') and (
                    number < 0 or number != number.to_integral_value()):
                raise ValueError('Count must be a nonnegative integer')
            result[key] = number
    if profile == 'BOOLEAN' and result['true_count'] > result['count']:
        raise ValueError('True count exceeds count')
    if profile == 'STRING' and result['distinct_count'] > result['count']:
        raise ValueError('Distinct count exceeds count')
    return result


def verify(proposal, *, context, sample, profile, compiler, execute):
    proposal = validate(proposal)
    address = sample_address(proposal, sample, profile)
    if not isinstance(context, str) or not context:
        raise ValueError('Sample verification needs its retained context')
    receipt = {'verification_version': 'binding-profile-v1', 'proposal': proposal,
               'context': context, 'address': address, 'observations': [],
               'status': 'UNVERIFIED', 'reason': None,
               'limits': ['Bounded aggregate witnesses do not prove global or rowwise equivalence, business intent or currency.']}
    try:
        plans = [compiler(proposal, side, context, address) for side in ('TARGET', 'SOURCE')]
        semantics=[p.get('string_semantics') if isinstance(p,dict) else None for p in plans]
        if any(s is not None for s in semantics):
            from .string_semantics import validate as validate_semantics
            if semantics[0]!=semantics[1] or not isinstance(semantics[0],dict):
                raise ValueError('String semantics declarations differ between probe plans')
            declared=semantics[0]
            if set(declared)!={'target','sources','comparison'} or declared['comparison']!='TARGET_SEMANTICS_ON_BOTH_SIDES':
                raise ValueError('Invalid comparison semantics declaration')
            validate_semantics(declared['target'])
            if set(declared['sources'])!={s['table'] for s in proposal['sources']}:
                raise ValueError('Source semantics do not cover the declared inputs')
            for value in declared['sources'].values():validate_semantics(value)
            receipt['string_semantics']=copy.deepcopy(declared)
        if profile == 'STRING' and not any(s is not None for s in semantics):
            normalizations = [p.get('normalization') if isinstance(p, dict) else None for p in plans]
            for norm in normalizations:
                if not isinstance(norm, dict) or norm.get('status') != 'DECLARED':
                    raise ValueError('COLLATION_UNDECLARED: comparison_normalization is required')
                if (not isinstance(norm.get('collation'), str) or not norm['collation']
                        or type(norm.get('trim')) is not bool or type(norm.get('case_fold')) is not bool
                        or not isinstance(norm.get('evidence'), str) or not norm['evidence']):
                    raise ValueError('Invalid declared comparison normalization')
            if normalizations[0] != normalizations[1]:
                raise ValueError('Comparison normalizations differ between probes')
            receipt['normalization'] = copy.deepcopy(normalizations[0])
    except (ValueError, NotImplementedError) as exc:
        receipt['reason'] = 'Cannot compile faithfully: ' + str(exc)
        return receipt
    for side, plan in zip(('TARGET', 'SOURCE'), plans):
        try:
            observation = execute(side, plan)
        except UsageHold as exc:
            receipt['reason'] = 'Verification stopped at the admitted budget or deadline: ' + str(exc)
            raise VerificationHold(receipt) from exc
        except (ValueError, OSError, TimeoutError) as exc:
            receipt['observations'].append({'status': 'FAILED', 'side': side,
                                           'error_type': type(exc).__name__, 'error': str(exc)})
            receipt['reason'] = 'The ' + side.lower() + ' read failed.'
            return receipt
        receipt['observations'].append(copy.deepcopy(observation))
        try:
            if observation['status'] != 'COMPLETED':
                raise ValueError('The ' + side.lower() + ' read did not complete')
            if observation['context'] != context or observation['address'] != address:
                raise ValueError('Observed context or binding sample differs')
            _quantities(observation['quantities'], profile)
            evidence = observation['evidence']
            if evidence['context_id'] != context:
                raise ValueError('Original probe context differs')
            rows=evidence.get('values')
            if not isinstance(rows,list) or len(rows)!=1 or not isinstance(rows[0],dict):
                raise ValueError('Original complete one-row profile was not obtained')
            original={}
            for name in PROFILES[profile]:
                item=rows[0][name]
                original[name]=item['value'] if isinstance(item,dict) else item
            if _quantities(original,profile)!=_quantities(observation['quantities'],profile):
                raise ValueError('Profile differs from original query values')
            if evidence['read_address'] != address:
                raise ValueError('Original probe address differs')
            from .process_debugging import attest_surface
            attestation = evidence['surface_attestation']
            if attest_surface(evidence['execution_surface'], evidence['surface_report'],
                              attestation.get('required_fields', ())) != attestation:
                raise ValueError('Original surface attestation differs')
        except (KeyError, ValueError, TypeError, ArithmeticError) as exc:
            receipt['reason'] = str(exc)
            return receipt
    from .surface_difference import grade, BOUNDARY_GRADES
    evidence = [o['evidence'] for o in receipt['observations']]
    receipt['surface_difference'] = grade(*evidence)
    if receipt['surface_difference']['grade'] not in BOUNDARY_GRADES:
        receipt['reason'] = 'No independent quantity-bound surface comparison'
        return receipt
    from .snapshot_attestation import comparison
    observation = {'upper_evidence_id': evidence[0]['id'], 'lower_evidence_id': evidence[1]['id'],
                   'upper_execution_surface': evidence[0]['execution_surface'],
                   'lower_execution_surface': evidence[1]['execution_surface']}
    snapshot = comparison(observation, *(e.get('snapshot_identity') for e in evidence))
    receipt['snapshot_attestation'] = snapshot
    receipt['snapshot_status'] = snapshot['status']
    receipt['requires_reverification'] = snapshot['status'] != 'SNAPSHOT_VERIFIED'
    if receipt['requires_reverification']:
        receipt['limits'].append('SNAPSHOT_UNVERIFIED: served versions were not bound and aligned to both value queries; timing is not excluded. Reverify on next use.')
    equal = (_quantities(receipt['observations'][0]['quantities'], profile) ==
             _quantities(receipt['observations'][1]['quantities'], profile))
    receipt['status'] = 'VERIFIED' if equal else 'FALSIFIED'
    receipt['reason'] = 'All bounded profile quantities agree.' if equal else 'Bounded profile quantities differ.'
    return receipt
