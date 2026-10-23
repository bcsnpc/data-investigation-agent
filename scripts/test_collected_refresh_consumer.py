"""Saved estate metadata regression; runs on the full checkout, never shipped as image data."""
import unittest
import copy
import test_ledger_investigator as base


class SavedRefreshConsumerTests(unittest.TestCase):
    def test_live_billing_empty_refresh_history_reaches_tool_despite_older_viewer_403(self):
        from pathlib import Path
        import json
        rows=json.loads((Path(__file__).parent/'fixtures/r21-billing-empty-refresh-history.json').read_text())['facts']
        tools,_,reader,_=base.ToolLoopTests().build()
        # Subject substitution is test-only; captured values/status/times stay intact.
        for row in rows:row['subject']='job'
        tools.now=max(row['collected_at'] for row in rows)
        tools.graph.node_facts.side_effect=lambda node,**kw:{'facts':copy.deepcopy(rows)}
        for name,args in (('last_refresh',{'model':'job'}),('last_run',{'job':'job'})):
            result=tools.invoke(name,args)
            self.assertEqual(result['status'],'OBSERVED')
            history=next(f for f in result['facts']if f['kind']=='RUN_HISTORY')
            self.assertEqual(history['value'],{'runs':[],'listing_complete':True})
            self.assertEqual(history['state'],'OBSERVED_NEGATIVE')
            if name=='last_refresh':self.assertTrue(any(f['state']=='UNAVAILABLE'for f in result['facts']))
        reader.assert_not_called()


if __name__=='__main__':unittest.main()
