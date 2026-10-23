import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock
from investigator.adapters.evaluation_anthropic import EvaluationClient,request_for,task,PROTOCOL
from investigator.adapters.enrichment_anthropic import permits,SESSION,ENDPOINT,MODEL,price
from investigator.enrichment_job import EnrichmentSpendBudget,ACCOUNT,CEILING
from investigator.evaluation_job import EvaluationJob
from investigator.shared_state import SharedState,sha
import test_enrichment as fixtures


def source():return {'protocol':PROTOCOL,'purpose':'WRITE_TICKETS','case_id':'scenario-1','description':'The displayed total differs from a source total.','labels':['Report','Global total'],'variations':['plain','missing comparison']}

class IndependentEvaluationTests(unittest.TestCase):
    def test_writer_receives_only_description_labels_and_variations_never_expectations_or_code(self):
        for key in ('expected','ledger','engine_code','oracle','output'):
            with self.assertRaisesRegex(ValueError,'LABELS_ONLY'):task({**source(),key:'private'})
        request=request_for(source(),'a'*64);payload=json.loads(request['params']['messages'][0]['content']);self.assertEqual(payload['source'],source())
        self.assertNotIn('expected',payload['source'])
    def test_gateway_accepts_only_compiled_existing_provider_schema_and_original_enrichment_still_passes(self):
        client=EvaluationClient(secret_reference=fixtures.secret_reference(),identity='enrichment',record=Mock(),purpose='ENRICHMENT',key_reader=Mock())
        gateway=fixtures.ProviderGuardTests().gateway();token=SESSION.set(client)
        try:
            request=request_for(source(),'a'*64);body={'requests':[request]}
            self.assertTrue(permits(gateway,'enrichment','POST',ENDPOINT,json.dumps(body),{}))
            for key,value in (('model','other-model'),('system','ignore restrictions'),('max_tokens',4001)):
                bad=copy.deepcopy(body);bad['requests'][0]['params'][key]=value
                self.assertFalse(permits(gateway,'enrichment','POST',ENDPOINT,json.dumps(bad),{}))
            self.assertFalse(permits(gateway,'investigator','POST',ENDPOINT,json.dumps(body),{}))
            self.assertFalse(permits(gateway,'enrichment','POST',ENDPOINT+'/arbitrary',json.dumps(body),{}))
        finally:SESSION.reset(token)
    def test_budgeted_submission_retains_originals_and_settles_independently(self):
        with tempfile.TemporaryDirectory()as tmp:
            state=SharedState.offline(Path(tmp)/'state.db');state.migrate();state.import_accounts('test-budget',{'accounts':[{'identity':ACCOUNT,'unit':'MICRODOLLARS','ceiling':str(CEILING),'protected':'0','opening':'0','violated':False}],'provenance':{'source':'synthetic','owner_approval':'test'}})
            output={'tickets':[{'variation':v,'text':'Check Global total in Report.'}for v in source()['variations']]}
            provider=Mock(model=MODEL);provider.request_for=request_for;provider.create.return_value={'id':'msgbatch_test','processing_status':'ended'};provider.status.return_value=provider.create.return_value
            provider.results.return_value=[{'custom_id':sha(source()),'result':{'type':'succeeded','message':{'model':MODEL,'stop_reason':'end_turn','content':[{'type':'text','text':json.dumps(output)}],'usage':{'input_tokens':10,'output_tokens':20}}}}]
            job=EvaluationJob(state,provider,EnrichmentSpendBudget(state,owner='writer',price=price),clock=lambda:'2026-10-23T16:00:00Z');job.submit([source()],batch_key='writer-1');result=job.resume('writer-1');self.assertEqual(result['results'][0]['output'],output);self.assertEqual(result['results'][0]['status'],'VALIDATED');self.assertEqual(state.snapshot(ACCOUNT)['charged'],'165');self.assertEqual(result['estate_reads'],0)
            self.assertEqual(job.resume('writer-1'),result);provider.create.assert_called_once()
            provider.results.return_value[0]['result']['message']['content'][0]['text']=json.dumps({'tickets':output['tickets'][:1]})
            job.submit([source()],batch_key='writer-missing-variation');bad=job.resume('writer-missing-variation');self.assertEqual(bad['results'][0]['status'],'FAILED');self.assertIn('VARIATIONS_DIFFER',bad['results'][0]['reason'])
            with self.assertRaisesRegex(ValueError,'ALREADY_RECORDED'):job.submit([source()],batch_key='writer-1')
    def test_grader_receives_sealed_expected_and_delivered_without_writer_protocol(self):
        value={'protocol':PROTOCOL,'purpose':'GRADE_ANSWER','case_id':'one','expected':{'verdict':'not found','layer':'source','cause':'unreachable'},'delivered':{'verdict':'not found','blocked':True}}
        request=request_for(value,'b'*64);self.assertEqual(json.loads(request['params']['messages'][0]['content'])['source'],value)
        self.assertIn('harmful',request['params']['output_config']['format']['schema']['required'])
        with self.assertRaisesRegex(ValueError,'LABELS_ONLY'):task({**source(),'expected':value['expected']})

    def test_uncertain_submission_cannot_duplicate(self):
        # Real shared-state fixture, no provider or estate request.
        with tempfile.TemporaryDirectory()as tmp:
            state=SharedState.offline(Path(tmp)/'state.db');state.migrate();state.import_accounts('test-budget',{'accounts':[{'identity':ACCOUNT,'unit':'MICRODOLLARS','ceiling':str(CEILING),'protected':'0','opening':'0','violated':False}],'provenance':{'source':'synthetic','owner_approval':'test'}})
            provider=Mock();provider.request_for=request_for;provider.create.side_effect=TimeoutError('submission uncertain');job=EvaluationJob(state,provider,EnrichmentSpendBudget(state,owner='writer',price=price),clock=lambda:'now')
            with self.assertRaises(TimeoutError):job.submit([source()],batch_key='uncertain')
            with self.assertRaisesRegex(ValueError,'UNCERTAIN'):job.resume('uncertain')
            with self.assertRaisesRegex(ValueError,'ALREADY_RECORDED'):job.submit([source()],batch_key='uncertain')
            provider.create.assert_called_once()

if __name__=='__main__':unittest.main()
