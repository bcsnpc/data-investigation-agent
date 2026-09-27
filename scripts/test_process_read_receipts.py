import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import test_flexible_investigation as fixture
from investigator.adaptive_runtime import AdaptiveRuntime
from investigator.process_debugging import VERSION
from investigator.process_read_receipts import accounting, receipt


class ProcessReadReceiptTests(unittest.TestCase):
    def test_read_survives_later_validation_failure_and_reload(self):
        helper=fixture.DynamicTests();helper.setUp();self.addCleanup(helper.doCleanups)
        envelope=copy.deepcopy(helper.envelope);envelope['strategy']=VERSION
        agent=AdaptiveRuntime(helper.runtime,lambda _:self.fail('no planner'))
        identity=agent.create(envelope,'failed-support')['id']
        with patch('investigator.assessment_support.validate',side_effect=ValueError('later failure')):
            state=agent.run(identity)
        self.assertEqual(state['status'],'HELD')
        self.assertEqual(len(helper.native_calls),1)
        self.assertEqual(accounting(state)['reads_dax'],1)
        self.assertEqual(accounting(agent.get(identity)),accounting(state))
        self.assertTrue(state['observations'])
        entries=state['process_read_receipts']
        self.assertTrue(entries[0]['receipt_id'])
        self.assertTrue(entries[0]['result_hash'])
        self.assertEqual(sum(e['kind']=='PROCESS_READ_RECORDED' for e in state['events']),1)
        self.assertIsNone(state.get('assessment'))

    def test_failure_and_metadata_accounting_are_not_success_assumptions(self):
        entries=[receipt(1,'bounded_dax',None,'TimeoutError'),
                 receipt(2,'fabric_endpoint_metadata',{'id':'endpoint','properties':{}}),
                 receipt(3,'bounded_fabric_sql',{'id':'sealed','status':'COMPLETED'})]
        result=accounting({'process_read_receipts':entries,'observations':[]})
        self.assertEqual((result['reads_total'],result['reads_completed'],result['reads_unsuccessful_or_uncertain']),(3,2,1))
        self.assertIsNone(entries[1]['receipt_id'])
        self.assertEqual(entries[1]['metadata_response']['id'],'endpoint')

    def test_correction_is_appended_and_does_not_add_an_investigation(self):
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'acceptance/unknown_domain'))
        from run_ledger import append,effective_rows
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'ledger.jsonl'
            append(path,{'session_id':'failed','reads_sql':0,'outcome_label':'HELD'})
            original=path.read_bytes()
            append(path,{'record_type':'CORRECTION','corrects_session_id':'failed',
                'original_row_sha256':hashlib.sha256(original.splitlines()[0]).hexdigest(),
                'corrected_fields':{'reads_sql':2}})
            self.assertTrue(path.read_bytes().startswith(original))
            self.assertEqual(effective_rows(path),[{'session_id':'failed','reads_sql':2,'outcome_label':'HELD'}])
