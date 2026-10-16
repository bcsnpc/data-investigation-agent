"""Typed bounded claim observations. Differences are observations, never causes."""
import copy
import json
import re
from decimal import Decimal, InvalidOperation, localcontext

from .onboarding import digest

KINDS = ('SET_RECONCILIATION', 'MULTIPLICITY', 'RECORD_VALUE', 'DECOMPOSITION')
LIMITS = [
    'SNAPSHOT_UNVERIFIED: the value queries do not bind aligned served versions; timing was not excluded.',
    'Observed differences do not establish a defect, business correctness, or its cause.',
]


def validate_request(request):
    if not isinstance(request, dict) or request.get('kind') not in KINDS:
        raise ValueError('CLAIM_PROJECTION_KIND_UNSUPPORTED')
    required = {'kind', 'keys'}
    required |= {'RECORD_VALUE': {'field_id'}, 'DECOMPOSITION': {'dimension_id', 'measure_id'}}.get(request['kind'], set())
    if set(request) != required:
        raise ValueError('CLAIM_PROJECTION_REQUEST_SHAPE')
    keys = request['keys']
    if (not isinstance(keys, list) or len(keys) > 6 or
            (not keys and request['kind'] not in ('DECOMPOSITION', 'MULTIPLICITY')) or
            any(not isinstance(k, str) or not re.fullmatch(r'-?(?:0|[1-9][0-9]*)', k) or
                k == '-0' or abs(int(k)) > 9007199254740991 for k in keys) or len(set(keys)) != len(keys)):
        raise ValueError('CLAIM_PROJECTION_REQUIRES_BOUNDED_EXACT_INTEGRAL_KEYS')
    for field in required - {'kind', 'keys'}:
        if not isinstance(request[field], str) or not request[field]:
            raise ValueError('CLAIM_PROJECTION_EXPLICIT_FIELD_REQUIRED')
    return request


def validate_address(value):
    if (not isinstance(value, dict) or set(value) != {'kind', 'layer', 'projection', 'mapping_hash', 'surface'} or
            value['kind'] != 'CLAIM_PROJECTION' or not isinstance(value['layer'], str) or not value['layer'] or
            not isinstance(value['mapping_hash'], str) or not re.fullmatch('[a-f0-9]{64}', value['mapping_hash'])):
        raise ValueError('CLAIM_PROJECTION_ADDRESS_INVALID')
    validate_request(value['projection'])
    surface = value['surface']
    if (not isinstance(surface, dict) or set(surface) != {'identity', 'engine', 'object', 'connection'} or
            any(not isinstance(v, str) or not v for v in surface.values())):
        raise ValueError('CLAIM_PROJECTION_EXPECTED_SURFACE_REQUIRED')
    return value


def cell(row, name):
    found = [row[k] for k in (name, '[' + name + ']') if k in row]
    if len(found) != 1 or not isinstance(found[0], dict) or set(found[0]) != {'type', 'value'}:
        raise ValueError('CLAIM_PROJECTION_MISSING_OR_AMBIGUOUS_CELL')
    value = found[0]
    if value['type'] == 'blank' and value['value'] is None:
        return copy.deepcopy(value)
    if value['type'] == 'string' and isinstance(value['value'], str):
        return copy.deepcopy(value)
    if value['type'] == 'boolean' and type(value['value']) is bool:
        return copy.deepcopy(value)
    if value['type'] != 'decimal' or not isinstance(value['value'], (str, int)) or isinstance(value['value'], bool):
        raise ValueError('CLAIM_PROJECTION_CELL_TYPE_INVALID')
    try:
        number = Decimal(str(value['value']))
        if not number.is_finite(): raise ValueError('CLAIM_PROJECTION_NONFINITE_VALUE')
    except InvalidOperation as exc:
        raise ValueError('CLAIM_PROJECTION_NUMBER_INVALID') from exc
    # No float conversion or implicit numeric coercion from string-valued cells.
    with localcontext() as context:
        context.prec = max(80, len(number.as_tuple().digits))
        return {'type': 'decimal', 'value': '0' if number == 0 else format(number.normalize(), 'f')}


def count(row, name):
    value = cell(row, name)
    if value['type'] != 'decimal': raise ValueError('CLAIM_PROJECTION_COUNT_UNAVAILABLE')
    number = Decimal(value['value'])
    if number < 0 or number != number.to_integral_value(): raise ValueError('CLAIM_PROJECTION_COUNT_INVALID')
    return int(number)


