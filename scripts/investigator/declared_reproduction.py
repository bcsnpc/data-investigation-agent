"""Optional, within-layer reproduction of a declared scope, not a boundary test.

Adapters resolve native declarations into typed IN restrictions and execute the
composed neutral scope. The engine never parses native definitions or queries.
The vertical outcome remains separate from this finding, including its refusals.
"""
import copy
import json
from decimal import Decimal, InvalidOperation
from . import proposal_limits as limits

CAPABILITY = 'declared_context_reproduction'
KIND = 'DECLARED_CONTEXT_REPRODUCTION'
LABELS = ('REPRODUCED', 'NOT_REPRODUCED')
NO_FIGURE = 'No reported figure supplied.'
BASELINE_LIMIT = 'The undeclared-context value remains subject to row-level security and other native restrictions; it is not an unrestricted or true total.'
ACTIVE_LIMIT = 'Declared-context reproduction does not establish the active selection, security context or cross-filtering, or whether the number is business-correct.'
TIMING_LIMIT = 'The within-layer reads are not bound to a shared served data version; timing may explain a mismatch.'
OPEN_LIMIT = 'An undeclared selection, security context, cross-filtering or a deeper divergence may account for the reported figure; none was excluded.'


def _typed(value):
    if value is not None and type(value) not in (str, int, float, bool):
        raise ValueError('Unsupported restriction value type')
    if (type(value) is str and len(value)>limits.FILTER_STRING
            or type(value) is int and abs(value)>limits.EXACT_INTEGER):
        raise ValueError('Restriction value exceeds the consumer bound')
    return json.dumps(value, sort_keys=True, allow_nan=False, ensure_ascii=False)


def compose(restrictions):
    """Intersect every same-field declaration; retain an empty intersection."""
    if not isinstance(restrictions, list) or not 1 <= len(restrictions) <= 32:
        raise ValueError('Declared restrictions require a bounded nonempty list')
    fields = {}
    for restriction in restrictions:
        if (not isinstance(restriction, dict) or set(restriction) != {'field_id', 'operator', 'values'}
                or not isinstance(restriction['field_id'], str) or not 1<=len(restriction['field_id'])<=limits.CONTEXT_ID
                or restriction['operator'] != 'IN' or not isinstance(restriction['values'], list)
                or len(restriction['values']) > limits.FILTER_VALUES):
            raise ValueError('Unsupported declared restriction; faithful translation required')
        values = {_typed(value): value for value in restriction['values']}
        field = restriction['field_id']
        fields[field] = ({key: value for key, value in fields[field].items() if key in values}
                         if field in fields else values)
    return [{'field_id': field, 'operator': 'IN', 'values': [values[k] for k in sorted(values)]}
            for field, values in sorted(fields.items())]


def applicable(restrictions, scope):
    """A predicate must concern an explicitly resolved ticket scope field."""
    fields = set(scope.get('dimension_ids') or [])
    for restriction in scope.get('filters') or []:
        field = restriction.get('column_id') or restriction.get('field_id')
        if field: fields.add(field)
    return bool(fields & {r['field_id'] for r in restrictions})


def number(value):
    if isinstance(value, dict) and set(value) == {'quantity'}: value = value['quantity']
    if value is None or isinstance(value, bool): raise ValueError('A finite scalar quantity is required')
    try:
        result = Decimal(str(value))
        if not result.is_finite() or (result and abs(result.adjusted()) > 100):
            raise ValueError('A finite bounded scalar quantity is required')
    except InvalidOperation as exc:
        raise ValueError('A finite scalar quantity is required') from exc
    text = format(result, 'f')
    return (text.rstrip('0').rstrip('.') if '.' in text else text) if result else '0'


def _label(reported, reproduced):
    return None if reported is None else ('REPRODUCED' if reported == reproduced else 'NOT_REPRODUCED')


def render(marker, business=False, include_limits=True):
    """Facts and qualifications are rendered by the engine, never model prose."""
    baseline = marker['undeclared_context_value']; declared = marker['reproduced_value']
    first = f'Within-layer check: the same calculation service and account returned an undeclared-context value of {baseline}, and the declared selections produced {declared}.'
    if marker['label'] == 'REPRODUCED':
        finding = f"The declared selections reproduce the reported figure of {marker['reported_figure']}; they account for that figure without requiring a difference further back."
    elif marker['label'] == 'NOT_REPRODUCED':
        finding = f"The declared selections do not reproduce the reported figure of {marker['reported_figure']}."
    else:
        finding = 'No reported figure supplied; the produced value has no reproduction verdict.'
    limits = ('This does not establish the active selections, business correctness or an unrestricted total. '
              'Different update times, other selections or security restrictions, and a difference further back remain possible.')
    if business:
        return first + ' ' + finding + ' ' + limits
    return (f"WITHIN_LAYER_CHECK ({marker['id']}): undeclared-context value {baseline}; declared-context value {declared}. "
            + finding + (' ' + limits if include_limits else ''))


