"""Real zero-socket replay from a verified code-only installation, without Git."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]


def image_layout(destination):
    from build_cloud_image_context import admitted
    from investigator.runtime import fingerprint_files
    names={p.relative_to(ROOT).as_posix() for p in ROOT.glob('scripts/**/*.py') if '__pycache__' not in p.parts}
    names.update(p.relative_to(ROOT).as_posix() for p in ROOT.glob('acceptance/**/*.py') if '__pycache__' not in p.parts)
    names.update(p.relative_to(ROOT).as_posix() for p in fingerprint_files(ROOT)[1])
    entries=[]
    for name in sorted(names):
        if not admitted(name):raise AssertionError('Nonpublic replay input:'+name)
        target=destination/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/name,target)
        entries.append({'path':name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
    (destination/'image-source-manifest.json').write_text(json.dumps({'version':2,'engine_revision':'a'*40,'files':entries}))


RECORD='''import json,sqlite3,sys
from pathlib import Path
root=Path(sys.argv[1]);work=Path(sys.argv[2]);sys.path.insert(0,str(root/'scripts'))
from investigator.onboarding import ModelStore
from investigator.runtime import Runtime
from investigator.adaptive_runtime import AdaptiveRuntime
from investigator.workspace import Workspace
from investigator import run_recording
store=ModelStore(work/'catalog.sqlite',work/'inventory.sqlite','synthetic-image')
with sqlite3.connect(store.inventory) as db:db.execute('CREATE TABLE synthetic(value INTEGER)')
policy={'environment':store.environment,'daily_limits':{'planner_calls':5,'cloud_calls':5,'input_characters':10000,'output_tokens':10000},'max_inflight_planners':1,'no_progress_limit':1}
agent=AdaptiveRuntime(Runtime(store,{},None,None),lambda _:None,usage_policy=policy)
workspace=Workspace(agent,execution_enabled=True)
run_recording.ROOT=work
try:workspace.intake.resolve({})
except ValueError:pass
paths=list((work/'.local/process-tapes').glob('*/tape.json'))
assert len(paths)==1,paths
(work/'capture-path.txt').write_text(str(paths[0]))
'''


class InstalledReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.temp.cleanup)
        cls.directory=Path(cls.temp.name);cls.image=cls.directory/'image';image_layout(cls.image)
        spec=importlib.util.spec_from_file_location('installed_recorded_engine',cls.image/'acceptance/unknown_domain/recorded_engine.py')
        cls.replayer=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.replayer)
        cls.work=cls.directory/'work';cls.work.mkdir()
        env={k:v for k,v in os.environ.items() if not k.startswith(('DIA_','INVESTIGATOR_'))}
        env.update(PYTHONDONTWRITEBYTECODE='1',INVESTIGATOR_RECORD_RUNS='1')
        run=subprocess.run([sys.executable,'-c',RECORD,str(cls.image),str(cls.work)],env=env,capture_output=True,text=True,timeout=60)
        if run.returncode:raise AssertionError('Synthetic recording failed:'+run.stderr)
        cls.tape=Path((cls.work/'capture-path.txt').read_text())

    def test_actual_code_only_replay_uses_verified_installed_bytes_without_git_or_drift(self):
        before=self.tape.read_bytes()
        # The only subprocess permitted is the existing isolated Python driver.
        original=subprocess.run
        def child_only(args,**kwargs):
            self.assertEqual(args[0],sys.executable)
            return original(args,**kwargs)
        with patch.object(self.replayer.subprocess,'run',side_effect=child_only),patch.object(self.replayer.subprocess,'check_output',side_effect=AssertionError('Git forbidden in image')):
            result=self.replayer.replay_revision(self.tape,self.directory/'replayed','a'*40)
        self.assertTrue(result['matched']);self.assertEqual(result['operations'],['intake'])
        self.assertEqual(result['network_requests'],0);self.assertFalse(result['recorded_engine_identity_used'])
        self.assertEqual(result['replay_engine_revision'],'a'*40)
        self.assertEqual(self.tape.read_bytes(),before)
        self.assertFalse((self.image/'.git').exists())
        self.assertFalse((self.image/'replay-pinned-driver.py').exists())

    def test_typed_investigation_entrypoint_replays_actual_tape_in_code_only_child(self):
        program="import json,sys;sys.path.insert(0,sys.argv[1]+'/scripts');from investigator.runner_replay import replay;print(json.dumps(replay({'format':'investigation','tape':sys.argv[2],'engine_revision':'a'*40},sys.argv[3])))"
        env={k:v for k,v in os.environ.items() if not k.startswith(('DIA_','INVESTIGATOR_'))}
        env['PYTHONDONTWRITEBYTECODE']='1'
        result=subprocess.run([sys.executable,'-c',program,str(self.image),str(self.tape),str(self.directory/'typed-replay')],env=env,capture_output=True,text=True,timeout=60)
        self.assertEqual(0,result.returncode,result.stderr)
        value=json.loads(result.stdout)
        self.assertTrue(value['matched']);self.assertEqual(0,value['network_requests'])
        self.assertFalse(value['recorded_engine_identity_used'])

    def test_different_revision_refuses_before_worker_and_never_fetches(self):
        with patch.object(self.replayer.subprocess,'run',side_effect=AssertionError('No child')),patch.object(self.replayer.subprocess,'check_output',side_effect=AssertionError('No Git')):
            with self.assertRaisesRegex(ValueError,'IMAGE_REPLAY_REVISION_DIFFERS'):
                self.replayer.replay_revision(self.tape,self.directory/'different','b'*40)
        self.assertFalse((self.directory/'different').exists())

    def test_changed_image_byte_refuses_before_child(self):
        source=self.image/'acceptance/unknown_domain/catalog_replay.py';before=source.read_bytes()
        try:
            source.write_bytes(before+b'\n')
            with patch.object(self.replayer.subprocess,'run',side_effect=AssertionError('No child')):
                with self.assertRaisesRegex(ValueError,'IMAGE_SOURCE_CHANGED'):
                    self.replayer.replay_revision(self.tape,self.directory/'tampered','a'*40)
        finally:source.write_bytes(before)

    def test_different_tape_runtime_hash_refuses_not_drift(self):
        from investigator.process_tape import bytes_of,sha
        target=self.directory/'changed-tape';target.mkdir()
        for name in ('catalog.sqlite','inventory.sqlite'):shutil.copyfile(self.tape.parent/name,target/name)
        body=json.loads(self.tape.read_bytes());event=body['events'][0]
        import base64
        bootstrap=json.loads(base64.b64decode(event['body']));bootstrap['engine_hash']='not-the-installed-engine'
        raw=bytes_of(bootstrap);event['body']=base64.b64encode(raw).decode();event['sha256']=sha(raw)
        body['seal']=sha(bytes_of({k:v for k,v in body.items() if k!='seal'}))
        changed=target/'tape.json';changed.write_bytes(bytes_of(body))
        from investigator.process_tape import TapeError
        with self.assertRaisesRegex(TapeError,'ENGINE_VERSION_MISMATCH'):
            self.replayer.replay_revision(changed,self.directory/'drift','a'*40)


if __name__=='__main__':unittest.main()