def facts(request, rows):
    validate_request(request)
    if not isinstance(rows, list): raise ValueError('CLAIM_PROJECTION_ROWS_REQUIRED')
    if request['kind'] == 'DECOMPOSITION':
        groups = []
        sentinels = 0
        for row in rows:
            marker = count(row, 'marker')
            if marker == 1:
                sentinels += 1
                if any(cell(row, name)['type'] != 'blank' for name in ('group_value', 'quantity', 'row_count')):
                    raise ValueError('CLAIM_PROJECTION_SENTINEL_INVALID')
                continue
            if marker != 0: raise ValueError('CLAIM_PROJECTION_SENTINEL_INVALID')
            group = cell(row, 'group_value')
            if group['type'] not in ('blank', 'decimal'):
                raise ValueError('CLAIM_PROJECTION_DIMENSION_TYPE_UNSUPPORTED')
            if group['type'] == 'decimal' and Decimal(group['value']) != Decimal(group['value']).to_integral_value():
                raise ValueError('CLAIM_PROJECTION_DIMENSION_TYPE_UNSUPPORTED')
            quantity = cell(row, 'quantity')
            if quantity['type'] not in ('blank', 'decimal'):
                raise ValueError('CLAIM_PROJECTION_QUANTITY_TYPE_INVALID')
            n = count(row, 'row_count')
            if n < 1: raise ValueError('CLAIM_PROJECTION_EMPTY_GROUP_INVALID')
            groups.append({'group': group, 'quantity': quantity, 'row_count': n})
        if sentinels > 1: raise ValueError('CLAIM_PROJECTION_REPEATED_SENTINEL')
        if len({digest(g['group']) for g in groups}) != len(groups):
            raise ValueError('CLAIM_PROJECTION_REPEATED_GROUP')
        return {'groups': sorted(groups, key=lambda g: digest(g['group']))}
    if len(rows) != 1: raise ValueError('CLAIM_PROJECTION_ONE_COUNT_ROW_REQUIRED')
    records = []
    for i, key in enumerate(request['keys']):
        n = count(rows[0], 'count_' + str(i))
        record = {'key': key, 'count': n, 'state': 'ABSENT' if n == 0 else 'PRESENT' if n == 1 else 'MULTIPLE'}
        if request['kind'] == 'RECORD_VALUE':
            raw = cell(rows[0], 'value_' + str(i))
            # An aggregate over duplicate keys is retained in the receipt but
            # is never selected as the record's value.
            record['value'] = raw if n == 1 else None
            record['value_state'] = 'OBSERVED' if n == 1 else 'NO_RECORD' if n == 0 else 'AMBIGUOUS_DUPLICATE_KEY'
        records.append(record)
    result = {'records': records}
    if request['kind'] == 'MULTIPLICITY':
        total, distinct, nulls = (count(rows[0], name) for name in ('all_rows', 'distinct_keys', 'null_keys'))
        if nulls > total or distinct > total - nulls:
            raise ValueError('CLAIM_PROJECTION_GLOBAL_COUNTS_INCONSISTENT')
        result['global_counts'] = {'row_count': total, 'distinct_nonnull_keys': distinct,
                                   'null_key_rows': nulls, 'duplicate_nonnull_rows': total - nulls - distinct}
    return result


def validate(observation, store=None, model_id=None):
    from .process_debugging import attest_surface
    address = validate_address(observation.get('read_address'))
    if observation.get('status') != 'COMPLETED' or observation.get('completeness') != 'COMPLETE_RESPONSE':
        raise ValueError('CLAIM_PROJECTION_INCOMPLETE_READ')
    attestation = attest_surface(address['surface'], observation.get('surface_report'), ('identity', 'engine', 'object'))
    if (attestation != observation.get('surface_attestation') or attestation.get('consistency') != 'MATCHED' or
            attestation.get('missing_required_fields') or observation.get('surface_report_binding') != 'VALUE_QUERY'):
        raise ValueError('CLAIM_PROJECTION_ATTESTATION_REQUIRED')
    actual = facts(address['projection'], observation.get('values'))
    if actual != observation.get('claim_projection'):
        raise ValueError('CLAIM_PROJECTION_FACTS_DIFFER')
    if store is not None:
        model = store.get(model_id)
        with store.connect() as db:
            row = db.execute('SELECT id,model_id,created,status,request,result FROM flexible_diagnostics WHERE id=? AND model_id=?',
                             (observation['id'], model_id)).fetchone()
            if row is None: raise ValueError('CLAIM_PROJECTION_RECEIPT_MISSING')
            from .receipt_integrity import verify
            seal = verify(db, observation['tool'], observation['id'], captured_row=list(row))
            if seal['state'] != 'SEALED': raise ValueError('CLAIM_PROJECTION_RECEIPT_UNSEALED')
        request, result = json.loads(row[4]), json.loads(row[5])
        plan = request['plan']
        if (not model['enabled'] or model['context_id'] != plan['context_id'] or model['revision'] != plan['revision'] or
                request.get('context_hash') != digest(model['context']) or request.get('tool') != observation['tool'] or
                plan.get('read_address') != address or row[3] != observation['status'] or
                digest({k: v for k, v in request.items() if k != 'plan'}) != observation['request_hash'] or
                any(result.get(k) != observation.get(v) for k, v in
                    [('rows', 'values'), ('completeness', 'completeness'), ('surface_report', 'surface_report'),
                     ('surface_report_binding', 'surface_report_binding')])):
            raise ValueError('CLAIM_PROJECTION_ORIGINAL_RECEIPT_DIFFERS')
    return actual


