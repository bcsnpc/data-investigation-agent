"""Cited values, false-question regressions and existing-reader native ports."""
from copy import deepcopy
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock,patch
import unittest
from investigator.grounded_answers import finding,question
from investigator.adapters.investigative_native import NativeQueries
from investigator.live_gateway import Gateway,GatewayDenied,validate_dax
from investigator.investigative_queries import validate
from test_round23_intake_queries import sql_objects,dax_objects


def case():
    q={'id':'q','status':'SUCCEEDED','layer':'gold','time':'2026-11-01T00:00:00Z',
       'text':'SELECT 950 AS untrusted_literal','parameters':[{'value':'950'}],
       'result':{'rows':[{'quantity':7}]}}
    return {'intake':{},'context':{'path':{'nodes':[{'id':'gold','label':'Serving'},
                {'id':'report','label':'Daily Sales'}]}},'queries':[q],'evidence':{}}


class AnswerTests(unittest.TestCase):
    def test_record_presence_source_comparison_uses_existing_trace_and_labels_its_scope(self):
        value=case();value['intake']={'issue_type':'RECORD_MISSING'}
        value['context'].update(system_of_record={'declared':True,'reachable':True,'layer':'source','asset_id':'source-table'},
            layers={'gold':{'label':'Serving'},'source':{'label':'Application'}})
        value['queries'][0]['result']['rows']=[{'movement_id':2,'units':7}]
        source=deepcopy(value['queries'][0]);source.update(id='source-q',layer='source',asset_ids=['source-table']);value['queries'].append(source)
        value['evidence']['trace']={'tool':'record_trace','result':{'key':'2','layers':[
            {'layer':'gold','query_id':'q','presence':'PRESENT','matching_rows':1,'truncated':False},
            {'layer':'source','query_id':'source-q','presence':'PRESENT','matching_rows':1,'truncated':False}]}}
        value['evidence']['definition']={'tool':'get_definition','result':{'content':'retained copy and visual definition','provenance':{'source':'retained'}}}
        args=self.proposal();args.update(verdict='as designed',evidence_ids=['trace','definition'])
        self.assertIn('key presence and matching row count',finding(args,value)['business'])
        value['evidence']['trace']['result']['layers'][1]['presence']='UNAVAILABLE'
        with self.assertRaisesRegex(ValueError,'unread layers'):finding(args,value)
        value['evidence']['trace']['result']['layers'][1].update(presence='PRESENT',matching_rows=2)
        with self.assertRaisesRegex(ValueError,'unread layers'):finding(args,value)

    def test_guided_failed_job_renders_cited_path_run_details_in_both_outputs(self):
        value=case();value['context']['path']['nodes'].append({'id':'pipeline','kind':'PIPELINE','label':'Actual copy'})
        fact={'subject':'pipeline','kind':'JOB_RUN','state':'OBSERVED','observed_at':'2026-10-27T01:02:00Z',
            'value':{'run_id':'native-42','status':'FAILED','start':'2026-10-27T01:00:00Z','end':'2026-10-27T01:01:00Z','error':'Actual native failure'}}
        unrelated={**deepcopy(fact),'subject':'outside-path','value':{**fact['value'],'run_id':'unrelated-run'}}
        value['evidence']['runtime']={'tool':'get_job_runs','result':{'status':'OBSERVED','source':'native-subject-history','observed_at':fact['observed_at'],'facts':[fact,unrelated]}}
        args=self.proposal();args.update(verdict='failed job',evidence_ids=['q','runtime'])
        result=finding(args,value)
        for text in (result['business'],' '.join(result['technical']['operational_details'])):
            for field in ('Actual copy','native-42','FAILED','2026-10-27T01:00:00Z','2026-10-27T01:01:00Z','Actual native failure'):self.assertIn(field,text)
            self.assertNotIn('unrelated-run',text)

    def proposal(self):return {'verdict':'observed value','cause':'The native quantity is 7.',
                               'numbers':[7],'checked':['gold'],'evidence_ids':['q']}
    def test_values_grounded_and_ui_uses_names(self):
        result=finding(self.proposal(),case())
        self.assertIn('Serving',result['business']);self.assertIn('Numbers: 7',result['business'])
        self.assertEqual(result['technical']['queries'][0]['text'],'SELECT 950 AS untrusted_literal')
    def test_query_literal_and_parameters_are_not_observed_results(self):
        args=self.proposal();args['numbers']=[950]
        with self.assertRaisesRegex(ValueError,'NUMBER_NOT_IN'):finding(args,case())
    def test_model_text_cannot_launder_itself_through_evidence_fetch(self):
        value=case();value['evidence']['model']={'kind':'MODEL_RESPONSE','response':{'made_up':999}}
        args=self.proposal();args['evidence_ids']=['model']
        with self.assertRaisesRegex(ValueError,'NOT_NATIVE'):finding(args,value)
        value['evidence']['fetch']={'tool':'get_evidence','result':value['evidence']['model']};args['evidence_ids']=['fetch']
        with self.assertRaises(ValueError):finding(args,value)
    def test_empty_is_not_zero_and_precision_qualification_in_both_outputs(self):
        value=case();value['queries'][0]['result']['rows']=[{'quantity':None}]
        args=self.proposal();args['numbers']=[0]
        with self.assertRaises(ValueError):finding(args,value)
        args['numbers']=[None];self.assertIn('BLANK',finding(args,value)['business'])
        value=case();value['intake']['reported_figure']={'state':'NUMBER','value':'7','precision':0}
        result=finding(self.proposal(),value)
        self.assertIn('weaker',result['business']);self.assertIn('weaker',str(result['technical']['qualifications']))
    def test_failed_query_cannot_prove_technical_finding_or_absence(self):
        value=case();value['queries'][0].update(status='ERROR',error='native connection failed')
        with self.assertRaisesRegex(ValueError,'FAILED_QUERY'):finding(self.proposal(),value)
        args=self.proposal();args.update(verdict='not found',numbers=[])
        self.assertIn('not found',finding(args,value)['business'])
    def test_source_consistency_cannot_be_claimed_from_one_recreated_value(self):
        args=self.proposal();args['verdict']='as designed'
        with self.assertRaisesRegex(ValueError,'SOURCE_CONSISTENCY_UNESTABLISHED'):finding(args,case())
        value=case();value['context'].update(system_of_record={'declared':True,'reachable':True,'layer':'source'},
                                            layers={'gold':{'label':'Serving'},'source':{'label':'Application'}})
        q=deepcopy(value['queries'][0]);q.update(id='source-q',layer='source')
        value['queries'].append(q);args['evidence_ids'].append('source-q')
        with self.assertRaisesRegex(ValueError,'RETAINED_DEFINITION'):finding(args,value)
        value['evidence']['definition']={'tool':'get_definition','result':{'content':'SUM(Items.quantity)',
                                         'provenance':{'source':'retained'}}}
        args['evidence_ids'].append('definition')
        self.assertIn('query-bound snapshot',finding(args,value)['business'])
        value['queries'][1]['result']['rows'][0]['quantity']=8
        with self.assertRaisesRegex(ValueError,'native values differ'):finding(args,value)
    def test_source_consistency_uses_declared_source_object_not_another_table(self):
        args=self.proposal();args.update(verdict='as designed',evidence_ids=['q','definition'])
        value=case();value['context'].update(system_of_record={'declared':True,'reachable':True,'layer':'gold','asset_id':'declared-source'},layers={'gold':{'label':'Serving'}})
        value['queries'][0]['asset_ids']=['other-source']
        value['evidence']['definition']={'tool':'get_definition','result':{'content':'SUM(Items.quantity)','provenance':{'source':'retained'}}}
        with self.assertRaisesRegex(ValueError,'declared source object was not queried'):finding(args,value)
        value['queries'][0]['asset_ids']=['declared-source']
        self.assertIn('query-bound snapshot',finding(args,value)['business'])

    def test_false_duplicate_report_questions_use_fixed_grounded_prose(self):
        for bad in ('There are two reports named Daily Sales; which one?',
                    'I found two duplicate Daily Sales reports; choose one.'):
            args={'question':bad,'choices':['Daily Sales','A spreadsheet'],'reason':'UNREADABLE_USER_FACT','evidence_ids':['q']}
            result=question(args,case())
            self.assertNotIn('two',result['question']);self.assertNotIn('duplicate',result['question'])
            self.assertEqual(result['choices'],['Daily Sales','A spreadsheet'])
    def test_internal_id_choice_and_reasked_report_rejected(self):
        args={'question':'x','choices':['gold','A spreadsheet'],'reason':'UNREADABLE_USER_FACT','evidence_ids':['q']}
        with self.assertRaises(ValueError):question(args,case())
        value=case();value['intake']['report']='report';args.update(field='REPORT',choices=['Daily Sales','A spreadsheet'])
        with self.assertRaisesRegex(ValueError,'REASKS'):question(args,value)


