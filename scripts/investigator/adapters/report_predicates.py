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
from .. import declared_reproduction, declaration_inventory, query_dax, proposal_limits as limits


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


def _enum(field, value):
    # Producer values come from the consumer schema, never a private vocabulary.
    return next(item for item in declaration_inventory.SCHEMA[field]['enum'] if item == value)


class ReportDeclarations:
    """Discover first; unknown units have an explicit UNSUPPORTED disposition.

    Restrictions exist only on inventory entries. A declaration is a native
    predicate, or an unrecognised/undetermined selection-bearing context.
    Plain bindings and known non-predicate structural parts are not predicates.
    """
    def __init__(self, documents):
        self.units = {}
        self.part_units = {}
        self.native_units = {}
        self.discovered = []
        self.documents = {part['id']: document for part, document in documents.values()}
        for path, (part, document) in sorted(documents.items()):
            self.part_units[part['id']] = []
            def discover(node, pointer):
                if isinstance(node, dict):
                    if 'Where' in node or (pointer.endswith('/filter') and set(node) != {'filter'}):
                        self.register(part, pointer, node, 'NATIVE_PREDICATE')
                        return
                    for key, value in sorted(node.items()):
                        discover(value, pointer + '/' + str(key).replace('~','~0').replace('/','~1'))
                elif isinstance(node, list):
                    for index, value in enumerate(node): discover(value, pointer + '/' + str(index))
            discover(document, '')
            # Unknown declaration containers cannot be assumed harmless merely
            # because their payload has no recognised predicate operator.
            if path == 'definition/report.json':
                known_keys = {'$schema','settings','themeCollection','filterConfig','layoutOptimization','resourcePackages'}
            elif re.fullmatch(r'definition/pages/[^/]+/page.json',path):
                known_keys = {'$schema','name','displayName','displayOption','height','width','objects',
                              'filterConfig','visualInteractions','pageBinding','type'}
            elif re.fullmatch(r'definition/pages/[^/]+/visuals/[^/]+/visual.json',path):
                known_keys = {'$schema','name','position','visual','filterConfig','syncGroup'}
            else: known_keys = None
            if known_keys is not None:
                for key in sorted(set(document) - known_keys):
                    pointer='/' + key.replace('~','~0').replace('/','~1')
                    if id(document[key]) not in self.native_units:
                        self.register(part,pointer,document[key],'UNKNOWN_DECLARATION_CONTAINER:' + key)
            visual = document.get('visual')
            if isinstance(visual, dict):
                for key in sorted(set(visual) - {'visualType','objects','visualContainerObjects','query','drillFilterOtherVisuals','syncGroup'}):
                    self.register(part,'/visual/'+key.replace('~','~0').replace('/','~1'),visual[key],'UNKNOWN_VISUAL_DECLARATION:' + key)
                kind = visual.get('visualType')
                from .report_cells import ROLES
                if kind not in (*ROLES, 'textbox', 'slicer'):
                    self.register(part, '/visual', visual, 'UNKNOWN_VISUAL_KIND:' + str(kind))
                elif kind == 'slicer' and not self.part_units[part['id']]:
                    self.register(part, '/visual', visual, 'SLICER_WITHOUT_ENUMERATED_SELECTION')
            elif path.startswith('definition/bookmarks/'):
                if not self.part_units[part['id']]: self.register(part, '', document, 'STORED_BOOKMARK')
            elif not (path in ('definition/report.json', 'definition/version.json', 'definition/pages/pages.json')
                      or re.fullmatch(r'definition/pages/[^/]+/page.json', path)):
                self.register(part, '', document, 'UNKNOWN_DEFINITION_PART')

    def register(self, part, pointer, native, form):
        source = {'location': part['id'] + '#' + pointer,
                  'content_hash': digest(native)}
        identity = declaration_inventory.identity(source)
        if identity in self.units: raise Refusal('DUPLICATE_DISCOVERED_DECLARATION')
        self.discovered.append(source)
        self.units[identity] = {'id': identity, 'source': source,
            'disposition': _enum('disposition','UNSUPPORTED'),
            'volatility': _enum('volatility','UNKNOWN'),
            'assumption': _enum('assumption','APPLICABILITY_UNKNOWN'),
            'opaque_provenance': json.dumps({'part_id':part['id'],'part_hash':part['content_hash'],'form':form},sort_keys=True),
            'restrictions': []}
        self.part_units[part['id']].append(identity)
        self.native_units[id(native)] = identity

    def classify(self, identity, disposition, *, restrictions=None, volatile=False, origin=None):
        entry = self.units[identity]
        entry['disposition'] = _enum('disposition',disposition)
        entry['volatility'] = _enum('volatility','VIEWER_CHANGEABLE' if volatile else
                                    ('UNKNOWN' if disposition == 'UNSUPPORTED' else 'FIXED'))
        entry['assumption'] = _enum('assumption','SAVED_DEFAULT' if volatile else
                                    ('INVOCATION_UNKNOWN' if disposition == 'CONDITIONAL' else
                                     ('APPLICABILITY_UNKNOWN' if disposition == 'UNSUPPORTED' else 'NONE')))
        entry['restrictions'] = copy.deepcopy(restrictions or [])
        if origin:
            provenance=json.loads(entry['opaque_provenance']);provenance['classification']=origin
            entry['opaque_provenance']=json.dumps(provenance,sort_keys=True)

    def active(self, native, part, origin, parsed):
        identity=self.native_units.get(id(native))
        if identity is None: raise Refusal('RESTRICTION_WITHOUT_DISCOVERED_DECLARATION')
        self.classify(identity,'ACTIVE',restrictions=parsed,
                      volatile=origin == 'SAVED_SLICER_SELECTION',origin=origin)

    def conditional(self, part, reason):
        for identity in self.part_units[part['id']]: self.classify(identity,'CONDITIONAL',origin=reason)

    def unsupported(self, part, form):
        for identity in self.part_units[part['id']]: self.classify(identity,'UNSUPPORTED',origin=form)
        if not self.part_units[part['id']]:
            # Native context may be unrenderable without an IN node (e.g. page binding).
            self.register(part, '', self.documents[part['id']], form)

    def result(self):
        return {'discovered':copy.deepcopy(self.discovered),
                'entries':[copy.deepcopy(self.units[key]) for key in sorted(self.units)]}


