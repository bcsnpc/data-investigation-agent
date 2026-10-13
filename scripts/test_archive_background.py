from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
from datetime import datetime,timezone

from investigator.artifact_store import canonical,digest,ArtifactError
from archive_background import admission,run
from investigator.streaming_archive_bundle import publish
from test_resumable_archive import Remote


POLICY={'batch_stored_bytes':134217728,'batch_controls':49,'total_stored_bytes':50000000000,
        'egress_usd_per_gb':'0.087','control_usd_each':'0.00001','archive_usd_per_gb_month':'0.00099',
        'platform_baseline_usd_month':'13.74','transfer_usd_cap':'4.50','control_usd_cap':'0.50','platform_total_usd_cap':'20'}


class Tests(unittest.TestCase):
    def test_decimal_cost_and_all_bounds(self):
        self.assertLess(float(admission(POLICY,0,0)['projected_platform_usd']),20)
        for changed,error in [({'total_stored_bytes':1},'STORED_BYTE_CAP'),
                              ({'transfer_usd_cap':'0'},'TRANSFER_CONTROL_CAP'),
                              ({'control_usd_cap':'0'},'TRANSFER_CONTROL_CAP'),
                              ({'platform_total_usd_cap':'13'},'PLATFORM_COST_CAP'),
                              ({'egress_usd_per_gb':0.087},'COST_POLICY'),
                              ({'egress_usd_per_gb':'-1'},'COST_POLICY')]:
            with self.assertRaisesRegex(ArtifactError,error):admission({**POLICY,**changed},0,0)
    def test_separate_oneoff_and_steady_caps_include_cool_minimum(self):
        policy={'version':2,'batch_stored_bytes':1000000000,'batch_controls':100,
                'total_stored_bytes':200000000000,'historical_stored_bytes':1000000000,
                'historical_controls':294,'cool_reserve_days':31,'cool_usd_per_gb_month':'0.0152',
                'archive_usd_per_gb_month':'0.00099','control_usd_each':'0.00001',
                'platform_baseline_usd_month':'19.99','platform_total_usd_cap':'20',
                'oneoff_usd_cap':'2','oneoff_prior_usd':'0.00045'}
        got=admission(policy,1000000000,294)
        self.assertEqual(got['projected_platform_usd_month'],'19.99198')
        self.assertGreater(float(got['reserved_oneoff_usd']),0.016)
        # Old mixed accounting would refuse despite both independent caps fitting.
        self.assertGreater(float(got['projected_platform_usd_month'])+float(got['reserved_oneoff_usd']),20)
        for patch_values,stored,controls,error in [
            ({'oneoff_usd_cap':'0.016'},1000000000,294,'ONEOFF_COST_CAP'),
            ({'platform_total_usd_cap':'19.99'},1000000000,294,'PLATFORM_COST_CAP'),
            ({'cool_reserve_days':30},1000000000,294,'COST_POLICY'),
            ({},999999999,294,'ACCOUNTING_CHECKPOINT'),
            ({'oneoff_usd_cap':'0.0172'},1000000000,400,'ONEOFF_COST_CAP'),
        ]:
            with self.assertRaisesRegex(ArtifactError,error):
                admission({**policy,**patch_values},stored,controls)
        # Retained retry charges and prior committed blobs cannot disappear.
        after=admission(policy,2000000000,394)
        self.assertGreater(float(after['reserved_oneoff_usd']),float(got['reserved_oneoff_usd']))

    def test_owner_stop_during_offline_measurement_never_creates_client(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);capture=root/'.local/round-five/capture';capture.mkdir(parents=True)
            (capture/'tape.json').write_bytes(canonical({'events':[]}))
            runtime=root/'runtime.py';runtime.write_text('# no captured dependencies')
            baseline=root/'baseline.json';baseline.write_bytes(canonical({'stored_bytes':0,'platform_controls':0}))
            policy={'version':2,'batch_stored_bytes':100000,'batch_controls':100,'total_stored_bytes':1000000,
                    'historical_stored_bytes':0,'historical_controls':0,'cool_reserve_days':31,
                    'cool_usd_per_gb_month':'0.0152','archive_usd_per_gb_month':'0.00099',
                    'control_usd_each':'0.00001','platform_baseline_usd_month':'14.82',
                    'platform_total_usd_cap':'20','oneoff_usd_cap':'2','oneoff_prior_usd':'0'}
            config={'workspace':str(root),'scope_approval':'synthetic','local_deletion':False,
                    'accounting_checkpoint':{'path':str(baseline),'sha256':digest(baseline.read_bytes())},
                    'previous_plans':[],'cutoff':datetime.fromtimestamp(time.time()+1,timezone.utc).isoformat(),
                    'admit_before':'2099-01-01T00:00:00+00:00','stop_file':str(root/'STOP'),
                    'max_batches':1,'max_original_bytes':10000,'max_files':10,'protected_paths':[],
                    'runtime_reference_paths':[str(runtime)],'verification_mode':'block-checksum-v1','cost_policy':policy}
            def measure(*args):
                (root/'STOP').touch()
                return {'blocks':[{}],'stored_bytes':100}
            def client(*args):self.fail('a stop during offline work must precede client creation')
            with patch('shutil.disk_usage',return_value=type('Usage',(),{'free':20*1024**3})()),patch('investigator.checksum_archive.measure',side_effect=measure):
                result=run(config,root/'output',client)
            self.assertEqual(result['batches'],[])
            self.assertIn('after measurement',(root/'output/controller.jsonl').read_text())

    def test_bounded_run_keeps_originals_and_cap_blocks_before_client(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);capture=root/'.local/round-five/capture';capture.mkdir(parents=True)
            (capture/'tape.json').write_bytes(canonical({'events':[]}))
            (capture/'receipt.json').write_bytes(b'fixture metadata')
            baseline=root/'baseline.json';baseline.write_bytes(canonical({'stored_bytes':0,'platform_controls':0}))
            config={'workspace':str(root),'scope_approval':'synthetic test','local_deletion':False,
                    'accounting_checkpoint':{'path':str(baseline),'sha256':digest(baseline.read_bytes())},
                    'previous_plans':[],'cutoff':datetime.fromtimestamp(time.time()+1,timezone.utc).isoformat(),
                    'admit_before':'2099-01-01T00:00:00+00:00','stop_file':str(root/'STOP'),
                    'max_batches':1,'max_original_bytes':10000,'max_files':10,'protected_paths':[],
                    'cost_policy':POLICY}
            clients=[]
            def factory(folder,cap):
                client=Remote();client.remaining=cap;clients.append(client);return client
            def producer(*args,**kwargs):
                result=publish(*args,**kwargs);args[5].remaining-=1;return result
            with patch('shutil.disk_usage',return_value=type('Usage',(),{'free':20*1024**3})()):
                result=run(config,root/'output',factory,publisher=producer)
                self.assertEqual(result['platform_controls'],1)
                self.assertTrue((capture/'tape.json').exists())
                self.assertFalse(list((root/'output').rglob('*.tar*')))
                with self.assertRaises(FileExistsError):run(config,root/'output',factory,publisher=producer)
                with self.assertRaisesRegex(ArtifactError,'PLATFORM_COST_CAP'):
                    run({**config,'cost_policy':{**POLICY,'platform_total_usd_cap':'13'}},root/'refused',factory)
                self.assertEqual(len(clients),1)
                stopped=run({**config,'admit_before':'2000-01-01T00:00:00+00:00'},root/'past-deadline',factory)
                self.assertEqual(stopped['batches'],[])
                (root/'STOP').touch()
                stopped=run(config,root/'owner-stopped',factory)
                self.assertEqual(stopped['batches'],[])
                self.assertEqual(len(clients),1)


if __name__=='__main__':unittest.main()
