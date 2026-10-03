"""Optional, within-layer reproduction of a declared scope, not a boundary test.

Adapters resolve native declarations into typed IN restrictions and execute the
composed neutral scope. The engine never parses native definitions or queries.
The vertical outcome remains separate from this finding, including its refusals.
"""
import copy
import json
from decimal import Decimal, InvalidOperation
from . import proposal_limits as limits
from . import reported_figure as figure

CAPABILITY = 'declared_context_reproduction'
KIND = 'DECLARED_CONTEXT_REPRODUCTION'
LABELS = ('REPRODUCED', 'NOT_REPRODUCED')
NO_FIGURE = 'No reported figure supplied.'
BASELINE_LIMIT = 'The undeclared-context value remains subject to row-level security and other native restrictions; it is not an unrestricted or true total.'
ACTIVE_LIMIT = 'Declared-context reproduction does not establish the active selection, security context or cross-filtering, or whether the number is business-correct.'
TIMING_LIMIT = 'The within-layer reads are not bound to a shared served data version; timing may explain a mismatch.'
OPEN_LIMIT = 'An undeclared selection, security context, cross-filtering or a deeper divergence may account for the reported figure; none was excluded.'


class UnsupportedRestriction(ValueError):
    """The whole declaration is incomplete, never a partially usable scope."""
    def __init__(self, form):
        self.form = form
        super().__init__(f'Unsupported declared restriction form {form}; faithful translation required.')


def _typed(value):
    if value is not None and type(value) not in (str, int, float, bool):
        raise UnsupportedRestriction('NON_SCALAR_IN_VALUE')
    if (type(value) is str and len(value)>limits.FILTER_STRING
            or type(value) is int and abs(value)>limits.EXACT_INTEGER):
        raise ValueError('Restriction value exceeds the consumer bound')
    return json.dumps(value, sort_keys=True, allow_nan=False, ensure_ascii=False)


def compose(restrictions):
    """Intersect every same-field declaration; retain an empty intersection."""
    if not isinstance(restrictions, list) or not 0 <= len(restrictions) <= 32:
        raise ValueError('Declared restrictions require a bounded list')
    fields = {}
    for restriction in restrictions:
        if isinstance(restriction, dict) and restriction.get('operator') != 'IN':
            operator = restriction.get('operator')
            # Name bounded neutral form labels, not arbitrary native definition text.
            form = operator if (isinstance(operator, str) and 1 <= len(operator) <= 64
                                and all(c.isascii() and (c.isalnum() or c == '_') for c in operator)) else 'UNKNOWN_OPERATOR'
            raise UnsupportedRestriction(form)
        if isinstance(restriction, dict) and set(restriction) != {'field_id', 'operator', 'values'}:
            raise UnsupportedRestriction('NON_ENUMERATED_RESTRICTION_SHAPE')
        if (not isinstance(restriction, dict) or set(restriction) != {'field_id', 'operator', 'values'}
                or not isinstance(restriction['field_id'], str) or not 1<=len(restriction['field_id'])<=limits.CONTEXT_ID
                or restriction['operator'] != 'IN' or not isinstance(restriction['values'], list)
                or len(restriction['values']) > limits.FILTER_VALUES):
            raise ValueError('Unsupported declared restriction; faithful translation required')
        values = {_typed(value): value for value in restriction['values']}
        # Opaque, fully resolved catalog column identity; never its display name.
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


def number(value, *, allow_blank=False):
    if isinstance(value, dict) and set(value) == {'quantity'}: value = value['quantity']
    if value is None and allow_blank:return None
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
    return figure.label(reported,reproduced)


