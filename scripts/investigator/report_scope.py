"""Consumer-owned report-scoped target contract, independent of native visual forms.

The previous unscoped target contract remains readable for historical evidence.
This contract admits no target or declaration from outside the stated report.
Adapter wiring and actual value-existence reads are separate implementation work.
"""
import copy
from collections import Counter
from jsonschema import Draft202012Validator
from . import declaration_inventory, reported_figure, definition_target
from .intake_confirmation import SCHEMA as CONFIRMATION_SCHEMA
from .onboarding import fields, text, digest

LEGACY_VERSION = 'report-scoped-target-v1'
VERSION = 'report-scoped-target-v2-confirmation'
ID = copy.deepcopy(definition_target.ID)
DISPOSITIONS = declaration_inventory.SCHEMA
EFFECTS = ('RESTRICTED', 'FULL_DOMAIN', 'EXCLUDED')
KINDS = ('EVIDENCE', 'OBSERVED', 'STATED', 'REFUSED')


def variant(discriminant, value, properties):
    properties = {discriminant: {'type': 'string', 'enum': [value]}, **properties}
    return {'type': 'object', 'additionalProperties': False, 'properties': properties, 'required': list(properties)}


STATED_REPORT_SCHEMA = variant('resolution_kind', 'STATED', {'report_id': ID, 'source': reported_figure.SPAN_SCHEMA})
CONFIRMED_REPORT_SCHEMA = variant('resolution_kind','USER_CONFIRMED',{
    'report_id':ID,'source':{'type':'null'},'confirmation':CONFIRMATION_SCHEMA})
from .input_reference import SCHEMA as REFERENCE_SCHEMA
REFERENCE_REPORT_SCHEMA=variant('resolution_kind','DECLARED_REFERENCE',{
    'report_id':ID,'source':{'type':'null'},'reference':REFERENCE_SCHEMA})
from .form_scope import REPORT as FORM_REPORT_SCHEMA
BINDING_SCHEMA={'anyOf':[STATED_REPORT_SCHEMA,CONFIRMED_REPORT_SCHEMA,REFERENCE_REPORT_SCHEMA,FORM_REPORT_SCHEMA]}
REPORT_SCHEMA = {'anyOf': [STATED_REPORT_SCHEMA,
    variant('resolution_kind', 'REFUSED', {
        'source': {'type': 'null'},
        'candidates': {'type': 'array', 'maxItems': 512, 'uniqueItems': True, 'items': ID},
        'reason': {'type': 'string', 'enum': ['UNNAMED']}}),
    variant('resolution_kind', 'REFUSED', {
        'source': reported_figure.SPAN_SCHEMA,
        'candidates': {'type': 'array', 'maxItems': 0, 'items': ID},
        'reason': {'type': 'string', 'enum': ['NO_EXACT_MATCH']}}),
    variant('resolution_kind', 'REFUSED', {
        'source': reported_figure.SPAN_SCHEMA,
        'candidates': {'type': 'array', 'minItems': 2, 'maxItems': 512, 'uniqueItems': True, 'items': ID},
            'reason': {'type': 'string', 'enum': ['MULTIPLE_EXACT_MATCHES']}}),CONFIRMED_REPORT_SCHEMA,REFERENCE_REPORT_SCHEMA,FORM_REPORT_SCHEMA]}
REFUSED_REPORT_SCHEMAS=[v for v in REPORT_SCHEMA['anyOf']
                        if v['properties']['resolution_kind']['enum']==['REFUSED']]
LOOKUP_SCHEMA = {'anyOf': [variant('status', state, {'receipt_ids': {
    'type': 'array', 'minItems': 0 if state == 'UNAVAILABLE' else 1,
    'maxItems': 0 if state == 'UNAVAILABLE' else 1, 'items': ID}})
    for state in ('MATCH', 'MISMATCH', 'UNAVAILABLE')]}

# A request is not a resolution. It can be carried through review without any
# estate read or guessed column. Reads occur inside the governed procedure.
REQUEST_SCHEMA = variant('state', 'REQUESTED', {
    'report_binding': BINDING_SCHEMA, 'value_source': reported_figure.SPAN_SCHEMA,
    'column_source': {'anyOf': [{'type': 'null'}, reported_figure.SPAN_SCHEMA]}})
from .selection_descriptor import SCHEMA as DESCRIPTOR_SCHEMA
# Historical requests have no descriptor field. New intake's wire requires it;
# it is part of this contract, never passed alongside the envelope.
REQUEST_SCHEMA['properties']['descriptor']=DESCRIPTOR_SCHEMA

