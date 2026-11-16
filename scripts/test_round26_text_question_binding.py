import copy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from cloud_guided_investigator import intake_question_outcome
from investigator.investigator_harness import CaseLog, RunHarness
from investigator.shared_state import StateConflict


class TextQuestionBindingTests(unittest.TestCase):
    def test_unadmitted_text_question_is_a_saved_outcome_not_a_binding_error(self):
        text='Which total should I check?'
        mapped={'status':'NEEDS_INPUT','question':{'text':'Which report?', 'fields':[]}}
        output=intake_question_outcome(text,mapped,resolution=None,step_costs=[],cost={'charged_microdollars':3})
        class User:
            def submit(self,ticket):return {'run_id':'one'}
            def poll(self,run):return {'status':'Succeeded'}
            def outcome(self,run,state):return copy.deepcopy(output)
        with TemporaryDirectory()as folder:
            result=RunHarness(User(),CaseLog(Path(folder)/'ok.jsonl'),admit=lambda _:None).run({'text':text})
            self.assertEqual(result['status'],'NEEDS_INPUT')
            self.assertEqual(result['physical_requests'],0)
            self.assertEqual(result['cost'],{'charged_microdollars':3})
            self.assertEqual(mapped,{'status':'NEEDS_INPUT','question':{'text':'Which report?', 'fields':[]}})
            with self.assertRaisesRegex(StateConflict,'DELIVERED_TICKET_TEXT_DIFFERS'):
                RunHarness(User(),CaseLog(Path(folder)/'wrong.jsonl'),admit=lambda _:None).run({'text':'A different ticket'})


if __name__=='__main__':unittest.main()