def extract(model, measure_id, scope):
    try:
        if 'definition_target_id' in scope:raise Refusal('LEGACY_SIDE_CHANNEL_TARGET')
        target=scope.get('definition_target')
        if target is None:
            result=_extract(model,measure_id,scope)
            _addressed(model, measure_id, scope, result)
            return result
        from .. import definition_target as contract
        try:contract.shape(target)
        except ValueError:raise Refusal('TARGET_RESOLUTION_CONTRACT')
        if target['resolution_kind']=='REFUSED':raise Refusal(('Target ambiguity: ' if target['candidates'] else 'Target unavailable: ')+', '.join(target['candidates']))
        available=targets(model,measure_id)
        columns=[{'column_id':a['id'],'name':a['name']} for a in assets(model['context']) if a['kind']=='SemanticColumn']
        request={'source':target['source']}
        if target['resolution_kind']=='STATED':request['column_id']=target['column_id']
        try:expected,_,_=contract.lookup(request,ticket=None,options=available,columns=columns)
        except contract.ResolutionRefused as exc:raise Refusal(str(exc))
        except ValueError:raise Refusal('TARGET_RESOLUTION_CONTRACT')
        if expected!=target:raise Refusal('TARGET_RESOLUTION_CHANGED')
        matching=[]
        for option in available:
            from ..report_scope import validate_inventory
            entries=validate_inventory(option['inventory'],option['restrictions'],binding=option['evidence']['report_binding'],reports=option['evidence']['report_catalog'])
            if target['resolution_kind']=='EVIDENCE':
                entry=next((e for e in entries if e['id']==target['inventory_entry_id']),None)
                applies=entry is not None and entry['disposition']=='ACTIVE' and any(r['field_id']==target['column_id'] for r in entry['restrictions'])
                if applies:contract.validate(target,inventory=option['inventory'],active=option['restrictions'],binding=option['evidence']['report_binding'],reports=option['evidence']['report_catalog'])
            else:applies=any(e['disposition']=='ACTIVE' and any(r['field_id']==target['column_id'] for r in e['restrictions']) for e in entries)
            if applies:matching.append(option)
        if len(matching)!=1:
            raise Refusal(('Target unavailable: ' if not matching else 'Target ambiguity: ')+('no ACTIVE declaration matches the target column' if not matching else
                'multiple visual contexts match: '+', '.join(o['target_id'] for o in matching)))
        result=_extract(model,measure_id,scope,matching[0]['target_id'])
        _addressed(model, measure_id, scope, result)
        result['evidence']['metadata']['target_resolution']=copy.deepcopy(target)
        return result
    except (Refusal, declared_reproduction.UnsupportedRestriction): raise
    except (KeyError, TypeError, AttributeError): raise Refusal('MALFORMED_NATIVE_DECLARATION')


