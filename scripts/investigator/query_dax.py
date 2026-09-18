"""A read-only DAX query grammar and catalog binder, not a DAX evaluator.

Only one EVALUATE expression is admitted. Unknown syntax/functions fail closed.
The AST is serialized from parsed tokens, so comments never become instructions.
"""
from .semantic_graph import tokenize

VERSION='bounded-dax-v1'
TABLE_FUNCTIONS={'ROW','SUMMARIZECOLUMNS','SUMMARIZE','SELECTCOLUMNS','ADDCOLUMNS','FILTER',
                 'CALCULATETABLE','VALUES','DISTINCT','ALL','ALLSELECTED','TOPN','TREATAS',
                 'DATESBETWEEN','DATESINPERIOD','DATEADD','SAMEPERIODLASTYEAR','EXCEPT','INTERSECT','UNION'}
FUNCTIONS=TABLE_FUNCTIONS|{'CALCULATE','SUM','SUMX','COUNT','COUNTX','COUNTROWS','DISTINCTCOUNT',
 'MIN','MAX','MINX','MAXX','AVERAGE','AVERAGEX','DIVIDE','IF','SWITCH','COALESCE','ISBLANK',
 'BLANK','TRUE','FALSE','ABS','ROUND','INT','DATE','YEAR','MONTH','DAY','DATEDIFF','TODAY',
 'NOW','KEEPFILTERS','REMOVEFILTERS','USERELATIONSHIP','HASONEVALUE','SELECTEDVALUE',
 'ISFILTERED','ISCROSSFILTERED','RELATED','RELATEDTABLE','LOOKUPVALUE'}
ENUMS={'ASC','DESC','DAY','MONTH','QUARTER','YEAR','SECOND','MINUTE','HOUR','WEEK'}
OPS={'+','-','*','/','^','&','=','<','>','<=','>=','<>','==','&&','||','IN'}


class Parser:
    def __init__(self,query,assets):
        if not isinstance(query,str) or not 1<=len(query)<=16000:raise ValueError('DAX text budget exceeded')
        tokens,gaps=tokenize(query)
        if gaps or not tokens or len(tokens)>1600:raise ValueError('Unsupported DAX token or syntax budget')
        # The shared metadata lexer produces single-character operators.
        self.tokens=[];i=0
        while i<len(tokens):
            if i+1<len(tokens) and tokens[i][0]==tokens[i+1][0]=='operator' and tokens[i][1]+tokens[i+1][1] in OPS:
                self.tokens.append(('operator',tokens[i][1]+tokens[i+1][1]));i+=2
            else:self.tokens.append(tokens[i]);i+=1
        self.i=0;self.depth=0;self.assets=assets;self.references=set();self.variables=set()
        self.tables={a['name'].casefold():a for a in assets if a['kind']=='SemanticTable'}
        self.members=[a for a in assets if a['kind'] in ('Measure','SemanticColumn')]

    def peek(self,value=None):
        return self.i<len(self.tokens) and (value is None or self.tokens[self.i][1].upper()==value)

    def take(self,value=None):
        if not self.peek(value):raise ValueError('Unsupported DAX query grammar')
        token=self.tokens[self.i];self.i+=1;return token

    def expression(self):
        self.depth+=1
        if self.depth>25:raise ValueError('DAX nesting budget exceeded')
        if self.peek('VAR'):
            chunks=[]
            while self.peek('VAR'):
                self.take();kind,name=self.take()
                if kind!='name' or name.upper() in FUNCTIONS|ENUMS|{'RETURN','EVALUATE','VAR'} or name.casefold() in self.variables or name.casefold() in self.tables:
                    raise ValueError('Invalid DAX variable')
                self.take('=');value,_=self.expression();self.variables.add(name.casefold())
                chunks.append('VAR '+name+' = '+value)
            self.take('RETURN');value,typ=self.expression();result=(' '.join(chunks)+' RETURN '+value,typ)
        else:
            value,typ=self.atom()
            while self.peek() and self.tokens[self.i][1].upper() in OPS:
                operator=self.take()[1];right,_=self.atom();value+=' '+operator+' '+right;typ='scalar'
            result=value,typ
        self.depth-=1
        return result

    def atom(self):
        kind,value=self.take()
        if value in ('+','-') or value.upper()=='NOT':
            child,_=self.atom();return value+' '+child,'scalar'
        if value=='(':
            child,typ=self.expression();self.take(')');return '('+child+')',typ
        if value=='{':
            values=[]
            if not self.peek('}'):
                while True:
                    child,_=self.expression();values.append(child)
                    if not self.peek(','):break
                    self.take(',')
            self.take('}')
            if len(values)>100:raise ValueError('DAX constructor budget exceeded')
            return '{'+','.join(values)+'}','table'
        if kind in ('number','string'):return value,'scalar'
        if kind=='name' and self.peek('('):
            function=value.upper()
            if function not in FUNCTIONS:raise ValueError('Unsupported DAX function: '+function)
            self.take('(');arguments=[]
            if not self.peek(')'):
                while True:
                    child,_=self.expression();arguments.append(child)
                    if not self.peek(','):break
                    self.take(',')
            self.take(')')
            if len(arguments)>80:raise ValueError('DAX argument budget exceeded')
            return function+'('+','.join(arguments)+')','table' if function in TABLE_FUNCTIONS else 'scalar'
        qualifier=None
        if kind in ('name','table'):
            name=value[1:-1].replace("''", "'") if kind=='table' else value
            if self.peek() and self.tokens[self.i][0]=='ref':
                qualifier=name;kind,member=self.take();value=value+member
            else:
                if kind=='name' and name.casefold() in self.variables:return name,'variable'
                table=self.tables.get(name.casefold())
                if table:self.references.add(table['id']);return value,'table'
                if kind=='name' and name.upper() in ENUMS:return name.upper(),'scalar'
                raise ValueError('Unknown DAX table/variable')
        else:member=value
        if kind!='ref':raise ValueError('Unsupported DAX expression')
        name=member[1:-1].replace(']]',']').casefold()
        matches=[a for a in self.members if a['name'].casefold()==name and
                 (a['parent_id']==self.tables.get(qualifier.casefold(),{}).get('id') if qualifier else a['kind']=='Measure')]
        if len(matches)!=1:raise ValueError('Unknown or ambiguous DAX member')
        self.references.add(matches[0]['id']);return value,'scalar'

    def parse(self):
        self.take('EVALUATE');expression,kind=self.expression()
        if self.peek() or kind not in ('table','variable'):raise ValueError('One table-valued EVALUATE required')
        if not self.references:raise ValueError('At least one discovered model reference required')
        return expression


def compile_query(query,assets,*,max_rows=250):
    if type(max_rows) is not int or not 1<=max_rows<=250:raise ValueError('Invalid row budget')
    parser=Parser(query,assets);expression=parser.parse()
    return {'query':'EVALUATE TOPN('+str(max_rows+1)+','+expression+')',
            'asset_ids':sorted(parser.references),'max_rows':max_rows+1,'validator_version':VERSION,
            'limitation':'Native DAX evaluates the proposed context; hidden report selections/RLS and cross-system equivalence are not implied.'}