def run(adapter, layer, measure_id, scope):
    """Callable independently, or before the vertical walk attempts a lower read.

    Not-declared/nonapplicable checks issue no value reads. Once applicable, both
    scopes use the same governed execution method; no baseline reuse or guessing.
    Exceptions from dispatch/budget admission propagate, never turn into findings.
    """
    from .process_debugging import attest, _observation, _surface_key
    if CAPABILITY not in adapter.capabilities():
        return {'status': 'UNDECLARED', 'observations': []}
    declaration = adapter.declared_context(layer, measure_id, copy.deepcopy(scope))
    if declaration.get('status') != 'DECLARED':
        return {'status': declaration.get('status', 'UNDECLARED'),
                'reason': declaration.get('reason') or 'Declared scope evidence is unavailable.', 'observations': []}
    restrictions = compose(declaration['restrictions'])
    if not applicable(restrictions, scope):
        return {'status': 'UNDECLARED', 'reason': 'No declared predicate bears on the resolved ticket scope.', 'observations': []}
    definition = _observation(declaration['evidence'], 'declared_context_definition')
    if (not definition or definition.get('status') != 'COMPLETED'
            or definition.get('completeness') != 'COMPLETE_RESPONSE'
            or definition.get('declaration_provenance') != 'DECLARED_BY_DEFINITION'
            or definition.get('declared_restrictions') != declaration['restrictions']):
        raise ValueError('Declared scope requires retained definition evidence and provenance')
    reported = scope.get('reported_figure')
    reported = number(reported) if reported is not None else None
    observations = [definition]
    probes = []
    for purpose, applied in (('UNDECLARED_CONTEXT', []), ('DECLARED_CONTEXT', restrictions)):
        probe = attest(adapter.evaluate_declared_context(layer, measure_id,
                        {'restrictions': copy.deepcopy(applied), 'dimension_ids': []}))
        if probe.evidence:
            observed = _observation(probe.evidence, 'declared_context_read')
            observed['execution_surface'] = probe.execution_surface
            observed['reproduction_purpose'] = purpose
            if probe.query: observed['query'] = probe.query
            observations.append(observed)
        if probe.status != 'OBSERVED' or not probe.evidence:
            return {'status': 'UNAVAILABLE', 'reason': probe.reason or 'Reproduction quantity unavailable.',
                    'observations': observations}
        if (probe.layer != layer['id'] or probe.evidence.get('applied_restrictions') != applied
                or probe.evidence.get('measure_id') != measure_id
                or probe.evidence.get('completeness') != 'COMPLETE_RESPONSE'):
            raise ValueError('Executed reproduction scope/measure/completeness differs')
        observations[-1]['reproduction_quantity'] = number(probe.value)
        probes.append(probe)
    a, b = probes
    if (_surface_key(a.execution_surface) is None or _surface_key(a.execution_surface) != _surface_key(b.execution_surface)
            or a.execution_surface['identity'].casefold() != b.execution_surface['identity'].casefold()):
        return {'status': 'UNAVAILABLE', 'reason': 'Reproduction requires the same execution surface and identity.', 'observations': observations}
    if len({o['id'] for o in observations}) != 3:
        raise ValueError('Reproduction requires distinct definition and read receipts')
    marker = _observation({'id': 'declared-reproduction-' + b.evidence['id'], 'tool': 'process',
        'check_kind': KIND, 'comparison_status': 'WITHIN_LAYER_CHECK',
        'definition_evidence_id': definition['id'], 'measure_id': measure_id,
        'upper_layer': a.layer, 'lower_layer': b.layer,
        'upper_evidence_id': a.evidence['id'], 'lower_evidence_id': b.evidence['id'],
        'upper_execution_surface': a.execution_surface, 'lower_execution_surface': b.execution_surface,
        'upper_surface_attestation': a.evidence['surface_attestation'], 'lower_surface_attestation': b.evidence['surface_attestation'],
        'composed_restrictions': restrictions,
        'undeclared_context_value': observations[-2]['reproduction_quantity'],
        'reproduced_value': observations[-1]['reproduction_quantity'], 'reported_figure': reported,
        'label': _label(reported, observations[-1]['reproduction_quantity']),
        'unavailability': NO_FIGURE if reported is None else None,
        'values_equal': observations[-2]['reproduction_quantity'] == observations[-1]['reproduction_quantity'],
        'limitations': [BASELINE_LIMIT, ACTIVE_LIMIT, TIMING_LIMIT, OPEN_LIMIT]}, 'declared_context_reproduction')
    observations.append(marker)
    validate(marker, {o['id']: o for o in observations})
    return {'status': 'COMPLETED', 'finding': marker, 'observations': observations,
            'business_output': render(marker,business=True), 'technical_output': render(marker)}


