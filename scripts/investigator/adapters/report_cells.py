"""Native visual roles become neutral measure-and-key cell addresses."""
import copy
import json
from ..onboarding import digest

# This knowledge is adapter-owned; no native role names cross this boundary.
ROLES = {
    'card': ({}, {'Values'}),
    'multiRowCard': ({}, {'Values'}),
    'tableEx': ({'Values': 'mixed'}, {'Values'}),
    'pivotTable': ({'Rows': 'group', 'Columns': 'group'}, {'Values'}),
    'clusteredBarChart': ({'Category': 'group', 'Series': 'group'}, {'Y'}),
    'clusteredColumnChart': ({'Category': 'group', 'Series': 'group'}, {'Y'}),
    'stackedBarChart': ({'Category': 'group', 'Series': 'group'}, {'Y'}),
    'stackedColumnChart': ({'Category': 'group', 'Series': 'group'}, {'Y'}),
    'lineChart': ({'Category': 'group', 'Series': 'group'}, {'Y'}),
}


def declared_aliases(model):
    """Projection display names are declared aliases, not inferred synonyms."""
    from .report_predicates import member, Refusal
    result={}
    for report in model['context'].get('reports',[]):
        for part in report.get('report_definitions',[]):
            if not part['name'].endswith('/visual.json'):continue
            document=json.loads(part['metadata']['content'])
            state=document.get('visual',{}).get('query',{}).get('queryState',{})
            for role in state.values():
                for projection in role.get('projections',[]):
                    alias=projection.get('displayName');field=projection.get('field',{})
                    if not isinstance(alias,str) or not alias:continue
                    for kind in ('Measure','Column'):
                        if kind not in field:continue
                        try:identity=member(model,field,kind)['id']
                        except Refusal:continue  # An unresolved alias grants no name match.
                        result.setdefault(identity,set()).add(alias)
    return {key:sorted(values) for key,values in result.items()}


def catalog(model):
    """Retained names and shapes only; never quantities or inferred targets."""
    from .report_predicates import member, Refusal
    result = []
    for report in model['context'].get('reports', []):
        pages = {}
        for part in report.get('report_definitions', []):
            path = part['name'].split('/')
            if len(path) == 4 and path[-1] == 'page.json':
                doc = json.loads(part['metadata']['content'])
                pages[path[2]] = doc.get('displayName')
        for part in report.get('report_definitions', []):
            path = part['name'].split('/')
            if len(path) != 6 or path[-1] != 'visual.json': continue
            doc = json.loads(part['metadata']['content'])
            state = doc.get('visual', {}).get('query', {}).get('queryState', {})
            measures = sorted({member(model, p['field'], 'Measure')['id']
                               for role in state.values() for p in role.get('projections', [])
                               if 'Measure' in p.get('field', {})})
            if not measures: continue
            names = [pages.get(path[2])]
            titles = doc.get('visual', {}).get('visualContainerObjects', {}).get('title', [])
            for title in titles:
                literal = title.get('properties', {}).get('text', {}).get('expr', {}).get('Literal', {}).get('Value')
                if isinstance(literal, str) and literal.startswith("'") and literal.endswith("'"):
                    names.append(literal[1:-1].replace("''", "'"))
            try:
                columns, _ = roles(model, doc)
                grouping = sorted(c['id'] for c in columns)
                unsupported = None
            except Refusal as exc:
                grouping = []
                unsupported = str(exc)
            result.append({'target_id': part['id'], 'report_id': report['report']['id'],
                           'names': sorted(set(n for n in names if n)),
                           'page_id': report['report']['id']+'/page/'+path[2],
                           'page_names': [pages[path[2]]] if pages.get(path[2]) else [],
                           'measure_ids': measures, 'grouping_columns': grouping,
                           'unsupported': unsupported,
                           'form': ('CARD' if doc['visual']['visualType'] in ('card','multiRowCard') else
                                    'MATRIX' if doc['visual']['visualType'] in ('tableEx','pivotTable') else
                                    'CHART' if doc['visual']['visualType'] in ROLES else None)})
    return sorted(result, key=lambda c: c['target_id'])


def projected_measure(model, document, measure_id):
    from .report_predicates import member
    state = document.get('visual', {}).get('query', {}).get('queryState', {})
    return any(isinstance(p, dict) and isinstance(p.get('field'), dict)
               and 'Measure' in p['field'] and member(model, p['field'], 'Measure')['id'] == measure_id
               for role in state.values() for p in role.get('projections', []))


def roles(model, document):
    from .report_predicates import member, Refusal
    visual = document.get('visual', {}); kind = visual.get('visualType')
    if kind not in ROLES: raise Refusal('UNSUPPORTED_VISUAL_TYPE: ' + str(kind))
    groups, value_roles = ROLES[kind]
    state = visual.get('query', {}).get('queryState', {})
    columns, measures = {}, {}
    for role, binding in state.items():
        if role not in groups and role not in value_roles:
            raise Refusal('UNSUPPORTED_PROJECTION_ROLE: ' + str(role))
        for projection in binding.get('projections', []):
            field = projection.get('field', {})
            if 'Column' in field and role in groups:
                asset = member(model, field, 'Column'); columns[asset['id']] = asset
            elif 'Measure' in field and role in value_roles:
                asset = member(model, field, 'Measure'); measures[asset['id']] = asset
            else:
                name = projection.get('displayName') or projection.get('queryRef') or str(next(iter(field), 'UNKNOWN'))
                raise Refusal('UNSUPPORTED_PROJECTED_FIELD: ' + name)
    return list(columns.values()), list(measures.values())


def addresses(model, document, target_id, measure_id, scope):
    from .report_predicates import Refusal
    from ..declared_reproduction import compose
    columns, measures = roles(model, document)
    if measure_id not in {m['id'] for m in measures}: return []
    referent = scope.get('target_visual')
    if referent is not None:
        if referent['target_id'] != target_id or referent['measure_id'] != measure_id:
            raise Refusal('TARGET_UNRESOLVED: addressed visual differs from the ticket referent')
    stated = {}
    for restriction in scope.get('filters', []):
        if restriction.get('operator', 'in') != 'in': continue
        stated.setdefault(restriction['column_id'], []).append({
            'field_id': restriction['column_id'], 'operator': 'IN', 'values': restriction['values']})
    keys = []; missing = []
    for column in columns:
        values = compose(stated[column['id']])[0]['values'] if column['id'] in stated else []
        if len(values) != 1: missing.append(column['name'])
        else: keys.append({'field_id': column['id'], 'operator': 'IN', 'values': values})
    def cell(keys, mode):
        result = {'target_id': target_id, 'measure_id': measure_id,
                  'grouping_columns': sorted(c['id'] for c in columns),
                  'key_restrictions': sorted(copy.deepcopy(keys), key=lambda r: r['field_id']), 'mode': mode}
        result['id'] = digest(result)
        return result
    if referent is not None and referent['mode'] == 'TOTAL':
        if not columns: raise Refusal('TARGET_UNRESOLVED: ungrouped visual has no total row')
        return [cell([], 'TOTAL')]
    if missing: raise Refusal('MISSING_CELL_KEYS: ' + ', '.join(missing))
    result = [cell(keys, 'KEYED' if columns else 'UNGROUPED')]
    if referent is not None:
        if result[0]['mode'] != referent['mode']:
            raise Refusal('TARGET_UNRESOLVED: addressed mode differs from the ticket referent')
        return result
    if columns: result.append(cell([], 'TOTAL'))
    return result