SCHEMA = {'anyOf': [
    variant('resolution_kind', 'EVIDENCE', {'report_binding': BINDING_SCHEMA, 'column_id': ID,
        'inventory_entry_id': ID, 'source': reported_figure.SPAN_SCHEMA}),
    variant('resolution_kind', 'OBSERVED', {'report_binding': BINDING_SCHEMA, 'column_id': ID,
        'receipt_id': ID, 'source': reported_figure.SPAN_SCHEMA}),
    variant('resolution_kind', 'STATED', {'report_binding': BINDING_SCHEMA, 'column_id': ID,
        'source': reported_figure.SPAN_SCHEMA, 'value_source': reported_figure.SPAN_SCHEMA,
        'lookup': LOOKUP_SCHEMA}),
    variant('resolution_kind', 'REFUSED', {'report_binding': BINDING_SCHEMA,
        'source': reported_figure.SPAN_SCHEMA,
        'candidates': {'type': 'array', 'maxItems': 512, 'uniqueItems': True, 'items': ID},
        'reason': {'type': 'string', 'enum': ['DECLARATION_AMBIGUITY', 'VALUE_ABSENT',
            'VALUE_AMBIGUITY', 'OBSERVATION_INCOMPLETE']}}),
    variant('resolution_kind', 'REFUSED', {'report_binding': {'anyOf': REFUSED_REPORT_SCHEMAS},
        'source': reported_figure.SPAN_SCHEMA,
        'candidates': {'type': 'array', 'maxItems': 512, 'uniqueItems': True, 'items': ID},
        'reason': {'type': 'string', 'enum': ['REPORT_UNRESOLVED']}})]}


def resolve_report(source, reports, ticket=None):
    if not isinstance(reports, list) or len(reports) > 512: raise ValueError('Report catalog exceeds bound')
    for report in reports:
        fields(report, ['id', 'name']); text(report['id'], 4000); text(report['name'], 4000)
    if len({r['id'] for r in reports}) != len(reports): raise ValueError('Duplicate report identity')
    quote = reported_figure.span(source, ticket) if source is not None else None
    matches=[]
    if quote is not None:
        from .intake_name_resolution import resolve as resolve_name
        try:matches=[resolve_name(quote,reports,'id')]
        except ValueError as exc:
            if str(exc).startswith('Ambiguous declared name:'):
                identities={c['id'] for c in exc.candidates}
                matches=[r for r in reports if r['id'] in identities]
    if len(matches) == 1:
        return {'resolution_kind': 'STATED', 'report_id': matches[0]['id'], 'source': copy.deepcopy(source)}
    return {'resolution_kind': 'REFUSED', 'source': copy.deepcopy(source),
            'candidates': sorted(r['id'] for r in (reports if source is None else matches)),
            'reason': 'UNNAMED' if source is None else 'NO_EXACT_MATCH' if not matches else 'MULTIPLE_EXACT_MATCHES'}


