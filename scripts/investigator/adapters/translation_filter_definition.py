"""Independent native PBIR compilation for narrowly established filter forms.

Unknown nodes, additional scope and unspecified Top-N tie ordering refuse.
No proposed expression or proposed answer participates in native compilation.
"""
from datetime import datetime, timezone, timedelta
from ..model_context import assets
from .report_predicates import member, Refusal


def closed(value, keys, form):
    if not isinstance(value, dict) or set(value) != set(keys): raise Refusal(form)
    return value


def records(value, low, high, form):
    if not isinstance(value, list) or not low <= len(value) <= high or any(not isinstance(v, dict) for v in value):
        raise Refusal(form)
    return value


def resolved_member(model, value, kind, aliases):
    body = closed(value, (kind,), 'TRANSLATION_NATIVE_MEMBER')[kind]
    closed(body, ('Expression', 'Property'), 'TRANSLATION_NATIVE_MEMBER')
    source = closed(body['Expression'], ('SourceRef',), 'TRANSLATION_NATIVE_MEMBER')['SourceRef']
    if (not isinstance(body['Property'], str) or not isinstance(source, dict)
            or set(source) not in ({'Source'}, {'Entity'})
            or not isinstance(next(iter(source.values())), str)):
        raise Refusal('TRANSLATION_NATIVE_MEMBER')
    return member(model, value, kind, aliases)


