"""Bounded static column tracing. Never execute/import notebook code or read data.

Only unchanged physical additive columns cross the supported operations. Row
multiplicity changes remain explicit; this traces the quantity, not business intent.
"""
import ast
import copy
import json
import re
from dataclasses import dataclass, field

@dataclass
class Frame:
    columns: dict
    origins: dict
    operations: list = field(default_factory=list)
    vocabulary: dict = field(default_factory=dict)

class Unsupported(ValueError):
    pass

class DeclaredQuantities:
    def __init__(self, code):
        if len(code)>1_000_000:raise Unsupported('Definition exceeds static-analysis budget')
        self.code=code;self.tree=ast.parse(code);self.env={};self.writes={};self.steps=0
        self.json_modules={n.names[0].asname or 'json' for n in self.tree.body
                           if isinstance(n,ast.Import) and len(n.names)==1 and n.names[0].name=='json'}
        self.functions={alias.asname or alias.name for n in self.tree.body
                        if isinstance(n,ast.ImportFrom) and n.module=='pyspark.sql'
                        for alias in n.names if alias.name=='functions'}
        for n in ast.walk(self.tree):
            if isinstance(n,(ast.Import,ast.ImportFrom)):
                for alias in n.names:
                    bound=alias.asname or alias.name.split('.')[0]
                    allowed=(isinstance(n,ast.Import) and alias.name=='json') or (
                        isinstance(n,ast.ImportFrom) and n.module=='pyspark.sql' and alias.name=='functions')
                    if bound=='spark' or (bound in self.json_modules|self.functions and not allowed):
                        raise Unsupported('Ambiguous imported reader or module binding')
        for n in ast.walk(self.tree):
            if isinstance(n,ast.Name) and isinstance(n.ctx,ast.Store) and n.id in self.json_modules|self.functions|{'spark'}:
                raise Unsupported('Reader or JSON module is reassigned')
        self.walk(self.tree.body)

    def tick(self):
        self.steps+=1
        if self.steps>50000:raise Unsupported('Static expression budget exceeded')

    def bind(self, target, value):
        if isinstance(target,ast.Name):self.env[target.id]=value
        elif isinstance(target,(ast.Tuple,ast.List)) and isinstance(value,(tuple,list)) and len(target.elts)==len(value):
            for t,v in zip(target.elts,value):self.bind(t,v)
        else:raise Unsupported('Unsupported assignment')

    def literal(self,n):
        self.tick()
        if isinstance(n,ast.Constant):return n.value
        if isinstance(n,ast.Name):return self.env.get(n.id)
        if isinstance(n,(ast.List,ast.Tuple)):return [self.literal(x) for x in n.elts]
        if isinstance(n,ast.Dict):return {self.literal(k):self.literal(v) for k,v in zip(n.keys,n.values)}
        if isinstance(n,ast.Subscript):return self.literal(n.value)[self.literal(n.slice)]
        if isinstance(n,ast.BinOp) and isinstance(n.op,ast.Add):return self.literal(n.left)+self.literal(n.right)
        if isinstance(n,ast.Compare) and len(n.ops)==1 and isinstance(n.ops[0],ast.Eq):return self.literal(n.left)==self.literal(n.comparators[0])
        if isinstance(n,ast.IfExp):return self.literal(n.body if self.literal(n.test) else n.orelse)
        if isinstance(n,(ast.GeneratorExp,ast.ListComp)) and len(n.generators)==1 and not n.generators[0].ifs:
            g=n.generators[0];items=self.literal(g.iter)
            if not isinstance(items,(tuple,list)) or len(items)>1000:raise Unsupported('Unbounded schema comprehension')
            saved=dict(self.env);result=[]
            for item in items:self.bind(g.target,item);result.append(self.literal(n.elt))
            self.env=saved;return result
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute):
            if isinstance(n.func.value,ast.Name) and n.func.value.id in self.json_modules and n.func.attr=='loads' and len(n.args)==1 and not n.keywords:
                # Literal only: no file, network, custom decoder or code evaluation.
                text=self.literal(n.args[0])
                if not isinstance(text,str):raise Unsupported('Nonliteral JSON')
                return json.loads(text)
            if n.func.attr=='join' and len(n.args)==1:
                base=self.literal(n.func.value)
                if isinstance(base,str):return base.join(self.literal(n.args[0]))
        raise Unsupported('Unsupported static value')

    def frame(self,n):
        self.tick()
        if isinstance(n,ast.Name):return self.env.get(n.id)
        if isinstance(n,ast.Attribute) and n.attr=='write':return self.frame(n.value)
        if not isinstance(n,ast.Call) or not isinstance(n.func,ast.Attribute):return None
        name=n.func.attr
        if name=='createDataFrame' and isinstance(n.func.value,ast.Name) and n.func.value.id=='spark':
            if len(n.args)!=2 or n.keywords:raise Unsupported('DataFrame schema must be explicit')
            rows=self.literal(n.args[0])
            if not isinstance(rows,list) or len(rows)>100000:raise Unsupported('Unresolved DataFrame source')
            schema=self.literal(n.args[1]);columns={}
            if not isinstance(schema,str):raise Unsupported('Unsupported DataFrame schema')
            for item in schema.split(','):
                match=re.fullmatch(r'\s*([A-Za-z_][A-Za-z0-9_]*)\s+(long|bigint|int|string|double|boolean)\s*',item)
                if not match or match[1] in columns:raise Unsupported('Unsupported or duplicate column declaration')
                columns[match[1]]=match[2]
            return Frame(columns,{})
        if name=='load':
            # Exact Spark Delta reader chain; unknown options are not transparent.
            if ast.unparse(n.func.value)!="spark.read.format('delta')":return None
            if len(n.args)!=1 or n.keywords:return None
            path=self.literal(n.args[0]);written=self.writes.get(path)
            if not written:return None
            return Frame(copy.deepcopy(written.columns),{c:(path,c) for c in written.columns})
        base=self.frame(n.func.value)
        if not isinstance(base,Frame):return None
        base=copy.deepcopy(base)
        if name in ('format','mode'):
            if len(n.args)!=1 or n.keywords:return None
            value=self.literal(n.args[0])
            if name=='format' and value!='delta':return None
            if name=='mode' and value not in ('errorifexists','overwrite'):return None
            return base
        if name=='dropDuplicates':
            if n.keywords or len(n.args)>1:return None
            keys=self.literal(n.args[0]) if n.args else list(base.columns)
            if not isinstance(keys,list) or set(keys)!=set(base.columns):return None
            base.operations.append({'operation':'DEDUPE','keys':sorted(keys),'grain':'whole-row duplicates removed',
                                    'line':n.lineno,'expression':ast.get_source_segment(self.code,n)})
            return base
        if name=='join':
            if len(n.args)!=3 or n.keywords:return None
            other=self.frame(n.args[0]);keys=self.literal(n.args[1]);how=self.literal(n.args[2])
            if not isinstance(other,Frame) or how not in ('left','inner') or not isinstance(keys,list) or not keys:return None
            if any(k not in base.columns or k not in other.columns or base.columns[k]!=other.columns[k] for k in keys):return None
            # Duplicate non-key columns are ambiguous; never choose a side.
            if (set(base.columns)&set(other.columns))-set(keys):return None
            # Keep lexical source spans separate from the executable contract.
            # These are names declared in the definition, not inferred semantics.
            expression=ast.get_source_segment(self.code,n)
            def term(node):
                if not isinstance(node,ast.Name):return None
                start=node.col_offset-n.col_offset
                if node.lineno!=n.lineno or expression[start:start+len(node.id)]!=node.id:return None
                return {'text':node.id,'source_start':start,'source_end':start+len(node.id),
                        'operation_index':len(base.operations)}
            left,right=term(n.func.value),term(n.args[0])
            vocabulary={}
            if left and right and not base.operations and not other.operations:
                for c in base.columns:vocabulary[c]={'subject':left,'matched':right}
                for c in other.columns:
                    if c not in base.columns:vocabulary[c]={'subject':right,'matched':left}
            for c in other.columns:
                if c not in keys:
                    base.columns[c]=other.columns[c]
                    if c in other.origins:base.origins[c]=other.origins[c]
            base.operations.append({'operation':'JOIN','how':how,'keys':keys,
                'inputs':sorted({x[0] for x in list(base.origins.values())+list(other.origins.values())}),
                'grain':'matching rows may multiply; uniqueness is not assumed',
                'line':n.lineno,'expression':ast.get_source_segment(self.code,n)})
            base.vocabulary=vocabulary
            return base
        if name=='withColumn':
            if len(n.args)!=2 or n.keywords:return None
            column=self.literal(n.args[0])
            if not isinstance(column,str):return None
            def scalar(expr):
                if isinstance(expr,ast.Constant):return type(expr.value) in (int,float,str)
                if isinstance(expr,ast.BinOp) and isinstance(expr.op,(ast.Add,ast.Sub,ast.Mult,ast.Div)):
                    return scalar(expr.left) and scalar(expr.right)
                return (isinstance(expr,ast.Call) and isinstance(expr.func,ast.Attribute)
                    and isinstance(expr.func.value,ast.Name) and expr.func.value.id in self.functions
                    and expr.func.attr=='col' and len(expr.args)==1 and not expr.keywords
                    and isinstance(expr.args[0],ast.Constant) and expr.args[0].value in base.columns)
            if not scalar(n.args[1]):return None
            # A changed/derived value is not an unchanged quantity. No translation.
            base.columns[column]='derived';base.origins.pop(column,None)
            base.operations.append({'operation':'DERIVED_COLUMN','column':column,'expression':ast.get_source_segment(self.code,n),'line':n.lineno})
            return base
        return None

    def walk(self,statements):
        for n in statements:
            self.tick()
            if isinstance(n,(ast.Import,ast.ImportFrom)):continue
            if isinstance(n,ast.Assign) and len(n.targets)==1:
                value=self.frame(n.value)
                if value is None:
                    try:value=self.literal(n.value)
                    except (Unsupported,TypeError,KeyError,IndexError):value=None
                self.bind(n.targets[0],value)
            elif isinstance(n,ast.For):
                items=self.literal(n.iter)
                if not isinstance(items,list) or len(items)>1000 or n.orelse:raise Unsupported('Unbounded dataflow loop')
                for item in items:self.bind(n.target,item);self.walk(n.body)
            elif isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute) and n.value.func.attr=='save':
                call=n.value
                if len(call.args)!=1 or call.keywords:raise Unsupported('Unsupported write')
                target=self.literal(call.args[0]);frame=self.frame(call.func.value)
                if target in self.writes:raise Unsupported('Multiple writers for one declared path')
                if not isinstance(target,str) or not isinstance(frame,Frame):raise Unsupported('Unresolved write or input')
                self.writes[target]=frame
            else:raise Unsupported('Unsupported control flow or side effect')
