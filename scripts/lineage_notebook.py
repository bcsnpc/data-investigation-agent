"""Conservative static notebook dataflow. Never imports or executes notebook code."""
import ast
import hashlib
from dataclasses import dataclass
import sqlglot
from sqlglot import exp
from sqlglot.optimizer.scope import traverse_scope


@dataclass
class Value:
    value: object = None
    refs: frozenset = frozenset()


class StaticNotebook:
    def __init__(self, code):
        self.code=code; self.env={}; self.nodes={}; self.views={}; self.writes=[]; self.gaps=[]; self.steps=0
        tree=ast.parse(code)
        helpers=[n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='read_pinned_bronze']
        self.pinned_reader = (len(helpers)==1 and helpers[0] in tree.body
            and hashlib.sha256(ast.dump(helpers[0],include_attributes=False).encode()).hexdigest()==
                'b005d4efea5c348430b46e5568506a158248449bb798769888bca75b666afdd4'
            and not any(isinstance(n,ast.Name) and isinstance(n.ctx,ast.Store) and n.id=='read_pinned_bronze' for n in ast.walk(tree)))

    def node(self, refs, line, detail, transparent=False):
        key='node:'+str(len(self.nodes))
        self.nodes[key]={'refs':set(refs),'line':line,'detail':detail,'transparent':transparent}
        return Value(None,frozenset({key}))

    def refs(self, value):
        if isinstance(value,Value): return set(value.refs)
        if isinstance(value,(list,tuple,set)): return set().union(*(self.refs(x) for x in value)) if value else set()
        if isinstance(value,dict): return self.refs(list(value.values()))
        return set()

    def bind(self,target,value):
        if isinstance(target,ast.Name): self.env[target.id]=value
        elif isinstance(target,(ast.Tuple,ast.List)):
            if isinstance(value,(tuple,list)) and len(target.elts)==len(value):
                for t,v in zip(target.elts,value): self.bind(t,v)
            else:
                for t in target.elts: self.bind(t,Value(None,frozenset(self.refs(value))))
        elif isinstance(target,ast.Subscript):
            parent=self.eval(target.value); key=self.eval(target.slice)
            if isinstance(parent,dict) and isinstance(key,(str,int)): parent[key]=value

    def eval(self,n):
        if n is None: return None
        if isinstance(n,ast.Constant): return n.value
        if isinstance(n,ast.Name): return self.env.get(n.id,Value())
        if isinstance(n,(ast.List,ast.Tuple,ast.Set)): return [self.eval(x) for x in n.elts]
        if isinstance(n,ast.Dict):
            return {self.eval(k):self.eval(v) for k,v in zip(n.keys,n.values) if k is not None and isinstance(self.eval(k),(str,int))}
        if isinstance(n,ast.Subscript):
            obj,key=self.eval(n.value),self.eval(n.slice)
            try: return obj[key]
            except (TypeError,KeyError,IndexError): return Value(None,frozenset(self.refs(obj)))
        if isinstance(n,ast.JoinedStr):
            pieces=[]; refs=set()
            for x in n.values:
                v=self.eval(x.value) if isinstance(x,ast.FormattedValue) else self.eval(x)
                refs |= self.refs(v); pieces.append(str(v) if not isinstance(v,Value) else '__dynamic__')
            result=''.join(pieces)
            return Value(result,frozenset(refs)) if refs else result
        if isinstance(n,ast.BinOp):
            a,b=self.eval(n.left),self.eval(n.right)
            if isinstance(n.op,ast.Add) and type(a)==type(b) and isinstance(a,(str,list,int)): return a+b
            return Value(None,frozenset(self.refs([a,b])))
        if isinstance(n,(ast.ListComp,ast.GeneratorExp)):
            if len(n.generators)!=1 or n.generators[0].ifs: return Value()
            gen=n.generators[0]; items=self.eval(gen.iter)
            if not isinstance(items,(list,tuple,dict)): return Value()
            saved=dict(self.env); result=[]
            if len(items)>1000: raise ValueError('Static comprehension budget exceeded')
            for item in items:
                self.bind(gen.target,item); result.append(self.eval(n.elt))
            self.env=saved; return result
        if isinstance(n,ast.Attribute): return self.eval(n.value)
        if not isinstance(n,ast.Call): return Value()
        args=[self.eval(a.value if isinstance(a,ast.Starred) else a) for a in n.args]
        keywords=[self.eval(k.value) for k in n.keywords]
        name=n.func.attr if isinstance(n.func,ast.Attribute) else getattr(n.func,'id','')
        base=self.eval(n.func.value) if isinstance(n.func,ast.Attribute) else Value()
        if isinstance(n.func,ast.Name) and name=='read_pinned_bronze':
            binding=args[2] if len(args)==3 else None
            if self.pinned_reader and isinstance(binding,dict) and binding.get('status')=='BOUND_INPUTS':
                tables=binding.get('tables',[])
                if isinstance(tables,list) and len(tables)==10 and all(isinstance(r,dict) and isinstance(r.get('source_table'),str) and isinstance(r.get('destination'),str) for r in tables) and len({r['source_table'] for r in tables})==10:
                    return {r['source_table']:Value(None,frozenset({r['destination']})) for r in tables}
            self.gaps.append((n.lineno,'Unrecognized pinned reader or unresolved binding'))
            return Value()
        if name in ('keys','values','items') and isinstance(base,dict): return list(getattr(base,name)())
        if name=='zip' and all(isinstance(a,(list,tuple)) for a in args): return list(zip(*args))
        if name=='dict' and args and isinstance(args[0],list):
            try: return dict(args[0])
            except (TypeError,ValueError): return {}
        if name=='list' and args and isinstance(args[0],(dict,list,tuple)): return list(args[0])
        if name=='join' and isinstance(base,str) and args and isinstance(args[0],list) and all(isinstance(x,str) for x in args[0]): return base.join(args[0])
        if name=='load' and args and isinstance(args[0],str): return Value(None,frozenset({args[0]}))
        if name=='sql' and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='spark':
            query=args[0] if args else Value()
            refs=self.refs(query); query=query.value if isinstance(query,Value) else query
            if not isinstance(query,str):
                self.gaps.append((n.lineno,'Dynamic SQL cannot be resolved')); return Value()
            try:
                for scope in traverse_scope(sqlglot.parse_one(query,read='spark')):
                    for _,source in scope.selected_sources.values():
                        if isinstance(source,exp.Table):
                            view=self.views.get(source.name)
                            refs |= self.refs(view) if view is not None else {'unresolved-table:'+source.sql()}
            except sqlglot.errors.SqlglotError:
                self.gaps.append((n.lineno,'SQL parsing failed')); refs.add('unresolved-sql:'+str(n.lineno))
            return self.node(refs,n.lineno,query)
        if name=='createOrReplaceTempView' and args and isinstance(args[0],str):
            self.views[args[0]]=base; return None
        if name=='save':
            if args and isinstance(args[0],str): self.writes.append((args[0],self.refs(base),n.lineno))
            else: self.gaps.append((n.lineno,'Dynamic write destination'))
            return None
        if isinstance(base,Value) and base.refs:
            if name in ('format','mode','option','cache','persist','unpersist'): return base
            refs=self.refs([base,args,keywords])
            supported={'select','selectExpr','distinct','dropDuplicates','withColumn','withColumnRenamed','drop',
                       'where','filter','join','union','unionByName','groupBy','agg','first','collect','count',
                       'asDict','items','keys','values','jsonValue','limit','exceptAll','orderBy','sort','repartition','coalesce'}
            if name not in supported:
                self.gaps.append((n.lineno,'Unsupported dataframe operation: '+name))
                refs.add('unresolved-operation:'+str(n.lineno))
            return self.node(refs,n.lineno,ast.get_source_segment(self.code,n) or name,
                             transparent=name=='withColumn' and bool(args) and isinstance(args[0],str) and args[0].startswith('_'))
        refs=self.refs([base,args,keywords])
        if refs: refs.add('unresolved-call:'+str(n.lineno))
        return Value(None,frozenset(refs))

    def walk(self,statements):
        for n in statements:
            self.steps+=1
            if self.steps>25000: raise ValueError('Notebook static-analysis budget exceeded')
            if isinstance(n,ast.Assign):
                value=self.eval(n.value)
                for target in n.targets: self.bind(target,value)
            elif isinstance(n,ast.Expr): self.eval(n.value)
            elif isinstance(n,ast.For):
                values=self.eval(n.iter)
                if isinstance(values,(list,tuple,dict)):
                    if len(values)>1000: raise ValueError('Static loop budget exceeded')
                    for item in values: self.bind(n.target,item); self.walk(n.body)
                elif any(isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr=='save' for x in ast.walk(n)):
                    self.gaps.append((n.lineno,'Unresolved loop containing write'))
            elif isinstance(n,ast.Try): self.walk(n.body)  # success path; exception/finally diagnostics are not data lineage
            elif isinstance(n,ast.If):
                self.gaps.append((n.lineno,'Conditional dataflow requires runtime evidence'))
                for statement in ast.walk(n):
                    if isinstance(statement,ast.Assign):
                        for target in statement.targets:
                            old=self.eval(target)
                            self.bind(target,Value(None,frozenset(self.refs(old)|{'unresolved-control:'+str(n.lineno)})))
            elif isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.While,ast.With)):
                if any(isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr=='save' for x in ast.walk(n)):
                    self.gaps.append((n.lineno,'Unsupported control flow containing write'))
            # Imports/functions/assertions are deliberately not executed.

    def analyze(self):
        self.walk(ast.parse(self.code).body)
        published={}
        def mark(ref,path,seen):
            if ref in seen or ref not in self.nodes: return
            seen.add(ref)
            if ref in published and published[ref]!=path: return
            published[ref]=path
            deps=self.nodes[ref]['refs']
            if self.nodes[ref]['transparent'] and len(deps)==1: mark(next(iter(deps)),path,seen)
        for path,refs,_ in self.writes:
            for ref in refs: mark(ref,path,set())
        result=[]
        for path,refs,line in self.writes:
            proofs=[]; visited=set()
            def resolve(ref):
                if ref in visited: return set()
                visited.add(ref)
                if ref in published and published[ref]!=path: return {published[ref]}
                if ref not in self.nodes: return {ref}
                node=self.nodes[ref]; proofs.append({'line':node['line'],'expression':node['detail']})
                return set().union(*(resolve(x) for x in sorted(node['refs']))) if node['refs'] else set()
            sources=set().union(*(resolve(r) for r in sorted(refs))) if refs else set()
            result.append({'destination':path,'sources':sorted(sources),'line':line,'proofs':proofs})
        return result,self.gaps