def render(marker, business=False, include_limits=True):
    """Facts and qualifications are rendered by the engine, never model prose."""
    baseline = marker['undeclared_context_value']; declared = marker['reproduced_value']
    baseline = 'blank' if baseline is None else baseline
    declared = 'blank' if declared is None else declared
    first = f'Within-layer check: the same calculation service and account returned an undeclared-context value of {baseline}, and the declared selections produced {declared}.'
    if marker['label'] == 'REPRODUCED':
        qualified=' at its stated precision' if figure.qualification(marker['reported_figure']) else ''
        finding = f"The declared selections reproduce the reported figure of {figure.display(marker['reported_figure'])}{qualified}; they account for that figure without requiring a difference further back."
    elif marker['label'] == 'NOT_REPRODUCED':
        finding = f"The declared selections do not reproduce the reported figure of {figure.display(marker['reported_figure'])}."
    else:
        finding = 'No reported figure supplied; the produced value has no reproduction verdict.'
    limits = ('This does not establish the active selections, business correctness or an unrestricted total. '
              'Different update times, other selections or security restrictions, and a difference further back remain possible.')
    from .declaration_inventory import qualifications
    specific = qualifications(marker['declarations'], marker['label'])[4:] + figure.qualification(marker['reported_figure'])
    if marker.get('selection_resolution'):
        from .report_scope import render as render_resolution
        finding += ' ' + render_resolution(marker['selection_resolution'],business)
    if marker.get('cell'):
        first = 'Cell ' + marker['cell']['mode'] + ': ' + first
    if business:
        from urllib.parse import unquote
        mode=marker.get('cell',{}).get('mode')
        subject='The selected row' if mode=='KEYED' else 'The displayed total row' if mode=='TOTAL' else 'The visual'
        declared_word='nothing' if marker['reproduced_value'] is None else declared
        first=f'{subject} produced {declared_word}; the same calculation without applying report selections returned {baseline}.'
        restrictions=marker['composed_restrictions']
        if restrictions:
            terms=[]
            for restriction in restrictions:
                name=unquote(restriction['field_id'].rstrip('/').rsplit('/',1)[-1]).replace('_',' ')
                from .business_vocabulary import validate_identifier_form
                try:validate_identifier_form(name)
                except ValueError:name='saved selection'
                values=', '.join(str(v) for v in restriction['values']) or 'no permitted values'
                try:validate_identifier_form(values)
                except ValueError:values='the recorded values'
                terms.append(name+': '+values)
            first+=' The applied selections were '+ '; '.join(terms)+'.'
        else:first+=' No saved report filter restricts this calculation.'
        return first + ' ' + finding + (' ' + limits + (' ' + ' '.join(specific) if specific else '') if include_limits else '')
    return ((f"Cell {marker['cell']['target_id']} ({marker['cell']['mode']}): " if marker.get('cell') else '') + f"WITHIN_LAYER_CHECK ({marker['id']}): undeclared-context value {baseline}; declared-context value {declared}. "
            + finding + (' ' + limits + (' ' + ' '.join(specific) if specific else '') if include_limits else ''))