def validate(marker, observations, quantities=None):
    """Validate originals (and sealed scalar quantities during synthesis)."""
    from .process_debugging import _surface_key, attest_surface
    if marker.get('check_kind') != KIND or marker.get('comparison_status') != 'WITHIN_LAYER_CHECK':
        raise ValueError('Reproduction is within-layer evidence only')
    if set(marker.get('process_roles', [])) != {'declared_context_reproduction'}:
        raise ValueError('Reproduction cannot satisfy boundary or presentation-context roles')
    refs = [marker.get(k) for k in ('definition_evidence_id', 'upper_evidence_id', 'lower_evidence_id')]
    if len(set(refs)) != 3 or any(r not in observations for r in refs):
        raise ValueError('Reproduction requires three distinct original receipts')
    definition, a, b = [observations[r] for r in refs]
    if (set(definition.get('process_roles', [])) != {'declared_context_definition'}
            or any(set(o.get('process_roles', [])) != {'declared_context_read'} for o in (a,b))):
        raise ValueError('Reproduction receipts cannot satisfy vertical outcome roles')
    if any(o.get('status') != 'COMPLETED' or o.get('completeness') != 'COMPLETE_RESPONSE' for o in (definition, a, b)):
        raise ValueError('Reproduction requires complete original receipts')
    if definition.get('declaration_provenance') != 'DECLARED_BY_DEFINITION':
        raise ValueError('Reproduction requires declared definition provenance')
    restrictions = compose(definition['declared_restrictions'])
    if marker['composed_restrictions'] != restrictions or a.get('applied_restrictions') != [] or b.get('applied_restrictions') != restrictions:
        raise ValueError('Reproduction scope does not preserve declared intersection')
    surfaces = [o.get('execution_surface') for o in (a, b)]
    if (_surface_key(surfaces[0]) is None or _surface_key(surfaces[0]) != _surface_key(surfaces[1])
            or any(not isinstance(s, dict) or not s.get('identity') for s in surfaces)
            or surfaces[0]['identity'].casefold() != surfaces[1]['identity'].casefold()
            or marker['upper_layer'] != marker['lower_layer']):
        raise ValueError('Reproduction requires the same surface, identity and layer')
    for side, observation in zip(('upper', 'lower'), (a, b)):
        attestation = observation.get('surface_attestation') or {}
        recomputed = attest_surface(observation['execution_surface'], observation.get('surface_report'),
                                   attestation.get('required_fields', ()))
        if (recomputed != attestation or attestation.get('status') != 'MATCHED'
                or marker[side + '_surface_attestation'] != attestation
                or marker[side + '_execution_surface'] != observation['execution_surface']
                or observation.get('measure_id') != marker['measure_id']):
            raise ValueError('Reproduction requires matching original scope and surface attestation')
    values = [number(o['reproduction_quantity']) for o in (a, b)]
    if quantities is not None and any(r not in quantities or number(quantities[r]) != value for r, value in zip(refs[1:], values)):
        raise ValueError('Reproduction differs from sealed quantity receipts')
    if (marker['undeclared_context_value'] != values[0] or marker['reproduced_value'] != values[1]
            or marker['values_equal'] is not (values[0] == values[1])
            or marker['label'] != _label(marker['reported_figure'], values[1])
            or marker['unavailability'] != (NO_FIGURE if marker['reported_figure'] is None else None)
            or marker['limitations'] != [BASELINE_LIMIT, ACTIVE_LIMIT, TIMING_LIMIT, OPEN_LIMIT]):
        raise ValueError('Reproduction verdict or mandatory limitations differ')
    return marker
