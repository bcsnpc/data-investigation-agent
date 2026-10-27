"""Offline synthetic tests; no estate, provider, oracle or held-out inputs."""
from copy import deepcopy
from io import BytesIO
import json
from types import SimpleNamespace
from unittest.mock import Mock, patch
import unittest
from investigator.guided_intake import Catalog, VERSION, admit, prefill
from investigator.investigative_queries import Queries, validate


def graph():
    kinds={'report':'REPORT','other':'REPORT','page':'PAGE','otherpage':'PAGE',
           'card':'VISUAL','othercard':'VISUAL','measure':'MEASURE','source':'SOURCE'}
    edges=[('report','page','CONTAINS'),('other','otherpage','CONTAINS'),
           ('page','card','CONTAINS'),('otherpage','othercard','CONTAINS'),
           ('card','measure','COMPUTED_FROM')]
    return {'nodes':[{'id':i,'kind':k,'label':i.title()} for i,k in kinds.items()],
            'edges':[{'source':s,'target':t,'kind':k} for s,t,k in edges]}


def request():
    return {'version':VERSION,'report':'report','page':'page','visual':'card',
            'issue_type':'NUMBER_LOOKS_WRONG','compared_with':{'kind':'NOTHING'},
            'reported_figure':{'state':'NUMBER','value':'950','precision':'EXACT'}}


def sql_objects():
    return [{'id':'table','metadata':{'schema_name':'dbo','name':'Items','type_desc':'USER_TABLE',
            'columns':[{'name':'id','data_type':'INT'},{'name':'quantity','data_type':'INT'}]}}]


def dax_objects():
    return [{'id':'t','kind':'SemanticTable','name':'Activity','parent_id':'model'},
            {'id':'m','kind':'Measure','name':'Quantity','parent_id':'t'},
            {'id':'c','kind':'SemanticColumn','name':'units','parent_id':'t'}]


