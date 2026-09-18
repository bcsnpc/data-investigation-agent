"""Parse a deliberately small native aggregate grammar; never evaluate DAX."""
from .model_context import assets as model_assets
from .semantic_graph import tokenize
from .onboarding import digest


def describe(model, measure_id):
    assets = model_assets(model['context'])
    measures = {a['id']: a for a in assets if a['kind'] == 'Measure'}
    if measure_id not in measures:raise ValueError('Unknown measure')
    measure = measures[measure_id]
    tokens, gaps = tokenize(measure['metadata'].get('expression'))
    result = {'version': 'aggregate-semantics-v1', 'measure_id': measure_id,
              'definition_hash': measure.get('content_hash', digest(measure['metadata'])),
              'state': 'UNSUPPORTED', 'operation': None, 'input_id': None}
    if gaps or len(tokens) not in (4, 5):
        return dict(result, reason='Only direct SUM(column) or COUNTROWS(table) supported')
    if tokens[0][0] != 'name' or tokens[1][1] != '(' or tokens[-1][1] != ')':
        return dict(result, reason='Expression is outside aggregate grammar')
    operator = tokens[0][1].upper()
    table_token = tokens[2]
    if table_token[0] not in ('name', 'table'):
        return dict(result, reason='Explicit table qualification required')
    table_name = table_token[1][1:-1].replace("''", "'") if table_token[0] == 'table' else table_token[1]
    tables = [a for a in assets if a['kind'] == 'SemanticTable' and a['name'].casefold() == table_name.casefold()]
    if len(tables) != 1:return dict(result, reason='Table binding is ambiguous')
    table = tables[0]
    if operator == 'COUNTROWS' and len(tokens) == 4:
        return dict(result, state='SUPPORTED', operation='count_rows', input_id=table['id'], reason='Direct row-count shape')
    if operator != 'SUM' or len(tokens) != 5 or tokens[3][0] != 'ref':
        return dict(result, reason='Expression is outside aggregate grammar')
    column_name = tokens[3][1][1:-1].replace(']]', ']')
    columns = [a for a in assets if a['kind'] == 'SemanticColumn' and a['parent_id'] == table['id'] and a['name'].casefold() == column_name.casefold()]
    if len(columns) != 1:return dict(result, reason='Column binding is ambiguous')
    column = columns[0]
    if column['metadata'].get('type', 'data') != 'data' or column['metadata'].get('expression'):
        return dict(result, reason='Calculated column semantics unavailable')
    if column['metadata'].get('dataType') not in ('int64', 'decimal'):
        return dict(result, reason='Only exact numeric column sums supported')
    return dict(result, state='SUPPORTED', operation='sum', input_id=column['id'], reason='Direct exact-numeric SUM shape')


def assess_mapping(model, contract, source):
    native = describe(model, contract['measure_id'])
    gaps = []
    if native['state'] != 'SUPPORTED':gaps.append('NATIVE_AGGREGATE_SHAPE_UNSUPPORTED')
    elif native['operation'] != contract['source_operation']:gaps.append('AGGREGATE_OPERATIONS_DIFFER')
    # Reviewed input identity is optional for legacy mappings. Missing identity
    # cannot be guessed from column names or a coincidentally equal number.
    if contract.get('native_input_id') != native['input_id'] or not contract.get('native_input_id'):
        gaps.append('NATIVE_INPUT_MAPPING_REQUIRED')
    if source['request']['plan']['operation'] != contract['source_operation']:
        gaps.append('SOURCE_OPERATION_DIFFERS')
    return {'native': native, 'state': 'SUPPORTED_DECLARED_SHAPE' if not gaps else 'PARTIAL', 'gaps': gaps,
            'semantic_equivalence_verified': False,
            'limitation': 'Operator/input shape only; declared grain, materialization lineage and effective context still need proof.'}


def dependency_shapes(model, measure_id):
    graph=model['context'].get('semantic_graph',{}).get('measures',{})
    pending=[measure_id]; seen=set(); nodes=[]
    while pending:
        identity=pending.pop()
        if identity in seen:continue
        if len(seen)>=1000:raise ValueError('Dependency analysis budget exceeded')
        seen.add(identity); node=graph.get(identity,{})
        shape=describe(model,identity)
        nodes.append({'measure_id':identity,'aggregate':shape,'operations':node.get('operations',[]),
                      'dependencies':node.get('dependencies',[]),'analysis_gaps':node.get('gaps',['Graph unavailable'])})
        pending.extend(node.get('dependencies',[]))
    return {'root':measure_id,'nodes':nodes,'native_evaluation_required':True,
            'limitation':'Complex parents retain their dependency graph; unsupported flat mappings do not block native reads.'}