def report_binding(binding, *, reports, ticket=None, allow_refused=False):
    if isinstance(binding,dict) and binding.get('resolution_kind')=='USER_SUPPLIED_FORM':
        Draft202012Validator(FORM_REPORT_SCHEMA).validate(binding)
        proof=binding['form']
        if binding['report_id']!=proof['report_id'] or sum(r['id']==binding['report_id'] for r in reports)!=1:
            raise ValueError('Form report differs from its retained selection')
        if ticket is not None and digest(ticket)!=proof['document_hash']:
            raise ValueError('Form report belongs to a different input document')
        return binding
    if isinstance(binding,dict) and binding.get('resolution_kind')=='DECLARED_REFERENCE':
        from .input_reference import validate
        Draft202012Validator(REFERENCE_REPORT_SCHEMA).validate(binding)
        validate(binding['reference'],reports=reports,ticket=ticket)
        if binding['report_id']!=binding['reference']['report_id']:
            raise ValueError('Declared reference report differs from its binding')
        return binding
    if isinstance(binding,dict) and binding.get('resolution_kind')=='USER_CONFIRMED':
        # Admission checks this against the server-retained ticket proof. Later
        # consumers receive the sealed scope, not a new model declaration.
        Draft202012Validator(CONFIRMED_REPORT_SCHEMA).validate(binding)
        proof_fields=binding['confirmation']['fields']
        selected=proof_fields.get('REPORT_PAGE',proof_fields.get('NUMBER',{})).get('value',{})
        if selected.get('report_id')!=binding['report_id']:
            raise ValueError('Confirmed report differs from the retained selection')
        if sum(r['id']==binding['report_id'] for r in reports)!=1:
            raise ValueError('Confirmed report is absent or ambiguous in the retained catalog')
        if ticket is not None and binding['confirmation']['request_hash']!=digest(ticket):
            raise ValueError('Confirmed report belongs to a different ticket')
        return binding
    if not isinstance(binding, dict) or binding.get('resolution_kind') not in ('STATED', 'REFUSED'):
        raise ValueError('Target requires a report binding')
    spec = next((v for v in REPORT_SCHEMA['anyOf'] if v['properties']['resolution_kind']['enum'] == [binding['resolution_kind']]
                 and (binding['resolution_kind'] != 'REFUSED' or binding.get('reason') in v['properties']['reason']['enum'])), None)
    if spec is None: raise ValueError('Unknown report refusal reason')
    fields(binding, spec['required'])
    if binding != resolve_report(binding['source'], reports, ticket):
        raise ValueError('Report binding differs from scored retained report-name resolution')
    if binding['resolution_kind'] != 'STATED' and not allow_refused:
        raise ValueError(('Report ambiguity: ' if binding['reason']=='MULTIPLE_EXACT_MATCHES' else 'Report unavailable: ') + binding['reason'] + ': ' + ', '.join(binding['candidates']))
    return binding


def inventory_identity(source):
    fields(source, ['report_id', 'location', 'content_hash'])
    text(source['report_id'], 4000)
    declaration_inventory.identity({k: source[k] for k in ('location', 'content_hash')})
    return digest(source)


def validate_inventory(inventory, active, *, binding, reports, ticket=None):
    if inventory is None: raise declaration_inventory.MissingInventory('Required declaration inventory was not supplied')
    report_binding(binding, reports=reports, ticket=ticket)
    if not isinstance(inventory,dict) or set(inventory)!={'report_id','discovered','entries'}: raise ValueError('Declaration inventory is malformed')
    fields(inventory, ['report_id', 'discovered', 'entries'])
    if inventory['report_id'] != binding['report_id']:
        raise ValueError('Report inventory conservation failed: report differs from target')
    if not isinstance(active,list): raise ValueError('Active restriction set requires a list')
    discovered, entries = inventory['discovered'], inventory['entries']
    if (not isinstance(discovered, list) or len(discovered) > 512 or not isinstance(entries, list)
            or len(entries) != len(discovered) or not isinstance(active, list)):
        raise ValueError('Report inventory conservation failed: declaration count differs')
    ids = []
    for source in discovered:
        ids.append(inventory_identity(source))
        if source['report_id'] != binding['report_id']:
            raise ValueError('Report inventory conservation failed: foreign declaration')
    if len(ids) != len(set(ids)): raise ValueError('Duplicate scoped declaration identity')
    represented, accounted = [], []
    for entry in entries:
        if not isinstance(entry,dict) or set(entry)!={'id','source','disposition','volatility','assumption','opaque_provenance','restrictions','effect'}:
            raise ValueError('Declaration entry requires exactly one disposition and all contract fields')
        fields(entry, ['id', 'source', 'disposition', 'volatility', 'assumption', 'opaque_provenance', 'restrictions', 'effect'])
        if entry['id'] != inventory_identity(entry['source']) or entry['source']['report_id'] != binding['report_id']:
            raise ValueError('Report inventory conservation failed: identity differs or foreign entry')
        accounted.append(entry['id'])
        for name, spec in DISPOSITIONS.items():
            if entry[name] not in spec['enum']: raise ValueError('Invalid declaration ' + name)
        if entry['effect'] not in EFFECTS: raise ValueError('Invalid declaration effect')
        if not isinstance(entry['restrictions'], list): raise ValueError('Declaration restrictions require a list')
        if not isinstance(entry['opaque_provenance'], str) or len(entry['opaque_provenance']) > 4000:
            raise ValueError('Opaque declaration provenance exceeds bound')
        if entry['disposition'] == 'ACTIVE':
            if entry['volatility'] == 'UNKNOWN' or entry['assumption'] not in ('NONE', 'SAVED_DEFAULT'):
                raise ValueError('Active applicability must be established')
            if entry['assumption'] == 'SAVED_DEFAULT' and entry['volatility'] != 'VIEWER_CHANGEABLE':
                raise ValueError('Saved default requires viewer-changeable volatility')
            if entry['effect'] == 'FULL_DOMAIN':
                if entry['restrictions']: raise ValueError('Full-domain declaration cannot restrict values')
            elif entry['effect'] == 'RESTRICTED':
                if not entry['restrictions']: raise ValueError('Restricted declaration requires a nonempty restriction list')
                from .declared_reproduction import compose
                compose(entry['restrictions'])
            else: raise ValueError('Active declaration cannot be excluded')
            represented.extend(entry['restrictions'])
        elif entry['effect'] != 'EXCLUDED' or entry['restrictions']:
            raise ValueError('Excluded declaration cannot carry an active restriction')
    if Counter(accounted) != Counter(ids): raise ValueError('Report inventory conservation failed: missing dispositions')
    canonical = lambda value: digest(value)
    if Counter(map(canonical, active)) != Counter(map(canonical, represented)):
        raise ValueError('Report inventory ACTIVE coverage failed')
    if active:
        from .declared_reproduction import compose
        compose(active)
    return sorted(copy.deepcopy(entries), key=lambda entry: entry['id'])


