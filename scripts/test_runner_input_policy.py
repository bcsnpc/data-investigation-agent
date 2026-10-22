import json,unittest
from investigator.adapters.runner_deployment import input_policy_preflight


class Tests(unittest.TestCase):
    def example(self):
        url='https://synthetic.blob.core.windows.net/captures/round21/input.zip'
        return {'capture':{'channel':'worker'},'input':{'url':url},'environment':{'DIA_PLATFORM_GATEWAY_POLICY':json.dumps(
            {'identities':{'worker':{'http':[{'method':'GET','purpose':'platform_blob','url':url}]}}})}}

    def test_prepared_input_and_exact_get_grant_agree(self):
        self.assertEqual(input_policy_preflight(self.example())['status'],'PASS')

    def test_new_input_without_rebound_read_grant_refuses_before_launch(self):
        config=self.example();config['input']['url']+='-changed'
        with self.assertRaisesRegex(ValueError,'EXACT_READ_NOT_DECLARED'):input_policy_preflight(config)

    def test_mutating_method_is_not_a_read_grant(self):
        config=self.example();policy=json.loads(config['environment']['DIA_PLATFORM_GATEWAY_POLICY'])
        policy['identities']['worker']['http'][0]['method']='PUT'
        config['environment']['DIA_PLATFORM_GATEWAY_POLICY']=json.dumps(policy)
        with self.assertRaises(ValueError):input_policy_preflight(config)


if __name__=='__main__':unittest.main()