def _run_one(adapter, layer, measure_id, scope):
    """Callable independently, or before the vertical walk attempts a lower read.

    Not-declared/nonapplicable checks issue no value reads. Once applicable, both
    scopes use the same governed execution method; no baseline reuse or guessing.
    Exceptions from dispatch/budget admission propagate, never turn into findings.
    """
    from .process_debugging import attest, _observation, _surface_key
    if CAPABILITY not in adapter.capabilities():
        return {'status': 'UNDECLARED', 'observations': []}
    if 'reported_figure' not in scope:
        return {'status':'UNAVAILABLE','reason':'Reported figure state was not supplied.','observations':[]}
    reported = figure.validate(scope['reported_figure'])
    if reported['state']=='UNSPECIFIED' and 'report_binding' not in scope:
        return {'status':'UNAVAILABLE','reason':NO_FIGURE,'observations':[]}
    declaration = adapter.declared_context(layer, measure_id, copy.deepcopy(scope))
    from . import declaration_inventory as inventory
    # Status is the existing declaration/refusal discriminant. An upstream
    # refusal produced no eligible input; downstream validation must not mask it.
    if not isinstance(declaration, dict) or declaration.get('status') not in ('DECLARED', 'UNDECLARED', 'UNAVAILABLE'):
        return {'status': 'UNDECLARED', 'reason': 'Declaration response has no valid status',
                'unsupported_form': 'DECLARATION_RESPONSE_CONTRACT', 'observations': []}
    if declaration['status'] != 'DECLARED':
        if not isinstance(declaration.get('reason'), str) or not declaration['reason'].strip():
            return {'status': 'UNDECLARED', 'reason': 'Upstream declaration refusal has no reason',
                    'unsupported_form': 'DECLARATION_RESPONSE_CONTRACT', 'observations': []}
        return {'status': declaration['status'], 'reason': declaration['reason'],
                **({'unsupported_form': declaration['unsupported_form']} if 'unsupported_form' in declaration else {}),
                'observations': []}
    try:
        entries = _entries(declaration['evidence'], declaration.get('inventory'), declaration.get('restrictions'))
    except inventory.MissingInventory as exc:
        return {'status': 'UNDECLARED', 'reason': str(exc), 'unsupported_form': 'DECLARATION_INVENTORY_ABSENT', 'observations': []}
    except UnsupportedRestriction as exc:
        return {'status': 'UNDECLARED', 'reason': str(exc), 'unsupported_form': exc.form, 'observations': []}
    except ValueError as exc:
        return {'status': 'UNDECLARED', 'reason': str(exc), 'unsupported_form': 'DECLARATION_INVENTORY_CONTRACT', 'observations': []}
    unsupported = [e for e in entries if e['disposition'] == 'UNSUPPORTED']
    if unsupported:
        return {'status': 'UNDECLARED', 'reason': 'Unsupported declarations: ' + declaration.get('unsupported_form','UNSUPPORTED_DECLARATION') + ' [' + ', '.join(e['id'] for e in unsupported) + ']' ,
                'unsupported_form': 'UNSUPPORTED_DECLARATION', 'inventory': inventory.neutral(entries), 'observations': []}
    cell = declaration.get('cell')
    keys = cell['key_restrictions'] if cell is not None else []
    if not declaration['restrictions'] and cell is None:
        return {'status': 'UNDECLARED', 'reason': 'No active declaration restrictions.', 'observations': []}
    try:
        restrictions = compose(declaration['restrictions'] + keys)
    except UnsupportedRestriction as exc:
        return {'status': 'UNDECLARED', 'reason': str(exc), 'unsupported_form': exc.form,
                'observations': []}
    if cell is None and not applicable(restrictions, scope):
        return {'status': 'UNDECLARED', 'reason': 'No declared predicate bears on the resolved ticket scope.', 'observations': []}
    definition = _observation(declaration['evidence'], 'declared_context_definition')
    definition['declaration_inventory'] = copy.deepcopy(declaration['inventory'])
    if (not definition or definition.get('status') != 'COMPLETED'
            or definition.get('completeness') != 'COMPLETE_RESPONSE'
            or definition.get('declaration_provenance') != 'DECLARED_BY_DEFINITION'
            or definition.get('declared_restrictions') != declaration['restrictions']):
        raise ValueError('Declared scope requires retained definition evidence and provenance')
    observations = [definition]
    probes = {}; quantities = {}
    planned=(('DECLARED_CONTEXT', restrictions), ('UNDECLARED_CONTEXT', []))
    for ordinal,(purpose, applied) in enumerate(planned):
        remaining=getattr(adapter,'remaining_diagnostic_reads',None)
        cost=adapter.declared_probe_cost(measure_id,declaration,applied,purpose) if hasattr(adapter,'declared_probe_cost') else 1
        if remaining is not None and remaining()<cost:
            stopped={'target_id':cell['target_id'] if cell else layer['id'],'purpose':purpose,
                'would_establish':('the value under the full declared restrictions' if purpose=='DECLARED_CONTEXT' else 'the value without applying the report declarations'),
                'reason':'Diagnostic read cap reached.'}
            return {'status':'UNAVAILABLE','reason':'Diagnostic read cap reached.','observations':observations,
                'unevaluated_probes':[dict(stopped,purpose=p,
                    would_establish=('the value under the full declared restrictions' if p=='DECLARED_CONTEXT' else 'the value without applying the report declarations')) for p,_ in planned[ordinal:]]}
        probe = attest(adapter.evaluate_declared_context(layer, measure_id,
                        {'restrictions': copy.deepcopy(applied), 'dimension_ids': [],
                         **({'cell_id': cell['id'],'probe_purpose':purpose} if cell is not None else {})}))
        if probe.evidence:
            observed = _observation(probe.evidence, 'declared_context_read')
            observed['execution_surface'] = probe.execution_surface
            if cell is None: observed['reproduction_purpose'] = purpose
            if probe.query: observed['query'] = probe.query
            observations.append(observed)
        if probe.status != 'OBSERVED' or not probe.evidence:
            return {'status': 'UNAVAILABLE', 'reason': probe.reason or 'Reproduction quantity unavailable.',
                    'observations': observations}
        if (probe.layer != layer['id'] or probe.evidence.get('applied_restrictions') != applied
                or probe.evidence.get('measure_id') != measure_id
                or probe.evidence.get('completeness') != 'COMPLETE_RESPONSE'):
            raise ValueError('Executed reproduction scope/measure/completeness differs')
        observations[-1]['reproduction_quantity'] = number(probe.value,allow_blank=True)
        quantities[purpose]=observations[-1]['reproduction_quantity']
        probes[purpose]=probe
    a, b = probes['UNDECLARED_CONTEXT'], probes['DECLARED_CONTEXT']
    if (_surface_key(a.execution_surface) is None or _surface_key(a.execution_surface) != _surface_key(b.execution_surface)
            or a.execution_surface['identity'].casefold() != b.execution_surface['identity'].casefold()):
        return {'status': 'UNAVAILABLE', 'reason': 'Reproduction requires the same execution surface and identity.', 'observations': observations}
    if a.evidence['id'] == b.evidence['id'] and restrictions:
        raise ValueError('Distinct applied scopes require distinct original read receipts')
    marker = _observation({'id': 'declared-reproduction-' + (cell['id'] if cell is not None else b.evidence['id']), 'tool': 'process',
        'check_kind': KIND, 'comparison_status': 'WITHIN_LAYER_CHECK',
        'definition_evidence_id': definition['id'], 'measure_id': measure_id,
        'upper_layer': a.layer, 'lower_layer': b.layer,
        'upper_evidence_id': a.evidence['id'], 'lower_evidence_id': b.evidence['id'],
        'upper_execution_surface': a.execution_surface, 'lower_execution_surface': b.execution_surface,
        'upper_surface_attestation': a.evidence['surface_attestation'], 'lower_surface_attestation': b.evidence['surface_attestation'],
        'composed_restrictions': restrictions,
        **({'selection_resolution':copy.deepcopy(scope['selection_resolution']),
            'selection_resolution_evidence_id':scope['selection_resolution_evidence_id']} if 'selection_resolution' in scope else {}),
        **({'cell': copy.deepcopy(cell), 'redundant_cell_keys':
            [r['field_id'] for r in keys if compose(declaration['restrictions'] + [r]) == compose(declaration['restrictions'])]} if cell is not None else {}),
        'undeclared_context_value': quantities['UNDECLARED_CONTEXT'],
        'reproduced_value': quantities['DECLARED_CONTEXT'], 'reported_figure': reported,
        'label': _label(reported, quantities['DECLARED_CONTEXT']),
        'unavailability': NO_FIGURE if reported['state'] == 'UNSPECIFIED' else None,
        'values_equal': quantities['UNDECLARED_CONTEXT'] == quantities['DECLARED_CONTEXT'],
        'declarations': inventory.neutral(entries),
        'limitations': inventory.qualifications(inventory.neutral(entries), _label(reported, quantities['DECLARED_CONTEXT'])) + figure.qualification(reported)}, 'declared_context_reproduction')
    observations.append(marker)
    validate(marker, {o['id']: o for o in observations + scope.get('selection_observations',[])})
    return {'status': 'UNAVAILABLE' if reported['state'] == 'UNSPECIFIED' else 'COMPLETED',
            **({'reason': NO_FIGURE} if reported['state'] == 'UNSPECIFIED' else {}), 'finding': marker, 'observations': observations,
            'business_output': render(marker,business=True), 'technical_output': render(marker)}


