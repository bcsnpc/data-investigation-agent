"""Synthetic sealed provider success followed by local accounting failures."""
import base64,copy,json,sqlite3,tempfile,unittest,traceback
from contextlib import contextmanager,closing
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from investigator import local_accounting as account,process_tape as journal,model_transport_retry as retry
from investigator.model_spend import admission,SpendBudget

class SealedJournal:
    def __init__(self,events=None,pin=True):
        self.replaying=events is not None;self.events=copy.deepcopy(events or []);self.index=0
        self.bootstrap={'state':{'local_accounting':account.PIN} if pin else {}}
    def event(self,kind,body):
        if self.replaying:
            if self.take(kind)!=body:raise journal.TapeError('Synthetic sealed body differs')
        else:
            self.events.append({'ordinal':len(self.events)+1,'kind':kind,'at':1,
                'body':base64.b64encode(body).decode(),'sha256':journal.sha(body)})
    def take(self,kind):
        e=self.events[self.index]
        if e['kind']!=kind:raise journal.TapeError('Synthetic order differs')
        b=journal.validate_event(e,self.index+1);self.index+=1;return b
    def peek(self,kind):
        if self.index>=len(self.events) or self.events[self.index]['kind']!=kind:return None
        return journal.validate_event(self.events[self.index],self.index+1)