def key_transitions(ids, request, observed):
    """Locate independent changes for each explicitly requested key.

    Inputs have already been recomputed from sealed, attested receipts. A
    missing layer breaks preceding coverage permanently; it is never a zero
    count. Field-value coverage additionally requires one unique row at every
    preceding layer. Count/presence evidence remains useful when values are
    ambiguous, and a different key's ambiguity cannot invalidate this key.
    """
    if request['kind'] == 'DECOMPOSITION':
        return []
    records = {identity: {row['key']: row for row in item['facts']['records']}
               for identity, item in observed.items()}
    result = []
    for key in request['keys']:
        preceding_complete = True
        preceding_unique = True
        seen_presence = seen_count = seen_value = False
        for index, identity in enumerate(ids):
            current = records.get(identity, {}).get(key)
            if current is None:
                preceding_complete = preceding_unique = False
            elif current['count'] != 1:
                preceding_unique = False
            if index == 0:
                continue
            previous = ids[index - 1]
            prior = records.get(previous, {}).get(key)
            if prior is None or current is None:
                continue
            presence_changed = (prior['count'] > 0) != (current['count'] > 0)
            count_changed = prior['count'] != current['count']
            values_comparable = (request['kind'] == 'RECORD_VALUE' and
                                 prior['count'] == current['count'] == 1)
            value_changed = values_comparable and prior['value'] != current['value']
            first_presence = preceding_complete and presence_changed and not seen_presence
            first_count = preceding_complete and count_changed and not seen_count
            first_value = preceding_complete and preceding_unique and value_changed and not seen_value
            kind = ('APPEARED' if prior['count'] == 0 and current['count'] > 0 else
                    'DISAPPEARED' if prior['count'] > 0 and current['count'] == 0 else
                    'COUNT_CHANGED' if count_changed else
                    'VALUE_CHANGED' if value_changed else
                    'NOT_COMPARABLE' if request['kind'] == 'RECORD_VALUE' and
                        (prior['count'] > 1 or current['count'] > 1) else 'UNCHANGED')
            first = (first_presence if request['kind'] == 'SET_RECONCILIATION' else
                     first_count if request['kind'] == 'MULTIPLICITY' else
                     first_presence if presence_changed else first_value)
            entry = {'key': key, 'input': previous, 'output': identity, 'kind': kind,
                     'input_count': prior['count'], 'output_count': current['count'],
                     'preceding_layers_complete': preceding_complete,
                     'first_presence_change_established': first_presence,
                     'first_count_change_established': first_count,
                     'first_value_change_established': first_value,
                     'first_change_established': first,
                     'first_layer': identity if first else None,
                     'evidence_ids': [observed[previous]['evidence_id'], observed[identity]['evidence_id']]}
            if request['kind'] == 'RECORD_VALUE':
                entry.update(input_value_state=prior['value_state'], output_value_state=current['value_state'],
                             input_value=prior['value'], output_value=current['value'],
                             values_comparable=values_comparable)
            result.append(entry)
            seen_presence = seen_presence or presence_changed
            seen_count = seen_count or count_changed
            seen_value = seen_value or value_changed
    return result


