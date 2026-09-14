"""Persist explicit planning requests; retries never repeat an uncertain paid call."""
from contextlib import closing
import json
import subprocess
from uuid import UUID
from metadata_config import ROOT


def launch(ticket_id, config_path):
    result = subprocess.run([str(ROOT / '.local/llm-env/Scripts/python.exe'),
        str(ROOT / 'scripts/run_azure_ticket_planner.py'), '--ticket-id', ticket_id,
        '--config', str(config_path)], capture_output=True, text=True, timeout=130)
    if result.returncode:
        raise ValueError('Planning failed')
    record = json.loads(result.stdout)
    if record.get('ticket_id') != ticket_id or record.get('status') not in ('NEEDS_INPUT','DRAFT_REQUIRES_REVIEW'):
        raise ValueError('Invalid planning response')
    return str(UUID(record['id']))


def request_plan(store, ticket_id, key, generate):
    key = str(UUID(key))
    with closing(store.connect()) as db:
        db.execute('CREATE TABLE IF NOT EXISTS planning_requests(ticket_id TEXT NOT NULL,request_key TEXT NOT NULL,status TEXT NOT NULL,plan_id TEXT,PRIMARY KEY(ticket_id,request_key))')
        db.commit();db.execute('BEGIN IMMEDIATE')
        old = db.execute('SELECT status,plan_id FROM planning_requests WHERE ticket_id=? AND request_key=?',(ticket_id,key)).fetchone()
        if old:
            return {'status':old[0],'plan_id':old[1],'replayed':True}
        db.execute('INSERT INTO planning_requests VALUES(?,?,?,NULL)',(ticket_id,key,'RUNNING'));db.commit()
    try:
        plan_id = generate(ticket_id)
        with closing(store.connect()) as db:
            row = db.execute('SELECT ticket_id FROM ticket_plans WHERE id=?',(plan_id,)).fetchone()
            if not row or row[0] != ticket_id:raise ValueError('Missing persisted plan')
        status = 'COMPLETED'
    except Exception:
        plan_id=None;status='FAILED'
    with closing(store.connect()) as db:
        db.execute('UPDATE planning_requests SET status=?,plan_id=? WHERE ticket_id=? AND request_key=?',
                   (status,plan_id,ticket_id,key));db.commit()
    return {'status':status,'plan_id':plan_id,'replayed':False}