class IntakeTests(unittest.TestCase):
    def test_investigative_convert_is_read_only_and_legacy_capability_unchanged(self):
        from investigator.query_sql import compile_query
        objects=sql_objects();layer={'dialect':'T-SQL','objects':objects}
        query='SELECT CONVERT(varchar(20), quantity) AS rendered FROM dbo.Items'
        result=validate(query,layer)
        self.assertIn('CONVERT',result['query'].upper())
        with self.assertRaises(ValueError):compile_query(query,objects)
        for text in ('UPDATE dbo.Items SET quantity=CONVERT(int, 1)',
                     'SELECT CONVERT(int, quantity) FROM dbo.Items; DELETE FROM dbo.Items',
                     'SELECT CONVERT(int, quantity) FROM dbo.Unknown'):
            with self.subTest(text=text),self.assertRaises(ValueError):validate(text,layer)

    def setUp(self):self.catalog=Catalog(graph())
    def test_catalog_dependencies_and_measure(self):
        self.assertEqual(len(self.catalog.reports()),2)
        self.assertEqual(self.catalog.pages('report'),[{'id':'page','name':'Page'}])
        self.assertEqual(self.catalog.visuals('report','page')[0]['measures'],[{'id':'measure','name':'Measure'}])
        self.assertEqual(admit(request(),self.catalog)['measure_candidates'],[{'id':'measure','name':'Measure'}])
    def test_wrong_report_page_or_visual_never_substituted(self):
        for key,value in [('page','otherpage'),('visual','othercard'),('report','unknown')]:
            item=request();item[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):admit(item,self.catalog)
    def test_optional_visual_and_nothing_do_not_block(self):
        item=request();del item['visual'];del item['page']
        self.assertEqual(admit(item,self.catalog)['status'],'READY')
    def test_exact_number_empty_and_stated_precision(self):
        for figure in ({'state':'EMPTY'}, {'state':'NUMBER','value':'3.4','precision':1},
                       {'state':'NUMBER','value':'950','precision':'EXACT'}):
            item=request();item['reported_figure']=figure
            self.assertEqual(admit(item,self.catalog)['reported_figure'],figure)
    def test_missing_precision_and_extra_tolerance_rejected(self):
        from jsonschema import ValidationError
        for figure in ({'state':'NUMBER','value':'3.4'},
                       {'state':'NUMBER','value':'950','precision':'EXACT','tolerance':10}):
            item=request();item['reported_figure']=figure
            with self.assertRaises(ValidationError):admit(item,self.catalog)
    def test_comparison_referents_checked(self):
        item=request();item['compared_with']={'kind':'ANOTHER_REPORT','target':{'report':'other','page':'page'}}
        with self.assertRaises(ValueError):admit(item,self.catalog)
        item['compared_with']={'kind':'SOURCE_SYSTEM','source':'source'}
        self.assertEqual(admit(item,self.catalog)['status'],'READY')
    def test_source_name_and_supporting_figure_preserved_without_changing_referent(self):
        item=request();figure={'state':'NUMBER','value':'700','precision':'EXACT'}
        item['compared_with']={'kind':'SOURCE_SYSTEM','source':'Source','figure':figure,
                              'target':{k:item[k] for k in ('report','page','visual')}}
        original=deepcopy(item);result=admit(item,self.catalog)
        self.assertEqual(item,original)
        self.assertEqual(result['compared_with'],{'kind':'SOURCE_SYSTEM','source':'source'})
        self.assertEqual(result['comparison_context']['figure'],figure)
        self.assertEqual(result['source_resolution']['basis'],'UNIQUE_EXACT_CATALOG_NAME')
        self.assertEqual(result['visual'],'card')
    def test_extra_competing_target_and_ambiguous_source_name_still_refuse(self):
        item=request();item['compared_with']={'kind':'SOURCE_SYSTEM','source':'source','target':{'report':'other'}}
        with self.assertRaisesRegex(ValueError,'CONFLICTING_COMPARISON_TARGET'):admit(item,self.catalog)
        g=graph();g['nodes'].append({'id':'source2','kind':'SOURCE','label':'Source'})
        item['compared_with']={'kind':'SOURCE_SYSTEM','source':'Source'}
        with self.assertRaisesRegex(ValueError,'SOURCE_NAME_UNRESOLVED_OR_AMBIGUOUS'):admit(item,Catalog(g))
    def test_free_text_one_combined_catalog_question_and_no_reask_named_report(self):
        result=prefill('It looks wrong',{},self.catalog)
        self.assertEqual([f['field'] for f in result['question']['fields']],['report','issue_type'])
        self.assertEqual(result['question']['fields'][0]['choices'],self.catalog.reports())
        result=prefill('Report looks wrong',{'report':'report'},self.catalog)
        self.assertEqual([f['field'] for f in result['question']['fields']],['issue_type'])
    def test_other_keeps_original_and_classification(self):
        item=request();item.update(issue_type='SOMETHING_ELSE',description='The daily number looks old',
                                   classified_issue_type='DATA_LOOKS_OLD')
        self.assertEqual(admit(item,self.catalog)['description'],item['description'])
        del item['classified_issue_type']
        self.assertEqual(admit(item,self.catalog)['classification_status'],'PENDING_INVESTIGATOR')
    def test_redundant_matching_classification_does_not_block_normal_issue(self):
        item=request();item['classified_issue_type']=item['issue_type']
        self.assertEqual(admit(item,self.catalog)['status'],'READY')
        item['classified_issue_type']='DATA_LOOKS_OLD'
        with self.assertRaisesRegex(ValueError,'CLASSIFICATION_ONLY_FOR_OTHER'):admit(item,self.catalog)
    def test_other_classification_is_required_from_model_before_final_delivery(self):
        from investigator.ai_investigation import toolbox
        tools=toolbox({}, {}, {'issue_type':'SOMETHING_ELSE'})
        submit=next(t for t in tools if t['name']=='submit_finding')['input_schema']
        self.assertIn('classified_issue_type',submit['required'])
        self.assertNotIn('SOMETHING_ELSE',submit['properties']['classified_issue_type']['enum'])
    def test_url_filters_are_preserved_not_fetched_or_dropped(self):
        item=request();item['details']={'report_url':'https://example.test/report?filter=Items%2Fid%20eq%207'}
        self.assertEqual(admit(item,self.catalog)['url_filters'],['Items/id eq 7'])
    def test_free_text_figure_and_visual_must_have_exact_token_provenance(self):
        text='Card shows 950.'
        item=request()
        result=prefill(text,item,self.catalog,provenance={'visual':[1,1],'reported_figure':[3,3]})
        self.assertEqual(result['provenance']['reported_figure']['quote'],'950')
        item['reported_figure']['value']='951'
        with self.assertRaisesRegex(ValueError,'FIGURE_OR_PRECISION'):prefill(text,item,self.catalog,
            provenance={'visual':[1,1],'reported_figure':[3,3]})
        item=request();item['visual']='othercard'
        with self.assertRaisesRegex(ValueError,'VISUAL_PROVENANCE'):prefill(text,item,self.catalog,
            provenance={'visual':[1,1],'reported_figure':[3,3]})
    def test_free_text_cannot_invent_or_widen_figure_precision(self):
        item=request()
        with self.assertRaisesRegex(ValueError,'PROVENANCE_REQUIRED'):prefill('Card shows 950.',item,self.catalog)
        item['reported_figure']['precision']=0
        with self.assertRaisesRegex(ValueError,'PRECISION_DIFFERS'):prefill('Card shows 950.',item,self.catalog,
            provenance={'visual':[1,1],'reported_figure':[3,3]})
    def test_service_read_only_catalog_and_validate(self):
        from investigator.guided_intake_service import GuidedIntakeService
        api=Mock();api.intake_catalog.return_value=graph()
        service=GuidedIntakeService(SimpleNamespace(guided_graph=api))
        self.assertEqual(service.handle('GET',['reports'],None),self.catalog.reports())
        self.assertEqual(service.handle('POST',['validate'],request())['status'],'READY')
    def test_existing_http_surface_exposes_graph_catalog(self):
        from investigator.workspace_api import create_app
        api=Mock();api.intake_catalog.return_value=graph()
        app=create_app(SimpleNamespace(guided_graph=api),'x'*32)
        env={'REQUEST_METHOD':'GET','PATH_INFO':'/api/workspace/guided/reports','HTTP_HOST':'127.0.0.1:8776',
             'REMOTE_ADDR':'127.0.0.1','HTTP_AUTHORIZATION':'Bearer '+'x'*32,'wsgi.input':BytesIO()}
        statuses=[];raw=b''.join(app(env,lambda status,headers:statuses.append(status)))
        self.assertEqual(statuses,['200 OK']);self.assertEqual(json.loads(raw),self.catalog.reports())


