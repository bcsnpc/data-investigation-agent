"""Authenticated routing review; approval records a decision, never sends anything."""
from contextlib import closing
import json
import re
import time
from uuid import UUID
from routing_drafts import digest,prepare,save
from ticket_workflow import Conflict


class RoutingReview:
    def __init__(self,store,evidence,policy_loader):
        self.store=store;self.evidence=evidence;self.policy_loader=policy_loader
        with closing(store.connect()) as db:
            db.execute('CREATE TABLE IF NOT EXISTS routing_drafts(fingerprint TEXT PRIMARY KEY,id TEXT UNIQUE,record TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS routing_approvals(draft_id TEXT PRIMARY KEY,draft_hash TEXT,reviewer TEXT,created REAL)');db.commit()

    def matches(self,path):return bool(re.fullmatch(r'/api/(?:routing/[^/]+(?:/approve)?|investigations/[^/]+/routing)',path))

    def detail(self,identity):
        with closing(self.store.connect()) as db:
            row=db.execute('SELECT record FROM routing_drafts WHERE id=?',(identity,)).fetchone()
            approved=db.execute('SELECT draft_hash,reviewer,created FROM routing_approvals WHERE draft_id=?',(identity,)).fetchone()
        if not row:raise KeyError('Unknown routing draft')
        record=json.loads(row[0])
        return {'record':record,'draft_hash':digest(record),'approval':None if not approved else dict(zip(('draft_hash','reviewer','created'),approved)),'delivery_enabled':False}

    def approve(self,identity,expected_hash):
        detail=self.detail(identity);record=detail['record']
        if detail['draft_hash']!=expected_hash:raise Conflict('Draft changed')
        item=self.evidence.get(record['investigation_id'])
        if item is None:raise Conflict('Evidence missing')
        current=prepare(item,self.policy_loader())
        if current['status']!='DRAFT_REQUIRES_REVIEW' or dict(record,id=None)!=dict(current,id=None):raise Conflict('Evidence or ownership changed')
        with closing(self.store.connect()) as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT record FROM routing_drafts WHERE id=?',(identity,)).fetchone()
            if row is None or digest(json.loads(row[0]))!=expected_hash:raise Conflict('Draft changed')
            db.execute('INSERT OR IGNORE INTO routing_approvals VALUES(?,?,?,?)',(identity,expected_hash,'local-api-operator',time.time()));db.commit()
        return self.detail(identity)

    def handle(self,environ,respond):
        path=environ['PATH_INFO'].split('/');method=environ['REQUEST_METHOD']
        identity=str(UUID(path[3]))
        if identity!=path[3] or environ.get('QUERY_STRING'):raise ValueError('Invalid routing request')
        preparing=path[2]=='investigations';approving=path[-1]=='approve'
        expected='POST' if preparing or approving else 'GET'
        if method!=expected:return respond('405 Method Not Allowed',{'error':'METHOD_NOT_ALLOWED'})
        if method=='POST':
            if environ.get('CONTENT_TYPE','').split(';')[0]!='application/json':return respond('415 Unsupported Media Type',{'error':'JSON_REQUIRED'})
            size=int(environ.get('CONTENT_LENGTH','0'))
            if not 1<=size<=1024:return respond('413 Payload Too Large',{'error':'INVALID_BODY_SIZE'})
            raw=environ['wsgi.input'].read(size)
            if len(raw)!=size:raise ValueError('Incomplete request')
            body=json.loads(raw)
            fields={'confirm'} if preparing else {'confirm','draft_hash'}
            if not isinstance(body,dict) or set(body)!=fields or body['confirm'] is not True:raise ValueError('Explicit confirmation required')
        if preparing:
            item=self.evidence.get(identity)
            if item is None:return respond('404 Not Found',{'error':'INVESTIGATION_NOT_FOUND'})
            record=save(self.store,item,self.policy_loader());return respond('200 OK',self.detail(record['id']))
        try:return respond('200 OK',self.approve(identity,body['draft_hash']) if approving else self.detail(identity))
        except KeyError:return respond('404 Not Found',{'error':'DRAFT_NOT_FOUND'})
