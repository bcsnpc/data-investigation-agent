import copy
import unittest
from unittest.mock import patch
from scan_estate_graph import validate,execute

class MultiEstateTests(unittest.TestCase):
    def config(self):
        budget={'environment':'shared','policy_sha256':'a'*64,'round_id':'ROUND_TEST','rolling_limit':3000}
        child={'estate':'first','workspace':'w','owners':['item'],'authentication':{},'storage':{},
            'definition_uri_prefix':'cas://definitions','budget':budget,'max_requests':40,'approval':'owner'}
        other=copy.deepcopy(child);other['estate']='second'
        return {'scans':[child,other],'budget':budget,'approval':'Owner approved both estates'}
    def test_one_job_scans_both_sequentially_with_same_budget_no_reset(self):
        config=self.config();before=copy.deepcopy(config)
        with patch('scan_estate_graph._execute_one',side_effect=[{'physical_requests':2},{'physical_requests':3}])as run:
            result=execute(config)
        self.assertEqual([call.args[0]['estate']for call in run.call_args_list],['first','second'])
        self.assertEqual(result['physical_requests'],5)
        self.assertEqual(config,before)
        self.assertEqual(run.call_args_list[0].args[0]['budget'],run.call_args_list[1].args[0]['budget'])
    def test_existing_job_plan_keeps_two_estates_in_one_config(self):
        from test_graph_scan_schedule_plan import PlanTests
        from graph_scan_schedule_plan import build
        setup=PlanTests();setup.setUp()
        result=build(setup.job,self.config(),setup.gateway,setup.image)
        import json
        containers=result['body']['properties']['template']['containers']
        self.assertEqual(len(containers),1)
        env={v['name']:v['value']for v in containers[0]['env']}
        self.assertEqual([v['estate']for v in json.loads(env['DIA_GRAPH_SCAN_CONFIG'])['scans']],['first','second'])
        self.assertEqual(result['budget'],self.config()['budget'])

    def test_failure_does_not_admit_second_estate(self):
        with patch('scan_estate_graph._execute_one',side_effect=PermissionError('refused'))as run:
            with self.assertRaises(PermissionError):execute(self.config())
        self.assertEqual(run.call_count,1)
    def test_different_budget_duplicate_estate_and_combined_cap_refused(self):
        changes=[lambda c:c['scans'][1]['budget'].update(rolling_limit=4000),
            lambda c:c['scans'][1].update(estate='first'),lambda c:c['scans'][1].update(max_requests=70)]
        for change in changes:
            c=self.config();change(c)
            with self.assertRaises(ValueError):validate(c)
    def test_nested_schedule_never_executes(self):
        c=self.config();c['scans'][0]=self.config()
        with self.assertRaisesRegex(ValueError,'NESTING'):validate(c)

if __name__=='__main__':unittest.main()