def _observation(receipt_id, observations, column_id, quote):
    from .process_debugging import attest_surface, _surface_key
    receipt = observations.get(receipt_id) if isinstance(observations, dict) else None
    if (not isinstance(receipt, dict) or receipt.get('id') != receipt_id or receipt.get('status') != 'COMPLETED'
            or receipt.get('completeness') != 'COMPLETE_RESPONSE' or receipt.get('column_id') != column_id
            or definition_target.literal_text(receipt.get('searched_value')) != quote
            or type(receipt.get('value_exists')) is not bool
            or receipt.get('check_kind') != 'COLUMN_VALUE_EXISTENCE'):
        raise ValueError('Observed target requires an original completed value-existence receipt')
    attestation = receipt.get('surface_attestation')
    if (not isinstance(attestation, dict) or _surface_key(receipt.get('execution_surface')) is None
            or receipt.get('surface_report_binding') != 'VALUE_QUERY'
            or receipt.get('surface_report_receipt_id') != receipt_id
            or attestation != attest_surface(receipt['execution_surface'], receipt.get('surface_report'), attestation.get('required_fields', ()))
            or attestation.get('status') not in ('MATCHED', 'PARTIAL') or attestation.get('missing_required_fields')
            or 'identity' not in attestation.get('attested_fields', [])):
        raise ValueError('Observed target requires query-bound reader attestation')
    return receipt