def validate(marker, observations, quantities=None):
    """Validate originals (and sealed scalar quantities during synthesis)."""
    from .process_debugging import _surface_key, attest_surface
    if marker.get('check_kind') != KIND or marker.get('comparison_status') != 'WITHIN_LAYER_CHECK':
        raise ValueError('Reproduction is within-layer evidence only')
    if set(marker.get('process_roles', [])) != {'declared_context_reproduction'}:
        raise ValueError('Reproduction cannot satisfy boundary or presentation-context roles')
    refs = [marker.get(k) for k in ('definition_evidence_id', 'upper_evidence_id', 'lower_evidence_id')]
    if refs[0] in refs[1:] or any(r not in observations for r in refs):
        raise ValueError('Reproduction requires original definition and read receipts')
    if refs[1] == refs[2] and (not marker.get('cell') or marker['composed_restrictions']):
        raise ValueError('Distinct scopes require distinct original read receipts')
    definition, a, b = [observations[r] for r in refs]
    if (set(definition.get('process_roles', [])) != {'declared_context_definition'}
            or any(set(o.get('process_roles', [])) != {'declared_context_read'} for o in (a,b))):
        raise ValueError('Reproduction receipts cannot satisfy vertical outcome roles')
    if any(o.get('status') != 'COMPLETED' or o.get('completeness') != 'COMPLETE_RESPONSE' for o in (definition, a, b)):
        raise ValueError('Reproduction requires complete original receipts')
    if definition.get('declaration_provenance') != 'DECLARED_BY_DEFINITION':
        raise ValueError('Reproduction requires declared definition provenance')
    from . import declaration_inventory as inventory
    entries = _entries(definition, definition.get('declaration_inventory'), definition['declared_restrictions'])
    if any(e['disposition'] == 'UNSUPPORTED' for e in entries) or marker.get('declarations') != inventory.neutral(entries):
        raise ValueError('Reproduction inventory differs or contains unsupported declarations')
    if marker.get('selection_resolution'):
        from .report_resolution import validate as validate_resolution
        resolution=observations.get(marker.get('selection_resolution_evidence_id'))
        if not resolution or resolution['target']!=marker['selection_resolution']: raise ValueError('Selection resolution differs from its original evidence')
        validate_resolution(resolution,observations)
    cell = marker.get('cell')
    if cell is not None:
        from .report_cell import validate as validate_cell
        validate_cell(cell, marker['measure_id'])
        shape=definition.get('cell_definition')
        if (not isinstance(shape,dict) or shape!={k:cell[k] for k in ('target_id','measure_id','grouping_columns')}
                or b.get('cell_address')!=cell):
            raise ValueError('Cell identity differs from original definition/read receipts')
    keys = cell['key_restrictions'] if cell is not None else []
    restrictions = compose(definition['declared_restrictions'] + keys)
    if cell is not None and marker.get('redundant_cell_keys') != [r['field_id'] for r in keys
            if compose(definition['declared_restrictions'] + [r]) == compose(definition['declared_restrictions'])]:
        raise ValueError('Cell-key redundancy differs from the original declaration')
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
        if (recomputed != attestation or attestation.get('status') not in ('MATCHED','PARTIAL') or attestation.get('missing_required_fields')
                or marker[side + '_surface_attestation'] != attestation
                or marker[side + '_execution_surface'] != observation['execution_surface']
                or observation.get('measure_id') != marker['measure_id']):
            raise ValueError('Reproduction requires matching original scope and surface attestation')
    values = [number(o['reproduction_quantity'],allow_blank=True) for o in (a, b)]
    if quantities is not None and any(r not in quantities or number(quantities[r],allow_blank=True) != value for r, value in zip(refs[1:], values)):
        raise ValueError('Reproduction differs from sealed quantity receipts')
    if (marker['undeclared_context_value'] != values[0] or marker['reproduced_value'] != values[1]
            or marker['values_equal'] is not (values[0] == values[1])
            or marker['label'] != _label(marker['reported_figure'], values[1])
            or marker['unavailability'] != (NO_FIGURE if marker['reported_figure']['state'] == 'UNSPECIFIED' else None)
            or marker['limitations'] != inventory.qualifications(inventory.neutral(entries), marker['label']) + figure.qualification(marker['reported_figure'])):
        raise ValueError('Reproduction verdict or mandatory limitations differ')
    return marker


