"""Retained PBIR declarations and catalog-bound native quantity compilation.

No report fetch, active-selection inference, or cross-surface translation.
"""
import copy
import json
import math
import re
from uuid import uuid4
from ..model_context import assets
from ..onboarding import Conflict, digest
from .. import declared_reproduction, query_dax, proposal_limits as limits


class Refusal(ValueError):
    def __init__(self, form):
        self.form = form
        super().__init__('Declared-context reproduction unavailable: ' + form + '.')


def pinned(adapter):
    model = adapter.model
    current = adapter.store.get(model['id'])
    if (not current['enabled'] or current['revision'] != model['revision']
            or current['context_id'] != model['context_id']
            or digest(current['context']) != digest(model['context'])
            or model['context'].get('id') != model['context_id']):
        raise Conflict('Declared reproduction pinned context or model revision changed')
    return model


def member(model, field, kind, aliases=None):
    if not isinstance(field, dict) or set(field) != {kind}:
        form = next(iter(field)) if isinstance(field, dict) and len(field) == 1 else 'COMPOUND'
        raise Refusal('FIELD_EXPRESSION_' + str(form))
    value = field[kind]
    if not isinstance(value, dict) or set(value) != {'Expression', 'Property'}: raise Refusal('FIELD_EXPRESSION')
    expression = value['Expression']
    if not isinstance(expression, dict) or set(expression) != {'SourceRef'}: raise Refusal('FIELD_EXPRESSION')
    source = expression['SourceRef']
    if not isinstance(source, dict): raise Refusal('SOURCE_REFERENCE')
    if set(source) == {'Entity'}: table = source['Entity']
    elif set(source) == {'Source'} and aliases is not None: table = aliases.get(source['Source'])
    else: raise Refusal('SOURCE_REFERENCE')
    if not isinstance(table, str) or not isinstance(value['Property'], str): raise Refusal('SOURCE_REFERENCE')
    catalog = assets(model['context'])
    tables = [a for a in catalog if a['kind'] == 'SemanticTable' and a['name'].casefold() == table.casefold()]
    if len(tables) != 1: raise Refusal('AMBIGUOUS_OR_MISSING_TABLE')
    candidates = [a for a in catalog if a['kind'] == ('SemanticColumn' if kind == 'Column' else 'Measure')
                  and a.get('parent_id') == tables[0]['id'] and a['name'].casefold() == value['Property'].casefold()]
    if len(candidates) != 1: raise Refusal('AMBIGUOUS_OR_MISSING_MEMBER')
    return candidates[0]


def literal(text, column):
    if not isinstance(text, str): raise Refusal('NON_LITERAL_VALUE')
    typ = column.get('metadata', {}).get('dataType')
    if typ == 'string' and re.fullmatch(r"'(?:''|[^'])*'", text):
        value = text[1:-1].replace("''", "'")
    elif typ == 'boolean' and text in ('true', 'false'): value = text == 'true'
    elif typ == 'int64' and re.fullmatch(r'-?\d+(?:L)?', text):
        digits = text.removesuffix('L').lstrip('-')
        if len(digits) > len(str(limits.EXACT_INTEGER)): raise Refusal('LITERAL_REPRESENTATION_BOUND')
        value = int(text.removesuffix('L'))
    elif typ in ('double', 'decimal') and re.fullmatch(r'-?\d+(?:\.\d+)?(?:[dD])?', text):
        # Decimal literals cannot be rounded on the way through neutral JSON.
        value = float(text.rstrip('dD'))
        from decimal import Decimal
        if not math.isfinite(value) or Decimal(str(value)) != Decimal(text.rstrip('dD')):
            raise Refusal('LOSSY_NUMERIC_LITERAL')
    else: raise Refusal('LITERAL_TYPE_' + str(typ))
    try: declared_reproduction.compose([{'field_id': column['id'], 'operator': 'IN', 'values': [value]}])
    except ValueError: raise Refusal('LITERAL_REPRESENTATION_BOUND')
    return value


