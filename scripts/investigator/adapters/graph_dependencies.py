"""Fixed, read-only semantic metadata requests; no implicit fallback or elevation.

The installed XMLA transport must return bounded rows and retain its native
refusal. A collector request is a metadata physical request, not a free control.
"""
import copy
import hashlib
from .. import estate_graph_contract as c
from ..process_tape import bounded_call

FUNCTIONS={'CALCULATIONS':'INFO.CALCDEPENDENCY','RELATIONSHIPS':'INFO.VIEW.RELATIONSHIPS',
           'MEASURES':'INFO.VIEW.MEASURES','COLUMNS':'INFO.VIEW.COLUMNS'}


def query(kind,row_cap=1000):
    if kind not in FUNCTIONS or type(row_cap) is not int or not 1<=row_cap<=1000:
        raise ValueError('GRAPH_DEPENDENCY_QUERY_BOUND')
    # Read one sentinel row to distinguish truncation from a complete result.
    source=FUNCTIONS[kind]+'()'
    if kind=='CALCULATIONS':
        columns=('DATABASE_NAME','OBJECT_TYPE','TABLE','OBJECT','REFERENCED_OBJECT_TYPE','REFERENCED_TABLE','REFERENCED_OBJECT')
        source='SELECTCOLUMNS('+source+', '+', '.join(chr(34)+name+chr(34)+', ['+name+']' for name in columns)+')'
    return f'EVALUATE TOPN({row_cap+1}, {source})'


def validate_query(statement):
    if not isinstance(statement,str):raise ValueError('GRAPH_DEPENDENCY_FIXED_QUERY_REQUIRED')
    if not any(statement==query(kind,cap) for kind in FUNCTIONS for cap in range(1,1001)):
        raise ValueError('GRAPH_DEPENDENCY_FIXED_QUERY_REQUIRED')


def collect(*,kind,target,identity,gateway,meter,transport,route='XMLA',row_cap=1000,timeout=60,
            semantic_write_permission=False):
    """meter(descriptor, thunk) reserves/settles and captures each physical send.

    No retries/polls are hidden here. A transport that retries must account each
    extra send itself. Missing transport or known unsupported route costs zero.
    Existing read-only identities cannot use CALCDEPENDENCY's write permission.
    """
    statement=query(kind,row_cap)
    if set(target)!={'workspace','model'} or any(not c.text(v) for v in target.values()):
        raise ValueError('GRAPH_DEPENDENCY_TARGET')
    if type(timeout) is not int or not 1<=timeout<=120:raise ValueError('GRAPH_DEPENDENCY_TIMEOUT')
    descriptor={'kind':kind,'target':copy.deepcopy(target),'identity':identity,'query':statement,
                'row_cap':row_cap,'timeout':timeout,'budget_class':'metadata','route':route}
    def unavailable(reason,remedy,receipt=None):
        return {'status':'UNKNOWN','request':descriptor,'rows':[],
                'unknown':{'reason':reason,'remedy':remedy},'receipt':receipt}
    if route not in ('XMLA','EXECUTE_DAX_QUERIES'):return unavailable('The ExecuteQueries REST surface does not support INFO functions or DMV queries.',
        'Provide an explicitly approved read-only XMLA metadata transport; do not change the identity scope.')
    if kind=='CALCULATIONS' and not semantic_write_permission:
        return unavailable('INFO.CALCDEPENDENCY requires semantic-model write permission, absent from this reader.',
            'Retain the dependency gap; use definition evidence or a separately approved metadata source. Do not elevate the investigator.')
    if transport is None:return unavailable('No approved metadata transport is installed for this reader.',
        'Install and verify the existing reader transport without granting write or administrator rights.')
    # REST adapter authorizes the exact endpoint and body immediately before send.
    if route=='XMLA':gateway.native_control(identity,'XMLA_GRAPH_METADATA',target,statement)
    response=meter(descriptor,lambda:bounded_call('graph_engine_dependencies',descriptor,
                   lambda:transport(copy.deepcopy(descriptor))))
    if not isinstance(response,dict) or set(response)!={'status','rows','error','receipt_id'}:
        raise ValueError('GRAPH_DEPENDENCY_RESPONSE_SHAPE')
    if not c.text(response['receipt_id']):raise ValueError('GRAPH_DEPENDENCY_RECEIPT_REQUIRED')
    if response['status']!='SUCCEEDED':
        if response['status'] not in ('PERMISSION_DENIED','UNSUPPORTED','FAILED') or not isinstance(response['error'],dict):
            raise ValueError('GRAPH_DEPENDENCY_FAILURE_SHAPE')
        return unavailable('Metadata query '+response['status']+': '+c.canonical(response['error'])[:1600],
            'Retain the exact refused request and resolve its declared permission or platform limitation.',copy.deepcopy(response))
    rows=response['rows']
    if not isinstance(rows,list) or any(not isinstance(row,dict) for row in rows) or len(c.canonical(response).encode())>2*1024*1024:
        raise ValueError('GRAPH_DEPENDENCY_RESPONSE_BOUND')
    if len(rows)>row_cap:return unavailable('Dependency metadata exceeded the bounded row limit; completeness is unknown.',
        'Collect an explicitly partitioned metadata scope within the approved request budget.',copy.deepcopy(response))
    return {'status':'COLLECTED','request':descriptor,'rows':copy.deepcopy(rows),'unknown':None,'receipt':copy.deepcopy(response)}


