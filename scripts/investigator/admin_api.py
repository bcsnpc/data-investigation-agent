"""Loopback admin UI/API. Separate admin and catalog-reader credentials."""
import hmac
import json
from pathlib import Path
import sqlite3
from .onboarding import Conflict, fields
from .capabilities import evaluate, assess
from .diagnostic_evidence import receipts, read
from .filter_scope import catalog as scope_catalog
from .source_diagnostics import evidence as source_evidence
from .comparisons import register as register_mapping, mapping as read_mapping, assess as compare, read as read_comparison
from .runtime import read_run
from .aggregate_semantics import describe as describe_aggregate, dependency_shapes
from .proof_requirements import readiness as proof_readiness
from .tool_registry import TOOLS
from .adaptive_projection import read as read_adaptive

ASSETS = Path(__file__).resolve().parents[2] / 'apps' / 'model-admin'


def create_app(store, admin_token, reader_token, scans=None):
    for token in (admin_token, reader_token):
        if not isinstance(token, str) or len(token) < 32 or not token.isascii():
            raise ValueError('Tokens must have at least 32 ASCII characters')
    if hmac.compare_digest(admin_token, reader_token):
        raise ValueError('Use distinct admin and reader credentials')

    def app(env, start):
        def respond(status, value, mime='application/json; charset=utf-8'):
            raw = value if isinstance(value, bytes) else json.dumps(value).encode()
            start(status, [('Content-Type',mime),('Content-Length',str(len(raw))),
                          ('Cache-Control','no-store'),('X-Content-Type-Options','nosniff'),
                          ('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'; base-uri 'none'")])
            return [raw]
        path, method = env.get('PATH_INFO',''), env.get('REQUEST_METHOD','GET')
        assets = {'/':('index.html','text/html; charset=utf-8'),'/admin.js':('admin.js','text/javascript'),'/style.css':('style.css','text/css')}
        if path in assets and method == 'GET':
            name,mime = assets[path]
            return respond('200 OK',(ASSETS/name).read_bytes(),mime)
        token = env.get('HTTP_AUTHORIZATION','')
        is_admin = token.isascii() and hmac.compare_digest(token,'Bearer '+admin_token)
        is_reader = token.isascii() and hmac.compare_digest(token,'Bearer '+reader_token)
        if not (is_admin or is_reader):
            return respond('401 Unauthorized',{'error':'Authentication required'})
        if env.get('QUERY_STRING'):
            return respond('400 Bad Request',{'error':'Unexpected query'})
        try:
            if path == '/api/v2/reports' and method == 'GET':
                return respond('200 OK',{'reports':[{'model_id':m['id'],'name':m['name'],
                     'report_id':r,'context_id':m['context_id'],'readiness':m['readiness'],
                     'execution_available':False} for m in store.list(True) for r in m['reports']]})
            if not is_admin:
                return respond('403 Forbidden',{'error':'Admin role required'})
            if path=='/api/v2/admin/tools' and method=='GET':
                return respond('200 OK',{'tools':[{'name':name,'cloud_call_cost':int(spec['cloud'])} for name,spec in TOOLS.items()],
                                         'action_limit':20,'cloud_call_limit':10,'adaptive_planner_available':True,'execution_entrypoint':'operator_cli','proof_complete':False})
            if path=='/api/v2/admin/connection' and method=='GET':
                return respond('200 OK',{'configured':scans is not None,
                     'workspace':scans.workspace if scans else None,
                     'profile_hash':scans.profile_hash if scans else None,
                     'limitation':'Configured metadata access only; inspect scan receipts for connectivity results. Native queries remain unverified.'})
            if method not in ('GET','POST'):
                return respond('405 Method Not Allowed',{'error':'Method not allowed'})
            body = None
            if method == 'POST':
                size = int(env.get('CONTENT_LENGTH','0'))
                if not 0 < size <= 16384 or env.get('CONTENT_TYPE','').split(';')[0] != 'application/json':
                    raise ValueError('Expected bounded JSON request')
                body = json.loads(env['wsgi.input'].read(size))
            base = '/api/v2/admin/models'
            if path == base:
                result = store.list() if method == 'GET' else store.register(body,'local-admin')
                return respond('200 OK',result)
            if not path.startswith(base+'/'):
                return respond('404 Not Found',{'error':'Not found'})
            parts = path[len(base)+1:].split('/')
            identity = parts[0]
            if len(parts)==4 and parts[1]=='adaptive-sessions' and method=='GET':
                return respond('200 OK',read_adaptive(store,identity,parts[2],parts[3]))
            if len(parts)==2 and parts[1]=='proof-readiness' and method=='GET':
                return respond('200 OK',proof_readiness(store.get(identity)))
            if len(parts)==3 and parts[1]=='investigations' and method=='GET':
                return respond('200 OK',read_run(store,identity,parts[2]))
            if len(parts)==2 and parts[1]=='aggregate-semantics' and method=='GET':
                model=store.get(identity)
                return respond('200 OK',{'context_id':model['context_id'],'measures':[
                    describe_aggregate(model,m['id']) for m in model['context']['measures']] if model['context'] else []})
            if len(parts)==2 and parts[1]=='aggregate-semantics' and method=='POST':
                fields(body,['measure_id'])
                return respond('200 OK',dependency_shapes(store.get(identity),body['measure_id']))
            if len(parts)==2 and parts[1]=='comparison-mappings' and method=='POST':
                return respond('200 OK',register_mapping(store,identity,body,'local-admin'))
            if len(parts)==3 and parts[1]=='comparison-mappings' and method=='GET':
                return respond('200 OK',read_mapping(store,identity,parts[2]))
            if len(parts)==2 and parts[1]=='comparisons' and method=='POST':
                return respond('200 OK',compare(store,identity,body))
            if len(parts)==3 and parts[1]=='comparisons' and method=='GET':
                return respond('200 OK',read_comparison(store,identity,parts[2]))
            if len(parts)==2 and parts[1]=='source-diagnostics' and method=='GET':
                return respond('200 OK',source_evidence(store,identity))
            if len(parts)==3 and parts[1]=='source-diagnostics' and method=='GET':
                return respond('200 OK',source_evidence(store,identity,parts[2]))
            if len(parts)==2 and parts[1]=='scope' and method=='GET':
                return respond('200 OK',scope_catalog(store.get(identity)))
            if len(parts)==2 and parts[1]=='capabilities' and method=='GET':
                return respond('200 OK',evaluate(store.get(identity)))
            if len(parts)==2 and parts[1]=='assess' and method=='POST':
                return respond('200 OK',assess(store.get(identity),body))
            if len(parts)==2 and parts[1]=='diagnostics' and method=='GET':
                return respond('200 OK',receipts(store,identity))
            if len(parts)==3 and parts[1]=='diagnostics' and method=='GET':
                return respond('200 OK',read(store,identity,parts[2]))
            if len(parts)==2 and parts[1]=='scans' and scans is not None:
                if method=='GET':return respond('200 OK',scans.list(identity))
                fields(body,['revision','request_key'])
                return respond('200 OK',scans.request(identity,body['revision'],body['request_key'],'local-admin'))
            if len(parts)==1 and method=='GET':
                return respond('200 OK',store.get(identity))
            if len(parts)==3 and parts[1]=='contexts' and method=='GET':
                return respond('200 OK',store.context(identity,parts[2]))
            if len(parts)!=2 or method!='POST':
                return respond('404 Not Found',{'error':'Not found'})
            action=parts[1]
            if action=='import':
                fields(body,['revision','scan_id'])
                result=store.import_scan(identity,body['revision'],body['scan_id'],'local-admin')
            elif action=='review':
                fields(body,['revision','business'])
                result=store.review(identity,body['revision'],body['business'],'local-admin')
            elif action=='enable':
                fields(body,['revision','enabled'])
                result=store.enable(identity,body['revision'],body['enabled'],'local-admin')
            else:
                return respond('404 Not Found',{'error':'Not found'})
            return respond('200 OK',result)
        except Conflict as exc:
            return respond('409 Conflict',{'error':str(exc)})
        except KeyError:
            return respond('404 Not Found',{'error':'Not found'})
        except (ValueError,TypeError,OverflowError):
            return respond('400 Bad Request',{'error':'Invalid request or incomplete metadata; review inputs and retained scan'})
        except (sqlite3.Error,OSError):
            return respond('503 Service Unavailable',{'error':'Metadata storage unavailable'})
    return app
