import copy
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from investigator.investigator_harness import CaseLog, RunHarness, AzureCLIUser, RunStillActive
from investigator.process_tape import bytes_of
from investigator.shared_state import StateConflict
import test_ledger_investigator as fixtures


class HarnessTests(unittest.TestCase):
    def test_artifact_get_retries_body_reset_without_resubmitting_job(self):
        user=object.__new__(AzureCLIUser);user._token='fixture-token';user.control=Mock()
        first=Mock();first.__enter__=Mock(return_value=first);first.__exit__=Mock(return_value=False)
        first.read.side_effect=ConnectionResetError('fixture network reset')
        second=Mock();second.__enter__=Mock(return_value=second);second.__exit__=Mock(return_value=False)
        second.read.return_value=b'sealed bytes';second.status=200
        with patch('investigator.adapters.investigator_harness_user.urlopen',side_effect=[first,second])as opened,patch('investigator.adapters.investigator_harness_user.time.sleep')as sleep:
            self.assertEqual(user._fetch('https://fixture.invalid/result.json'),b'sealed bytes')
        self.assertEqual(opened.call_count,2);sleep.assert_called_once_with(30)
        self.assertEqual(user.control.call_args_list[0].args[0]['kind'],'PLATFORM_ARTIFACT_RETRY')
        self.assertNotIn('fixture-token',json.dumps(user.control.call_args_list[0].args[0]))

    def test_artifact_permission_refusal_is_not_retried(self):
        from urllib.error import HTTPError
        user=object.__new__(AzureCLIUser);user._token='fixture-token';user.control=Mock()
        with patch('investigator.adapters.investigator_harness_user.urlopen',side_effect=HTTPError('https://fixture.invalid',403,'Forbidden',{},None))as opened,patch('investigator.adapters.investigator_harness_user.time.sleep')as sleep:
            with self.assertRaises(HTTPError):user._fetch('https://fixture.invalid/result.json')
        self.assertEqual(opened.call_count,1);sleep.assert_not_called()

    def test_guided_structured_ticket_preserves_the_submitted_target(self):
        intake={'version':'IntakeRequest/1','report_id':'selected-report','description':'Question'}
        class User:
            def submit(self,ticket):return {'run_id':'one'}
            def poll(self,run):return {'status':'Succeeded'}
            def outcome(self,run,state):return {'ticket':copy.deepcopy(intake)}
        with tempfile.TemporaryDirectory()as tmp:
            user=User();ticket={'intake':copy.deepcopy(intake)}
            RunHarness(user,CaseLog(Path(tmp)/'good.jsonl'),admit=lambda _:None).run(ticket)
            intake['report_id']='other-report'
            with self.assertRaisesRegex(StateConflict,'DELIVERED_INTAKE_DIFFERS'):
                RunHarness(user,CaseLog(Path(tmp)/'bad.jsonl'),admit=lambda _:None).run(ticket)

    def test_legacy_request_envelope_binds_without_rewriting_the_output(self):
        result={'request':{'text':'Original question'},'revision':1,
            'ticket':{'version':'smart-ticket-v1','state':'HELD'}}
        class User:
            def submit(self,ticket):return {'run_id':'one'}
            def poll(self,run):return {'status':'Succeeded'}
            def outcome(self,run,state):return copy.deepcopy(result)
        with tempfile.TemporaryDirectory()as tmp:
            log=CaseLog(Path(tmp)/'case.jsonl')
            actual=RunHarness(User(),log,admit=lambda _:None).run({'text':'Original question'})
            self.assertEqual(actual,result)
            self.assertNotIn('text',actual['ticket'])
            result['request']['text']='Different question'
            with self.assertRaisesRegex(StateConflict,'TICKET_TEXT_DIFFERS'):
                RunHarness(User(),CaseLog(Path(tmp)/'other.jsonl'),admit=lambda _:None).run({'text':'Original question'})

    def test_fixture_ticket_submits_polls_and_receives_real_engine_case_log(self):
        calls = []; tools, engine, _, _ = fixtures.ToolLoopTests().build()
        def decide(payload, **kwargs):
            recitation = {key: payload['case_file'][key] for key in ('plan', 'current_step')}
            if not payload['case_file']['decisions']:
                return {'action': 'TOOL', 'summary': 'Compare admitted layers', 'hypotheses': ['failed job'],
                        'tool': 'compare_layers', 'arguments': {'key': 'record-1', 'layers': ['down', 'up'],
                        'filters': tools.context}, 'recitation': recitation}
            return {'action': 'VERDICT', 'verdict': 'failed job', 'summary': 'Report the linked failed load',
                    'hypotheses': ['failed job'], 'evidence_ids': list(tools.evidence._values), 'recitation': recitation}
        engine.decide = decide
        class User:
            def submit(self, ticket): calls.append('submit'); return {'run_id': 'one'}
            def poll(self, run):
                calls.append('poll')
                return {'status': 'Running' if calls.count('poll') == 1 else 'Succeeded'}
            def outcome(self, run, state):
                calls.append('outcome'); return engine.run({'visual': 'visual', 'text': 'Why is this lower?'})
        with tempfile.TemporaryDirectory() as tmp:
            log = CaseLog(Path(tmp)/'case.jsonl'); ticket = {'id': 'fixture-1', 'target': 'fixture-A', 'text':'Why is this lower?'}
            result = RunHarness(User(), log, admit=lambda _: None, sleep=lambda _: None).run(ticket)
            self.assertEqual(result['verdict'], 'failed job')
            self.assertEqual(result['case_file']['current_step'], 'deliver')
            self.assertEqual(calls, ['submit', 'poll', 'poll', 'outcome'])
            retained = CaseLog(log.path)
            self.assertEqual(retained.events[-1]['event'], 'OUTCOME')
            self.assertEqual(RunHarness(User(), retained, admit=lambda _: None).run(ticket), result)
            self.assertEqual(calls.count('submit'), 1)
            with self.assertRaises(StateConflict):
                RunHarness(User(), retained, admit=lambda _: None).run({'id': 'other'})

    def test_azure_adapter_submits_through_dia_cli_and_polls_the_returned_execution(self):
        import sys
        commands=[];user=AzureCLIUser.__new__(AzureCLIUser)
        user.runner=Path('fixture-runner.json');user.config={'checks':{'A':{'kind':'ledger-investigation'}}};user.baseline=False
        user.cli=['existing-az'];user.group='fixture-group';user.job='existing-job'
        def execute(command,**kwargs):
            commands.append(command)
            if 'dia.py' in command[1]:return SimpleNamespace(stdout=json.dumps({'status':'STARTED','run_id':'one','execution_name':'execution-one','image':'pinned'}))
            return SimpleNamespace(stdout=json.dumps({'properties':{'status':'Succeeded','startTime':'start','endTime':'end'}}))
        user.execute=execute
        run=user.submit({'target':'A'})
        self.assertEqual(commands[0][:1],[sys.executable]);self.assertEqual(commands[0][2:4],['run','A'])
        self.assertEqual(commands[0][-2:],['--runtime','azure'])
        self.assertEqual(user.poll(run)['status'],'Succeeded')
        self.assertIn('execution-one',commands[1])
        with self.assertRaises(ValueError):user.submit({'target':'not-declared'})
        self.assertEqual(len(commands),2)

    def test_wrong_ticket_echo_is_refused_and_logged_not_scored(self):
        class User:
            def submit(self,ticket):return {'run_id':'one'}
            def poll(self,run):return {'status':'Succeeded'}
            def outcome(self,run,state):return {'ticket':{'text':'A different question'},'verdict':'as designed'}
        with tempfile.TemporaryDirectory()as tmp:
            log=CaseLog(Path(tmp)/'case.jsonl')
            with self.assertRaisesRegex(StateConflict,'TICKET_TEXT_DIFFERS'):
                RunHarness(User(),log,admit=lambda _:None).run({'text':'The question actually submitted'})
            self.assertEqual(log.events[-1]['event'],'BLOCK')
            self.assertFalse(any(e['event']=='OUTCOME'for e in log.events))

    def test_new_submission_requires_fresh_capture_binding(self):
        from unittest.mock import patch
        with patch('investigator.unified_runner.load',return_value={'per_execution':False}):
            with self.assertRaisesRegex(ValueError,'FRESH_EXECUTION_BINDING'):
                AzureCLIUser('fixture.json')

    def test_uncertain_submission_never_silently_starts_a_second_execution(self):
        calls = []
        class User:
            def submit(self, ticket): calls.append('submit'); raise TimeoutError('control response unavailable')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'case.jsonl'; ticket = {'id': 'fixture'}
            with self.assertRaises(TimeoutError): RunHarness(User(), CaseLog(path), admit=lambda _: None).run(ticket)
            with self.assertRaises(RunStillActive): RunHarness(User(), CaseLog(path), admit=lambda _: None).run(ticket)
            self.assertEqual(calls, ['submit'])

    def test_sealed_outcome_not_azure_success_is_the_delivered_answer(self):
        result = {'status': 'blocked', 'verdict': 'not found', 'case_file': {'calls_blocked': ['retained']}}
        raw = bytes_of(result); key = 'one/00000010-result.json'
        manifest = {'version': 'dia-run-record-v1', 'run_id': 'one',
                    'records': [{'key': key, 'sha256': hashlib.sha256(raw).hexdigest()}]}
        manifest['seal'] = hashlib.sha256(bytes_of(manifest)).hexdigest()
        user = AzureCLIUser.__new__(AzureCLIUser)
        user.config = {'capture': {'account_url': 'https://fixture.blob.core.windows.net', 'prefix': 'runs'}}
        user.fetch = lambda url: bytes_of(manifest) if url.endswith('run-record.json') else raw
        answer = user.outcome({'run_id': 'one', 'image': 'pinned-image'}, {'status': 'Succeeded'})
        self.assertEqual(answer['result']['status'], 'blocked')
        corrupted = copy.deepcopy(manifest); corrupted['records'][0]['sha256'] = '0'*64
        user.fetch = lambda url: bytes_of(corrupted) if url.endswith('run-record.json') else raw
        with self.assertRaises(StateConflict): user.outcome({'run_id': 'one', 'image': 'pinned'}, {'status': 'Succeeded'})


if __name__ == '__main__':
    unittest.main()