def compile_native(model, request, address):
    closed(request['definition'], ('pbir_filter',), 'TRANSLATION_NATIVE_DEFINITION')
    if request['scope'] != {'restrictions': []}:
        raise Refusal('TRANSLATION_NATIVE_ADDITIONAL_SCOPE_NOT_COMPILED')
    doc = request['definition']['pbir_filter']
    closed(doc, ('Version', 'From', 'Where'), 'TRANSLATION_NATIVE_FILTER_SHAPE')
    records(doc['Where'], 1, 1, 'TRANSLATION_NATIVE_FILTER_CONDITIONS')
    records(doc['From'], 1, 16, 'TRANSLATION_NATIVE_SOURCES')
    if type(doc['Version']) is not int or doc['Version'] != 2: raise Refusal('TRANSLATION_NATIVE_FILTER_VERSION_OR_CONDITIONS')
    aliases = {}; subqueries = {}
    for source in doc['From']:
        if type(source.get('Type')) is not int: raise Refusal('TRANSLATION_NATIVE_SOURCE_TYPE')
        if source.get('Type') == 0:
            closed(source, ('Name', 'Entity', 'Type'), 'TRANSLATION_NATIVE_SOURCE')
            target = aliases
            value = source['Entity']
        elif source.get('Type') == 2:
            closed(source, ('Name', 'Expression', 'Type'), 'TRANSLATION_NATIVE_SUBQUERY')
            closed(source['Expression'], ('Subquery',), 'TRANSLATION_NATIVE_SUBQUERY')
            closed(source['Expression']['Subquery'], ('Query',), 'TRANSLATION_NATIVE_SUBQUERY')
            target = subqueries; value = source['Expression']['Subquery']['Query']
        else: raise Refusal('TRANSLATION_NATIVE_SOURCE_TYPE')
        if not isinstance(source['Name'], str) or not source['Name']:
            raise Refusal('TRANSLATION_NATIVE_SOURCE_NAME')
        if source['Name'] in aliases or source['Name'] in subqueries: raise Refusal('TRANSLATION_NATIVE_DUPLICATE_ALIAS')
        target[source['Name']] = value
    closed(doc['Where'][0], ('Condition',), 'TRANSLATION_NATIVE_CONDITION')
    condition = doc['Where'][0]['Condition']
    columns = request['metadata']['native_key_columns']
    if len(columns) != 1: raise Refusal('TRANSLATION_NATIVE_SINGLE_KEY_ONLY')
    catalog = {a['id']:a for a in assets(model['context'])}
    key = catalog.get(columns[0])
    if not key or key['kind'] != 'SemanticColumn': raise Refusal('TRANSLATION_NATIVE_KEY')
    def ref(asset):
        table = catalog[asset['parent_id']]['name'].replace("'", "''")
        return "'" + table + "'[" + asset['name'].replace(']', ']]') + ']'
    keyref = ref(key)
    if isinstance(condition, dict) and set(condition) == {'In'}:
        body = closed(condition['In'], ('Expressions', 'Table'), 'TRANSLATION_NATIVE_TOP_IN')
        records(body['Expressions'], 1, 1, 'TRANSLATION_NATIVE_TOP_KEY')
        if len(body['Expressions']) != 1 or resolved_member(model, body['Expressions'][0], 'Column', aliases)['id'] != key['id']:
            raise Refusal('TRANSLATION_NATIVE_TOP_KEY')
        source = closed(closed(body['Table'], ('SourceRef',), 'TRANSLATION_NATIVE_TOP_TABLE')['SourceRef'],
                        ('Source',), 'TRANSLATION_NATIVE_TOP_TABLE')['Source']
        if not isinstance(source, str) or set(subqueries) != {source}: raise Refusal('TRANSLATION_NATIVE_TOP_SOURCE')
        query = closed(subqueries[source], ('Version', 'From', 'Select', 'OrderBy', 'Top'), 'TRANSLATION_NATIVE_TOP_QUERY')
        records(query['From'], 1, 16, 'TRANSLATION_NATIVE_TOP_SOURCE')
        records(query['Select'], 1, 1, 'TRANSLATION_NATIVE_TOP_PROJECTION')
        records(query['OrderBy'], 2, 2, 'TRANSLATION_NATIVE_TOP_TIE_ORDER_UNESTABLISHED')
        if query['Version'] != 2 or type(query['Top']) is not int or not 1 <= query['Top'] <= 62:
            raise Refusal('TRANSLATION_NATIVE_TOP_BOUND')
        inner = {}
        for item in query['From']:
            closed(item, ('Name', 'Entity', 'Type'), 'TRANSLATION_NATIVE_TOP_SOURCE')
            if (type(item['Type']) is not int or item['Type'] != 0 or not isinstance(item['Name'],str)
                    or item['Name'] in inner): raise Refusal('TRANSLATION_NATIVE_TOP_SOURCE')
            inner[item['Name']] = item['Entity']
        if len(query['Select']) != 1: raise Refusal('TRANSLATION_NATIVE_TOP_PROJECTION')
        selected = query['Select'][0]
        closed(selected, ('Column', 'Name'), 'TRANSLATION_NATIVE_TOP_PROJECTION')
        if resolved_member(model, {'Column':selected['Column']}, 'Column', inner)['id'] != key['id']:
            raise Refusal('TRANSLATION_NATIVE_TOP_PROJECTION')
        ordering = query['OrderBy']
        # The final key ordering is declared, not invented. VALUES groups that
        # same key, so distinct groups cannot tie under its own engine semantics.
        if len(ordering) != 2: raise Refusal('TRANSLATION_NATIVE_TOP_TIE_ORDER_UNESTABLISHED')
        terms = []
        for index, order in enumerate(ordering):
            closed(order, ('Direction', 'Expression'), 'TRANSLATION_NATIVE_TOP_ORDER')
            if type(order['Direction']) is not int or order['Direction'] not in (1, 2): raise Refusal('TRANSLATION_NATIVE_TOP_ORDER')
            item = resolved_member(model, order['Expression'], 'Measure' if index == 0 else 'Column', inner)
            if index == 1 and item['id'] != key['id']: raise Refusal('TRANSLATION_NATIVE_TOP_TIE_ORDER_UNESTABLISHED')
            terms.extend((ref(item), 'ASC' if order['Direction'] == 1 else 'DESC'))
        expression = 'TOPN(' + str(query['Top']) + ',VALUES(' + keyref + '),' + ','.join(terms) + ')'
    elif isinstance(condition, dict) and set(condition) == {'Between'}:
        if subqueries: raise Refusal('TRANSLATION_NATIVE_DATE_SUBQUERY')
        body = closed(condition['Between'], ('Expression', 'LowerBound', 'UpperBound'), 'TRANSLATION_NATIVE_DATE_BETWEEN')
        column_expression = body['Expression']; column_day = False
        if isinstance(column_expression, dict) and set(column_expression) == {'DateSpan'}:
            wrapped = closed(column_expression['DateSpan'], ('TimeUnit', 'Expression'), 'TRANSLATION_NATIVE_DATE_COLUMN_SPAN')
            if type(wrapped['TimeUnit']) is not int or wrapped['TimeUnit'] != 0: raise Refusal('TRANSLATION_NATIVE_DATE_DAY_ONLY')
            column_expression = wrapped['Expression']; column_day = True
        column = resolved_member(model, column_expression, 'Column', aliases)
        if column['parent_id'] != key['parent_id'] or column.get('metadata',{}).get('dataType') != 'dateTime':
            raise Refusal('TRANSLATION_NATIVE_DATE_COLUMN')
        if not request['relative'] or not request['evaluation_timestamp']: raise Refusal('TRANSLATION_NATIVE_DATE_ANCHOR')
        anchor = datetime.fromisoformat(request['evaluation_timestamp'].replace('Z', '+00:00'))
        if anchor.tzinfo is None: raise Refusal('TRANSLATION_NATIVE_DATE_ANCHOR')
        anchor = anchor.astimezone(timezone.utc).date()
        def day(node):
            span = closed(node, ('DateSpan',), 'TRANSLATION_NATIVE_DATE_SPAN')['DateSpan']
            closed(span, ('TimeUnit', 'Expression'), 'TRANSLATION_NATIVE_DATE_SPAN')
            if type(span['TimeUnit']) is not int or span['TimeUnit'] != 0: raise Refusal('TRANSLATION_NATIVE_DATE_DAY_ONLY')
            inner = span['Expression']; offset = 0
            if not isinstance(inner, dict): raise Refusal('TRANSLATION_NATIVE_DATE_EXPRESSION')
            if set(inner) == {'DateAdd'}:
                add = closed(inner['DateAdd'], ('Amount', 'TimeUnit', 'Expression'), 'TRANSLATION_NATIVE_DATE_ADD')
                if type(add['TimeUnit']) is not int or add['TimeUnit'] != 0 or type(add['Amount']) is not int or abs(add['Amount']) > 36500:
                    raise Refusal('TRANSLATION_NATIVE_DATE_DAY_ONLY')
                offset = add['Amount']; inner = add['Expression']
            closed(inner, ('Now',), 'TRANSLATION_NATIVE_DATE_NOW')
            if inner['Now'] != {}: raise Refusal('TRANSLATION_NATIVE_DATE_NOW')
            date = anchor + timedelta(days=offset)
            return date, f'DATE({date.year},{date.month},{date.day})'
        lower, ltext = day(body['LowerBound']); upper, utext = day(body['UpperBound'])
        if lower > upper: raise Refusal('TRANSLATION_NATIVE_DATE_INVERTED')
        table = "'" + catalog[key['parent_id']]['name'].replace("'", "''") + "'"
        comparable = 'INT(' + ref(column) + ')' if column_day else ref(column)
        expression = 'FILTER(' + table + ',' + comparable + '>=' + ltext + '&&' + comparable + '<=' + utext + ')'
    else: raise Refusal('TRANSLATION_NATIVE_CONDITION_UNSUPPORTED')
    return 'EVALUATE DISTINCT(SELECTCOLUMNS(' + expression + ',"translation_key_0",' + keyref + '))'
