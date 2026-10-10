"""Pending consumer tests: synthetic calls only, no provider or estate access."""
import importlib.util,sqlite3,tempfile,unittest
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from investigator.usage_governance import UsageGovernor,UsageHold

from investigator import model_transport_retry as retry

class Throttle(Exception):status_code=429
class Denied(Exception):status_code=403

@contextmanager
def no_sidecar(*args,**kwargs):yield

class RetryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        database=Path(self.temp.name)/'budget.sqlite'
        @contextmanager
        def db():
            connection=sqlite3.connect(database);connection.row_factory=sqlite3.Row
            try:
                with connection:yield connection
            finally:connection.close()
        self.runtime=SimpleNamespace(store=SimpleNamespace(environment='test'),db=db)
        self.policy={'environment':'test','daily_limits':{'planner_calls':10,'cloud_calls':10,
            'input_characters':100000,'output_tokens':24000},'max_inflight_planners':4,'no_progress_limit':2}
        self.governor=UsageGovernor(self.runtime,self.policy,lambda:1000)
        with db() as connection:
            connection.execute('BEGIN IMMEDIATE');self.governor.reserve(connection,'session','initial','planner',100,output_tokens=8000)
        self.body={'input':'synthetic question','max_output_tokens':8000}
        self.admissions=[]
    def scope(self):
        def admit(db,key,characters,output):self.admissions.append((key,characters,output))
        return retry.scope(self.governor,'session','initial',100,8000,admit_extra=admit)
    def rows(self):
        with self.runtime.db() as db:return [dict(r) for r in db.execute('SELECT * FROM adaptive_usage ORDER BY reservation_key')]

    def test_429_then_success_owns_two_reservations_identical_bodies_and_one_ticket(self):
        calls=[];waits=[]
        def invoke(body):
            calls.append(retry.journal.bytes_of(body))
            if len(calls)==1:raise Throttle('capacity')
            return SimpleNamespace(usage={'input_tokens':2,'output_tokens':3})
        with self.scope(),patch('investigator.planner_recording.recording',no_sidecar),patch.object(retry.time,'sleep',waits.append):
            retry.dispatch(self.body,invoke)
        self.assertEqual(len(calls),2);self.assertEqual(calls[0],calls[1]);self.assertEqual(waits,[2])
        rows=self.rows();self.assertEqual(len(rows),2);self.assertEqual({r['session_id'] for r in rows},{'session'})
        self.assertEqual(rows[0]['status'],'UNCERTAIN');self.assertEqual(rows[1]['status'],'SETTLED')
        # The existing outer owner cannot overwrite the first failed attempt
        # with the final successful attempt's usage.
        with self.runtime.db() as db:
            db.execute('BEGIN IMMEDIATE');self.governor.settle(db,'session','initial',{'output_tokens':3})
        self.assertEqual(self.rows()[0]['status'],'UNCERTAIN')

    def test_three_capacity_attempts_are_bounded_and_semantic_or_permission_errors_do_not_retry(self):
        calls=[];waits=[]
        def invoke(body):calls.append(1);raise Throttle('capacity')
        with self.scope(),patch('investigator.planner_recording.recording',no_sidecar),patch.object(retry.time,'sleep',waits.append),self.assertRaises(Throttle):
            retry.dispatch(self.body,invoke)
        self.assertEqual(len(calls),3);self.assertEqual(waits,[2,4]);self.assertEqual(len(self.rows()),3)
        for error in (ValueError('invalid semantic record'),Denied('permission')):
            calls=[]
            def fail(body):calls.append(1);raise error
            with patch.object(retry.time,'sleep',side_effect=AssertionError('no backoff')),self.assertRaises(type(error)):
                retry.dispatch(self.body,fail)
            self.assertEqual(len(calls),1)

    def test_existing_budget_refuses_retry_before_another_request(self):
        self.governor.policy['daily_limits']['output_tokens']=8000
        calls=[]
        def invoke(body):calls.append(1);raise Throttle('capacity')
        with self.scope(),patch.object(retry.time,'sleep',lambda seconds:None),self.assertRaises(UsageHold):
            retry.dispatch(self.body,invoke)
        self.assertEqual(len(calls),1);self.assertEqual(len(self.rows()),1)

    def test_each_physical_provider_attempt_has_its_own_dollar_guard_and_recorded_control(self):
        from investigator.model_spend import SpendBudget
        dollars=SpendBudget(Path(self.temp.name)/'dollars.sqlite',1000000)
        class Journal:
            replaying=False
            def __init__(self):self.events=[]
            def event(self,kind,body):self.events.append((kind,body))
        tape=Journal();calls=[]
        def invoke(body):
            reservation=dollars.reserve(body);usage=None
            retry.journal.event('PROVIDER_REQUEST',body);calls.append(1)
            try:
                if len(calls)==1:
                    retry.journal.event('PROVIDER_RESPONSE',{'status':429,'body':'capacity'})
                    raise Throttle('capacity')
                usage={'input_tokens':2,'output_tokens':3}
                retry.journal.event('PROVIDER_RESPONSE',{'status':200,'body':'success'})
                return SimpleNamespace(usage=usage)
            finally:dollars.settle(reservation,usage)
        token=retry.journal.ACTIVE.set(tape)
        try:
            with self.scope(),patch('investigator.planner_recording.recording',no_sidecar),patch.object(retry.time,'sleep',lambda seconds:None):retry.dispatch(self.body,invoke)
        finally:retry.journal.ACTIVE.reset(token)
        with dollars.connect() as db:
            rows=list(db.execute('SELECT status FROM model_spend'))
        self.assertEqual(rows,[('UNCERTAIN',),('SETTLED',)])
        self.assertEqual(sum(k=='PROVIDER_REQUEST' for k,b in tape.events),2)
        self.assertEqual(sum(k=='PROVIDER_RESPONSE' for k,b in tape.events),2)
        self.assertEqual(sum(k=='CONFIGURATION' for k,b in tape.events),2)

    def test_each_read_retry_enters_the_existing_physical_admission_and_never_retries_403(self):
        calls=[];controls=[]
        def read(request):
            calls.append(request)
            if len(calls)==1:raise Throttle('capacity')
            return {'value':1}
        with patch.object(retry.time,'sleep',lambda seconds:None):
            self.assertEqual(retry.retry_read({'query':'read'},read,controls.append),{'value':1})
        self.assertEqual(len(calls),2);self.assertEqual(calls[0],calls[1]);self.assertEqual(len(controls),1)
        with self.assertRaises(Denied):retry.retry_read({},lambda request:(_ for _ in ()).throw(Denied('no permission')),controls.append)
        self.assertEqual(len(controls),1)

if __name__=='__main__':unittest.main()