class NativeTests(unittest.TestCase):
    def test_sql_uses_existing_reader_and_read_only_guard_with_no_attestation_wrapper(self):
        config={'fabric':{'sql_reader':{'mode':'federated_reader','principal_id':'same-reader'}}}
        routes={'gold':{'kind':'FABRIC_SQL','config':config,'database':'gold-db','asset_ids':['table'],'objects':sql_objects()}}
        fabric=Mock(return_value={'rows':[{'id':1}],'read_only_verified':True})
        native=NativeQueries(routes,source=Mock(),fabric=fabric,dax=Mock(),offline=True)
        bound=validate('WITH q AS (SELECT id FROM dbo.Items) SELECT id FROM q',{'dialect':'T-SQL','objects':sql_objects()})
        result=native('gold',bound,timeout_seconds=30)
        self.assertEqual(result['rows'],[{'id':1}])
        self.assertEqual(fabric.call_args.kwargs,{'attestation':False})
        sent=fabric.call_args.args[2];self.assertTrue(sent['require_read_only'])
        self.assertEqual(sent['read_only_objects'],['[dbo].[Items]'])
        self.assertEqual(fabric.call_args.args[0],config)
    def test_no_read_only_receipt_is_hard_stop(self):
        native=NativeQueries({'gold':{'kind':'SOURCE_SQL','config':{},'asset_ids':['table'],'objects':sql_objects()}},
            source=Mock(return_value={'rows':[]}),fabric=Mock(),dax=Mock(),offline=True)
        bound=validate('SELECT id FROM dbo.Items',{'dialect':'T-SQL','objects':sql_objects()})
        with self.assertRaises(GatewayDenied):native('gold',bound,timeout_seconds=30)
    def test_dax_route_has_no_owner_fallback(self):
        native=NativeQueries({'model':{'kind':'DAX','config':{'fabric':{}},'asset_ids':['m'],'workspace':'w','model':'m'}},
            source=Mock(),fabric=Mock(),dax=Mock(),offline=True)
        with self.assertRaises(GatewayDenied):native('model',{'asset_ids':['m']},timeout_seconds=30)


