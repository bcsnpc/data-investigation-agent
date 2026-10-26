import unittest
from investigator.investigator_case import CaseFile
from investigator.investigator_playbook import allowed
import test_ledger_investigator as fixtures

class PlaybookTests(unittest.TestCase):
    def test_forbidden_tool_never_dispatches_and_code_advance_changes_tools(self):
        tools,_,reader,_=fixtures.ToolLoopTests().build();case=CaseFile({'id':'one'})
        case.advance('quick_facts');tools.step_provider=lambda:case.value['current_step']
        args={'key':'record-1','layers':['down','up'],'filters':tools.context}
        with self.assertRaisesRegex(ValueError,'NOT_PERMITTED'):
            tools.invoke('compare_layers',args)
        reader.assert_not_called()
        self.assertIn('refresh_facts',allowed('quick_facts'))
        case.advance('investigate')
        self.assertIn('compare_layers',allowed('investigate'))
        self.assertNotIn('refresh_facts',allowed('investigate'))
        self.assertEqual(tools.invoke('compare_layers',args)['status'],'OBSERVED')
        self.assertEqual(reader.call_count,2)
        case.advance('deliver')
        with self.assertRaisesRegex(ValueError,'NOT_PERMITTED'):
            tools.invoke('compare_layers',args)

if __name__=='__main__':unittest.main()
