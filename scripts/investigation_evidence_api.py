"""Read-only WSGI API for retained investigation evidence; no query execution."""
from contextlib import closing
import hmac
import json
from pathlib import Path
import sqlite3
from urllib.parse import parse_qs
from uuid import UUID
from ticket_workflow import Conflict
from evidence_summary import summarize


class EvidenceStore:
    def __init__(self, database):
        self.uri=Path(database).resolve().as_uri()+'?mode=ro'

    def connect(self):
        connection=sqlite3.connect(self.uri,uri=True,timeout=5)
        connection.execute('PRAGMA query_only=ON')
        return connection

    @staticmethod
    def decode(row, detail=False):
        identity,lineage,created,request,result=row
        request,result=json.loads(request),json.loads(result)
        item={'id':identity,'lineage_run':lineage,'created_at':created,
              'kind':request.get('kind','deterministic_checks'),
              'classification':result.get('classification','UNRESOLVED')}
        if detail:
            item.update(request=request,result=result)
        return item

    def list(self, limit, offset):
        with closing(self.connect()) as db:
            rows=db.execute('SELECT id,lineage_run,created,request,result FROM investigation_runs '
                            'ORDER BY created DESC,id DESC LIMIT ? OFFSET ?',(limit+1,offset)).fetchall()
        return {'items':[self.decode(row) for row in rows[:limit]],
                'next_offset':offset+limit if len(rows)>limit else None}

    def get(self, identity):
        with closing(self.connect()) as db:
            row=db.execute('SELECT id,lineage_run,created,request,result FROM investigation_runs WHERE id=?',(identity,)).fetchone()
        return self.decode(row,True) if row else None


def create_app(database, token, workflow=None, lineage_run=None, reviews=None):
    if not isinstance(token,str) or len(token)<32 or not token.isascii():
        raise ValueError('API token must contain at least 32 ASCII characters')
    store=EvidenceStore(database)
    if workflow is not None:lineage_run=str(UUID(lineage_run))

    def application(environ,start_response):
        def respond(status, body):
            encoded=json.dumps(body,ensure_ascii=False).encode('utf-8')
            headers=[('Content-Type','application/json; charset=utf-8'),('Content-Length',str(len(encoded))),
                     ('Cache-Control','no-store'),('X-Content-Type-Options','nosniff')]
            if status.startswith('401'):headers.append(('WWW-Authenticate','Bearer'))
            if status.startswith('405'):
                allowed='POST' if reviews is not None and environ.get('PATH_INFO','').startswith('/api/plans/') and environ.get('PATH_INFO','').endswith('/approve') else 'GET'
                headers.append(('Allow',allowed))
            start_response(status,headers)
            return [encoded]

        supplied=environ.get('HTTP_AUTHORIZATION','')
        if not supplied.isascii() or not hmac.compare_digest(supplied,'Bearer '+token):
            return respond('401 Unauthorized',{'error':'UNAUTHORIZED'})
        method=environ.get('REQUEST_METHOD')
        review_route=reviews is not None and reviews.matches(environ.get('PATH_INFO',''))
        if method!='GET' and not (method=='POST' and (review_route or (workflow is not None and environ.get('PATH_INFO')=='/api/tickets'))):
            return respond('405 Method Not Allowed',{'error':'READ_ONLY_API'})
        path=environ.get('PATH_INFO','')
        query=environ.get('QUERY_STRING','')
        try:
            if review_route:return reviews.handle(environ,respond)
            if workflow is not None and path=='/api/tickets' and method=='POST':
                if query:return respond('400 Bad Request',{'error':'INVALID_REQUEST'})
                if environ.get('CONTENT_TYPE','').split(';')[0].strip()!='application/json':
                    return respond('415 Unsupported Media Type',{'error':'JSON_REQUIRED'})
                try:
                    length=int(environ.get('CONTENT_LENGTH','0'))
                    if not 1<=length<=16384:return respond('413 Payload Too Large',{'error':'INVALID_BODY_SIZE'})
                    raw=environ['wsgi.input'].read(length)
                    if len(raw)!=length:raise ValueError('Incomplete body')
                    body=json.loads(raw.decode('utf-8'))
                except (ValueError,UnicodeError):return respond('400 Bad Request',{'error':'INVALID_JSON'})
                identity,created=workflow.submit(body,environ.get('HTTP_IDEMPOTENCY_KEY',''),lineage_run)
                return respond('201 Created' if created else '200 OK',{'ticket_id':identity,'created':created,
                               'status_url':'/api/tickets/'+identity})
            if workflow is not None and path.startswith('/api/tickets/'):
                if query:raise ValueError('Unexpected query')
                raw=path[len('/api/tickets/'):];identity=str(UUID(raw))
                if identity!=raw:raise ValueError('Canonical ticket UUID required')
                item=workflow.get(identity)
                if item is None:return respond('404 Not Found',{'error':'TICKET_NOT_FOUND'})
                return respond('200 OK',{'ticket':item})
            if path=='/api/investigations':
                params=parse_qs(query,keep_blank_values=True,strict_parsing=True,max_num_fields=2)
                if set(params)-{'limit','offset'} or any(len(v)!=1 for v in params.values()):
                    raise ValueError('Invalid pagination')
                limit_text=params.get('limit',['20'])[0];offset_text=params.get('offset',['0'])[0]
                if not limit_text.isascii() or not limit_text.isdecimal() or not offset_text.isascii() or not offset_text.isdecimal():
                    raise ValueError('Invalid pagination')
                limit,offset=int(limit_text),int(offset_text)
                if not 1<=limit<=100 or not 0<=offset<=100000:raise ValueError('Pagination out of range')
                return respond('200 OK',store.list(limit,offset))
            prefix='/api/investigations/'
            if path.startswith(prefix):
                if query:raise ValueError('Unexpected query parameters')
                raw=path[len(prefix):]
                identity=str(UUID(raw))
                if identity!=raw:raise ValueError('Canonical run UUID required')
                item=store.get(identity)
                if item is None:return respond('404 Not Found',{'error':'INVESTIGATION_NOT_FOUND'})
                return respond('200 OK',{'investigation':item,
                    'summary':summarize(item),
                    'capabilities':{'read_saved_evidence':True,'execute_queries':False,'route_defects':False},
                    'evidence_scope':'Historical recorded observations; statuses are preserved, not recomputed or promoted to root cause'})
            return respond('404 Not Found',{'error':'NOT_FOUND'})
        except Conflict:
            return respond('409 Conflict',{'error':'IDEMPOTENCY_CONFLICT'})
        except (sqlite3.Error,json.JSONDecodeError,KeyError,TypeError,AttributeError,OSError):
            return respond('503 Service Unavailable',{'error':'EVIDENCE_STORE_UNAVAILABLE'})
        except ValueError:
            return respond('400 Bad Request',{'error':'INVALID_REQUEST'})
    return application