def validate_target(target, *, reports, ticket=None, inventory=None, active=None,
                    observations=None, grouping_columns=None, columns=None):
    if not isinstance(target, dict) or target.get('resolution_kind') not in KINDS:
        raise ValueError('Scoped target requires a resolution kind and report binding')
    spec = next((v for v in SCHEMA['anyOf'] if v['properties']['resolution_kind']['enum'] == [target['resolution_kind']]
                 and (target['resolution_kind'] != 'REFUSED' or target.get('reason') in v['properties']['reason']['enum'])), None)
    if spec is None: raise ValueError('Unknown target refusal reason')
    fields(target, spec['required'])
    report_binding(target['report_binding'], reports=reports, ticket=ticket,
                   allow_refused=target['resolution_kind'] == 'REFUSED' and target['reason'] == 'REPORT_UNRESOLVED')
    if target['resolution_kind'] == 'REFUSED' and target['reason'] == 'REPORT_UNRESOLVED' and target['report_binding']['resolution_kind'] != 'REFUSED':
        raise ValueError('Report-unresolved refusal requires an unresolved report binding')
    quote = reported_figure.span(target['source'], ticket)
    if target['resolution_kind'] == 'REFUSED':
        if target['reason'] not in spec['properties']['reason']['enum']: raise ValueError('Unknown target refusal')
        if not isinstance(target['candidates'], list) or target['candidates'] != sorted(set(target['candidates'])) or len(target['candidates']) > 512:
            raise ValueError('Refusal candidates must be canonical')
        for candidate in target['candidates']: text(candidate, 4000)
        return target
    text(target['column_id'], 4000)
    if target['resolution_kind'] == 'EVIDENCE':
        entries = validate_inventory(inventory, active, binding=target['report_binding'], reports=reports, ticket=ticket)
        matching = [(entry['id'], r['field_id']) for entry in entries if entry['disposition'] == 'ACTIVE'
                    for r in entry['restrictions'] if any(definition_target.literal_text(v) == quote for v in r['values'])]
        if set(matching) != {(target['inventory_entry_id'], target['column_id'])}:
            raise ValueError('Evidence target requires exactly one matching ACTIVE entry in the stated report')
    elif target['resolution_kind'] == 'OBSERVED':
        entries = validate_inventory(inventory, active, binding=target['report_binding'], reports=reports, ticket=ticket)
        if any(entry['disposition'] == 'UNSUPPORTED' for entry in entries):
            raise ValueError('Observed no-declaration resolution requires complete supported declaration coverage')
        if any(definition_target.literal_text(v) == quote for e in entries if e['disposition'] == 'ACTIVE' for r in e['restrictions'] for v in r['values']):
            raise ValueError('Observed lookup cannot replace existing declaration evidence')
        if not isinstance(grouping_columns, list) or not grouping_columns or grouping_columns != sorted(set(grouping_columns)):
            raise ValueError('Observed resolution requires all scoped grouping columns')
        receipts = [o for o in (observations or {}).values() if o.get('check_kind') == 'COLUMN_VALUE_EXISTENCE'
                    and o.get('report_id') == target['report_binding']['report_id']
                    and definition_target.literal_text(o.get('searched_value')) == quote]
        by_column = {}
        for receipt in receipts:
            _observation(receipt['id'], observations, receipt.get('column_id'), quote)
            if receipt['column_id'] in by_column: raise ValueError('Duplicate existence observation for a grouping column')
            by_column[receipt['column_id']] = receipt
        if set(by_column) != set(grouping_columns): raise ValueError('Value-existence coverage is incomplete')
        found = [o for o in by_column.values() if o['value_exists']]
        if len(found) != 1 or found[0]['id'] != target['receipt_id'] or found[0]['column_id'] != target['column_id']:
            raise ValueError('Observed target requires exactly one matching column and its receipt')
    else:
        column = next((c for c in columns or [] if c['id'] == target['column_id']), None)
        if column is None or column['name'] != quote or sum(c['name'] == quote for c in columns) != 1:
            raise ValueError('Stated column must match exactly one catalog column')
        value_quote = reported_figure.span(target['value_source'], ticket)
        fields(target['lookup'], ['status', 'receipt_ids'])
        status, ids = target['lookup']['status'], target['lookup']['receipt_ids']
        if status not in ('MATCH', 'MISMATCH', 'UNAVAILABLE') or not isinstance(ids, list) or ids != sorted(set(ids)):
            raise ValueError('Stated lookup audit differs')
        if status == 'UNAVAILABLE':
            if ids: raise ValueError('Unavailable lookup cannot claim observed receipts')
        else:
            if len(ids) != 1: raise ValueError('Stated lookup requires one original receipt')
            receipt = _observation(ids[0], observations, target['column_id'], value_quote)
            if receipt.get('report_id') != target['report_binding']['report_id'] or receipt['value_exists'] != (status == 'MATCH'):
                raise ValueError('Stated lookup mismatch was not preserved')
    return target


def render(target, business=False):
    kind = target['resolution_kind']
    if kind == 'OBSERVED':
        return (target['source']['quote'] + ' was found as a value used to address the displayed row; no declared report filter restricts the figure to it.' if business else
                target['source']['quote'] + ' is a value of ' + target['column_id'] + '; no declared filter restricts this report to it. Resolution OBSERVED, receipt ' + target['receipt_id'] + '.')
    if kind == 'EVIDENCE': return 'The stated report declares a restriction carrying ' + target['source']['quote'] + '; resolution EVIDENCE.'
    if kind == 'STATED': return 'The column was explicitly stated; resolution STATED. Value lookup: ' + target['lookup']['status'] + '.'
    return 'Target resolution REFUSED: ' + target['reason'] + '.'


def validate_request(request, *, reports, ticket=None):
    fields(request, REQUEST_SCHEMA['required']+(['descriptor'] if 'descriptor' in request else []))
    if request['state'] != 'REQUESTED': raise ValueError('Selection request is not a resolution')
    report_binding(request['report_binding'], reports=reports, ticket=ticket)
    if 'descriptor' in request:
        from .selection_descriptor import validate
        validate(request['descriptor'],request['value_source'],ticket=ticket)
    reported_figure.span(request['value_source'], ticket)
    if request['column_source'] is not None: reported_figure.span(request['column_source'], ticket)
    return request
