"""A read-only DAX query grammar and catalog binder, not a DAX evaluator.

Only one EVALUATE expression is admitted. Unknown syntax/functions fail closed.
The AST is serialized from parsed tokens, so comments never become instructions.
"""
from . import proposal_limits as limits
from .semantic_graph import tokenize

VERSION='bounded-dax-v1'
TABLE_FUNCTIONS={'ROW','SUMMARIZECOLUMNS','SUMMARIZE','SELECTCOLUMNS','ADDCOLUMNS','FILTER',
                 'CALCULATETABLE','VALUES','DISTINCT','ALL','ALLSELECTED','TOPN','TREATAS',
                 'DATESBETWEEN','DATESINPERIOD','DATEADD','SAMEPERIODLASTYEAR','EXCEPT','INTERSECT','UNION'}
FUNCTIONS=TABLE_FUNCTIONS|{'CALCULATE','SUM','SUMX','COUNT','COUNTX','COUNTROWS','DISTINCTCOUNT',
 'MIN','MAX','MINX','MAXX','AVERAGE','AVERAGEX','DIVIDE','IF','SWITCH','COALESCE','ISBLANK',
 'BLANK','TRUE','FALSE','ABS','ROUND','INT','DATE','YEAR','MONTH','DAY','DATEDIFF','TODAY',
 'NOW','DATEVALUE','VALUE','IFERROR','KEEPFILTERS','REMOVEFILTERS','USERELATIONSHIP','HASONEVALUE','SELECTEDVALUE',
 'ISFILTERED','ISCROSSFILTERED','RELATED','RELATEDTABLE','LOOKUPVALUE','USERPRINCIPALNAME'}
ENUMS={'ASC','DESC','DAY','MONTH','QUARTER','YEAR','SECOND','MINUTE','HOUR','WEEK'}
OPS={'+','-','*','/','^','&','=','<','>','<=','>=','<>','==','&&','||','IN'}


def capabilities():
    return {'tool':'bounded_dax','validator_version':VERSION,'mode':'READ_ONLY_EVALUATE',
            'supported_functions':sorted(FUNCTIONS),'max_result_rows':250,
            'prerequisites':['Approved discovered model','Isolated native reader'],
            'experiments':['Native cardinality','Measure components','Dimension sensitivity','Date sensitivity'],
            'limits':'Power BI executes expressions. Observed behavior does not establish intended additivity, visual filters or RLS equivalence.'}


class Parser:
    def __init__(self,query,assets,*,identity=False):
        self.identity=identity;self.volatile=False
        if not isinstance(query,str) or not 1<=len(query)<=limits.QUERY_TEXT:raise ValueError('DAX text budget exceeded')
        tokens,gaps=tokenize(query)
        if gaps or not tokens or len(tokens)>1600:raise ValueError('Unsupported DAX token or syntax budget')
        # The shared metadata lexer produces single-character operators.
        self.tokens=[];i=0
        while i<len(tokens):
            if i+1<len(tokens) and tokens[i][0]==tokens[i+1][0]=='operator' and tokens[i][1]+tokens[i+1][1] in OPS:
                self.tokens.append(('operator',tokens[i][1]+tokens[i+1][1]));i+=2
            else:self.tokens.append(tokens[i]);i+=1
        self.i=0;self.depth=0;self.projected_columns={};self.assets=assets;self.references=set();self.variables=set()
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
        # Narrow scalar self-description, not general INFO-table access or a
        # bypass of catalog binding. Exact token grammar keeps synthetic rowset
        # columns out of model-member resolution everywhere else.
        from .adapters.microsoft_self_report import SCALARS
        for expression in SCALARS:
            expected,_=tokenize(expression)
            candidate=self.tokens[self.i:self.i+len(expected)]
            if [(k,v.upper() if k=='name' else v) for k,v in candidate]==[(k,v.upper() if k=='name' else v) for k,v in expected]:
                self.i+=len(expected)
                # Preserve the expression in the compiled fingerprint rather
                # than erasing it or disabling existing scope deduplication.
                return expression,'scalar'
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
            if function in ('NOW','TODAY'):self.volatile=True
            if not self.peek(')'):
                while True:
                    child,_=self.expression();arguments.append(child)
                    if not self.peek(','):break
                    self.take(',')
            self.take(')')
            if len(arguments)>80:raise ValueError('DAX argument budget exceeded')
            if self.identity and self.depth==1 and function=='ROW':
                # Only outer ROW labels are presentation. Never erase nested labels.
                if len(arguments)%2==0:arguments=sorted(arguments[1::2])
            rendered=function+'('+','.join(arguments)+')'
            # Projection is computed from parsed table constructors, never from
            # labels merely occurring inside a scalar or query comment.
            columns=set()
            if function=='ROW': labels=arguments[::2]
            elif function in ('ADDCOLUMNS','SELECTCOLUMNS'): labels=arguments[1::2]
            else: labels=[]
            if function in ('ADDCOLUMNS','FILTER','TOPN','DISTINCT','CALCULATETABLE','EXCEPT','INTERSECT','UNION'):
                base=arguments[1] if function=='TOPN' and len(arguments)>1 else arguments[0] if arguments else ''
                columns.update(self.projected_columns.get(base,set()))
            for label in labels:
                if label.startswith('"') and label.endswith('"'):columns.add(label[1:-1].replace('""','"'))
            self.projected_columns[rendered]=columns
            return rendered,'table' if function in TABLE_FUNCTIONS else 'scalar'
        qualifier=None
        if kind in ('name','table'):
            name=value[1:-1].replace("''", "'") if kind=='table' else value
            if self.peek() and self.tokens[self.i][0]=='ref':
                qualifier=name;kind,member=self.take();value=value+member
            else:
                if kind=='name' and name.casefold() in self.variables:return name,'variable'
                table=self.tables.get(name.casefold())
                if table:self.references.add(table['id']);return (repr(table['id']) if self.identity else value),'table'
                if kind=='name' and name.upper() in ENUMS:return name.upper(),'scalar'
                raise ValueError('Unknown DAX table/variable')
        else:member=value
        if kind!='ref':raise ValueError('Unsupported DAX expression')
        name=member[1:-1].replace(']]',']').casefold()
        matches=[a for a in self.members if a['name'].casefold()==name and
                 (a['parent_id']==self.tables.get(qualifier.casefold(),{}).get('id') if qualifier else a['kind']=='Measure')]
        if len(matches)!=1:raise ValueError('Unknown or ambiguous DAX member')
        self.references.add(matches[0]['id']);return (repr(matches[0]['id']) if self.identity else value),'scalar'

    def parse(self):
        self.take('EVALUATE');expression,kind=self.expression()
        if self.peek() or kind not in ('table','variable'):raise ValueError('One table-valued EVALUATE required')
        if not self.references:raise ValueError('At least one discovered model reference required')
        self.output_columns=self.projected_columns.get(expression,set())
        return expression


def compile_query(query,assets,*,max_rows=limits.QUERY_ROWS):
    if type(max_rows) is not int or not 1<=max_rows<=limits.QUERY_ROWS:raise ValueError('Invalid row budget')
    parser=Parser(query,assets);expression=parser.parse()
    identity=Parser(query,assets,identity=True);bound=identity.parse()
    return {'query':'EVALUATE TOPN('+str(max_rows+1)+','+expression+')',
            'compiled_read':None if identity.volatile else bound,
            'result_columns':sorted(parser.output_columns),'asset_ids':sorted(parser.references),'max_rows':max_rows+1,'validator_version':VERSION,
            'limitation':'Native DAX evaluates the proposed context; hidden report selections/RLS and cross-system equivalence are not implied.'}