def run(adapter, layer, measure_id, scope):
    """Evaluate independent cells, retaining named refusals and cap-limited candidates."""
    if hasattr(adapter,'report_catalog') and 'report_binding' not in scope:
        return {'status':'UNDECLARED','unsupported_form':'REPORT_BINDING_ABSENT',
            'reason':'Report ambiguity: no stated report binding was supplied; model-wide declarations are not eligible.',
            'observations':[]}
    if not hasattr(adapter, 'declared_cells') or 'report_binding' not in scope:
        return _run_one(adapter, layer, measure_id, scope)
    if CAPABILITY not in adapter.capabilities(): return {'status': 'UNDECLARED', 'observations': []}
    if 'reported_figure' not in scope: return {'status': 'UNAVAILABLE', 'reason': 'Reported figure state was not supplied.', 'observations': []}
    figure.validate(scope['reported_figure'])
    batch = adapter.declared_cells(layer, measure_id, copy.deepcopy(scope))
    if batch['status'] != 'DECLARED': return {**batch, 'observations': []}
    from .report_cell import validate as validate_cell
    from .process_debugging import _observation
    observations = []; results = []; skipped = list(batch['refusals'])
    for declaration in batch['cells']:
        validate_cell(declaration['cell'], measure_id, scope)
        class Selected:
            def capabilities(self): return adapter.capabilities()
            def declared_context(self, *args): return copy.deepcopy(declaration)
            def evaluate_declared_context(self, *args): return adapter.evaluate_declared_context(*args)
            remaining_diagnostic_reads=staticmethod(adapter.remaining_diagnostic_reads) if getattr(adapter,'remaining_diagnostic_reads',None) is not None else None
            def declared_probe_cost(self,*args):return adapter.declared_probe_cost(*args) if hasattr(adapter,'declared_probe_cost') else 1
        checked = _run_one(Selected(), layer, measure_id, scope)
        for observation in checked['observations']:
            if observation['id'] not in {o['id'] for o in observations}: observations.append(observation)
        skipped.extend(checked.get('unevaluated_probes',[]))
        results.append({'cell': declaration['cell'], 'status': checked['status'],
                        **{k: checked[k] for k in ('reason', 'finding') if k in checked}})
        if checked.get('unsupported_form'):
            skipped.append({'target_id': declaration['cell']['target_id'], 'reason': checked['reason']})
    for event in getattr(adapter,'duplicate_read_events',[]):
        if event['id'] not in {o['id'] for o in observations}: observations.append(_observation(event,'established'))
    if skipped:
        observations.append(_observation({'id': 'declared-cells-unevaluated', 'tool': 'process',
            'check_kind': 'DECLARED_CONTEXT_REPRODUCTION_UNAVAILABLE', 'capability_status': 'UNAVAILABLE',
            'reason': 'Unevaluated cells: ' + '; '.join(str(x['target_id']) + ': ' + x['reason'] for x in skipped),
            'unevaluated_cells': skipped,'unevaluated_probes':[x for x in skipped if 'purpose' in x]}, 'established'))
    if len(batch['cells']) == 1 and len(results) == 1 and not batch['refusals'] and not checked.get('unevaluated_probes'):
        return {**checked,'observations':observations, 'cells': results, 'unevaluated_cells': []}
    findings = [r['finding'] for r in results if 'finding' in r]
    result = {'status': 'COMPLETED' if findings and scope['reported_figure']['state'] != 'UNSPECIFIED' else 'UNAVAILABLE',
              'observations': observations, 'cells': results, 'unevaluated_cells': skipped}
    if result['status'] == 'UNAVAILABLE': result['reason'] = NO_FIGURE if findings else ('; '.join(x['reason'] for x in skipped) or 'No addressable candidate visual.')
    if len(findings) == 1: result['finding'] = findings[0]
    if findings:
        result['business_output'] = ' '.join(render(f, business=True) for f in findings)
        result['technical_output'] = '\n'.join(render(f) for f in findings)
    stopped=[x for x in skipped if 'purpose' in x]
    if stopped:
        for output,business in (('business_output',True),('technical_output',False)):
            result[output]=result.get(output,'')+' '+render_stopped(stopped,business)
    return result


def _entries(definition, inventory, restrictions):
    from .report_scope import validate_inventory
    return validate_inventory(inventory,restrictions,binding=definition.get('report_binding'),reports=definition.get('report_catalog'))


def render_stopped(probes,business=False):
    return ' '.join(('Candidate '+str(index) if business else row['target_id'])+
        ': the '+('declared-context check' if row['purpose']=='DECLARED_CONTEXT' else 'check without report declarations')+
        ' did not run because the diagnostic read cap was reached; it would establish '+row['would_establish']+'.'
        for index,row in enumerate(probes,1))
