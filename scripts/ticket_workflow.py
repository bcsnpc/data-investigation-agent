"""Durable local ticket queue with idempotency, leases and an append-only timeline."""
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
import time
from uuid import UUID,uuid4


class Conflict(ValueError):pass


def validate_ticket(body):
    allowed={'title','report','description','metric','currency','order_id'}
    if not isinstance(body,dict) or set(body)-allowed:raise ValueError('Unsupported ticket fields')
    result={}
    for key,maximum in [('title',200),('report',200),('description',10000)]:
        value=body.get(key)
        if not isinstance(value,str) or not value.strip() or len(value)>maximum:raise ValueError('Required ticket field invalid')
        result[key]=value.strip()
    for key,maximum in [('metric',100),('currency',3),('order_id',20)]:
        value=body.get(key)
        if value is not None:
            if not isinstance(value,str) or not value.strip() or len(value)>maximum:raise ValueError('Optional ticket field invalid')
            result[key]=value.strip()
    return result


class TicketStore:
    def __init__(self,database):
        self.database=Path(database)
        self.database.parent.mkdir(parents=True,exist_ok=True)
        with closing(self.connect()) as db:
            db.executescript('''CREATE TABLE IF NOT EXISTS tickets(
              id TEXT PRIMARY KEY,idempotency_key TEXT UNIQUE NOT NULL,body_hash TEXT NOT NULL,
              body TEXT NOT NULL,lineage_run TEXT NOT NULL,status TEXT NOT NULL,created REAL NOT NULL,
              updated REAL NOT NULL,claim TEXT,lease_until REAL,run_id TEXT,outcome TEXT);
              CREATE TABLE IF NOT EXISTS ticket_events(
              sequence INTEGER PRIMARY KEY AUTOINCREMENT,ticket_id TEXT NOT NULL,at REAL NOT NULL,
              status TEXT NOT NULL,detail TEXT NOT NULL);''')
            db.commit()

    def connect(self):return sqlite3.connect(self.database,timeout=10)

    @staticmethod
    def event(db,identity,status,detail,now):
        db.execute('INSERT INTO ticket_events(ticket_id,at,status,detail) VALUES(?,?,?,?)',
                   (identity,now,status,json.dumps(detail)))

    def submit(self,body,key,lineage_run):
        body=validate_ticket(body);key=str(UUID(key));lineage_run=str(UUID(lineage_run))
        encoded=json.dumps(body,sort_keys=True);digest=hashlib.sha256(encoded.encode()).hexdigest()
        now=time.time()
        with closing(self.connect()) as db:
            db.execute('BEGIN IMMEDIATE')
            old=db.execute('SELECT id,body_hash FROM tickets WHERE idempotency_key=?',(key,)).fetchone()
            if old:
                if old[1]!=digest:raise Conflict('Idempotency key reused with different ticket')
                return old[0],False
            identity=str(uuid4())
            db.execute('INSERT INTO tickets(id,idempotency_key,body_hash,body,lineage_run,status,created,updated) VALUES(?,?,?,?,?,?,?,?)',
                       (identity,key,digest,encoded,lineage_run,'QUEUED',now,now))
            self.event(db,identity,'QUEUED',{'reason':'Ticket accepted'},now);db.commit()
            return identity,True

    def get(self,identity):
        identity=str(UUID(identity))
        with closing(self.connect()) as db:
            row=db.execute('SELECT id,body,lineage_run,status,created,updated,run_id,outcome FROM tickets WHERE id=?',(identity,)).fetchone()
            if not row:return None
            events=db.execute('SELECT sequence,at,status,detail FROM ticket_events WHERE ticket_id=? ORDER BY sequence',(identity,)).fetchall()
        return dict(id=row[0],ticket=json.loads(row[1]),lineage_run=row[2],status=row[3],created_at=row[4],updated_at=row[5],
                    investigation_run_id=row[6],outcome=json.loads(row[7]) if row[7] else None,
                    timeline=[dict(sequence=e[0],at=e[1],status=e[2],detail=json.loads(e[3])) for e in events])

    def claim(self,now=None,approved_only=False):
        now=time.time() if now is None else now
        with closing(self.connect()) as db:
            db.execute('BEGIN IMMEDIATE')
            if approved_only:
                if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='plan_approvals'").fetchone():return None
                # Ambiguous expired runs require operator recovery, never automatic replay.
                row=db.execute("SELECT id,body,lineage_run,status FROM tickets WHERE status='QUEUED' AND EXISTS (SELECT 1 FROM plan_approvals WHERE child_ticket_id=tickets.id) ORDER BY created,id LIMIT 1").fetchone()
            else:
                row=db.execute("SELECT id,body,lineage_run,status FROM tickets WHERE status='QUEUED' OR (status='RUNNING' AND lease_until<?) ORDER BY created,id LIMIT 1",(now,)).fetchone()
            if not row:return None
            claim=str(uuid4())
            db.execute("UPDATE tickets SET status='RUNNING',claim=?,lease_until=?,updated=? WHERE id=?",(claim,now+1800,now,row[0]))
            self.event(db,row[0],'RUNNING',{'reason':'Recovered expired lease' if row[3]=='RUNNING' else 'Worker claimed ticket'},now);db.commit()
            return dict(id=row[0],body=json.loads(row[1]),lineage_run=row[2],claim=claim)

    def finish(self,job,status,outcome,run_id=None):
        if status not in ('COMPLETED','NEEDS_INPUT','FAILED'):raise ValueError('Invalid terminal status')
        now=time.time()
        with closing(self.connect()) as db:
            db.execute('BEGIN IMMEDIATE')
            changed=db.execute("UPDATE tickets SET status=?,outcome=?,run_id=?,updated=?,claim=NULL,lease_until=NULL WHERE id=? AND status='RUNNING' AND claim=? AND lease_until>=?",
                               (status,json.dumps(outcome),run_id,now,job['id'],job['claim'],now)).rowcount
            if changed!=1:raise Conflict('Worker claim no longer current')
            self.event(db,job['id'],status,outcome,now);db.commit()
