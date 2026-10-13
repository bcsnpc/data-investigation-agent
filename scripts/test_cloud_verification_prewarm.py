import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

from cloud_binding_verifier import prewarm_source,plan
from investigator.process_tape import Tape,active
from test_process_tape import bootstrap
from test_serverless_source_controls import CONFIG,ASSET,FAILED
from test_cloud_binding_verifier import VerificationPlanTests


class PrewarmVerificationTests(unittest.TestCase):
    def spec(self):
        spec=VerificationPlanTests().spec();spec['prewarm']={'asset_ids':[ASSET]};return spec

    def run_control(self,spec,config,execute,governor=None):
        governor=governor or Mock()
        governor.metered_read.side_effect=lambda session,key,call:call()
        record={};sleep=Mock()
        prewarm_source(spec,config,{'source':{'asset_id':ASSET}},governor,
            {'session_id':'verification','deadline':99999999999},record,execute=execute,sleep=sleep)
        return record,governor,sleep

    def test_control_request_wait_and_result_replay_without_sleep_or_probe_budget(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'tape.json';tape=Tape(path,bootstrap())
            with active(tape):
                record,governor,sleep=self.run_control(self.spec(),CONFIG,Mock(side_effect=[FAILED,{'status':'CONNECTED'}]))
            tape.finish(record)
            self.assertEqual(sleep.call_count,1)
            self.assertEqual(governor.metered_read.call_count,2)
            self.assertTrue(all(c.args[0]=='verification:prewarm-controls' for c in governor.metered_read.call_args_list))
            self.assertTrue(all(e['class']=='CONTROL'for e in record['control_events']))
            self.assertEqual(sum(e['kind']=='SERVERLESS_RESUME_WAIT'for e in record['control_events']),2)
            replay=Tape(path)
            with active(replay):
                repeated,_,no_sleep=self.run_control(self.spec(),CONFIG,Mock(side_effect=[FAILED,{'status':'CONNECTED'}]))
                replay.finish(repeated)
            no_sleep.assert_not_called();self.assertEqual(repeated,record)
            self.assertEqual(plan(self.spec())['verification_cap'],40)
            self.assertEqual(plan(self.spec())['verification_reads_needed'],40)

    def test_opt_in_and_scope_fail_closed_before_transport(self):
        execute=Mock();governor=Mock()
        prewarm_source({},CONFIG,{},governor,{}, {},execute=execute)
        execute.assert_not_called();governor.metered_read.assert_not_called()
        with tempfile.TemporaryDirectory() as folder,active(Tape(Path(folder)/'tape.json',bootstrap())):
            config=copy.deepcopy(CONFIG);config['_estate']['layers'][0]['serverless']=False
            with self.assertRaisesRegex(ValueError,'SOURCE_NOT_DECLARED'):self.run_control(self.spec(),config,execute)
            spec=self.spec();spec['prewarm']['asset_ids']=['sql://other/db/object/2']
            with self.assertRaisesRegex(ValueError,'SOURCE_NOT_DECLARED'):self.run_control(spec,CONFIG,execute)
        execute.assert_not_called()

    def test_failed_control_stops_verification_and_retains_result(self):
        with tempfile.TemporaryDirectory() as folder,active(Tape(Path(folder)/'tape.json',bootstrap())):
            execute=Mock(return_value=dict(FAILED,sql_error_number=18456))
            with self.assertRaisesRegex(ValueError,'PREWARM_FAILED'):self.run_control(self.spec(),CONFIG,execute)
            self.assertEqual(execute.call_count,1)

    def test_bad_prewarm_plan_rejected(self):
        for declaration in ({},{'asset_ids':[]},{'asset_ids':[ASSET,ASSET]},{'asset_ids':[ASSET],'query':'SELECT 1'}):
            spec=self.spec();spec['prewarm']=declaration
            with self.assertRaisesRegex(ValueError,'PREWARM_DECLARATION'):plan(spec)


if __name__=='__main__':unittest.main()
