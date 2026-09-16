"""Browser/API/runtime verification with injected data; no cloud calls.

Requires agent-browser installed with its browser. This is a UI integration
test, not hidden-measure or live causal acceptance.
"""
import argparse
import json
from pathlib import Path
import secrets
import subprocess
from threading import Thread
import time
from wsgiref.simple_server import make_server

from investigator.workspace_api import create_app, WorkspaceServer
from serve_investigations import QuietHandler
from test_investigator_workspace import WorkspaceTests
from test_adaptive_investigation import decision


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent-browser', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    helper = WorkspaceTests(); helper.setUp()
    helper.clock.side_effect = time.time
    helper.workspace.clock = time.time
    original = helper.planner.side_effect
    def planner(payload):
        time.sleep(.3)
        if payload['symptom'].startswith('Please clarify') and 'Clarification:' not in payload['symptom']:
            return decision(question='Which period should be checked?'), {}
        return original(payload)
    helper.planner.side_effect = planner
    key = secrets.token_urlsafe(40)
    server = make_server('127.0.0.1', 0, create_app(helper.workspace, key), server_class=WorkspaceServer, handler_class=QuietHandler)
    server.set_app(create_app(helper.workspace, key, server.server_port))
    browser_session = 'workspace-verify-' + secrets.token_hex(4)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    command_log = args.output.parent / (browser_session + '-commands')
    command_log.mkdir()
    def browser(*command, script=None):
        # A Windows daemon may inherit stdout/stderr handles. File-backed output
        # avoids waiting for pipe EOF from a daemon that deliberately stays alive.
        out = command_log / (secrets.token_hex(6) + '.json')
        err = out.with_suffix('.stderr')
        with out.open('w', encoding='utf-8') as stdout, err.open('w', encoding='utf-8') as stderr:
            result = subprocess.run([args.agent_browser, '--session', browser_session, '--json', *command],
                input=script, stdout=stdout, stderr=stderr, text=True, encoding='utf-8', timeout=40)
        if result.returncode:
            raise RuntimeError('Browser command failed: ' + command[0])
        data = json.loads(out.read_text(encoding='utf-8'))
        if not data['success']:
            raise RuntimeError('Browser operation failed: ' + command[0])
        return data['data']
    def evaluate(script): return browser('eval', '--stdin', script=script)['result']
    def wait(script):
        for _ in range(45):
            if evaluate(script): return
            time.sleep(.25)
        raise AssertionError('Browser state did not arrive: ' + script)
    def fill(selector, value): browser('fill', selector, value)
    def click(selector):
        names = {'#new-investigation': '+ New investigation', '#add-filter': '+ Add filter', '#review': 'Review scope',
                 '#start': 'Start investigation', '#login-form button': 'Open workspace', '#technical-tab': 'Technical evidence',
                 '#business-tab': 'Overview', '#refresh-history': 'Refresh investigations', '#clarify': 'Clarify and review a new scope',
                 '#cancel': 'Cancel investigation', '#signout': 'Sign out'}
        snapshot = browser('snapshot', '-i')
        if selector in names:
            matches = [key for key, value in snapshot['refs'].items() if value['name'].strip() == names[selector] and value['role'] in ('button', 'tab')]
            if len(matches) != 1:
                raise AssertionError('Ambiguous control: ' + selector)
            browser('click', '@' + matches[0])
        else:
            browser('click', selector)
        time.sleep(.15)
    def begin(symptom):
        click('#new-investigation'); browser('snapshot', '-i')
        fill('#symptom', symptom); click('#add-filter'); fill('#filters textarea', 'USD'); click('#review')
        wait("!document.getElementById('preview').hidden")
        browser('snapshot', '-i'); click('#start')
        wait("!document.getElementById('result').hidden")
    worker = Thread(target=helper.workspace.work, daemon=True)
    web = Thread(target=server.serve_forever, daemon=True)
    try:
        worker.start(); web.start()
        browser('open', f'http://127.0.0.1:{server.server_port}')
        browser('snapshot', '-i')
        assert evaluate("document.body.innerText.includes('Follow the numbers.')")
        browser('screenshot', str(args.output.with_suffix('.login.png').resolve()))
        assert browser('errors').get('errors', []) == []
        fill('#access-key', key); click('#login-form button')
        wait("!document.getElementById('workspace').hidden")
        browser('snapshot', '-i')
        # Explicit scope choice: no silent all-records default.
        fill('#symptom', 'A value looks different.'); click('#review')
        wait("!document.getElementById('error').hidden")
        assert helper.planner.call_count == 0
        begin('The reported number looks lower than expected.')
        wait("document.getElementById('status').textContent==='Checks finished'")
        browser('snapshot', '-i')
        assert evaluate("document.querySelector('.fact .value').textContent==='7'")
        assert evaluate("document.getElementById('business').dataset.outcomeHash===document.getElementById('technical').dataset.outcomeHash")
        first_calls = helper.native.call_count
        click('#technical-tab'); browser('snapshot', '-i')
        assert evaluate("!document.getElementById('technical').hidden && document.getElementById('technical-outcome').textContent.includes('false')")
        click('#business-tab'); click('#refresh-history'); click('#history button'); browser('snapshot', '-i')
        assert helper.native.call_count == first_calls
        browser('screenshot', str(args.output.with_suffix('.overview.png').resolve()), '--full')
        begin('Please clarify this number.')
        wait("document.getElementById('status').textContent==='Needs your input'")
        browser('snapshot', '-i'); click('#clarify')
        fill('#symptom', 'Please clarify this number. Clarification: use the selected USD records.')
        click('#review'); wait("!document.getElementById('preview').hidden"); click('#start')
        wait("document.getElementById('status').textContent==='Checks finished'")
        assert helper.workspace.sessions()['sessions'][0]['id'] is not None
        # Hold the planner briefly so a real cancel click races with execution.
        helper.planner.side_effect = lambda payload: (time.sleep(3) or decision(), {})
        begin('Cancel this check.')
        click('#cancel'); wait("document.getElementById('status').textContent==='Cancelled'")
        browser('snapshot', '-i')
        # Mobile layout must stay inside the viewport.
        browser('set', 'viewport', '390', '844')
        assert evaluate('document.documentElement.scrollWidth<=window.innerWidth')
        browser('screenshot', str(args.output.with_suffix('.mobile.png').resolve()), '--full')
        click('#signout'); wait("!document.getElementById('login').hidden")
        assert evaluate("document.getElementById('access-key').value==='' && localStorage.length===0 && sessionStorage.length===0")
        assert browser('errors').get('errors', []) == []
        # New metadata, same UI/runtime: review measure-local filters before start
        # and distinguish a repeated child by its calculation path after capture.
        from test_dependency_context import fixture as context_fixture
        helper.model.clear(); helper.model.update(context_fixture()); helper.config['fabric']['workspace_id']='workspace'
        def contextual_planner(payload):
            choices=[c for c in payload['candidates'] if c['dimension_id'] is None]
            if len(payload['observations'])>=3:return decision(),{}
            chosen=next((c for c in choices if c.get('dependency_context')),None)
            chosen=chosen or next((c for c in choices if c['measure_id']=='Replaced'),choices[0])
            return decision(chosen['id']),{}
        helper.planner.side_effect=contextual_planner
        fill('#access-key',key);click('#login-form button');wait("!document.getElementById('workspace').hidden")
        click('#new-investigation');browser('select','#metric','Combined')
        fill('#symptom','Why do the component totals differ?');click('#add-filter');fill('#filters textarea','false');click('#review')
        wait("!document.getElementById('preview').hidden")
        assert evaluate("document.getElementById('preview-contexts').textContent.includes('replaces existing filter') && document.getElementById('preview-contexts').textContent.includes('intersects existing filter')")
        browser('screenshot',str(args.output.with_suffix('.context-review.png').resolve()),'--full')
        click('#start');wait("document.getElementById('status').textContent==='Checks finished'")
        assert evaluate("document.getElementById('facts').textContent.includes('Calculation path: Combined → Replaced → Base')")
        assert evaluate("document.getElementById('business').dataset.outcomeHash===document.getElementById('technical').dataset.outcomeHash")
        assert evaluate('document.documentElement.scrollWidth<=window.innerWidth')
        browser('screenshot',str(args.output.with_suffix('.context-results.png').resolve()),'--full')
        assert browser('errors').get('errors',[])==[]
        click('#signout')
        # Business text -> clarification -> scope review -> same adaptive runtime.
        from investigator.question_intake import Intake
        from test_question_intake import ask
        from unittest.mock import MagicMock
        def resolve_question(payload):
            if 'Clarification:' not in payload['text']: return ask(), {}
            return {'action':'PROPOSE','model_id':helper.model['id'],'measure_id':'Combined',
                    'metric_quote':'Combined','question':None,'filters':[{'column_id':'f','operator':'in','values':[False]}],
                    'dimension_ids':[],'scope_quotes':[{'column_id':'f','quote':'Flag false'}]}, {}
        resolver=MagicMock(side_effect=resolve_question)
        helper.workspace.intake=Intake(helper.workspace,resolver)
        fill('#access-key',key);click('#login-form button');wait("!document.getElementById('workspace').hidden")
        before=helper.native.call_count
        fill('#business-question','This report seems off.');click('#resolve-question')
        wait("document.getElementById('intake-status').textContent.includes('Which metric')")
        assert helper.native.call_count==before
        click('#refresh-history');click('#question-history button')
        assert resolver.call_count==1
        fill('#business-question','Combined metric for Flag false.');click('#resolve-question')
        wait("document.getElementById('intake-status').textContent.includes('Metric and filters suggested')")
        assert evaluate("document.getElementById('metric').value==='Combined' && document.querySelector('#filters textarea').value==='false'")
        assert helper.native.call_count==before
        click('#review');wait("!document.getElementById('preview').hidden")
        browser('screenshot',str(args.output.with_suffix('.question-review.png').resolve()),'--full')
        click('#start');wait("document.getElementById('status').textContent==='Checks finished'")
        click('#technical-tab')
        assert evaluate("document.getElementById('technical-scope').textContent.includes('SAVED_LLM_SCOPE_PROPOSAL')")
        click('#business-tab');browser('screenshot',str(args.output.with_suffix('.question-results.png').resolve()),'--full')
        calls=helper.native.call_count;click('#refresh-history');click('#question-history button')
        assert resolver.call_count==2 and helper.native.call_count==calls
        fill('#symptom','Manually corrected question about Combined for Flag false.')
        click('#review');wait("!document.getElementById('preview').hidden")
        assert evaluate("preview.intake===null")
        assert evaluate('document.documentElement.scrollWidth<=window.innerWidth')
        assert browser('errors').get('errors',[])==[]
        click('#signout');assert evaluate("document.getElementById('question-history').children.length===0")
        result = {'status': 'PASSED', 'checks': ['login', 'explicit_scope', 'preview_start', 'saved_numeric_values',
            'shared_outcome', 'technical_view', 'history_no_requery', 'clarification_successor', 'cancellation', 'mobile_layout', 'signout', 'no_console_errors',
            'context_preview','context_result_labels','question_clarification','question_scope_review','question_runtime_provenance','question_history_no_calls','manual_scope_provenance'],
            'injected_native_calls': helper.native.call_count, 'live_cloud_calls': 0,
            'causal_acceptance': False}
        args.output.write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result))
    except Exception:
        browser('screenshot', str(args.output.with_suffix('.failure.png').resolve()), '--full')
        args.output.with_suffix('.failure.json').write_text(json.dumps({
            'page': evaluate('document.body.innerText'), 'errors': browser('errors'),
            'overflow': evaluate("Array.from(document.querySelectorAll('body *')).filter(e=>e.getBoundingClientRect().right>innerWidth+1).map(e=>({tag:e.tagName,id:e.id,width:e.getBoundingClientRect().width,right:e.getBoundingClientRect().right})).slice(0,15)"),
            'snapshot': browser('snapshot', '-i')}, indent=2), encoding='utf-8')
        raise
    finally:
        helper.workspace.stopping.set()
        server.shutdown(); server.server_close(); worker.join(10)
        try: browser('close')
        finally: helper.doCleanups()


if __name__ == '__main__': main()
