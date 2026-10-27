import unittest
from unittest.mock import Mock
from investigator.guided_live_facts import PathFacts
from investigator.guided_investigator_installation import Factory
from test_round23_intake_queries import graph,request

NOW='2026-10-27T02:00:00Z'


class FactTests(unittest.TestCase):
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
        factory=object.__new__(Factory);factory.graph=fake
        intake=request();del intake['visual']
        result=factory.target_path(intake)
        fake.path_to_source.assert_called_once_with('card')
        self.assertIn('visual remains optional',result['target_selection'])
        self.assertEqual({n['id'] for n in result['nodes']},{'report','page','card','measure'})


if __name__=='__main__':unittest.main()
