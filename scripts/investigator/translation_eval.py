"""An authored SQLite fixture: no estate transport and no answer in model input."""
import copy,sqlite3
from contextlib import ExitStack
from . import translation_proposer as t
from .onboarding import digest
from .process_debugging import attest_surface
from .verification_budget import VerificationBudget

ROWS=((1,10,'2026-09-30'),(2,40,'2026-10-01'),(3,30,'2026-10-06'),(4,20,'2026-10-07'))


def request(case):
    cells=[]
    for key in ('1','2','3'):
        cell={'measure_id':'m','target_id':'v','mode':'KEYED','grouping_columns':['k'],
              'key_restrictions':[{'field_id':'k','operator':'IN','values':[key]}]}
        cell['id']=digest(cell);cells.append(cell)
    metadata=copy.deepcopy(case.get('metadata',{'objects':{'items':'TABLE'},
          'columns':{'items':{'k':'INTEGER','v':'INTEGER','day':'ISO_DATE_TEXT'}},
          'normalization':{'encoding':'typed-json-utf8','case_fold':False,'trim':False}}))
    return {'kind':case['kind'],'definition':copy.deepcopy(case['definition']),
        'definition_hash':t.seal(case['definition']),'target_engine':'sqlite','grouping':[],
        'relative':case['relative'],'evaluation_timestamp':'2026-10-06T20:00:00+00:00' if case['relative'] else None,
        'context':'authored-sqlite-v1','available_cells':cells,'precision':{'state':'EXACT'},
        'scope':{'restrictions':[]},'metadata':metadata}


def verify(case,proposal):
    """Native statements were authored independently before any proposal call.

    Separate SQLite connections expose the measure boundary. Filter comparisons
    intentionally use one connection; both sides read the real items table.
    """
    req=request(case);events=[]
    with ExitStack() as stack:
        databases={side:sqlite3.connect(':memory:') for side in ('NATIVE','PROPOSED')}
        objects={side:('items' if case['kind']=='FILTER' else side.casefold()+'_items') for side in databases}
        for side,db in databases.items():
            stack.callback(db.close)
            db.execute('create table '+objects[side]+'(k integer,v integer,day text)')
            db.executemany('insert into '+objects[side]+' values(?,?,?)',ROWS)
        if case['kind']=='FILTER':databases['PROPOSED']=databases['NATIVE']
        def compile(p,side,r,address):
            import sqlglot
            sql=case['native_sql'] if side=='NATIVE' else (
                'select k from items where '+p['expression'] if case['kind']=='FILTER'
                else 'select '+p['expression']+' from items')
            if side=='PROPOSED' and case['kind']=='MEASURE':
                try:full=sqlglot.parse(p['expression'],read='sqlite')
                except Exception:full=[]
                if len(full)==1 and isinstance(full[0],sqlglot.exp.Select):sql=p['expression']
            try:statements=sqlglot.parse(sql,read='sqlite')
            except Exception as exc:raise ValueError('Synthetic proposal does not parse') from exc
            if len(statements)!=1 or not isinstance(statements[0],sqlglot.exp.Select):
                raise ValueError('Only one synthetic SELECT is allowed')
            if len(statements[0].expressions)!=1:
                raise ValueError('Synthetic translation must project one quantity or key')
            if any(table.name!='items' or table.db or table.catalog for table in statements[0].find_all(sqlglot.exp.Table)):
                raise ValueError('Synthetic query object outside metadata')
            # Explicit fixture binding maps the logical items table onto two
            # genuinely distinct created objects; connection alone cannot earn
            # the engine's OBJECT_DISTINCT evidence grade.
            for table in statements[0].find_all(sqlglot.exp.Table):
                if not table.args.get('alias'):
                    table.set('alias',sqlglot.exp.TableAlias(this=sqlglot.exp.to_identifier('items')))
                table.set('this',sqlglot.exp.to_identifier(objects[side]))
            return {'query':statements[0].sql(dialect='sqlite'),'address':address,'object':objects[side]}
        def execute(side,plan):
            db=databases[side]
            # Defense in depth: generated local statements cannot mutate even
            # this disposable fixture or attach another file/database.
            allowed={sqlite3.SQLITE_SELECT,sqlite3.SQLITE_READ,sqlite3.SQLITE_FUNCTION,sqlite3.SQLITE_RECURSIVE}
            db.set_authorizer(lambda operation,*args:sqlite3.SQLITE_OK if operation in allowed else sqlite3.SQLITE_DENY)
            try:rows=db.execute(plan['query']).fetchall()
            except sqlite3.Error as exc:raise ValueError('Synthetic evaluation refused or failed') from exc
            surface={'engine':'sqlite','connection':'native' if case['kind']=='FILTER' else side.casefold(),
                     'object':plan['object'],'identity':'local-synthetic-reader'}
            receipt={'id':'synthetic-'+str(len(events)+1),'context_id':req['context'],
                     'read_address':plan['address'],'execution_surface':surface,'surface_report':surface,
                     'surface_report_binding':'VALUE_QUERY','surface_report_types':{'engine':'ENGINE_PRODUCT','object':'SYNTHETIC_TABLE','connection':'SYNTHETIC_CONNECTION'}}
            receipt['surface_report_receipt_id']=receipt['id']
            receipt['surface_attestation']=attest_surface(surface,surface,tuple(surface))
            observed={'status':'COMPLETED','evidence':receipt}
            if case['kind']=='FILTER':observed.update(keys=[list(row) for row in rows],complete=True,normalization=req['metadata']['normalization'])
            else:observed['quantity']={'state':'BLANK'} if rows[0][0] is None else {'state':'NUMBER','value':str(rows[0][0])}
            receipt['translation_result']=copy.deepcopy({k:observed[k] for k in ('quantity','keys','complete','normalization') if k in observed})
            events.append({'side':side,'statement':plan['query'],'receipt_id':receipt['id']})
            return observed
        budget_events=[]
        budget=VerificationBudget({'binding_verification':{'metadata_probes':0}},3,record=budget_events.append)
        result=t.verify(proposal,req,cells=req['available_cells'] if case['kind']=='MEASURE' else [None],
            compiler=compile,execute=execute,budget=budget,cross_boundary=case['kind']=='MEASURE')
        return {'verification':result,'local_probes':events,'verification_probe_count':budget.count,'budget_events':budget_events,
                'estate_physical_requests':0,'fixture_authored':True}


def score(golden,records,model_version):
    cases={c['id']:c for c in golden['cases']};indexed={}
    for r in records:
        if r['case_id'] not in cases or r['case_id'] in indexed or r['model_version']!=model_version:
            raise ValueError('Unknown, duplicate or mixed-version translation case')
        indexed[r['case_id']]=r
    verified=sum((r.get('evaluation') or {}).get('verification',{}).get('status')=='VERIFIED' for r in indexed.values())
    failures=sum(bool(r.get('provider_error')) for r in indexed.values())
    return {'step':'translation','model_version':model_version,'cases':len(cases),'evaluated':len(indexed),
        'suite_hash':digest(golden),'status':'COMPLETE' if len(indexed)==len(cases) else 'INCOMPLETE',
        'score':verified/len(cases),'first_proposal_verified':verified,'provider_failures':failures,
        'validation_failures':sum(bool(r.get('validation_error') or r.get('offline_validation_error')) for r in indexed.values()),
        'estate_physical_requests':0,'limits':['Authored local fixture; verification is bounded evidence, not global equivalence or aligned snapshots.']}