def restrictions(model, document):
    if not isinstance(document, dict) or set(document) - {'Version', 'From', 'Where'}:
        raise Refusal('SEMANTIC_FILTER_SHAPE')
    if document.get('Version') != 2: raise Refusal('SEMANTIC_FILTER_VERSION')
    aliases = {}
    for source in document.get('From', []):
        if (not isinstance(source, dict) or set(source) != {'Name', 'Entity', 'Type'}
                or source['Type'] != 0 or source['Name'] in aliases): raise Refusal('SOURCE_REFERENCE')
        aliases[source['Name']] = source['Entity']
    where = document.get('Where')
    if not isinstance(where, list) or not where: raise Refusal('MISSING_CONDITION')
    result = []
    for entry in where:
        if not isinstance(entry, dict) or set(entry) != {'Condition'}: raise Refusal('CONDITION_SHAPE')
        condition = entry['Condition']
        if not isinstance(condition, dict) or set(condition) != {'In'}:
            form = next(iter(condition), 'EMPTY_CONDITION') if isinstance(condition, dict) and len(condition) == 1 else 'COMPOUND_CONDITION'
            raise Refusal('CONDITION_' + str(form))
        body = condition['In']
        if not isinstance(body, dict) or set(body) != {'Expressions', 'Values'}: raise Refusal('IN_SHAPE')
        expressions, values = body['Expressions'], body['Values']
        if not isinstance(expressions, list) or len(expressions) != 1: raise Refusal('TUPLE_IN')
        column = member(model, expressions[0], 'Column', aliases)
        if not isinstance(values, list) or len(values) > limits.FILTER_VALUES: raise Refusal('IN_VALUE_BOUND')
        decoded = []
        for row in values:
            if (not isinstance(row, list) or len(row) != 1 or not isinstance(row[0], dict)
                    or set(row[0]) != {'Literal'} or not isinstance(row[0]['Literal'], dict)
                    or set(row[0]['Literal']) != {'Value'}): raise Refusal('NON_LITERAL_IN')
            decoded.append(literal(row[0]['Literal']['Value'], column))
        result.append({'field_id': column['id'], 'operator': 'IN', 'values': decoded})
    return result


def _native_filters(value):
    """Stored alternatives stay evidence, even when their form is unsupported."""
    if isinstance(value, dict):
        if 'Where' in value: yield value
        else:
            for child in value.values(): yield from _native_filters(child)
    elif isinstance(value, list):
        for child in value: yield from _native_filters(child)


def _sync_declared(value):
    if isinstance(value, dict):
        return any('sync' in str(key).casefold() or _sync_declared(child) for key, child in value.items())
    return isinstance(value, list) and any(_sync_declared(child) for child in value)


def _inverted_selection(value):
    if isinstance(value, dict):
        return any(key == 'isInvertedSelectionMode' or _inverted_selection(child) for key, child in value.items())
    return isinstance(value, list) and any(_inverted_selection(child) for child in value)


def extract(model, measure_id, scope):
    try: return _extract(model, measure_id, scope)
    except (Refusal, declared_reproduction.UnsupportedRestriction): raise
    except (KeyError, TypeError, AttributeError): raise Refusal('MALFORMED_NATIVE_DECLARATION')


