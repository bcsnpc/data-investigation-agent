"""Registered Gold reference and observed semantic publication alignment."""
from contextlib import closing
import hashlib
import json
import sqlite3
from uuid import UUID
from source_snapshot import canonical
from gold_snapshot_input import build_gold
from gold_publication import validate
from build_powerbi_model import TABLES


def registered_gold(database, estate):
    run=str(UUID(estate['snapshot_gold']['run_id']))
    silver=build_gold(database,estate)
    with closing(sqlite3.connect(database)) as db:
        row=db.execute('SELECT proof_sha256,proof FROM gold_snapshot_publications WHERE run_id=?',(run,)).fetchone()
    if not row:raise ValueError('Registered Gold publication required')
    proof=json.loads(row[1])
    if hashlib.sha256(canonical(proof).encode()).hexdigest()!=row[0]:raise ValueError('Gold proof hash differs')
    root=f"abfss://{estate['workspace_id']}@onelake.dfs.fabric.microsoft.com/{estate['gold_lakehouse_id']}"
    result=validate(silver,proof['report'],root)
    if result!=proof['result'] or result['gold_run_id']!=run or proof['job']['status']!='Completed':
        raise ValueError('Gold publication evidence differs')
    return {'gold_proof_sha256':row[0],'report':proof['report']}


def alignment_query():
    fields=[]
    for table in TABLES:
        fields.extend([f'"{table}:run",CONCATENATEX(DISTINCT({table}[_gold_run_id]),{table}[_gold_run_id],",")',
                       f'"{table}:rows",COUNTROWS({table})',
                       f'"{table}:nulls",COUNTROWS(FILTER({table},ISBLANK({table}[_gold_run_id])))'])
    return 'EVALUATE ROW('+','.join(fields)+')'


def validate_alignment(gold,row):
    for table,source in TABLES.items():
        if row.get(f'[{table}:run]')!=gold['run_id']:
            raise ValueError('Semantic run differs: '+table)
        count=row.get(f'[{table}:rows]')
        if type(count) is not int or count!=gold['counts'][source]:
            raise ValueError('Semantic count differs: '+table)
        if row.get(f'[{table}:nulls]') not in (None,0):
            raise ValueError('Missing semantic run marker: '+table)
        if f'[{table}:nulls]' not in row:raise ValueError('Missing null-count evidence')
    return {'status':'SEMANTIC_RUN_ALIGNED','gold_run_id':gold['run_id'],
            'snapshot_comparable':False,
            'scope':'Observed model run markers and counts; DAX does not prove engine Delta version selection'}
