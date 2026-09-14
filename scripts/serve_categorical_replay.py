"""Authenticated loopback UI for reviewed local categorical replay."""
import argparse
from contextlib import closing
import hmac
import json
import os
from pathlib import Path
from uuid import UUID
from wsgiref.simple_server import make_server
from approved_categorical_replay import ReplayReview,digest
from report_slicer_context import assess
from categorical_filter_replay import SUPPORTED
from defect_lab import ROOT
from ticket_workflow import Conflict
from serve_investigations import QuietHandler


def create_app(database,lab,definitions,page,token):
    if not isinstance(token,str) or len(token)<32 or not token.isascii():raise ValueError('Operator token required')
    definitions=json.loads(json.dumps(definitions))
    context=assess(definitions,page)
    if context['unsupported'] or not context['slicers'] or any((s['table'],s['column']) not in SUPPORTED for s in context['slicers']):raise ValueError('Supported local slicer page required')
    lab=str(Path(lab).resolve());service=ReplayReview(database)
    binding={'lab':lab,'definitions':definitions['bundle_hash'],'page':page}
    with closing(service.connect()) as db:
        db.execute('CREATE TABLE IF NOT EXISTS replay_server_binding(id INTEGER PRIMARY KEY CHECK(id=1),binding TEXT)')
        db.execute('INSERT OR IGNORE INTO replay_server_binding VALUES(1,?)',(digest(binding),))
        if db.execute('SELECT binding FROM replay_server_binding WHERE id=1').fetchone()[0]!=digest(binding):raise ValueError('Replay database belongs to another server scope')
        db.commit()
    fields=[{'id':s['visual_id'],'label':s['table']+' / '+s['column']} for s in context['slicers']]
    def detail(identity):
        record=service.get(identity);scope=record['scope']
        if scope['lab']!=lab or scope['page']!=page or scope['definitions']['bundle_hash']!=binding['definitions']:raise Conflict('Review belongs to another scope')
        return {'id':identity,'scope_hash':record['scope_hash'],'status':record['status'],'selections':scope['selections'],'result':record['result']}
    def app(environ,start_response):
        def respond(status,value,mime='application/json'):
            body=json.dumps(value).encode() if mime=='application/json' else value
            start_response(status,[('Content-Type',mime),('Content-Length',str(len(body))),('Cache-Control','no-store'),('X-Content-Type-Options','nosniff'),('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'")]);return [body]
        path=environ.get('PATH_INFO','');method=environ.get('REQUEST_METHOD','GET')
        if method=='GET' and path in ('/','/replay.js','/review.css'):
            target=ROOT/'apps/categorical-replay'/('index.html' if path=='/' else 'replay.js')
            if path=='/review.css':target=ROOT/'apps/investigation-review/review.css'
            return respond('200 OK',target.read_bytes(),'text/html; charset=utf-8' if path=='/' else 'text/css' if path.endswith('css') else 'text/javascript')
        if not hmac.compare_digest(environ.get('HTTP_AUTHORIZATION',''),'Bearer '+token):return respond('401 Unauthorized',{'error':'UNAUTHORIZED'})
        try:
            if environ.get('QUERY_STRING'):raise ValueError('Unexpected query')
            if path=='/api/context' and method=='GET':return respond('200 OK',{'report':definitions['report'].get('name','Retained report'),'fields':fields})
            if method=='POST':
                length=int(environ.get('CONTENT_LENGTH','0'))
                if not 1<=length<=20000 or environ.get('CONTENT_TYPE','').split(';')[0]!='application/json':raise ValueError('Invalid body')
                body=json.loads(environ['wsgi.input'].read(length))
                if not isinstance(body,dict):raise ValueError('Object required')
                if path=='/api/reviews':
                    if set(body)!={'selections'}:raise ValueError('Selections required')
                    r=service.prepare(lab,definitions,page,body['selections']);return respond('201 Created',detail(r['id']))
            parts=path.strip('/').split('/')
            if len(parts) not in (3,4) or parts[:2]!=['api','reviews']:return respond('404 Not Found',{'error':'NOT_FOUND'})
            identity=str(UUID(parts[2]));record=detail(identity)
            if method=='GET' and len(parts)==3:return respond('200 OK',record)
            if method!='POST' or len(parts)!=4:return respond('405 Method Not Allowed',{'error':'METHOD_NOT_ALLOWED'})
            if set(body)!={'confirm','scope_hash'} or body['confirm'] is not True:raise ValueError('Explicit confirmation required')
            if parts[3]=='approve':service.approve(identity,body['scope_hash'],'local-api-operator')
            elif parts[3]=='run':service.run(identity,body['scope_hash'])
            else:return respond('404 Not Found',{'error':'NOT_FOUND'})
            return respond('200 OK',detail(identity))
        except Conflict:return respond('409 Conflict',{'error':'REVIEW_CONFLICT'})
        except (ValueError,KeyError,TypeError):return respond('400 Bad Request',{'error':'INVALID_OR_CHANGED_SCOPE'})
        except Exception:return respond('500 Internal Server Error',{'error':'REPLAY_FAILED_CHECK_SAVED_STATUS'})
    return app


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('database','lab','definitions'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--page',required=True);parser.add_argument('--port',type=int,default=8782);args=parser.parse_args()
    if not 1<=args.port<=65535:parser.error('Invalid port')
    app=create_app(args.database,args.lab,json.loads(args.definitions.read_text()),args.page,os.environ.get('INVESTIGATOR_API_TOKEN',''))
    with make_server('127.0.0.1',args.port,app,handler_class=QuietHandler) as server:
        print('Local categorical review ready',flush=True);server.serve_forever()