def _extract(model, measure_id, scope):
    """Select a unique declared scalar visual; never combine reports or pages."""
    candidates = []
    exclusions = []
    target = scope.get('definition_target_id')
    for report in model['context'].get('reports', []):
        if target is not None and not any(p['id'] == target for p in report.get('report_definitions', [])):
            continue
        if report.get('binding_status') != 'RESOLVED_EXPLICIT_ID' or report.get('gaps'):
            if target is None or any(p['id'] == target for p in report.get('report_definitions', [])):
                raise Refusal('INCOMPLETE_REPORT_BINDING_OR_DEFINITION')
            continue
        if report.get('model_id') != 'fabric://' + model['workspace'] + '/' + model['native_id']:
            raise Refusal('REPORT_MODEL_BINDING')
        parts = report.get('report_definitions', [])
        if len(parts) > 500 or sum(len(p.get('metadata', {}).get('content', '')) for p in parts) > 2 * 1024 * 1024:
            raise Refusal('DEFINITION_BOUND')
        documents = {}
        for part in parts:
            if part.get('availability', 'CURRENT') != 'CURRENT': raise Refusal('NON_CURRENT_DEFINITION')
            name = part['name']
            if name in documents: raise Refusal('AMBIGUOUS_DEFINITION_PART')
            if name.endswith('.json'):
                try: document = json.loads(part['metadata']['content'])
                except (ValueError, KeyError, TypeError): raise Refusal('MALFORMED_DEFINITION_PART')
                if not isinstance(document, dict): raise Refusal('DEFINITION_PART_SHAPE')
                documents[name] = (part, document)
        for path, (part, document) in documents.items():
            if not re.fullmatch(r'definition/pages/[^/]+/visuals/[^/]+/visual.json', path): continue
            if target is not None and part['id'] != target: continue
            projections = document.get('visual', {}).get('query', {}).get('queryState', {}).get('Values', {}).get('projections', [])
            if any(isinstance(p, dict) and p.get('field', {}).get('Measure') and
                   member(model, p['field'], 'Measure')['id'] == measure_id for p in projections):
                candidates.append((report, documents, path, part, document))
    if len(candidates) != 1:
        raise Refusal('AMBIGUOUS_OR_MISSING_DECLARATION_TARGET' + (': ' + ', '.join(c[3]['id'] for c in candidates) if candidates else ''))
    report, documents, path, selected_part, selected = candidates[0]
    visual = selected['visual']; state = visual.get('query', {}).get('queryState', {})
    if (visual.get('visualType') != 'card' or set(state) != {'Values'}
            or len(state['Values'].get('projections', [])) != 1): raise Refusal('NON_SCALAR_VISUAL_CONTEXT')
    page_path = path.split('/visuals/', 1)[0] + '/page.json'
    if page_path not in documents or 'definition/report.json' not in documents: raise Refusal('MISSING_PARENT_DEFINITION')
    page_part, page = documents[page_path]
    active, sources = [], []

    def add(document, part, origin):
        parsed = restrictions(model, document)
        active.extend(parsed)
        sources.append({'part_id': part['id'], 'content_hash': part['content_hash'],
                        'origin': origin, 'restrictions': parsed, 'applies_by_default': True})

    def filters(document, part, origin):
        config = document.get('filterConfig', {'filters': []})
        if not isinstance(config, dict) or set(config) - {'filters', 'filterSortOrder'}: raise Refusal('FILTER_CONFIG_SHAPE')
        entries = config.get('filters', [])
        if not isinstance(entries, list): raise Refusal('FILTER_CONFIG_SHAPE')
        known = [e.get('filter') for e in entries if isinstance(e, dict) and e.get('filter') is not None]
        if any(native not in known for native in _native_filters(document)):
            raise Refusal('FILTER_APPLICABILITY_UNKNOWN')
        for entry in entries:
            if not isinstance(entry, dict): raise Refusal('FILTER_ENTRY_SHAPE')
            if set(entry) - {'name', 'displayName', 'ordinal', 'field', 'type', 'filter', 'restatement',
                             'howCreated', 'isHiddenInViewMode', 'isLockedInViewMode', 'objects'}:
                raise Refusal('FILTER_ENTRY_MODIFIER')
            if _inverted_selection(entry): raise Refusal('INVERTED_SELECTION_MODE')
            if entry.get('filter') is None:
                exclusions.append({'part_id': part['id'], 'reason': 'FIELD_REFERENCE_WITHOUT_PREDICATE', 'declaration': entry})
                continue
            if entry.get('type') not in (None, 'Categorical'): raise Refusal('FILTER_TYPE_' + str(entry['type']))
            if 'field' in entry:
                declared_column = member(model, entry['field'], 'Column')
                if any(r['field_id'] != declared_column['id'] for r in restrictions(model, entry['filter'])):
                    raise Refusal('FILTER_FIELD_DECLARATION_DISAGREES')
            add(entry['filter'], part, origin)

    if page.get('pageBinding') or page.get('type') in ('Drillthrough', 'Tooltip'):
        raise Refusal('CONDITIONAL_PAGE_CONTEXT')
    filters(documents['definition/report.json'][1], documents['definition/report.json'][0], 'REPORT_FILTER')
    filters(page, page_part, 'PAGE_FILTER'); filters(selected, selected_part, 'VISUAL_FILTER')
    for other_path, (part, document) in documents.items():
        if other_path.startswith('definition/bookmarks/'):
            alternatives = []
            for native in _native_filters(document):
                try: alternatives.append({'restrictions': restrictions(model, native)})
                except Refusal as exc: alternatives.append({'unsupported_form': exc.form, 'declaration': native})
            exclusions.append({'part_id': part['id'], 'content_hash': part['content_hash'],
                'reason': 'STORED_BOOKMARK_REQUIRES_INVOCATION', 'applies_by_default': False,
                'alternatives': alternatives,
                'non_reproduction_limit': 'An invoked bookmark may produce the reported figure; invocation is unknown.'})
        source_visual = document.get('visual', {})
        if source_visual.get('visualType') == 'slicer' and _sync_declared(document):
            raise Refusal('SLICER_SYNC_CONTEXT')
        if not other_path.startswith(page_path.removesuffix('page.json') + 'visuals/'): continue
        if source_visual.get('visualType') != 'slicer': continue
        if _inverted_selection(document): raise Refusal('INVERTED_SELECTION_MODE')
        if 'syncGroup' in document or 'syncGroup' in source_visual: raise Refusal('SLICER_SYNC_CONTEXT')
        interactions = [i for i in page.get('visualInteractions', [])
                        if i.get('source') == document.get('name') and i.get('target') == selected.get('name')]
        if len(interactions) != 1 or interactions[0].get('type') not in ('DataFilter', 'NoFilter'):
            raise Refusal('SLICER_INTERACTION_APPLICABILITY_UNKNOWN')
        if interactions[0]['type'] == 'NoFilter':
            exclusions.append({'part_id': part['id'], 'reason': 'DECLARED_NO_FILTER_INTERACTION'})
            continue
        state = source_visual.get('query', {}).get('queryState', {})
        if set(state) != {'Values'} or len(state['Values'].get('projections', [])) != 1:
            raise Refusal('SLICER_FIELD_CONTEXT')
        selected_column = member(model, state['Values']['projections'][0]['field'], 'Column')
        data = source_visual.get('objects', {}).get('data', [])
        if len(data) != 1 or data[0].get('selector'):
            raise Refusal('SLICER_MODE_APPLICABILITY_UNKNOWN')
        properties = data[0].get('properties', {})
        if set(properties) != {'mode'}:
            raise Refusal('SLICER_DATA_MODIFIER')
        mode = properties['mode'].get('expr', {}).get('Literal', {}).get('Value')
        if mode not in ("'Dropdown'", "'List'"):
            raise Refusal('NON_ENUMERATED_SLICER_MODE')
        # A slicer's own filter pane constrains its choices, not necessarily its selection.
        if source_visual.get('filterConfig') or document.get('filterConfig'):
            raise Refusal('SLICER_CHOICE_FILTER_CONTEXT')
        general = source_visual.get('objects', {}).get('general', [])
        known = [item.get('properties', {}).get('filter', {}).get('filter') for item in general]
        if any(native not in known for native in _native_filters(document)):
            raise Refusal('SLICER_SELECTION_APPLICABILITY_UNKNOWN')
        for item in general:
            selection = item.get('properties', {}).get('filter')
            if selection is None: continue
            if item.get('selector') or not isinstance(selection, dict) or set(selection) != {'filter'}:
                raise Refusal('SLICER_SELECTION_APPLICABILITY_UNKNOWN')
            if any(r['field_id'] != selected_column['id'] for r in restrictions(model, selection['filter'])):
                raise Refusal('SLICER_FIELD_DECLARATION_DISAGREES')
            add(selection['filter'], part, 'SAVED_SLICER_SELECTION')
    if not active: raise Refusal('NO_ACTIVE_PREDICATE')
    # Validate representability/bounds before either query, without doing native extraction in the engine.
    try: declared_reproduction.compose(active)
    except declared_reproduction.UnsupportedRestriction: raise
    except ValueError: raise Refusal('RESTRICTION_REPRESENTATION_BOUND')
    return {'status': 'DECLARED', 'restrictions': active,
        'evidence': {'id': 'declared-context-' + str(uuid4()), 'tool': 'context',
            'completeness': 'COMPLETE_RESPONSE', 'declaration_provenance': 'DECLARED_BY_DEFINITION',
            'declared_restrictions': copy.deepcopy(active), 'conditional_declarations': copy.deepcopy(exclusions),
            'metadata': {'context_version': model['context_id'], 'model_revision': model['revision'],
                'model_id': model['id'], 'definition_target_id': selected_part['id'],
                'report_id': report['report']['id'], 'active_declarations': sources,
                'excluded_declarations': exclusions,
                'pinned_context_hash': digest(model['context'])}}}


