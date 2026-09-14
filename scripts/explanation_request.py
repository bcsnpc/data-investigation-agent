"""At most one automatic explanation attempt per saved run; uncertain calls stay held."""
from contextlib import closing
import json
import subprocess
from uuid import UUID
from metadata_config import ROOT
from investigation_explanation import latest


def launch(run_id,config_path):
    result=subprocess.run([str(ROOT/'.local/llm-env/Scripts/python.exe'),
        str(ROOT/'scripts/run_azure_ticket_planner.py'),'--explain',run_id,
        '--config',str(config_path)],capture_output=True,text=True,timeout=130)
    if result.returncode:raise ValueError('Explanation failed')
    record=json.loads(result.stdout)
    if record.get('run_id')!=run_id or record.get('status')!='VALIDATED':raise ValueError('Invalid explanation response')
    return str(UUID(record['id']))


def request_explanation(store,evidence,run_id,generate):
    run_id=str(UUID(run_id));item=evidence.get(run_id)
    if item is None:raise ValueError('Unknown investigation')
    with closing(store.connect()) as db:
        db.execute('CREATE TABLE IF NOT EXISTS explanation_requests(run_id TEXT PRIMARY KEY,status TEXT NOT NULL,explanation_id TEXT)')
        db.commit();db.execute('BEGIN IMMEDIATE')
        old=db.execute('SELECT status,explanation_id FROM explanation_requests WHERE run_id=?',(run_id,)).fetchone()
        if old:return {'status':old[0],'explanation_id':old[1],'replayed':True}
        db.execute('INSERT INTO explanation_requests VALUES(?,?,NULL)',(run_id,'RUNNING'));db.commit()
    identity=None
    try:
        record=latest(store,item)
        if record is None:
            identity=generate(run_id)
            record=latest(store,item)
            if record is None or record['id']!=identity:raise ValueError('Missing validated explanation')
        identity=record['id'];status='COMPLETED'
    except Exception:
        identity=None;status='FAILED'
    with closing(store.connect()) as db:
        db.execute('UPDATE explanation_requests SET status=?,explanation_id=? WHERE run_id=?',(status,identity,run_id));db.commit()
    return {'status':status,'explanation_id':identity,'replayed':False}
