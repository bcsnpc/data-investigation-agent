import unittest
from unittest.mock import Mock
from investigator.guided_live_facts import PathFacts
from investigator.guided_investigator_installation import Factory
from test_round23_intake_queries import graph,request

NOW='2026-10-27T02:00:00Z'


class FactTests(unittest.TestCase):
    def test_scan_allocation_refusal_keeps_investigation_alive_without_dispatch(self):
        from investigator.usage_governance import UsageHold
        ledger=Mock();ledger.read.return_value={'facts':[]}
        collector=Mock(side_effect=UsageHold('MONTHLY_PHYSICAL_SCAN_EXHAUSTED'))
        port=PathFacts(ledger=ledger,estate='fixture',path={'nodes':[{'id':'model','kind':'MODEL'}]},collector=collector,now=lambda:NOW)
        triage=port.run()
        collector.assert_called_once()
        self.assertEqual(triage['facts'][0]['state'],'UNAVAILABLE')
        self.assertEqual(triage['facts'][0]['detail'],'MONTHLY_PHYSICAL_SCAN_EXHAUSTED')
        self.assertEqual(port.history('model',{'REFRESH_RUN'})['reason'],'MONTHLY_PHYSICAL_SCAN_EXHAUSTED')

    def test_total_and_investigation_caps_still_stop_triage(self):
        from investigator.usage_governance import UsageHold
        for reason in ('MONTHLY_PHYSICAL_EXHAUSTED','MONTHLY_PHYSICAL_INVESTIGATION_EXHAUSTED'):
            with self.subTest(reason=reason):
                ledger=Mock();ledger.read.return_value={'facts':[]}
                port=PathFacts(ledger=ledger,estate='fixture',path={'nodes':[{'id':'model','kind':'MODEL'}]},collector=Mock(side_effect=UsageHold(reason)),now=lambda:NOW)
                with self.assertRaisesRegex(UsageHold,reason):port.run()

    def test_job_status_older_than_thirty_seconds_is_not_presented_as_current(self):
        ledger=Mock();ledger.read.return_value={'facts':[{'subject':'job','kind':'JOB_RUN','state':'OBSERVED','freshness':'CURRENT','collected_at':'2026-10-27T01:59:00Z','value':{'status':'FAILED'}}]}
        port=PathFacts(ledger=ledger,estate='fixture',path={'nodes':[{'id':'job','kind':'PIPELINE'}]},now=lambda:NOW)
        self.assertIsNone(port.lookup('JOB_RUNS',[]))
        ledger.read.return_value['facts'][0]['collected_at']='2026-10-27T01:59:45Z';port.snapshot=None
        self.assertIsNotNone(port.lookup('JOB_RUNS',[]))

    def test_installed_collector_run_method_is_used(self):
        from types import SimpleNamespace
        ledger=Mock();ledger.read.return_value={'facts':[]}
        run=Mock(return_value={'status':'COLLECTED'})
        port=PathFacts(ledger=ledger,estate='fixture',path={'nodes':[{'id':'model','kind':'MODEL'}]},
                       collector=SimpleNamespace(run=run),now=lambda:NOW)
        port.run()
        run.assert_called_once_with('fixture',['model'],now=NOW,force=True)

    def test_missing_facts_refresh_once_for_ticket_path_and_keep_unavailable_distinct(self):
        ledger=Mock();collector=Mock();latest=[]
        ledger.read.side_effect=lambda *a,**k:{'facts':latest}
        def refresh(estate,subjects,**kwargs):
            self.assertEqual(subjects,['model'])
            latest.append({'subject':'model','kind':'REFRESH_RUN','state':'OBSERVED_NEGATIVE',
                           'freshness':'CURRENT','collected_at':NOW,'value':[]})
            return {'status':'COLLECTED'}
        collector.side_effect=refresh
        result=PathFacts(ledger=ledger,estate='fixture',path={'nodes':[{'id':'model','kind':'MODEL'}]},
                         collector=collector,now=lambda:NOW).run()
        collector.assert_called_once()
        self.assertEqual(result['facts'][0]['state'],'OBSERVED_NEGATIVE')
        self.assertEqual(result['facts'][2]['state'],'UNAVAILABLE')

    def test_current_job_facts_expose_specific_native_run_and_no_top_up(self):
        collector=Mock();ledger=Mock()
        fact={'subject':'job','kind':'JOB_RUN','state':'OBSERVED','freshness':'CURRENT',
              'collected_at':NOW,'value':{'run_id':'native-run','status':'FAILED','error':'native error'}}
        ledger.read.return_value={'facts':[fact]}
        port=PathFacts(ledger=ledger,estate='fixture',path={'nodes':[{'id':'job','kind':'PIPELINE'}]},collector=collector)
        result=port.history('job',{'JOB_RUN'})
        self.assertEqual(result['facts'][0]['value']['run_id'],'native-run');collector.assert_not_called()


class OptionalVisualTests(unittest.TestCase):
    def test_report_page_only_uses_actual_visual_candidates_without_selecting_one(self):
        retained=graph();fake=Mock();fake.intake_catalog.return_value=retained
        fake.path_to_source.side_effect=lambda root:{'nodes':[n for n in retained['nodes'] if n['id'] in (root,'measure')],
                                                   'edges':[]}
        factory=object.__new__(Factory);factory.graph=fake;factory.routes={};factory.associated_nodes=None
        intake=request();del intake['visual']
        result=factory.target_path(intake)
        fake.path_to_source.assert_called_once_with('card')
        self.assertIn('visual remains optional',result['target_selection'])
        self.assertEqual({n['id'] for n in result['nodes']},{'report','page','card','measure'})


if __name__=='__main__':unittest.main()