def quantity_query(model, measure_id, restrictions):
    catalog = assets(model['context']); by_id = {a['id']: a for a in catalog}
    measure = by_id.get(measure_id)
    if not measure or measure['kind'] != 'Measure': raise Refusal('MEASURE_BINDING')
    def reference(asset):
        table = by_id.get(asset.get('parent_id'))
        if not table or table['kind'] != 'SemanticTable': raise Refusal('TABLE_BINDING')
        return "'" + table['name'].replace("'", "''") + "'[" + asset['name'].replace(']', ']]') + ']'
    terms, paths = [], set()
    for restriction in restrictions:
        if restriction['operator'] != 'IN': raise Refusal('RENDER_OPERATOR_' + str(restriction['operator']))
        column = by_id.get(restriction['field_id'])
        if not column or column['kind'] != 'SemanticColumn': raise Refusal('COLUMN_BINDING')
        path = reference(column)
        if path.casefold() in paths: raise Refusal('DUPLICATE_NATIVE_COLUMN_PATH')
        paths.add(path.casefold())
        values = []
        typ = column.get('metadata', {}).get('dataType')
        for value in restriction['values']:
            if typ == 'string' and type(value) is str: rendered = '"' + value.replace('"', '""') + '"'
            elif typ == 'boolean' and type(value) is bool: rendered = 'TRUE()' if value else 'FALSE()'
            elif typ == 'int64' and type(value) is int: rendered = str(value)
            elif typ in ('double', 'decimal') and type(value) in (int, float):
                from decimal import Decimal
                rendered = format(Decimal(str(value)), 'f')
            else: raise Refusal('RENDER_VALUE_TYPE_' + str(typ))
            values.append(rendered)
        # A constructor-free empty relation stays a filter; never omit it.
        terms.append('TREATAS({' + ','.join(values) + '},' + path + ')' if values
                     else 'FILTER(VALUES(' + path + '),FALSE())')
    expression = reference(measure)
    if terms: expression = 'CALCULATE(' + expression + ',' + ','.join(terms) + ')'
    query = 'EVALUATE ROW("quantity",' + expression + ',"surface_identity",USERPRINCIPALNAME())'
    try: query_dax.compile_query(query, catalog, max_rows=20)
    except ValueError: raise Refusal('NATIVE_QUERY_COMPILATION')
    return query
