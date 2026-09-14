"""Explicit local replay approval and one-attempt execution; no production dispatch."""
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
from uuid import uuid4
import duckdb
from defect_lab import fingerprints
from report_slicer_context import assess
from categorical_filter_replay import execute,SUPPORTED
from ticket_workflow import Conflict


def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()

class ReplayReview:
    def __init__(self,database):
        self.database=Path(database)
        self.database.parent.mkdir(parents=True,exist_ok=True)
        with closing(self.connect()) as db:
            db.execute('CREATE TABLE IF NOT EXISTS categorical_reviews(id TEXT PRIMARY KEY,scope TEXT,scope_hash TEXT,status TEXT,reviewer TEXT,result TEXT)');db.commit()
    def connect(self):return sqlite3.connect(self.database,timeout=10)
    def prepare(self,lab,definitions,page,selections):
        context=assess(definitions,page,selections)
        if context['status']!='CONTEXT_SUPPLIED' or any((s['table'],s['column']) not in SUPPORTED for s in context['slicers']):
            raise ValueError('Supported complete categorical scope required')
        lab=Path(lab).resolve()
        if not lab.is_file():raise ValueError('Existing lab required')
        with closing(duckdb.connect(str(lab),read_only=True)) as db:
            db.execute('BEGIN TRANSACTION');snapshot=fingerprints(db)
        scope={'mode':'isolated_categorical_replay','lab':str(lab),'definitions':definitions,'page':page,
               'selections':selections,'snapshot':snapshot}
        identity=str(uuid4());sha=digest(scope)
        with closing(self.connect()) as db:
            db.execute('INSERT INTO categorical_reviews VALUES(?,?,?,?,NULL,NULL)',(identity,json.dumps(scope),sha,'DRAFT_REQUIRES_REVIEW'));db.commit()
        return self.get(identity)
    def get(self,identity):
        with closing(self.connect()) as db:row=db.execute('SELECT scope,scope_hash,status,reviewer,result FROM categorical_reviews WHERE id=?',(identity,)).fetchone()
        if row is None:raise ValueError('Unknown replay review')
        scope=json.loads(row[0])
        if digest(scope)!=row[1]:raise Conflict('Stored replay scope changed')
        return {'id':identity,'scope':scope,'scope_hash':row[1],'status':row[2],'reviewer':row[3],'result':json.loads(row[4]) if row[4] else None}
    def approve(self,identity,expected_hash,reviewer):
        if not isinstance(reviewer,str) or not reviewer.strip() or len(reviewer)>100:raise ValueError('Reviewer required')
        record=self.get(identity)
        if record['scope_hash']!=expected_hash:raise Conflict('Reviewed scope differs')
        with closing(self.connect()) as db:
            db.execute('BEGIN IMMEDIATE')
            current=db.execute('SELECT scope,scope_hash,status FROM categorical_reviews WHERE id=?',(identity,)).fetchone()
            if current[1]!=expected_hash or json.loads(current[0])!=record['scope']:raise Conflict('Replay changed during approval')
            if current[2]=='APPROVED':return self.get(identity)
            if current[2]!='DRAFT_REQUIRES_REVIEW':raise Conflict('Replay is not awaiting approval')
            db.execute("UPDATE categorical_reviews SET status='APPROVED',reviewer=? WHERE id=?",(reviewer.strip(),identity));db.commit()
        return self.get(identity)
    def run(self,identity,expected_hash):
        record=self.get(identity)
        if record['scope_hash']!=expected_hash:raise Conflict('Approved hash differs')
        with closing(self.connect()) as db:
            db.execute('BEGIN IMMEDIATE')
            current=db.execute('SELECT scope,scope_hash,status,result FROM categorical_reviews WHERE id=?',(identity,)).fetchone()
            if current[1]!=expected_hash or json.loads(current[0])!=record['scope']:raise Conflict('Replay scope changed')
            if current[2]=='COMPLETED':return json.loads(current[3])
            if current[2]!='APPROVED':raise Conflict('Approved one-attempt replay required')
            db.execute("UPDATE categorical_reviews SET status='UNCERTAIN' WHERE id=?",(identity,));db.commit()
        scope=record['scope']
        # Snapshot validation occurs inside the same read transaction as capture.
        # Exceptions/crashes retain UNCERTAIN and are never retried automatically.
        result=execute(scope['lab'],scope['definitions'],scope['page'],scope['selections'],self.database,expected_fingerprints=scope['snapshot'])
        with closing(self.connect()) as db:
            db.execute("UPDATE categorical_reviews SET status='COMPLETED',result=? WHERE id=? AND status='UNCERTAIN'",(json.dumps(result),identity));db.commit()
        return result


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database',type=Path,required=True)
    sub=parser.add_subparsers(dest='action',required=True)
    prepare=sub.add_parser('prepare');prepare.add_argument('--lab',type=Path,required=True);prepare.add_argument('--definitions',type=Path,required=True);prepare.add_argument('--page',required=True);prepare.add_argument('--selections',type=Path,required=True)
    for action in ('show','approve','run'):
        command=sub.add_parser(action);command.add_argument('--id',required=True)
        if action!='show':command.add_argument('--hash',required=True)
        if action=='approve':command.add_argument('--reviewer',required=True)
    args=parser.parse_args();service=ReplayReview(args.database)
    if args.action=='prepare':result=service.prepare(args.lab,json.loads(args.definitions.read_text()),args.page,json.loads(args.selections.read_text()))
    elif args.action=='show':result=service.get(args.id)
    elif args.action=='approve':result=service.approve(args.id,args.hash,args.reviewer)
    else:result=service.run(args.id,args.hash)
    print(json.dumps(result,indent=2))
