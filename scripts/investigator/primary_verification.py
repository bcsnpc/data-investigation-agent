"""Bind displayed-value verification to its cited, admitted native measure read.

An incidental upstream difference is not a comparison supplied by the user.
This does not infer business correctness or choose a target from its value.
"""
from .investigation_read_tools import compare_figure


def no_comparison(intake):
    context=intake.get('comparison_context') or {}
    return (intake.get('compared_with', {}).get('kind') == 'NOTHING'
            and context.get('kind','NOTHING')=='NOTHING')


def query_references(case, identities):
    queries = {q['id'] for q in case.get('queries', [])}
    found, seen = set(), set()
    pending = list(identities)
    while pending:
        identity = pending.pop()
        if not isinstance(identity, str):
            continue
        if identity in seen:
            continue
        seen.add(identity)
        if identity in queries:
            found.add(identity)
            continue
        record = case.get('evidence', {}).get(identity, {})
        if record.get('kind') == 'MODEL_RESPONSE' or record.get('rejected_tool'):
            continue
        result = record.get('result', {})
        if not isinstance(result, dict):
            continue
        result = result.get('record', result)
        if not isinstance(result, dict):
            continue
        if isinstance(result.get('id'), str):
            pending.append(result['id'])
        if isinstance(result.get('query_ids'), list):
            pending.extend(result['query_ids'])
        checks = result.get('layers', result.get('checks', []))
        for check in checks if isinstance(checks, list) else []:
            if isinstance(check, dict) and check.get('query_id'):
                pending.append(check['query_id'])
    return found


def recreation(case, args):
    intake = case.get('intake', {})
    figure = intake.get('reported_figure')
    selected = intake.get('measure') or intake.get('details', {}).get('measure')
    if not figure or not selected:
        return 'UNESTABLISHED'
    nodes = case.get('context', {}).get('path', {}).get('nodes', [])
    measures = [n for n in nodes if n.get('kind') == 'MEASURE' and n['id'] == selected]
    if len(measures) != 1:
        return 'UNESTABLISHED'
    asset = measures[0].get('properties', {}).get('asset_id')
    if not asset:
        return 'UNESTABLISHED'
    cited = query_references(case, args.get('evidence_ids', []))
    observations = []
    for query in case.get('queries', []):
        if (query['id'] not in cited or query.get('status') != 'SUCCEEDED'
                or query.get('purpose') != 'recreate' or query.get('truncated')
                or asset not in query.get('asset_ids', [])):
            continue
        layer = case.get('context', {}).get('layers', {}).get(query.get('layer'), {})
        if layer.get('dialect') != 'DAX':
            continue
        rows = query.get('result', {}).get('rows', [])
        if len(rows) != 1 or not isinstance(rows[0], dict) or not rows[0]:
            continue
        if len(rows[0])==1:value=next(iter(rows[0].values()))
        else:
            column=direct_row_measure_column(query,layer,asset,rows[0])
            if column is None:continue
            value=rows[0][column]
        try:
            observations.append(compare_figure(figure,value)['matches'])
        except (ValueError, TypeError, ArithmeticError, KeyError):
            continue
    if not observations:
        return 'UNESTABLISHED'
    if all(observations):
        return 'MATCH'
    return 'DIFFERS' if not any(observations) else 'MIXED'


def direct_row_measure_column(query,layer,asset,row):
    """Bind a native ROW projection by its parsed measure, never by its value.

    A second diagnostic column must not erase a measured target or become the
    target merely because its numeric value happens to match the ticket.
    Other table expressions remain unestablished by this narrow binder.
    """
    from .query_dax import Parser
    try:
        parser=Parser(query.get('text',''),layer.get('objects',[]),identity=True)
        parser.take('EVALUATE');parser.take('ROW');parser.take('(')
        labels=[];selected=[]
        while True:
            kind,label=parser.take()
            if kind!='string':return None
            label=label[1:-1].replace('""','"')
            labels.append(label)
            parser.take(',');expression,_=parser.expression()
            if expression==repr(asset):selected.append(label)
            if not parser.peek(','):break
            parser.take(',')
        parser.take(')')
        if parser.peek() or len(selected)!=1 or len({x.casefold() for x in labels})!=len(labels):return None
        if parser.references!=set(query.get('asset_ids',[])):return None
        matches=[k for k in row if k in (selected[0],'['+selected[0]+']')]
        return matches[0] if len(matches)==1 else None
    except (ValueError,KeyError,TypeError):return None


def is_display_verification(case, args):
    intake = case.get('intake', {})
    issue = intake.get('classified_issue_type') or intake.get('issue_type')
    # A calculation question without a stated number is not evidence that a
    # displayed value has been verified. Its inclusion/exclusion comparison
    # still needs the exact-question evaluator; do not invent agreement here.
    return (no_comparison(intake) and issue in ('HOW_IS_THIS_CALCULATED','NUMBER_LOOKS_WRONG')
            and recreation(case,args)=='MATCH')