def targets(model,measure_id,report_id=None):
    """Enumerate native candidate visuals locally; never combine their contexts."""
    candidates=[]
    for report in model['context'].get('reports',[]):
        if report_id is not None and report['report']['id'] != report_id: continue
        parts=report.get('report_definitions',[])
        if len(parts)>500 or sum(len(p.get('metadata',{}).get('content','')) for p in parts)>2*1024*1024:
            raise Refusal('DEFINITION_BOUND')
        for part in parts:
            if not re.fullmatch(r'definition/pages/[^/]+/visuals/[^/]+/visual.json',part['name']):continue
            try:document=json.loads(part['metadata']['content'])
            except (ValueError,KeyError,TypeError):raise Refusal('MALFORMED_DEFINITION_PART')
            if not isinstance(document,dict):raise Refusal('DEFINITION_PART_SHAPE')
            from .report_cells import projected_measure
            if projected_measure(model, document, measure_id):
                declaration=_extract(model,measure_id,{'report_binding': {'report_id': report_id}} if report_id is not None else {},part['id'])
                candidates.append({'target_id':part['id'],'inventory':declaration['inventory'],'restrictions':declaration['restrictions'],'evidence':declaration['evidence']})
                if len(candidates)>512:raise Refusal('DEFINITION_TARGET_BOUND')
    return candidates

