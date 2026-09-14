"""Local DuckDB lab using shared Gold SQL; no cloud clients or credentials."""
import argparse
from contextlib import closing
import hashlib
import importlib.util
import json
from pathlib import Path
import duckdb

ROOT=Path(__file__).resolve().parents[1]
SOURCE=('s_dim_product','s_fact_order','s_fact_order_line','s_fact_refund_line')
TABLES=SOURCE+('g_order_line_summary',)
SCENARIO='LAB-GOLD-OMIT-PARTIAL'


def query():
    spec=importlib.util.spec_from_file_location('lab_gold',ROOT/'infra/fabric/gold_models.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.QUERIES['order_line_summary']


def digest(value):return hashlib.sha256(value.encode()).hexdigest()


def fingerprints(db):
    result={}
    for table in TABLES:
        rows=db.execute('SELECT * FROM '+table+' ORDER BY ALL').fetchall()
        schema=db.execute('DESCRIBE '+table).fetchall()
        result[table]=digest(json.dumps({'rows':rows,'schema':schema},default=str,sort_keys=True))
    return result


def initialize(path):
    path=Path(path)
    if path.exists():raise ValueError('Lab already exists; initialize never overwrites')
    path.parent.mkdir(parents=True,exist_ok=True)
    # Operators use one process per lab; DuckDB provides its own writer locking.
    with closing(duckdb.connect(str(path))) as db:
        db.execute('BEGIN TRANSACTION')
        try:
            db.execute((ROOT/'infra/lab/baseline.sql').read_text())
            db.execute('CREATE TABLE g_order_line_summary AS '+query())
            db.execute('CREATE TABLE lab_control(baseline VARCHAR,query_hash VARCHAR)')
            db.execute('INSERT INTO lab_control VALUES (?,?)',[json.dumps(fingerprints(db)),digest(query())])
            db.execute('CREATE TABLE lab_events(sequence BIGINT,action VARCHAR,created TIMESTAMP DEFAULT current_timestamp)')
            db.execute("INSERT INTO lab_events(sequence,action) VALUES(1,'INITIALIZE')")
            db.execute('COMMIT')
        except Exception:db.execute('ROLLBACK');raise
    return validate(path)


def inspect(db):
    baseline,code_hash=db.execute('SELECT baseline,query_hash FROM lab_control').fetchone()
    expected=json.loads(baseline);actual=fingerprints(db)
    changed=[table for table in TABLES if actual[table]!=expected[table]]
    code_changed=code_hash!=digest(query())
    return {'status':'READY' if not changed and not code_changed else 'NOT_READY',
            'changed_tables':changed,'transformation_changed':code_changed}


def validate(path):
    with closing(duckdb.connect(str(path),read_only=True)) as db:return inspect(db)


def mutate(path,action):
    if action not in ('inject','reset'):raise ValueError('Unknown lab action')
    if not Path(path).is_file():raise ValueError('Initialize the lab first')
    with closing(duckdb.connect(str(path))) as db:
        db.execute('BEGIN TRANSACTION')
        try:
            state=inspect(db)
            if state['transformation_changed'] or any(t in SOURCE for t in state['changed_tables']):
                raise ValueError('Source or transformation drift; refusing to bless or reset it')
            if action=='inject':
                if state['status']!='READY':raise ValueError('Reset and validate before injecting')
                db.execute("DELETE FROM g_order_line_summary WHERE status='PARTIALLY_RETURNED'")
            else:
                db.execute('DELETE FROM g_order_line_summary')
                db.execute('INSERT INTO g_order_line_summary '+query())
                if inspect(db)['status']!='READY':raise ValueError('Reset did not reproduce baseline')
            db.execute('INSERT INTO lab_events(sequence,action) SELECT COALESCE(MAX(sequence),0)+1,? FROM lab_events',[action.upper()])
            db.execute('COMMIT')
        except Exception:db.execute('ROLLBACK');raise
    return validate(path)


def evidence(path):
    # Strict business-table projection: excludes lab control, events and evaluation answers.
    with closing(duckdb.connect(str(path),read_only=True)) as db:
        rows=db.execute('''WITH silver AS (SELECT o.order_id,o.currency,o.captured_amount-COALESCE(r.refunded,0) silver_net_cash FROM s_fact_order o
            LEFT JOIN (SELECT l.order_id,SUM(r.merchandise_amount+r.tax_amount) refunded
            FROM s_fact_refund_line r JOIN s_fact_order_line l USING(order_line_id) GROUP BY l.order_id) r USING(order_id)
            ) SELECT COALESCE(s.order_id,g.order_id),COALESCE(s.currency,g.currency),
            s.silver_net_cash,g.gold_net_cash,s.order_id IS NOT NULL,g.order_id IS NOT NULL
            FROM silver s FULL OUTER JOIN
            (SELECT order_id,currency,SUM(net_cash_amount) gold_net_cash FROM g_order_line_summary GROUP BY order_id,currency) g
            ON s.order_id=g.order_id AND s.currency=g.currency ORDER BY 1,2''').fetchall()
        return {'mode':'local_lab','rows':[dict(zip(('order_id','currency','silver_net_cash','gold_net_cash','silver_present','gold_present'),r)) for r in rows]}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('initialize','validate','inject','reset','evidence'))
    args=parser.parse_args();path=ROOT/'.local/defect-lab/lab.duckdb'
    result=initialize(path) if args.action=='initialize' else mutate(path,args.action) if args.action in ('inject','reset') else validate(path) if args.action=='validate' else evidence(path)
    print(json.dumps(result,default=str,indent=2))
