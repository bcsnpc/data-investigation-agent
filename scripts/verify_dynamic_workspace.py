"""Browser-to-runtime acceptance for a discovered model and dynamic diagnostics.

Provider transports are injected. This does not replace live LLM/query acceptance.
"""
import argparse
import json
from pathlib import Path
import secrets
import subprocess
from threading import Thread
import time
from wsgiref.simple_server import make_server

from test_flexible_investigation import DynamicTests
from investigator.adaptive_runtime import AdaptiveRuntime
from investigator.workspace import Workspace
from investigator.workspace_api import create_app,WorkspaceServer
from serve_investigations import QuietHandler


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent-browser',required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();helper=DynamicTests();helper.setUp();turns=[]
    def planner(payload):
        turns.append(payload)
        if len(turns)==1:return helper.decision('LOOKUP',lookup={'operation':'search','value':'Entities'})
        if len(turns)==2:return helper.decision('QUERY',query={'tool':'bounded_dax','text':'EVALUATE ROW("Observed value",[Total])','max_rows':20})
        return helper.decision('STOP',stop_reason='ENOUGH_DIAGNOSTICS',assessment={
            'classification':'INSUFFICIENT_EVIDENCE','claim':'The report returned a value. An expected business value is still needed.',
            'evidence_ids':[o['id'] for o in payload['observations'] if o['tool']!='context'],
            'alternatives':['The report may match its current definition'],'limits':['Business intent is not confirmed']})
    policy={'environment':'test','daily_limits':{'planner_calls':20,'cloud_calls':20,'input_characters':500000,'output_tokens':30000},'max_inflight_planners':1,'no_progress_limit':3}
    agent=AdaptiveRuntime(helper.runtime,planner,usage_policy=policy)
    workspace=Workspace(agent,execution_enabled=True);key=secrets.token_urlsafe(40)
    server=make_server('127.0.0.1',0,create_app(workspace,key),server_class=WorkspaceServer,handler_class=QuietHandler)
    server.set_app(create_app(workspace,key,server.server_port))
    session='dynamic-verify-'+secrets.token_hex(4);args.output.parent.mkdir(parents=True,exist_ok=True)
    def browser(*command,script=None):
        path=args.output.parent/(session+'-'+secrets.token_hex(4)+'.json')
        with path.open('w',encoding='utf-8') as stdout,path.with_suffix('.stderr').open('w',encoding='utf-8') as stderr:
            result=subprocess.run([args.agent_browser,'--session',session,'--json',*command],input=script,stdout=stdout,stderr=stderr,text=True,encoding='utf-8',timeout=40)
        if result.returncode:raise RuntimeError('Browser command failed: '+command[0])
        result=json.loads(path.read_text(encoding='utf-8'))
        if not result['success']:raise RuntimeError('Browser operation failed')
        return result['data']
    def evaluate(script):return browser('eval','--stdin',script=script)['result']
    def wait(script):
        for _ in range(60):
            if evaluate(script):return
            time.sleep(.2)
        raise AssertionError('Expected browser state did not arrive')
    try:
        Thread(target=workspace.work,daemon=True).start();Thread(target=server.serve_forever,daemon=True).start()
        browser('open','http://127.0.0.1:'+str(server.server_port));browser('snapshot','-i')
        browser('fill','#access-key',key);browser('click','#login-form button')
        wait("!document.getElementById('workspace').hidden")
        browser('snapshot','-i');browser('fill','#symptom','The total seems low. Please investigate the current global value.')
        browser('click','#review');wait("!document.getElementById('preview').hidden")
        assert evaluate("document.getElementById('preview-note').textContent.includes('read-only checks')")
        browser('snapshot','-i');browser('click','#start')
        wait("document.getElementById('status').textContent==='Checks finished'")
        assert evaluate("document.getElementById('summary').textContent.includes('Suggested explanation')")
        assert evaluate("document.getElementById('facts').textContent.includes('12')")
        assert evaluate("document.getElementById('facts').textContent.includes('value')")
        assert evaluate("document.getElementById('activity').textContent.includes('Reading definitions')")
        browser('screenshot',str(args.output.with_suffix('.png').resolve()),'--full')
        browser('click','#technical-tab');browser('snapshot','-i')
        assert evaluate("document.getElementById('technical-decisions').textContent.includes('QUERY')")
        assert evaluate("document.getElementById('technical-outcome').textContent.includes('LLM_INFERRED')")
        before=len(helper.native_calls);browser('click','#refresh-history')
        assert len(helper.native_calls)==before==1
        errors=browser('errors');assert not errors.get('errors'),errors
        result={'status':'PASSED','checks':['discovered_catalog','global_scope_review','context_lookup','proposed_native_query',
            'numeric_fact','qualified_summary','activity','technical_receipts','history_no_requery','no_browser_errors'],
            'injected_native_calls':len(helper.native_calls),'live_cloud_calls':0}
        args.output.write_text(json.dumps(result,indent=2));print(json.dumps(result))
    finally:
        browser('close');workspace.stopping.set();server.shutdown();server.server_close();helper.doCleanups()


if __name__=='__main__':main()