class LocalAccountingTests(unittest.TestCase):
    def run_owner(self,tape,inject):
        decisions=[];attempts=[]
        @contextmanager
        def db():
            attempts.append(1)
            if inject and len(attempts)==1:raise sqlite3.OperationalError('database is locked')
            yield SimpleNamespace(execute=lambda statement:None)
        def settle(db,sid,key,usage,uncertain=False):
            decision={'usage':usage,'uncertain':uncertain};decisions.append(decision)
            journal.event('BUDGET',decision)
        governor=SimpleNamespace(runtime=SimpleNamespace(db=db),settle=settle)
        owner=retry.Scope(governor,'synthetic','one',20,1500,lambda *a:None,{},None,lambda:1)
        request={'model':'fixture','input':'one synthetic question','max_output_tokens':1500}
        provider={'status':200,'body':{'usage':{'input_tokens':2,'output_tokens':3},'status':'completed'}}
        def invoke(body):
            journal.event('PROVIDER_REQUEST',body);journal.event('PROVIDER_RESPONSE',provider)
            return SimpleNamespace(usage=provider['body']['usage'])
        token=journal.ACTIVE.set(tape);owner_token=retry.ACTIVE.set(owner)
        try:
            with self.assertRaisesRegex(sqlite3.OperationalError,'database is locked'):retry.dispatch(request,invoke)
        finally:retry.ACTIVE.reset(owner_token);journal.ACTIVE.reset(token)
        return decisions
    def test_completed_http_body_owner_failure_replays_unknown_settlement_without_mutating_seal(self):
        original=SealedJournal();self.assertEqual(self.run_owner(original,True),[{'usage':None,'uncertain':True}])
        sealed=journal.bytes_of(original.events);replay=SealedJournal(original.events)
        self.assertEqual(self.run_owner(replay,False),[{'usage':None,'uncertain':True}])
        self.assertEqual(replay.index,len(replay.events));self.assertEqual(journal.bytes_of(original.events),sealed)
        physical=[e for e in original.events if e['kind'].startswith('PROVIDER_')]
        self.assertEqual([journal.validate_event(e,e['ordinal']) for e in physical],
                         [journal.validate_event(e,e['ordinal']) for e in replay.events if e['kind'].startswith('PROVIDER_')])
    def test_spend_failure_retains_full_bound_and_replays_without_private_dollar_database(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'dollars.sqlite';tape=SealedJournal();real=SpendBudget.settle
            count=[]
            def fail_once(budget,identity,usage=None):
                count.append(1)
                if len(count)==1:raise sqlite3.OperationalError('database is locked')
                return real(budget,identity,usage)
            token=journal.ACTIVE.set(tape)
            try:
                with patch.dict('os.environ',{'INVESTIGATOR_MODEL_SPEND_DB':str(path),'INVESTIGATOR_MODEL_SPEND_MICRODOLLARS':'1000000'}),patch.object(SpendBudget,'settle',fail_once):
                    with self.assertRaises(sqlite3.OperationalError),admission({'input':'synthetic','max_output_tokens':1500}) as settle:
                        journal.event('PROVIDER_RESPONSE',{'status':200,'usage':{'input_tokens':2,'output_tokens':3}})
                        settle({'input_tokens':2,'output_tokens':3})
            finally:journal.ACTIVE.reset(token)
            with closing(sqlite3.connect(path)) as db:
                row=db.execute('SELECT status,reserved,charged FROM model_spend').fetchone()
            self.assertEqual(row[0],'UNCERTAIN');self.assertEqual(row[1],row[2])
            sealed=journal.bytes_of(tape.events);replay=SealedJournal(tape.events);token=journal.ACTIVE.set(replay)
            try:
                with patch.object(SpendBudget,'__init__',side_effect=AssertionError('No private DB in replay')):
                    with self.assertRaises(sqlite3.OperationalError),admission({'input':'synthetic','max_output_tokens':1500}) as settle:
                        journal.event('PROVIDER_RESPONSE',{'status':200,'usage':{'input_tokens':2,'output_tokens':3}})
                        settle({'input_tokens':2,'output_tokens':3})
            finally:journal.ACTIVE.reset(token)
            self.assertEqual(replay.index,len(replay.events));self.assertEqual(journal.bytes_of(tape.events),sealed)
    def test_unknown_sqlite_message_is_withheld_and_old_tape_has_no_new_events(self):
        tape=SealedJournal();token=journal.ACTIVE.set(tape)
        try:
            with self.assertRaises(sqlite3.OperationalError) as caught:account.boundary('MODEL_OWNER_SETTLE',lambda:(_ for _ in ()).throw(sqlite3.OperationalError('secret literal')))
        finally:journal.ACTIVE.reset(token)
        self.assertNotIn(b'secret literal',journal.bytes_of(tape.events))
        self.assertNotIn('secret literal',''.join(traceback.format_exception(caught.exception)))
        old=SealedJournal(pin=False);token=journal.ACTIVE.set(old)
        try:self.assertEqual(account.boundary('MODEL_OWNER_SETTLE',lambda:16),16)
        finally:journal.ACTIVE.reset(token)
        self.assertEqual(old.events,[])
    def test_sqlite_code_and_safe_message_survive_but_provider_body_changes_still_refuse(self):
        error=sqlite3.OperationalError('database is locked');error.sqlite_errorcode=5;error.sqlite_errorname='SQLITE_BUSY'
        tape=SealedJournal();token=journal.ACTIVE.set(tape)
        try:
            with self.assertRaises(sqlite3.OperationalError):account.boundary('MODEL_OWNER_SETTLE',lambda:(_ for _ in ()).throw(error))
        finally:journal.ACTIVE.reset(token)
        replay=SealedJournal(tape.events);token=journal.ACTIVE.set(replay)
        try:
            with self.assertRaises(sqlite3.OperationalError) as caught:account.boundary('MODEL_OWNER_SETTLE',lambda:None)
        finally:journal.ACTIVE.reset(token)
        self.assertEqual(caught.exception.sqlite_errorcode,5);self.assertEqual(caught.exception.sqlite_errorname,'SQLITE_BUSY')
        original=SealedJournal();original.event('PROVIDER_REQUEST',journal.bytes_of({'input':'sealed'}))
        with self.assertRaises(journal.TapeError):SealedJournal(original.events).event('PROVIDER_REQUEST',journal.bytes_of({'input':'changed'}))
    def test_real_projected_tape_retains_accounting_failure_and_never_writes_raw_secret(self):
        from investigator.privacy_projection import Projection,canonical
        from investigator.privacy_tape import PrivacyTape
        policy={'tape_class':'PRIVACY_PROJECTED','version':'estate-privacy-projection-v1',
                'estate_id':'synthetic','key_reference':'secret/synthetic','columns':['person']}
        key=lambda _:b'synthetic-in-memory-key-32-bytes!!'
        secret='PRIVATE_PERSON_ACCOUNTING_TEST'
        bootstrap={'state':{'local_accounting':account.PIN,'accounting_version':3}}
        request={'input':{'person':secret}};response={'status':200,'person':secret,'usage':{'input_tokens':2,'output_tokens':3}}
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'projected.json';projection=Projection(policy,key);projection.bind('person',secret)
            tape=PrivacyTape(path,projection);tape.event('BOOTSTRAP',canonical(bootstrap));token=journal.ACTIVE.set(tape)
            try:
                journal.event('PROVIDER_REQUEST',request);journal.event('PROVIDER_RESPONSE',response)
                with self.assertRaises(sqlite3.OperationalError):
                    account.boundary('MODEL_OWNER_SETTLE',lambda:(_ for _ in ()).throw(sqlite3.OperationalError(secret)))
                journal.event('BUDGET',{'usage':None,'uncertain':True})
            finally:journal.ACTIVE.reset(token)
            tape.finish({'person':secret,'settlement':'UNCERTAIN'})
            sealed=path.read_bytes();self.assertNotIn(secret.encode(),sealed)
            replay_projection=Projection(policy,key);replay_projection.bind('person',secret)
            replay=PrivacyTape(path,replay_projection,replay=True);replay.event('BOOTSTRAP',canonical(bootstrap))
            token=journal.ACTIVE.set(replay)
            try:
                journal.event('PROVIDER_REQUEST',request);journal.event('PROVIDER_RESPONSE',response)
                with self.assertRaisesRegex(sqlite3.OperationalError,'message withheld'):
                    account.boundary('MODEL_OWNER_SETTLE',lambda:self.fail('Recorded failure must inject before producer'))
                journal.event('BUDGET',{'usage':None,'uncertain':True})
            finally:journal.ACTIVE.reset(token)
            outputs=replay.finish({'person':secret,'settlement':'UNCERTAIN'})
            self.assertEqual(path.read_bytes(),sealed);self.assertNotIn(secret.encode(),canonical(outputs))
            self.assertEqual([p.name for p in Path(folder).iterdir()],['projected.json'])

if __name__=='__main__':unittest.main()