class QueryTests(unittest.TestCase):
    def test_native_blank_count_is_readonly_and_bound_to_the_discovered_column(self):
        layer={'dialect':'DAX','objects':dax_objects()}
        result=validate('EVALUATE ROW("BlankCount", COUNTBLANK(Activity[units]))',layer)
        self.assertIn('COUNTBLANK',result['query'])
        with self.assertRaises(ValueError):validate('EVALUATE ROW("BlankCount", COUNTBLANK(Unknown[quantity]))',layer)

    def setUp(self):
        self.layers={'gold':{'dialect':'T-SQL','objects':sql_objects()},
                     'spark':{'dialect':'Spark SQL','objects':sql_objects()},
                     'model':{'dialect':'DAX','objects':dax_objects()}}
    def test_sql_is_bound_and_forced_limit(self):
        for layer in ('gold','spark'):
            result=validate('WITH x AS (SELECT id, quantity FROM dbo.Items) SELECT SUM(quantity) AS total FROM x',self.layers[layer])
            self.assertIn('251',result['query']);self.assertEqual(result['asset_ids'],['table'])
    def test_ast_red_team(self):
        for text in ('UPDATE dbo.Items SET quantity=0','SELECT id INTO dbo.X FROM dbo.Items',
                     'SELECT id FROM dbo.Items; DELETE FROM dbo.Items',"EXEC('SELECT 1')",
                     'SELECT id FROM other.Items','SELECT id FROM remote.dbo.Items',
                     'SELECT id FROM #Temp','SET NOCOUNT ON; SELECT id FROM dbo.Items',
                     "SELECT * FROM OPENROWSET('secret')"):
            for layer in ('gold','spark'):
                with self.subTest(text=text,layer=layer),self.assertRaises(Exception):validate(text,self.layers[layer])
    def test_discovered_view_allowed_unknown_view_not(self):
        item=deepcopy(self.layers['gold']);item['objects'][0]['metadata']['type_desc']='VIEW'
        self.assertEqual(validate('SELECT id FROM dbo.Items',item)['asset_ids'],['table'])
        with self.assertRaises(ValueError):validate('SELECT id FROM dbo.Unknown',item)
    def test_ai_select_can_read_computed_columns_set_operations_and_wider_joins(self):
        item=deepcopy(self.layers['gold'])
        item['objects'][0]['metadata']['columns'].append({'name':'doubled','data_type':'INT','computed_definition':'quantity*2'})
        self.assertIn('doubled',validate('SELECT doubled FROM dbo.Items',item)['query'])
        value=validate('SELECT id FROM dbo.Items UNION ALL SELECT id FROM dbo.Items',item)
        self.assertEqual(value['asset_ids'],['table']);self.assertIn('251',value['query'])
        query='SELECT a0.id FROM dbo.Items a0 '+' '.join('JOIN dbo.Items a'+str(i)+' ON a0.id=a'+str(i)+'.id' for i in range(1,6))
        self.assertEqual(validate(query,item)['asset_ids'],['table'])
    def test_temporal_history_all_is_native_read_not_a_session_or_write(self):
        result=validate('SELECT id, quantity FROM dbo.Items FOR SYSTEM_TIME ALL',self.layers['gold'])
        self.assertIn('SYSTEM_TIME ALL',result['query'])
        from investigator.live_gateway import validate_sql
        validate_sql(result['query'],{('dbo','items')})
        with self.assertRaises(ValueError):validate("SELECT id FROM dbo.Items FOR SYSTEM_TIME AS OF '2026-10-20'",self.layers['gold'])
    def test_dax_evaluate_define_var_define_measure(self):
        for text in ('EVALUATE ROW("n",[Quantity])',
                     'DEFINE VAR x = [Quantity] EVALUATE ROW("n",x)',
                     "DEFINE MEASURE 'Activity'[Test] = SUM('Activity'[units]) EVALUATE ROW(\"n\",[Test])"):
            with self.subTest(text=text):
                value=validate(text,self.layers['model']);self.assertIn('TOPN(251,',value['query'])
    def test_dax_rejects_ddl_external_refs_and_multiple_evaluates(self):
        for text in ('CREATE TABLE Evil','EVALUATE Other',
                     'EVALUATE ROW("x",[Quantity]) EVALUATE Activity',
                     "DEFINE MEASURE 'Other'[X]=1 EVALUATE ROW(\"n\",[X])"):
            with self.subTest(text=text),self.assertRaises(ValueError):validate(text,self.layers['model'])
    def port(self,execute=None):
        self.events=[];self.reserve=Mock();self.execute=execute or Mock(return_value={'rows':[[7]]})
        return Queries(self.layers,execute=self.execute,reserve=self.reserve,save=self.events.append)
    def test_success_repeat_reuses_evidence_and_no_new_read(self):
        port=self.port();one=port.run('gold','SELECT SUM(quantity) AS n FROM dbo.Items',kind='sql',purpose='recreate')
        two=port.run('gold','SELECT SUM(quantity) AS n FROM dbo.Items',kind='sql',purpose='recreate')
        self.assertEqual(two['already_have'],one['id']);self.assertEqual(self.reserve.call_count,1)
        self.execute.assert_called_once();self.assertEqual(self.execute.call_args.kwargs['timeout_seconds'],30)
        self.assertEqual(one['row_count'],1);self.assertTrue(one['result_digest'])
    def test_error_is_visible_two_corrections_then_continue_elsewhere(self):
        port=self.port(Mock(side_effect=RuntimeError('Invalid column quantity')))
        for _ in range(3):
            value=port.run('gold','SELECT quantity FROM dbo.Items',kind='sql',purpose='recreate')
            self.assertEqual(value['error'],'Invalid column quantity')
        self.assertEqual(port.run('gold','SELECT id FROM dbo.Items',kind='sql',purpose='recreate')['error'],
                         'QUERY_CORRECTION_LIMIT')
        self.assertEqual(self.execute.call_count,3)
        self.assertEqual(len({call.args[1] for call in self.reserve.call_args_list}),3)
        self.assertEqual(port.run('spark','SELECT id FROM dbo.Items',kind='sql',purpose='recreate')['status'],'ERROR')
    def test_rejected_query_does_not_reserve_or_execute(self):
        port=self.port()
        with self.assertRaises(ValueError):port.run('gold','DELETE FROM dbo.Items',kind='sql',purpose='recreate')
        self.reserve.assert_not_called();self.execute.assert_not_called()
    def test_budget_stop_is_never_softened(self):
        from investigator.model_spend import SpendHold
        port=self.port();self.reserve.side_effect=SpendHold('cap')
        with self.assertRaises(SpendHold):port.run('gold','SELECT id FROM dbo.Items',kind='sql',purpose='recreate')
        self.execute.assert_not_called()
    def test_resume_uses_saved_native_result(self):
        port=self.port();record=port.run('gold','SELECT id FROM dbo.Items',kind='sql',purpose='record')
        new=Queries(self.layers,execute=Mock(side_effect=AssertionError('repeat')),reserve=Mock(),save=lambda _:None,restored=[record])
        self.assertEqual(new.run('gold','SELECT id FROM dbo.Items',kind='sql',purpose='record')['already_have'],record['id'])


if __name__=='__main__':unittest.main()
