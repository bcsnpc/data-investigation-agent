"""Fixed-schema enrichment, independent spending and human priority regression tests."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock,patch
from investigator.enrichment import EnrichmentStore,validate_output,export_csv,import_csv,cache_key
from investigator.enrichment_job import EnrichmentJob,EnrichmentSpendBudget,ACCOUNT,CEILING
from investigator.adapters.enrichment_anthropic import BatchClient,price,request_for,permits,SESSION,ENDPOINT,MODEL
from investigator.adapters.enrichment_stub import RecordedEnrichmentStub
from investigator.shared_state import SharedState,StateConflict
from investigator.estate_graph_repository import GraphRepository
from investigator.live_gateway import Gateway,GatewayDenied
from enrich_estate import plan,recorded_stub
from test_estate_graph import graph,T0,T1


def source(subject='measure',definition='SUM([units])'):
    return {'estate':'estate','subject':subject,'kind':'MEASURE','definition_hash':hashlib.sha256(definition.encode()).hexdigest(),
        'definition':definition,'neighbours':[{'id':'column','kind':'COLUMN','label':'Units'}],'evidence_ids':['definition-receipt']}


def output():
    return {'business_meaning':'Quantity handled by the selected activity.','synonyms':['quantity','handled units'],
        'calculation_explanation':'Adds the retained units column.','hidden_logic':[],
        'proposed_links':[{'target':'column','relationship':'COMPUTED_FROM','start':4,'end':11,'quote':'[units]'}]}


def secret_reference():
    return {'vault_url':'https://example.vault.azure.net','secret_name':'anthropic-api-key','secret_version':'a'*32,
        'identity':{'mode':'managed_identity','tenant_id':'11111111-1111-1111-1111-111111111111','client_id':'22222222-2222-2222-2222-222222222222','principal_id':'33333333-3333-3333-3333-333333333333'}}


class EnrichmentTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.state=SharedState.offline(Path(self.tmp.name)/'state.sqlite');self.state.migrate();self.store=EnrichmentStore(self.state)
        self.state.import_accounts('test-enrichment',{'accounts':[
            {'identity':ACCOUNT,'unit':'MICRODOLLARS','ceiling':str(CEILING),'protected':'0','opening':'0','violated':False},
            {'identity':'model-microdollars:2026-10','unit':'MICRODOLLARS','ceiling':'40000000','protected':'0','opening':'12','violated':False}],
            'provenance':{'source':'synthetic'}})

    def job(self,outputs=None):
        provider=RecordedEnrichmentStub(outputs or {'measure':output()})
        budget=EnrichmentSpendBudget(self.state,owner='test-worker',price=price)
        return EnrichmentJob(self.state,provider,budget,clock=lambda:T1)

    def test_fixed_schema_span_and_target_validator(self):
        bad=output();bad['status']='VERIFIED'
        with self.assertRaisesRegex(ValueError,'OUTPUT_SHAPE'):validate_output(bad,source())
        bad=output();bad['proposed_links'][0]['quote']='different'
        with self.assertRaisesRegex(ValueError,'NOT_VERBATIM'):validate_output(bad,source())
        bad=output();bad['proposed_links'][0]['target']='invented'
        with self.assertRaisesRegex(ValueError,'NOT_IN_INPUT'):validate_output(bad,source())

    def test_stub_end_to_end_separate_account_and_cached_second_pass(self):
        job=self.job();before=self.state.snapshot('model-microdollars:2026-10')['charged']
        job.submit([source()],batch_key='stub-1');result=job.resume('stub-1')
        self.assertEqual(result['status'],'COMPLETED');self.assertEqual(result['recording_class'],'RECORDED_STUB')
        self.assertEqual(self.state.snapshot(ACCOUNT)['charged'],'90')
        self.assertEqual(self.state.snapshot('model-microdollars:2026-10')['charged'],before)
        self.assertEqual(job.submit([source()],batch_key='stub-2')['status'],'CACHED')
        row=self.store.projection('estate','measure',source()['definition_hash'])
        self.assertEqual(row['status'],'INFERRED');self.assertEqual(row['proposed_links'][0]['status'],'INFERRED')
        self.assertFalse(row['stale_definition'])

    def test_changed_definition_misses_cache(self):
        job=self.job();job.submit([source()],batch_key='one');job.resume('one')
        changed=source(definition='SUM([units]) + 0')
        self.assertIsNone(self.store.cached(changed));self.assertTrue(self.store.projection('estate','measure',changed['definition_hash'])['stale_definition'])

    def test_human_changes_win_and_no_graph_link_promotion(self):
        job=self.job();job.submit([source()],batch_key='one');job.resume('one')
        edited=output();edited['business_meaning']='Owner corrected meaning.'
        self.store.confirm(source(),edited,at=T1,reviewer='Business owner')
        row=self.store.apply(source(),output(),at=T1,producer='model',recording_class='EXACT',evidence_ids=['receipt'])
        self.assertEqual(row['business_meaning'],'Owner corrected meaning.')
        self.assertEqual(row['status'],'HUMAN_CONFIRMED');self.assertEqual(row['proposed_links'][0]['status'],'INFERRED')
        # An updated definition cannot silently overwrite confirmed owner prose.
        row=self.store.apply(source(definition='SUM([units]) + 0'),output(),at=T1,producer='model',recording_class='EXACT',evidence_ids=['receipt'])
        self.assertEqual(row['business_meaning'],'Owner corrected meaning.')

    def test_csv_roundtrip_records_reviewer_and_validates_all_rows_before_write(self):
        job=self.job();job.submit([source()],batch_key='one');job.resume('one')
        text=export_csv([self.store.projection('estate','measure')])
        text=text.replace('Quantity handled by the selected activity.','Owner meaning.')
        result=import_csv(self.store,text,at=T1,reviewer='Owner')
        self.assertEqual(result[0]['status'],'HUMAN_CONFIRMED')
        self.assertEqual(result[0]['provenance']['human_reviewer'],'Owner')
        with self.assertRaisesRegex(ValueError,'CSV_COLUMNS'):import_csv(self.store,'subject\nx\n',at=T1,reviewer='Owner')

    def test_budget_refusal_before_provider_and_no_worker_account_creation(self):
        with self.state.transaction() as db:db.execute('UPDATE state_accounts SET opening=? WHERE identity=?',(str(CEILING),ACCOUNT))
        job=self.job();job.provider.create=Mock()
        with self.assertRaisesRegex(StateConflict,'CAP_REACHED'):job.submit([source()],batch_key='over')
        job.provider.create.assert_not_called()
        with self.assertRaisesRegex(ValueError,'SEPARATE_ENRICHMENT'):EnrichmentSpendBudget(self.state,owner='test',price=price,account='model-microdollars:2026-10')

    def test_unknown_usage_keeps_full_reservation(self):
        budget=EnrichmentSpendBudget(self.state,owner='test-worker',price=price)
        budget.reserve(request_for(source(),'a'*64),'one');before=budget.snapshot()['charged']
        budget.settle('one',None)
        self.assertEqual(budget.snapshot()['charged'],before)
        self.assertEqual(budget.snapshot()['reservations'][0]['status'],'UNCERTAIN')

    def test_output_rejection_is_charged_and_not_cached(self):
        bad=output();bad['proposed_links'][0]['quote']='not verbatim'
        job=self.job({'measure':bad});job.submit([source()],batch_key='bad');result=job.resume('bad')
        self.assertEqual(result['status'],'PARTIAL');self.assertEqual(result['results'][0]['status'],'REJECTED')
        self.assertEqual(self.state.snapshot(ACCOUNT)['charged'],'90');self.assertIsNone(self.store.cached(source()))

    def test_resubmission_and_unknown_result_identity_refused(self):
        job=self.job();job.submit([source()],batch_key='one')
        with self.assertRaisesRegex(ValueError,'ALREADY_ADMITTED'):job.submit([source()],batch_key='one')
        job.provider.results=Mock(return_value=[{'custom_id':'wrong','result':{'type':'expired'}}])
        with self.assertRaisesRegex(ValueError,'IDENTITY_DIFFERS'):job.resume('one')
        self.assertIsNone(self.store.cached(source()))

    def test_definition_change_enqueues_in_same_graph_transaction(self):
        repo=GraphRepository(self.state);repo.migrate();repo.replace(graph())
        rows=self.state.list('enrichment_queue');self.assertEqual(len(rows),1)
        repo.replace(graph());self.assertEqual(len(self.state.list('enrichment_queue')),1)
        changed=copy.deepcopy(graph());changed.update(definition_hash='b'*64,observed_at=T1);repo.replace(changed)
        self.assertEqual(len(self.state.list('enrichment_queue')),2)

    def test_stub_cannot_be_written_to_live_postgresql(self):
        fake=Mock(backend='postgresql',mode='live')
        with self.assertRaisesRegex(ValueError,'STUB_PRIVATE_OFFLINE_ONLY'):
            EnrichmentJob(fake,RecordedEnrichmentStub({}),Mock(),clock=lambda:T1)
        fake.put.assert_not_called()

    def test_plan_has_no_reads_or_model_calls(self):
        self.assertEqual(plan([source()])['model_calls'],0)
        self.assertEqual(plan([source()])['estate_requests'],0)


class ProviderGuardTests(unittest.TestCase):
    def client(self,record=None):
        return BatchClient(secret_reference=secret_reference(),identity='enrichment',record=record or Mock(),purpose='ENRICHMENT',key_reader=Mock(return_value='secret-in-memory-not-recorded'))

    def gateway(self):
        return Gateway({'version':1,'live_enabled':True,'identities':{'enrichment':{'role':'enrichment','enrichment_batches':{'provider':'anthropic','purpose':'ENRICHMENT_ONLY','model':MODEL}}}})

    def test_price_exact_batch_rate_rounds_up_and_rejects_float(self):
        self.assertEqual(price(1,0),2);self.assertEqual(price(10,10),90)
        with self.assertRaises(ValueError):price(1.0,0)

    def test_dedicated_provider_not_available_to_investigator(self):
        with self.assertRaisesRegex(ValueError,'ONLY_FOR_ENRICHMENT'):
            BatchClient(secret_reference=secret_reference(),identity='agent',record=Mock(),purpose='INVESTIGATION')

    def test_gateway_allows_only_compiled_batch_and_response_bound_results(self):
        client=self.client();gateway=self.gateway();token=SESSION.set(client)
        self.addCleanup(SESSION.reset,token)
        body={'requests':[request_for(source(),'a'*64)]}
        self.assertTrue(permits(gateway,'enrichment','POST',ENDPOINT,json.dumps(body),{}))
        self.assertFalse(permits(gateway,'enrichment','GET',ENDPOINT+'/msgbatch_unrelated',None,{}))
        client.admitted.add('msgbatch_one')
        self.assertTrue(permits(gateway,'enrichment','GET',ENDPOINT+'/msgbatch_one',None,{}))
        self.assertFalse(permits(gateway,'enrichment','GET',ENDPOINT+'/msgbatch_one/results',None,{}))
        client.ended.add('msgbatch_one')
        self.assertTrue(permits(gateway,'enrichment','GET',ENDPOINT+'/msgbatch_one/results',None,{}))
        body['requests'][0]['params']['model']='unapproved-model'
        self.assertFalse(permits(gateway,'enrichment','POST',ENDPOINT,json.dumps(body),{}))
        self.assertFalse(permits(gateway,'enrichment','POST','https://api.anthropic.com/v1/messages',json.dumps(body),{}))

    def test_provider_record_replay_never_opens_network_or_key_vault_on_replay(self):
        import io
        from contextlib import closing
        from investigator.process_tape import ACTIVE
        class MemoryTape:
            replaying=False
            def __init__(self):self.events=[]
            def event(self,kind,body):self.events.append((kind,body))
            def take(self,kind):
                recorded,body=self.events.pop(0)
                if recorded!=kind:raise AssertionError('tape kind differs')
                return body
        tape=MemoryTape();marker=ACTIVE.set(tape)
        try:
            raw=json.dumps({'id':'msgbatch_replay','processing_status':'in_progress'}).encode()
            with patch('investigator.live_gateway.open_http',return_value=closing(io.BytesIO(raw))):
                recorded=self.client().create([request_for(source(),'a'*64)])
            tape.replaying=True
            client=self.client();client.key_reader=Mock(side_effect=AssertionError('Key Vault must not run on replay'))
            with patch('investigator.live_gateway.open_http',side_effect=AssertionError('network must not run on replay')):
                replayed=client.create([request_for(source(),'a'*64)])
            self.assertEqual(recorded,replayed);self.assertEqual(tape.events,[])
            client.key_reader.assert_not_called()
        finally:ACTIVE.reset(marker)

    def test_transport_records_no_api_key_or_headers(self):
        import io
        from contextlib import closing
        records=[]
        client=self.client(record=lambda k,v:records.append((k,v)))
        raw=json.dumps({'id':'msgbatch_test','processing_status':'in_progress'}).encode()
        with patch('investigator.live_gateway.open_http',return_value=closing(io.BytesIO(raw))) as send:
            result=client.create([request_for(source(),'a'*64)])
        self.assertEqual(result['id'],'msgbatch_test')
        saved=json.dumps(records)
        self.assertNotIn('secret-in-memory-not-recorded',saved);self.assertNotIn('x-api-key',saved)
        self.assertEqual(send.call_args.args[1].get_header('X-api-key'),'secret-in-memory-not-recorded')


if __name__=='__main__':unittest.main()
