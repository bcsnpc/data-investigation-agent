"""Copy to scripts/test_workspace_admission.py only after admission patch approval."""
import copy,sqlite3,unittest
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from investigator.workspace import Workspace
from investigator.onboarding import Conflict
from investigator import process_tape as journal
from investigator.workspace_admission import admit
from test_investigator_workspace import WorkspaceTests


class WorkspaceAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.fixture=WorkspaceTests();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
    def workspace(self,limit=4):
        return Workspace(self.fixture.agent,execution_enabled=True,clock=self.fixture.clock,concurrency_limit=limit)
    def test_four_concurrent_admissions_fifth_refused_then_terminal_releases_slot(self):
        workspaces=[self.workspace() for _ in range(5)]
        previews=[w.preview(copy.deepcopy(self.fixture.request)) for w in workspaces]
        with ThreadPoolExecutor(max_workers=4) as pool:
            results=list(pool.map(lambda pair:pair[0].start(pair[1]['id']),zip(workspaces[:4],previews[:4])))
        self.assertEqual(len(results),4)
        with self.assertRaises(Conflict):workspaces[4].start(previews[4]['id'])
        with self.fixture.store.connect() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM workspace_jobs WHERE status='QUEUED'").fetchone()[0],4)
            db.execute("UPDATE workspace_jobs SET status='FINISHED' WHERE preview_id=?",(previews[0]['id'],))
        workspaces[4].start(previews[4]['id'])
        with self.fixture.store.connect() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM workspace_jobs WHERE status='QUEUED'").fetchone()[0],4)

    def test_same_owner_remains_one_active_and_default_limit_is_one(self):
        first=self.workspace();first.start(first.preview(copy.deepcopy(self.fixture.request))['id'])
        with self.assertRaises(Conflict):first.start(first.preview(copy.deepcopy(self.fixture.request))['id'])
        default=Workspace(self.fixture.agent,execution_enabled=True,clock=self.fixture.clock)
        self.assertEqual(default.concurrency_limit,1)
        with self.assertRaises(Conflict):default.start(default.preview(copy.deepcopy(self.fixture.request))['id'])
        for limit in (0,9,True):
            with self.assertRaises(ValueError):self.workspace(limit)

    def test_recorded_external_job_inputs_survive_other_owners_finishing_before_replay(self):
        class Journal:
            replaying=False
            bootstrap={'state':{'workspace_concurrency_limit':4}}
            def event(self,kind,body):self.body=body
            def take(self,kind):return self.body
        tape=Journal()
        with self.fixture.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute("INSERT INTO workspace_jobs VALUES('other','model','session','other-owner','RUNNING',0,NULL)")
            token=journal.ACTIVE.set(tape)
            try:
                admit(db,'mine',4)
                db.execute("UPDATE workspace_jobs SET status='FINISHED' WHERE preview_id='other'")
                tape.replaying=True
                admit(db,'mine',4)
                self.assertEqual(db.execute("SELECT status FROM workspace_jobs WHERE preview_id='other'").fetchone()[0],'FINISHED')
            finally:journal.ACTIVE.reset(token)

    def test_legacy_missing_concurrency_pin_emits_no_new_replay_event(self):
        tape=SimpleNamespace(replaying=True,bootstrap={'state':{}},event=lambda *a: self.fail('legacy tape emits new event'),take=lambda *a:self.fail('legacy tape consumes new event'))
        with self.fixture.store.connect() as db:
            db.execute('BEGIN IMMEDIATE');token=journal.ACTIVE.set(tape)
            try:admit(db,'mine',1)
            finally:journal.ACTIVE.reset(token)


if __name__=='__main__':unittest.main()