def dependency_edges(result,*,estate,owner,model,bindings,expected,definition_hash,observed_at,definition_sink):
    """Exact catalog keys (native kind, table, object) -> graph node ID.

    Omitted requested producers and unresolved row endpoints are named gaps;
    an empty metadata result never establishes an empty dependency set.
    """
    c.timestamp(observed_at);edges=[];gaps=[];seen=set();unresolved=set()
    if result['status']!='COLLECTED':return {'edges':[],'gaps':[copy.deepcopy(result['unknown'])],'covered':[]}
    if result['request']['kind']!='CALCULATIONS':raise ValueError('GRAPH_CALCULATION_ROWS_REQUIRED')
    raw=c.canonical(result['receipt']).encode();reference=definition_sink(raw)
    if reference.get('sha256')!=hashlib.sha256(raw).hexdigest() or reference.get('bytes')!=len(raw) or not reference.get('uri'):
        raise ValueError('GRAPH_DEPENDENCY_RETAINED_RESPONSE_REQUIRED')
    for index,row in enumerate(result['rows']):
        source=(row.get('OBJECT_TYPE'),row.get('TABLE'),row.get('OBJECT'))
        target=(row.get('REFERENCED_OBJECT_TYPE'),row.get('REFERENCED_TABLE'),row.get('REFERENCED_OBJECT'))
        if row.get('DATABASE_NAME')!=model or source not in bindings or target not in bindings:
            unresolved.add(source)
            gaps.append({'reason':'Engine dependency row has an unresolved model or endpoint: '+str(index),
                         'remedy':'Resolve the exact native type, table and object in the retained model catalog.'});continue
        seen.add(source)
        proof={'source':'ENGINE_DEPENDENCY','source_id':result['receipt']['receipt_id'],
               'definition_hash':reference['sha256'],'observed_at':observed_at,
               'span':{'kind':'JSON_POINTER','path':'/rows/'+str(index)}}
        eid=c.identity(estate,owner,'COMPUTED_FROM',[bindings[source],bindings[target],index])
        edges.append(c.edge(eid,owner,'COMPUTED_FROM',bindings[source],bindings[target],proof,
                            properties={'native_row_hash':c.digest(row),'completeness':'ROW_ONLY',
                                'definition':reference,'model_definition_hash':definition_hash}))
    for producer in sorted(set(expected)-seen):
        gaps.append({'reason':'Requested calculation has no resolved dependency row: '+c.canonical(producer),
                     'remedy':'Retain UNKNOWN until engine metadata or exact definition evidence covers this calculation.'})
    return {'edges':edges,'gaps':gaps,'covered':sorted(seen-unresolved)}
