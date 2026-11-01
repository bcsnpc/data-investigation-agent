import copy
import json
import unittest
from unittest.mock import patch
from renew_platform_cost_observation import cost_only_template,main


class MaintenanceTests(unittest.TestCase):
    def test_plan_never_dispatches(self):
        with patch('renew_platform_cost_observation.subprocess.run')as execute:
            self.assertEqual(main(['--publish-schedules']),0)
        execute.assert_not_called()

    def test_only_existing_observation_changes_without_image_role_schedule_changes(self):
        config={'platform_cost_observation':{'observed_at':1,'charged_microdollars':5},'image':'frozen-image','environment':{'gateway':'unchanged'}}
        job={'identity':{'type':'UserAssigned'},'properties':{'configuration':{'cron':'0 6 * * *'},'template':{'containers':[{'name':'worker','image':'frozen-image','resources':{'cpu':.5,'memory':'1Gi'},'env':[{'name':'DIA_RUNNER_ESTATE_JSON','value':json.dumps(config)},{'name':'OTHER','value':'unchanged'}]}]}}}
        before=copy.deepcopy(job);obs={'observed_at':2,'charged_microdollars':7,'source':'local receipt'}
        template,changed=cost_only_template(job,obs)
        self.assertTrue(changed);self.assertEqual(job,before)
        actual=json.loads(template['containers'][0]['env'][0]['value'])
        self.assertEqual(actual,{**config,'platform_cost_observation':obs})
        self.assertEqual(template['containers'][0]['resources'],job['properties']['template']['containers'][0]['resources'])
        self.assertEqual(template['containers'][0]['image'],'frozen-image')
        del config['platform_cost_observation'];job['properties']['template']['containers'][0]['env'][0]['value']=json.dumps(config)
        _,changed=cost_only_template(job,obs);self.assertFalse(changed)


if __name__=='__main__':unittest.main()