def reduce(store, model_id, path, request, observations, unavailable, *, expected_requests=None):
    validate_request(request)
    layers = list(reversed(path['layers']))
    ids = [layer['id'] for layer in layers]
    if not ids:
        raise ValueError('CLAIM_PROJECTION_PATH_HAS_NO_LAYERS')
    if len(ids) != len(set(ids)): raise ValueError('CLAIM_PROJECTION_PATH_REPEATS_LAYER')
    observed = {}
    for observation in observations:
        address = validate_address(observation.get('read_address'))
        if address['projection'] != request or address['layer'] not in ids or address['layer'] in observed:
            raise ValueError('CLAIM_PROJECTION_SCOPE_OR_LAYER_DIFFERS')
        expected = (expected_requests or {}).get(address['layer'], {})
        if (expected.get('status') != 'COMPILED' or expected.get('request_hash') != observation.get('request_hash') or
                expected.get('read_address') != address):
            raise ValueError('CLAIM_PROJECTION_COMPILED_REQUEST_DIFFERS')
        actual = validate(observation, store, model_id)
        observed[address['layer']] = {'layer': address['layer'], 'evidence_id': observation['id'],
                                      'facts': actual, 'attestation': observation['surface_attestation']}
    unavailable_by_id = {entry['layer']: entry['reason'] for entry in unavailable}
    if len(unavailable_by_id) != len(unavailable):
        raise ValueError('CLAIM_PROJECTION_REPEATED_UNAVAILABLE_LAYER')
    if any(identity not in ids or identity in observed for identity in unavailable_by_id):
        raise ValueError('CLAIM_PROJECTION_AVAILABILITY_CONFLICT')
    missing = [{'layer': identity, 'reason': unavailable_by_id.get(identity, 'No completed attested read was obtained.')}
               for identity in ids if identity not in observed]
    comparison_gaps = [{'layer': identity, 'reason': 'Duplicate keys prevent choosing a unique record field value.'}
                       for identity in ids if identity in observed and request['kind'] == 'RECORD_VALUE' and
                       any(record['value_state'] == 'AMBIGUOUS_DUPLICATE_KEY' for record in observed[identity]['facts']['records'])]
    ambiguous = {gap['layer'] for gap in comparison_gaps}
    boundaries = []
    preceding_complete = True
    for index, identity in enumerate(ids):
        if identity not in observed or identity in ambiguous: preceding_complete = False
        if index == 0: continue
        previous = ids[index - 1]
        if previous not in observed or identity not in observed: continue
        left, right = observed[previous]['facts'], observed[identity]['facts']
        boundaries.append({'input': previous, 'output': identity, 'agrees': None if {previous, identity} & ambiguous else left == right,
                           'difference': {'input': left, 'output': right} if left != right else None,
                           'first_change_established': preceding_complete and previous not in ambiguous and left != right and
                               all(boundary['agrees'] for boundary in boundaries),
                           'evidence_ids': [observed[previous]['evidence_id'], observed[identity]['evidence_id']]})
    differing = any(b['agrees'] is False for b in boundaries)
    scope = ('DECLARED_UNFILTERED_ENTITY_KEY_COUNTS' if request['kind'] == 'MULTIPLICITY' else
             'EXPLICIT_EXAMPLE_KEYS_ONLY' if request['keys'] else 'DECLARED_UNFILTERED_ENTITY_GROUPS')
    limits = list(LIMITS)
    if request['kind'] == 'MULTIPLICITY':
        limits.append('Global counts cover the declared record key; NULL/BLANK key rows are counted separately and excluded from distinct nonnull keys. Business-key intent and whether duplicates are erroneous were not established.')
        limits.append('Equal global counts do not establish that the member keys or record values are equal.')
    elif request['keys']:
        limits.append('Only the named example keys were checked; unknown extra keys and whole-table multiplicity were not assessed.')
    if request['kind'] == 'DECOMPOSITION':
        limits.append('Grouped totals cover the declared integral dimension only; matching totals do not establish matching member records or explain a cause.')
    if comparison_gaps: limits.append('Duplicate keys prevent a unique field-value comparison; no aggregate value was substituted for one record.')
    if not boundaries:
        reason = 'No adjacent pair of layers has completed attested observations; boundary agreement was not established.'
        comparison_gaps.append({'layer': ids[0], 'reason': reason})
        limits.append(reason)
    for item in observed.values():
        unattested = item['attestation'].get('unattested_fields', [])
        if unattested:
            limits.append('Surface fields not self-reported for receipt ' + item['evidence_id'] + ': ' + ', '.join(unattested) + '.')
    if missing: limits.append('Missing layers were not read as absent records; a first-change claim requires every preceding layer to have been checked.')
    return {'status': 'NOT_COMPARABLE' if missing or comparison_gaps else 'OBSERVED_DIFFERENCE' if differing else 'OBSERVED_EQUAL',
            'kind': request['kind'], 'coverage': scope, 'layer_order': ids,
            'observations': [observed[i] for i in ids if i in observed], 'boundaries': boundaries,
            'key_transitions': key_transitions(ids, request, observed),
            'missing_layers': missing, 'comparison_gaps': comparison_gaps, 'snapshot_status': 'SNAPSHOT_UNVERIFIED', 'limits': limits,
            'cause_verified': False, 'defect_established': False}
