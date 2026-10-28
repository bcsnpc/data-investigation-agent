"""Safety-only adapter for model-written SQL/DAX. It never writes a calculation.

Layer routes and object catalogs come from the admitted estate, never from tool
arguments. Execution ports must enforce their timeout and the existing gateway.
The journal passed here is private case storage, not the shared usage ledger.
"""
from copy import deepcopy
from datetime import datetime, timezone
from time import monotonic
from .estate_graph_contract import digest


def validate(text, layer, *, rows=250):
    dialect=layer['dialect']
    if dialect=='DAX':
        from .query_dax import compile_query
        return compile_query(text,layer['objects'],max_rows=rows,allow_define=True)
    if dialect=='T-SQL':
        from .query_sql import compile_query
        return compile_query(text,layer['objects'],max_rows=rows,allow_views=True,allow_computed=True,
                             allow_set_operations=True,allow_temporal_all=True,allow_convert=True,max_joins=16,max_selects=24,literal_limit=4000)
    if dialect!='Spark SQL':raise ValueError('UNKNOWN_LAYER_DIALECT')
    from sqlglot import parse, exp
    from sqlglot.optimizer.scope import traverse_scope
    from sqlglot.optimizer.qualify import qualify
    from .query_sql import NODES, MAX_JOINS, MAX_SELECTS
    if not isinstance(text,str) or not 1<=len(text)<=32000:raise ValueError('QUERY_TEXT_BOUND')
    if type(rows) is not int or not 1<=rows<=250:raise ValueError('QUERY_ROW_BOUND')
    statements=parse(text,read='spark')
    if len(statements)!=1 or not isinstance(statements[0],exp.Select):raise ValueError('ONE_SELECT_REQUIRED')
    tree=statements[0]
    nodes=list(tree.walk())
    if len(nodes)>1200 or {type(n).__name__ for n in nodes}-NODES:
        raise ValueError('UNSUPPORTED_SPARK_READ_SYNTAX')
    if any(n.args.get('recursive') for n in tree.find_all(exp.With)) or list(tree.find_all(exp.Parameter)):
        raise ValueError('UNSUPPORTED_SPARK_READ_SYNTAX')
    if len(list(tree.find_all(exp.Join)))>MAX_JOINS or len(list(tree.find_all(exp.Select)))>MAX_SELECTS:
        raise ValueError('QUERY_COMPLEXITY_BOUND')
    schema={};allowed={}
    for obj in layer['objects']:
        m=obj['metadata'];key=(m['schema_name'].casefold(),m['name'].casefold())
        if key in allowed:raise ValueError('AMBIGUOUS_GRAPH_OBJECT')
        allowed[key]=obj
        schema.setdefault(m['schema_name'],{})[m['name']]={c['name']:c['data_type'] for c in m['columns']}
    references=set()
    for scope in traverse_scope(tree):
        for source in scope.sources.values():
            if not isinstance(source,exp.Table):continue
            if source.catalog or not source.db or not isinstance(source.this,exp.Identifier):
                raise ValueError('GRAPH_SCHEMA_TABLE_REQUIRED')
            obj=allowed.get((source.db.casefold(),source.name.casefold()))
            if obj is None or obj['metadata']['type_desc'] not in ('USER_TABLE','VIEW'):
                raise ValueError('OBJECT_OUTSIDE_ESTATE_GRAPH')
            if any(v for k,v in source.args.items() if k not in ('this','db','catalog','alias')):
                raise ValueError('TABLE_MODIFIER_REFUSED')
            references.add(obj['id'])
    if not references:raise ValueError('GRAPH_REFERENCE_REQUIRED')
    tree=qualify(tree,dialect='spark',schema=schema,validate_qualify_columns=True,identify=True)
    limit=tree.args.get('limit');requested=None
    if limit:
        value=limit.expression
        if not isinstance(value,exp.Literal) or not value.is_int or int(value.this)<1:
            raise ValueError('CONSTANT_POSITIVE_LIMIT_REQUIRED')
        requested=int(value.this)
    tree.set('limit',exp.Limit(expression=exp.Literal.number(min(requested or rows+1,rows+1))))
    query=tree.sql(dialect='spark',comments=False)
    return {'query':query,'parameters':[],'compiled_read':query,'asset_ids':sorted(references),
            'max_rows':rows+1,'validator_version':'spark-read-ast-v1'}


