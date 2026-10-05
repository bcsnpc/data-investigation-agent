"""Bounded language extraction into a neutral relational expression.

The literal evaluator never executes code. Literal seed data can supply a schema,
but a seed without a read is never proposed as a source binding.
"""
import ast
import copy
from .code_static import DeclaredQuantities,Frame,Unsupported

def column(name):return {'kind':'COLUMN','name':name}
def project(frame,columns):
    out=copy.deepcopy(frame)
    out.plan={'kind':'PROJECT','input':frame.plan,'columns':columns}
    out.columns={c['name']:frame.columns.get(c['expression'].get('name'),'derived') for c in columns}
    return out

class Reader(DeclaredQuantities):
    def __init__(self,code,catalog):
        self.catalog=catalog;self.write_locations={}
        super().__init__(code)
    def scalar(self,node):
        if isinstance(node,ast.Constant):return {'kind':'LITERAL','value':node.value}
        if isinstance(node,ast.BinOp):
            operators={ast.Add:'ADD',ast.Sub:'SUBTRACT',ast.Mult:'MULTIPLY',ast.Div:'DIVIDE'}
            if type(node.op) not in operators:raise Unsupported('Unsupported arithmetic')
            return {'kind':operators[type(node.op)],'left':self.scalar(node.left),'right':self.scalar(node.right)}
        if isinstance(node,ast.Compare) and len(node.ops)==1:
            operators={ast.Eq:'EQ',ast.NotEq:'NE',ast.Gt:'GT',ast.GtE:'GE',ast.Lt:'LT',ast.LtE:'LE'}
            if type(node.ops[0]) not in operators:raise Unsupported('Unsupported comparison')
            return {'kind':operators[type(node.ops[0])],'left':self.scalar(node.left),'right':self.scalar(node.comparators[0])}
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and isinstance(node.func.value,ast.Name) and node.func.value.id in self.functions:
            name=node.func.attr
            if name=='col' and len(node.args)==1 and not node.keywords:return column(self.literal(node.args[0]))
            if name=='lit' and len(node.args)==1 and not node.keywords:return {'kind':'LITERAL','value':self.literal(node.args[0])}
            if name in ('sum','count','min','max','avg') and len(node.args)==1 and not node.keywords:
                operand=column(self.literal(node.args[0])) if isinstance(node.args[0],ast.Constant) else self.scalar(node.args[0])
                return {'kind':name.upper(),'operand':operand}
        raise Unsupported('Expression requires model proposal')
    def selected(self,node):
        if isinstance(node,ast.Constant) and isinstance(node.value,str):return {'name':node.value,'expression':column(node.value)}
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='alias' and len(node.args)==1 and not node.keywords:
            return {'name':self.literal(node.args[0]),'expression':self.scalar(node.func.value)}
        expr=self.scalar(node)
        if expr['kind']=='COLUMN':return {'name':expr['name'],'expression':expr}
        raise Unsupported('Derived projection requires explicit alias')
    def frame(self,node):
        self.tick()
        if isinstance(node,ast.Name):return self.env.get(node.id)
        if isinstance(node,ast.Attribute) and node.attr=='write':return self.frame(node.value)
        if not isinstance(node,ast.Call) or not isinstance(node.func,ast.Attribute):return None
        name=node.func.attr
        if name in ('load','table'):
            if len(node.args)!=1 or node.keywords:return None
            reader=ast.unparse(node.func.value)
            if (name=='load' and reader!="spark.read.format('delta')") or (name=='table' and reader!='spark'):return None
            path=self.literal(node.args[0]);written=self.writes.get(path)
            schema=written.columns if written else self.catalog.get(path)
            if not schema:return None
            frame=Frame(copy.deepcopy(schema),{c:(path,c) for c in schema})
            frame.plan={'kind':'SCAN','table':path,'columns':list(schema)};return frame
        if name=='createDataFrame':
            frame=super().frame(node)
            if isinstance(frame,Frame):frame.plan=None
            return frame
        if name=='sql' and ast.unparse(node.func.value)=='spark' and len(node.args)==1 and not node.keywords:
            from .transformation_sql import parse_select
            return parse_select(self.literal(node.args[0]),self.catalog)
        base=self.frame(node.func.value)
        if not isinstance(base,Frame):return None
        frame=copy.deepcopy(base)
        if name in ('format','mode'):
            value=self.literal(node.args[0]) if len(node.args)==1 and not node.keywords else None
            if (name=='format' and value=='delta') or (name=='mode' and value in ('errorifexists','overwrite')):return frame
            return None
        if base.plan is None:return None
        if name=='dropDuplicates':
            keys=self.literal(node.args[0]) if node.args else list(base.columns)
            if node.keywords or len(node.args)>1 or not isinstance(keys,list) or set(keys)!=set(base.columns):
                raise Unsupported('Partial-key deduplication chooses unspecified surviving values')
            frame.plan={'kind':'DEDUPE','input':base.plan,'keys':keys};return frame
        if name=='join':
            if len(node.args)!=3 or node.keywords:return None
            other=self.frame(node.args[0]);keys=self.literal(node.args[1]);how=self.literal(node.args[2])
            if isinstance(keys,str):keys=[keys]
            if not isinstance(other,Frame) or other.plan is None or how not in ('left','inner') or not isinstance(keys,list) or not keys:return None
            if any(k not in base.columns or k not in other.columns for k in keys):return None
            if (set(base.columns)&set(other.columns))-set(keys):raise Unsupported('Duplicate non-key join columns are ambiguous')
            frame.columns.update({k:v for k,v in other.columns.items() if k not in keys})
            frame.plan={'kind':'JOIN','left':base.plan,'right':other.plan,'how':how.upper(),'keys':keys};return frame
        if name=='select':return project(frame,[self.selected(n) for n in node.args]) if not node.keywords else None
        if name=='withColumnRenamed' and len(node.args)==2 and not node.keywords:
            old,new=[self.literal(n) for n in node.args]
            if old not in base.columns or new in base.columns:raise Unsupported('Rename source missing or destination ambiguous')
            return project(frame,[{'name':new if c==old else c,'expression':column(c)} for c in base.columns])
        if name=='withColumn' and len(node.args)==2 and not node.keywords:
            name=self.literal(node.args[0]);expr=self.scalar(node.args[1])
            fields=[{'name':c,'expression':expr if c==name else column(c)} for c in base.columns]
            if name not in base.columns:fields.append({'name':name,'expression':expr})
            return project(frame,fields)
        if name in ('filter','where') and len(node.args)==1 and not node.keywords:
            if isinstance(node.args[0],ast.Constant) and isinstance(node.args[0].value,str):
                from .transformation_sql import scalar
                from sqlglot import parse_one
                predicate=scalar(parse_one(node.args[0].value,read='spark'))
            else:predicate=self.scalar(node.args[0])
            frame.plan={'kind':'FILTER','input':base.plan,'predicate':predicate};return frame
        if name=='groupBy' and not node.keywords:
            frame.groups=[self.literal(n) for n in node.args]
            if any(g not in base.columns for g in frame.groups):return None
            return frame
        if name=='agg' and hasattr(base,'groups') and not node.keywords:
            fields=[{'name':g,'expression':column(g)} for g in base.groups]+[self.selected(n) for n in node.args]
            frame.columns={c['name']:'derived' for c in fields}
            frame.plan={'kind':'AGGREGATE','input':base.plan,'groups':base.groups,'columns':fields};return frame
        return None
    def walk(self,statements):
        # The parent enforces literal-only loops, bounded iteration, exactly one
        # writer and a refusal for unknown control flow. Capture writer spans
        # separately, never infer them from a target's display name.
        super().walk(statements)
        for node in statements:
            if isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Attribute) and node.value.func.attr=='save':
                path=self.literal(node.value.args[0])
                self.write_locations[path]=(node.lineno,node.end_lineno)