class GatewayTests(unittest.TestCase):
    def setUp(self):
        # This class calls only the in-memory authorizer, never a transport.
        # Docker still has --network=none; leave the production kill switch alone.
        guard=patch.dict(os.environ,{'DIA_LIVE_ACCESS_DISABLED':'0'})
        guard.start();self.addCleanup(guard.stop)

    def test_define_is_explicit_opt_in_recursive_grammar_not_gateway_bypass(self):
        query="DEFINE MEASURE 'Activity'[X]=SUM('Activity'[units]) EVALUATE ROW(\"n\",[X])"
        with TemporaryDirectory() as folder,patch.dict(os.environ,{'DIA_GATEWAY_AUDIT_FILE':str(Path(folder)/'audit.jsonl')}):
            with self.assertRaises(GatewayDenied):validate_dax(query)
            self.assertEqual(validate_dax(query,allow_define=True),query)
            for bad in (query+' EVALUATE Activity',query+' DELETE Activity',
                        'DEFINE VAR x=CALL_EXTERNAL() EVALUATE ROW("n",x)'):
                with self.assertRaises(GatewayDenied):validate_dax(bad,allow_define=True)
    def test_reasoning_endpoint_cannot_be_used_for_server_tools_or_other_models(self):
        endpoint='https://api.anthropic.com/v1/messages'
        gateway=Gateway({'version':1,'live_enabled':True,'identities':{'existing-provider':{
            'role':'model','reasoning_models':['offline-claude'],
            'http':[{'method':'POST','url':endpoint,'purpose':'reasoning_model'}]}}})
        body={'model':'offline-claude','max_tokens':100,'system':[{'type':'text','text':'stable','cache_control':{'type':'ephemeral'}}],
              'messages':[],'tools':[{'name':'run_sql','description':'Read only','input_schema':{'type':'object'}}]}
        with TemporaryDirectory() as folder,patch.dict(os.environ,{'DIA_GATEWAY_AUDIT_FILE':str(Path(folder)/'audit.jsonl')}):
            gateway.http('existing-provider','POST',endpoint,json.dumps(body))
            bad=deepcopy(body);bad['model']='unpriced-model'
            with self.assertRaises(GatewayDenied):gateway.http('existing-provider','POST',endpoint,json.dumps(bad))
            bad=deepcopy(body);bad['tools']=[{'type':'web_search_20250305','name':'web_search'}]
            with self.assertRaises(GatewayDenied):gateway.http('existing-provider','POST',endpoint,json.dumps(bad))


if __name__=='__main__':unittest.main()