class Queries:
    def __init__(self,layers,*,execute,reserve,save,clock=monotonic,now=None,timeout=30,restored=None,available_layers=None):
        if type(timeout) is not int or not 1<=timeout<=60:raise ValueError('QUERY_TIMEOUT_BOUND')
        self.layers=deepcopy(layers);self.execute=execute;self.reserve=reserve;self.save=save
        self.available_layers=deepcopy(available_layers or layers)
        if any(self.available_layers.get(k)!=v for k,v in layers.items()):raise ValueError('INITIAL_LAYER_REGISTRY_DIFFERS')
        self.clock=clock;self.now=now or (lambda:datetime.now(timezone.utc).isoformat())
        self.timeout=timeout;self.cache={};self.attempts={};self.records=[]
        for record in restored or []:
            self.records.append(deepcopy(record))
            if record['status']=='SUCCEEDED':self.cache[record['signature']]=record
            if record['status']=='ERROR':
                key=(record['layer'],record['purpose']);self.attempts[key]=self.attempts.get(key,0)+1

    def activate(self,identities):
        if not set(identities)<=self.available_layers.keys():raise ValueError('LAYER_OUTSIDE_INSTALLED_REGISTRY')
        added={i:deepcopy(self.available_layers[i]) for i in identities if i not in self.layers}
        self.layers.update(added)
        return added

    def run(self,layer_id,text,*,kind,purpose):
        layer=self.layers.get(layer_id)
        if layer is None:raise ValueError('LAYER_OUTSIDE_TICKET_PATH')
        if kind not in ('sql','dax') or (kind=='dax')!=(layer['dialect']=='DAX'):
            raise ValueError('QUERY_DIALECT_DIFFERS')
        if purpose not in ('recreate','compare','record','lookup','security','different_question','history'):
            raise ValueError('QUERY_PURPOSE_REQUIRED')
        key=(layer_id,purpose)
        try:bound=validate(text,layer)
        except Exception as error:
            if self.attempts.get(key,0)>=3:
                return {'status':'ERROR','error':'QUERY_CORRECTION_LIMIT','layer':layer_id,'purpose':purpose,'corrections_allowed':2}
            # Preserve the direct refusal contract for obvious write proposals.
            import re
            if not isinstance(text,str) or not re.match(r'^\s*(SELECT|WITH|EVALUATE|DEFINE)\b',text,re.I):raise
            from .query_feedback import classify,schema_slice
            from .planner_recording import _safe
            message=str(error);_safe(message.encode())
            record={'id':'query:'+digest([layer_id,text])+':'+str(len(self.records)+1),
                'text':text,'layer':layer_id,'purpose':purpose,'time':self.now(),'status':'ERROR',
                'error_type':type(error).__name__,'error':message,'failure_class':classify(message,validation=True),
                'schema_slice':schema_slice(layer),'native_dispatched':False,'row_count':None,'result_digest':None,
                'duration_seconds':0,'signature':digest([layer_id,text])}
            self.attempts[key]=self.attempts.get(key,0)+1;self.records.append(record)
            self.save({'event':'QUERY_RESULT','query':deepcopy(record)})
            return deepcopy(record)
        signature=digest([layer_id,bound.get('compiled_read') or bound['query'],bound.get('parameters',[])])
        if signature in self.cache:
            prior=deepcopy(self.cache[signature])
            return {'already_have':prior['id'],'note':'Already have this result as evidence '+prior['id'],
                    'record':prior}
        key=(layer_id,purpose)
        if self.attempts.get(key,0)>=3:
            return {'error':'QUERY_CORRECTION_LIMIT','layer':layer_id,'purpose':purpose}
        record={'id':'query:'+signature+':'+str(len(self.records)+1),'signature':signature,'text':text,'layer':layer_id,'purpose':purpose,
                'executed_text':bound['query'],'parameters':bound.get('parameters',[]),'asset_ids':bound['asset_ids'],'time':self.now()}
        # The real governor reserves physical requests immediately before the
        # gateway dispatch. Unknown completion remains charged there.
        self.reserve(layer_id,record['id'])
        self.save({'event':'QUERY_DISPATCH','query':deepcopy(record)})
        started=self.clock()
        try:
            result=self.execute(layer_id,bound,timeout_seconds=self.timeout)
            if not isinstance(result,dict) or not isinstance(result.get('rows'),list):
                raise ValueError('QUERY_RESULT_ROWS_REQUIRED')
            raw_rows=result['rows']
            if len(raw_rows)>bound['max_rows']:raise ValueError('QUERY_RESPONSE_ROW_BOUND')
            record.update(status='SUCCEEDED',row_count=len(raw_rows),result_digest=digest(result),result=result,
                          truncated=len(raw_rows)>=bound['max_rows'])
        except Exception as error:
            from .model_spend import SpendHold
            from .usage_governance import UsageHold
            from .live_gateway import GatewayDenied
            if isinstance(error,(SpendHold,UsageHold,GatewayDenied)):raise
            # Native diagnostics are case-private, checked for accidental
            # credentials before either persistence or model feedback.
            from .planner_recording import _safe
            message=str(error)
            try:_safe(message.encode())
            except ValueError:message='Native error details withheld by secret protection'
            from .query_feedback import classify,schema_slice
            record.update(status='ERROR',error_type=type(error).__name__,error=message,
                          failure_class=classify(message),schema_slice=schema_slice(layer,bound['asset_ids']),
                          native_dispatched=True,row_count=None,result_digest=None)
            self.attempts[key]=self.attempts.get(key,0)+1
        record['duration_seconds']=max(0,self.clock()-started)
        from .planner_recording import _safe
        from .estate_graph_contract import canonical
        _safe(canonical(record).encode())
        self.save({'event':'QUERY_RESULT','query':deepcopy(record)})
        self.records.append(record)
        if record['status']=='SUCCEEDED':self.cache[signature]=deepcopy(record)
        return deepcopy(record)