def _extract(model, measure_id, scope, selected_target=None):
    """Select a unique declared scalar visual; never combine reports or pages."""
    candidates = []
    exclusions = []
    target = selected_target
    for report in model['context'].get('reports', []):
        if scope.get('report_binding') and report['report']['id'] != scope['report_binding']['report_id']: continue
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
            from .report_cells import projected_measure
            if projected_measure(model, document, measure_id):
                candidates.append((report, documents, path, part, document))
    if len(candidates) != 1:
        raise Refusal(('MISSING_DECLARATION_TARGET' if not candidates else 'AMBIGUOUS_DECLARATION_TARGET') + (': ' + ', '.join(c[3]['id'] for c in candidates) if candidates else ''))
    report, documents, path, selected_part, selected = candidates[0]
    page_path = path.split('/visuals/', 1)[0] + '/page.json'
    if page_path not in documents or 'definition/report.json' not in documents: raise Refusal('MISSING_PARENT_DEFINITION')
    page_part, page = documents[page_path]
    inventory = ReportDeclarations(documents)

    def add(document, part, origin):
        parsed = restrictions(model, document)
        inventory.active(document, part, origin, parsed)

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

    for document, part, origin in ((documents['definition/report.json'][1],documents['definition/report.json'][0],'REPORT_FILTER'),
                                    (page,page_part,'PAGE_FILTER'),(selected,selected_part,'VISUAL_FILTER')):
        try:
            if part == page_part and (page.get('pageBinding') or page.get('type') in ('Drillthrough','Tooltip')):
                raise Refusal('CONDITIONAL_PAGE_CONTEXT')
            filters(document,part,origin)
        except (Refusal, declared_reproduction.UnsupportedRestriction) as exc:
            inventory.unsupported(part,exc.form)
    for other_path, (part, document) in documents.items():
        try:
            if other_path.startswith('definition/bookmarks/'):
                alternatives = []
                for native in _native_filters(document):
                    try: alternatives.append({'restrictions': restrictions(model, native)})
                    except Refusal as exc: alternatives.append({'unsupported_form': exc.form, 'declaration': native})
                inventory.conditional(part, 'STORED_BOOKMARK_REQUIRES_INVOCATION')
                exclusions.append({'part_id': part['id'], 'content_hash': part['content_hash'],
                    'reason': 'STORED_BOOKMARK_REQUIRES_INVOCATION', 'applies_by_default': False,
                    'alternatives': alternatives,
                    'non_reproduction_limit': 'An invoked bookmark may produce the reported figure; invocation is unknown.'})
            source_visual = document.get('visual', {})
            from .report_cells import ROLES
            # Filters attached to a different known visual/page are stored
            # alternatives, not active in the selected cell. Unknown containers
            # remain UNSUPPORTED; do not blanket-classify a whole part.
            other_known_visual = (part['id'] != selected_part['id'] and source_visual.get('visualType') in ROLES)
            other_page = re.fullmatch(r'definition/pages/[^/]+/page.json', other_path) and other_path != page_path
            if other_known_visual or other_page:
                for item in document.get('filterConfig', {}).get('filters', []):
                    native = item.get('filter') if isinstance(item, dict) else None
                    if native is not None:
                        identity = inventory.native_units.get(id(native))
                        if identity is None: raise Refusal('UNACCOUNTED_ALTERNATIVE_DECLARATION')
                        inventory.classify(identity, 'CONDITIONAL', origin='OTHER_VISUAL_OR_PAGE_CONTEXT')
            if source_visual.get('visualType') == 'slicer' and _sync_declared(document):
                raise Refusal('SLICER_SYNC_CONTEXT')
            if not other_path.startswith(page_path.removesuffix('page.json') + 'visuals/'):
                if source_visual.get('visualType') == 'slicer':
                    for identity in inventory.part_units[part['id']]:
                        form=json.loads(inventory.units[identity]['opaque_provenance'])['form']
                        if form in ('NATIVE_PREDICATE','SLICER_WITHOUT_ENUMERATED_SELECTION'):
                            inventory.classify(identity,'CONDITIONAL',origin='OTHER_PAGE_SAVED_SELECTION')
                continue
            if source_visual.get('visualType') != 'slicer': continue
            if _inverted_selection(document): raise Refusal('INVERTED_SELECTION_MODE')
            if 'syncGroup' in document or 'syncGroup' in source_visual: raise Refusal('SLICER_SYNC_CONTEXT')
            general = source_visual.get('objects', {}).get('general', [])
            if not general and not list(_native_filters(document)) and scope.get('report_binding'):
                state = source_visual.get('query', {}).get('queryState', {})
                if set(state) != {'Values'} or len(state['Values'].get('projections', [])) != 1:
                    raise Refusal('SLICER_FIELD_CONTEXT')
                member(model, state['Values']['projections'][0]['field'], 'Column')
                objects=source_visual.get('objects',{})
                if set(objects)-{'data','general'}: raise Refusal('SLICER_SELECTION_CONTAINER_UNKNOWN')
                data=objects.get('data',[])
                if len(data)!=1 or data[0].get('selector'): raise Refusal('SLICER_MODE_APPLICABILITY_UNKNOWN')
                properties=data[0].get('properties',{})
                if set(properties)!={'mode'}: raise Refusal('SLICER_DATA_MODIFIER')
                mode=properties['mode'].get('expr',{}).get('Literal',{}).get('Value')
                if mode not in ("'Dropdown'","'List'"): raise Refusal('NON_ENUMERATED_SLICER_MODE')
                if document.get('filterConfig') or source_visual.get('filterConfig'): raise Refusal('SLICER_CHOICE_FILTER_CONTEXT')
                # Saved absence is a full-domain declaration, not an inferred value.
                inventory.classify(inventory.native_units[id(source_visual)], 'ACTIVE',
                                   origin='SAVED_FULL_DOMAIN', volatile=True)
                continue
            interactions = [i for i in page.get('visualInteractions', [])
                            if i.get('source') == document.get('name') and i.get('target') == selected.get('name')]
            if len(interactions) != 1 or interactions[0].get('type') not in ('DataFilter', 'NoFilter'):
                raise Refusal('SLICER_INTERACTION_APPLICABILITY_UNKNOWN')
            if interactions[0]['type'] == 'NoFilter':
                inventory.conditional(part, 'DECLARED_NO_FILTER_INTERACTION')
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
        except (Refusal, declared_reproduction.UnsupportedRestriction) as exc:
            inventory.unsupported(part, exc.form)
    inventory_result = inventory.result()
    from .. import report_scope
    binding = scope.get('report_binding')
    if not binding or set(binding)=={'report_id'}:
        name=report['report']['name']
        binding=report_scope.resolve_report({'start':0,'end':len(name),'quote':name},report_catalog(model))
    report_scope.report_binding(binding,reports=report_catalog(model))
    if binding['report_id']!=report['report']['id']: raise Refusal('REPORT_SCOPE_MISMATCH')
    for source in inventory_result['discovered']: source['report_id']=binding['report_id']
    for entry in inventory_result['entries']:
        entry['source']['report_id']=binding['report_id']
        entry['id']=report_scope.inventory_identity(entry['source'])
        entry['effect']=('RESTRICTED' if entry['restrictions'] else 'FULL_DOMAIN') if entry['disposition']=='ACTIVE' else 'EXCLUDED'
    inventory_result['report_id']=binding['report_id']
    active = [copy.deepcopy(r) for entry in inventory_result['entries']
              if entry['disposition'] == _enum('disposition','ACTIVE') for r in entry['restrictions']]
    return {'status': 'DECLARED', 'inventory': inventory_result, 'restrictions': active,
        'evidence': {'id': 'declared-context-' + str(uuid4()), 'tool': 'context',
            'completeness': 'COMPLETE_RESPONSE', 'declaration_provenance': 'DECLARED_BY_DEFINITION',
            'declared_restrictions': copy.deepcopy(active), 'conditional_declarations': copy.deepcopy(exclusions),
            'report_binding':copy.deepcopy(binding),'report_catalog':report_catalog(model),
            'metadata': {'context_version': model['context_id'], 'model_revision': model['revision'],
                'model_id': model['id'], 'definition_target_id': selected_part['id'],
                'report_id': report['report']['id'],
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
    query = 'EVALUATE ROW("quantity",' + expression + ')'
    try: query_dax.compile_query(query, catalog, max_rows=20)
    except ValueError: raise Refusal('NATIVE_QUERY_COMPILATION')
    return query


def _document(model, target_id):
    parts = [p for r in model['context']['reports'] for p in r['report_definitions'] if p['id'] == target_id]
    if len(parts) != 1: raise Refusal('AMBIGUOUS_DEFINITION_PART')
    return json.loads(parts[0]['metadata']['content'])


def _addressed(model, measure_id, scope, declaration):
    from .report_cells import addresses
    target_id = declaration['evidence']['metadata']['definition_target_id']
    return addresses(model, _document(model, target_id), target_id, measure_id, scope)


def report_catalog(model):
    return [{'id': r['report']['id'], 'name': r['report']['name']}
            for r in model['context'].get('reports', [])]


def scoped_declaration(model, measure_id, scope, target_id):
    """Produce the new inventory from the discovered units, not a second filter path."""
    from .. import report_scope
    result = _extract(model, measure_id, scope, target_id)
    binding = scope['report_binding']; inventory = result['inventory']
    report_scope.validate_inventory(inventory,result['restrictions'],binding=binding,reports=report_catalog(model))
    forms=sorted({json.loads(e['opaque_provenance'])['form'] for e in inventory['entries'] if e['disposition']=='UNSUPPORTED'})
    if forms: result['unsupported_form']=', '.join(forms)
    return result


def scoped_options(model, measure_id, binding):
    from .. import report_scope
    report_scope.report_binding(binding, reports=report_catalog(model))
    options = targets(model, measure_id, binding['report_id'])
    return [scoped_declaration(model, measure_id, {'report_binding': binding}, o['target_id']) for o in options]


def cells(model, measure_id, scope):
    """Only the stated report is enumerated, after conserved inventory resolution."""
    from .. import report_scope
    from .report_cells import addresses
    report_scope.report_binding(scope.get('report_binding'), reports=report_catalog(model))
    declarations = scoped_options(model, measure_id, scope['report_binding'])
    result = []; refused = []
    for declaration in declarations:
        target_id = declaration['evidence']['metadata']['definition_target_id']
        try:
            for address in addresses(model, _document(model, target_id), target_id, measure_id, scope):
                item = copy.deepcopy(declaration); item['cell'] = address
                item['evidence']['cell'] = copy.deepcopy(address)
                result.append(item)
        except Refusal as exc:
            refused.append({'target_id': target_id, 'reason': str(exc), 'form': exc.form})
            if exc.form.startswith('MISSING_CELL_KEYS:'):
                from .report_cells import roles
                columns,_=roles(model,_document(model,target_id))
                address={'target_id':target_id,'measure_id':measure_id,'grouping_columns':sorted(c['id'] for c in columns),
                    'key_restrictions':[],'mode':'TOTAL'}
                address['id']=digest(address)
                item=copy.deepcopy(declaration);item['cell']=address;item['evidence']['cell']=copy.deepcopy(address)
                result.append(item)
    return {'status': 'DECLARED', 'cells': result, 'refusals': refused}
