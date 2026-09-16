"""Bounded metadata-only dependency contexts. Power BI still evaluates all DAX.

Recognizes neutral arithmetic/DIVIDE measure expressions and top-level CALCULATE
of a direct measure with simple typed equality filters, optionally KEEPFILTERS.
No row context, table filters, date/relationship switches or arbitrary functions.
"""
from .onboarding import digest
from .semantic_graph import tokenize
from .filter_scope import scalar

VERSION = 'dependency-context-v1'


def table(name): return "'" + name.replace("'", "''") + "'"
def bracket(name): return '[' + name.replace(']', ']]') + ']'


class Unsupported(ValueError):
    pass


class Parser:
    def __init__(self, assets, measure):
        self.assets = assets
        self.tables = {a['id']: a for a in assets if a['kind'] == 'SemanticTable'}
        self.measure = measure
        self.tokens, gaps = tokenize(measure.get('metadata', {}).get('expression'))
        if gaps or not self.tokens or len(self.tokens) > 400: raise Unsupported('Expression syntax is outside the context subset')
        self.i = 0; self.depth = 0

    def peek(self, value=None):
        return self.i < len(self.tokens) and (value is None or self.tokens[self.i][1].upper() == value)

    def take(self, value=None):
        if not self.peek(value): raise Unsupported('Unexpected context expression')
        token = self.tokens[self.i]; self.i += 1; return token

    def reference(self, kind):
        qualifier = None
        if self.peek() and self.tokens[self.i][0] in ('name', 'table'):
            typ, qualifier = self.take()
            if typ == 'table': qualifier = qualifier[1:-1].replace("''", "'")
        typ, value = self.take()
        if typ != 'ref': raise Unsupported('Expected catalog reference')
        name = value[1:-1].replace(']]', ']')
        possible = [a for a in self.assets if a['kind'] in ('Measure', 'SemanticColumn') and a['name'].casefold() == name.casefold()]
        if qualifier is not None:
            possible = [a for a in possible if self.tables.get(a.get('parent_id'), {}).get('name', '').casefold() == qualifier.casefold()]
        elif kind == 'SemanticColumn':
            raise Unsupported('Filter column must be table-qualified')
        else:
            possible = [a for a in possible if a['kind'] == 'Measure' or a.get('parent_id') == self.measure['parent_id']]
        if len(possible) != 1 or possible[0]['kind'] != kind: raise Unsupported('Ambiguous catalog reference')
        return possible[0]

    def literal(self, kind):
        if kind not in ('string', 'boolean', 'int64', 'decimal'):
            raise Unsupported('Filter type is outside the context subset')
        sign = ''
        if self.peek('-'): self.take('-'); sign = '-'
        typ, value = self.take()
        if typ == 'string' and not sign:
            parsed = value[1:-1].replace('""', '"')
        elif typ == 'number':
            parsed = sign + value if kind == 'decimal' else int(sign + value) if '.' not in value else None
            if parsed is None: raise Unsupported('Unsupported numeric literal')
        elif value.upper() in ('TRUE', 'FALSE') and not sign:
            self.take('('); self.take(')'); parsed = value.upper() == 'TRUE'
        else: raise Unsupported('Only nonblank typed constants are supported')
        try: expression, _ = scalar(parsed, kind, allow_blank=False)
        except ValueError as exc: raise Unsupported('Literal differs from column type') from exc
        return parsed, expression

    def predicate(self):
        keep = self.peek('KEEPFILTERS')
        if keep: self.take(); self.take('(')
        column = self.reference('SemanticColumn'); self.take('=')
        value, expression = self.literal(column.get('metadata', {}).get('dataType'))
        if keep: self.take(')')
        ref = table(self.tables[column['parent_id']]['name']) + bracket(column['name'])
        sql = ref + '=' + expression
        if keep: sql = 'KEEPFILTERS(' + sql + ')'
        return {'column_id': column['id'], 'value': value, 'mode': 'INTERSECT' if keep else 'REPLACE', 'expression': sql}

    def expression(self):
        self.depth += 1
        if self.depth > 20: raise Unsupported('Expression nesting budget exceeded')
        children = self.atom()
        while self.peek() and self.tokens[self.i][1] in ('+', '-', '*', '/'):
            self.take(); children |= self.atom()
        self.depth -= 1
        return children

    def atom(self):
        if self.peek('('):
            self.take(); children = self.expression(); self.take(')'); return children
        if self.peek('DIVIDE'):
            self.take(); self.take('('); children = self.expression(); self.take(','); children |= self.expression()
            if self.peek(','):
                self.take(',')
                if self.peek('-'): self.take()
                if self.take()[0] != 'number': raise Unsupported('DIVIDE fallback must be constant')
            self.take(')'); return children
        if self.peek('-'): self.take()
        if self.peek() and self.tokens[self.i][0] == 'number': self.take(); return set()
        return {self.reference('Measure')['id']}

    def parse(self):
        filters = []
        if self.peek('CALCULATE'):
            self.take(); self.take('(')
            children = {self.reference('Measure')['id']}
            self.take(',')
            filters.append(self.predicate())
            while self.peek(','): self.take(); filters.append(self.predicate())
            self.take(')')
            if len(filters) > 8 or len({f['column_id'] for f in filters}) != len(filters):
                raise Unsupported('Duplicate or excessive CALCULATE filters')
        else:
            children = self.expression()
        if self.i != len(self.tokens): raise Unsupported('Unsupported context expression tail')
        return [{'child_id': child, 'filters': filters} for child in sorted(children)]


def edges(model, measure_id):
    assets = model['context']['reports'][0]['model_assets']
    measures = {a['id']: a for a in assets if a['kind'] == 'Measure'}
    if measure_id not in measures: raise Unsupported('Unknown measure')
    return Parser(assets, measures[measure_id]).parse()


def compile_path(model, path, selected):
    if (not isinstance(path, list) or not 2 <= len(path) <= 5 or path[-1] != selected
            or any(not isinstance(p, str) for p in path) or len(set(path)) != len(path)):
        raise Unsupported('Expected bounded acyclic root-to-measure path')
    assets = model['context']['reports'][0]['model_assets']
    index = {a['id']: a for a in assets}; wrappers = []; steps = []
    for parent, child in zip(path, path[1:]):
        found = [e for e in edges(model, parent) if e['child_id'] == child]
        if len(found) != 1: raise Unsupported('Path is not a supported catalog dependency')
        filters = found[0]['filters']
        wrappers.append(filters)
        steps.append({'parent_id': parent, 'child_id': child, 'definition_hash': digest(index[parent].get('metadata')),
                      'filters': filters})
    if not any(wrappers): raise Unsupported('Context path must contain a filter transformation')
    target = index.get(selected)
    if not target or target['kind'] != 'Measure': raise Unsupported('Unknown path target')
    expression = table(index[target['parent_id']]['name']) + bracket(target['name'])
    for filters in reversed(wrappers):
        if filters: expression = 'CALCULATE(' + expression + ',' + ','.join(f['expression'] for f in filters) + ')'
    return {'version': VERSION, 'path': path, 'steps': steps, 'expression': expression,
            'provenance': 'RETAINED_DEFINITION_CONTEXT_SUBSET', 'effective_report_context_verified': False,
            'limitation': 'Native evaluation under supported measure-local filters, not report/RLS, source equivalence or causal proof.'}
