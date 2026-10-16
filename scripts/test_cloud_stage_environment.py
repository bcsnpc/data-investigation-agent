import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from cloud_stage_environment import build,install
from test_slim_recording import CONFIG as SLIM

STAGE={'phase':'prepare','identity':SLIM['identity'],'channel':'worker:state',
       'input_url':SLIM['account_url']+'/captures/input.zip',
       'output_url':SLIM['account_url']+'/captures/output.zip'}
PLATFORM={'identity':SLIM['identity'],'postgres':{'host':'host','database':'state','user':'worker'}}
POLICY={'version':1,'live_enabled':True,'identities':{
    'worker:state':{'role':'platform','platform_databases':[{'host':'host','database':'state'}],
        'http':[{'method':method,'url':STAGE[key],'purpose':'platform_blob'} for method,key in (('GET','input_url'),('PUT','output_url'))]},
    'worker-snapshots':{'role':'platform','platform_cas':[{'account_url':SLIM['account_url'],'container':'snapshots'}]},
    'worker-tapes':{'role':'platform','platform_cas':[{'account_url':SLIM['account_url'],'container':'tapes'}]},
    'investigation':{'http':[]},'model':{'http':[]}}}


class StageEnvironmentTests(unittest.TestCase):
    def test_build_and_install_public_files_child_workers_can_read(self):
        result=build(STAGE,POLICY,PLATFORM,SLIM,worker_id='prepare-1',ceiling_microdollars=20000000,margin_microdollars=10000000)
        env={r['name']:r['value'] for r in result['env']}
        self.assertEqual(env['INVESTIGATOR_STATE_BACKEND'],'postgresql')
        self.assertEqual(env['INVESTIGATOR_MODEL_SPEND_MARGIN_MICRODOLLARS'],'10000000')
        with tempfile.TemporaryDirectory() as folder:
            install(environment=env,work=Path(folder))
            self.assertEqual(json.loads(Path(env['DIA_GATEWAY_POLICY']).read_bytes()),POLICY)
            self.assertEqual(json.loads(Path(env['DIA_SLIM_RECORDING_CONFIG']).read_bytes()),SLIM)
            install(environment=env,work=Path(folder))
            Path(env['DIA_GATEWAY_POLICY']).write_text('{}')
            with self.assertRaisesRegex(ValueError,'ALREADY_DIFFERS'):install(environment=env,work=Path(folder))

    def test_missing_exact_cas_archive_or_database_grant_refuses(self):
        for channel,field in [('worker:state','http'),('worker:state','platform_databases'),('worker-tapes','platform_cas')]:
            policy=copy.deepcopy(POLICY);policy['identities'][channel][field]=[]
            with self.assertRaisesRegex(ValueError,'GRANT_MISSING'):
                build(STAGE,policy,PLATFORM,SLIM,worker_id='test',ceiling_microdollars=20,margin_microdollars=10)
        slim=copy.deepcopy(SLIM);slim['identity']['principal_id']='44444444-4444-4444-4444-444444444444'
        with self.assertRaisesRegex(ValueError,'IDENTITIES_DIFFER'):
            build(STAGE,POLICY,PLATFORM,slim,worker_id='test',ceiling_microdollars=20,margin_microdollars=10)

    def test_kill_switch_is_not_overridden_by_bootstrap(self):
        policy=copy.deepcopy(POLICY);policy['live_enabled']=False
        result=build(STAGE,policy,PLATFORM,SLIM,worker_id='test',ceiling_microdollars=20,margin_microdollars=10)
        env={r['name']:r['value'] for r in result['env']}
        with tempfile.TemporaryDirectory() as folder:install(environment=env,work=Path(folder))
        self.assertEqual(env['DIA_LIVE_ACCESS_DISABLED'],'1')

    def test_model_vault_fetch_uses_model_auth_channel_not_investigation(self):
        from investigator.adapters import managed_identity as auth
        with patch.dict('os.environ',{'DIA_GATEWAY_HTTP_IDENTITY':'investigation','DIA_GATEWAY_MODEL_IDENTITY':'model'}), \
                patch.object(auth,'secret',return_value='private-key') as secret:
            self.assertEqual(auth.model_key({'credential':{'mode':'key_vault','reference':{'synthetic':'reference'}}}),'private-key')
        secret.assert_called_once_with({'synthetic':'reference'},gateway_identity='model')


if __name__=='__main__':unittest.main()
