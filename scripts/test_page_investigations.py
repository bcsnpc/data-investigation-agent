"""Page consumer rules with synthetic full-report transport; REST is tested separately."""
import copy,json,unittest
from types import SimpleNamespace
from unittest.mock import Mock,patch
from investigator.onboarding import digest
from investigator.page_investigations import PageInvestigations
from investigator.adapters import report_cells,form_candidate_values
from investigator.workspace import Workspace
from investigator import native_identity
import test_declared_predicate_adapter as fixture

def confirmed(catalog,model,measure,report,page):
    claim={'facts':[],'settled':{'metric':[{'phrase':'Revenue'}],'scope':{'kind':'PAGE','report_id':report,'page_id':page},'direction':'DIFFERENT'},
           'selected_binding':{'model_id':model,'measure_id':measure,'report_id':report,'page_id':page,'target_ids':[]}}
    interpretation={'text':'Compare the Revenue visuals on this page.','fact_ids':[]}
    confirmation={'authority':'USER_CONFIRMED','interpretation_hash':digest(interpretation),'catalog_hash':digest(catalog)}
    return {'status':'CONFIRMED','claim':claim,'interpretation':interpretation,'confirmation':confirmation,'catalog_hash':digest(catalog),
            'engine_admission':{'claim_hash':digest(claim),'confirmation_hash':digest(confirmation)},'documents':[]}

class Tests(unittest.TestCase):
    def setUp(self):
        # Positive page-proof cases need query-bound engine/object evidence.
        # This explicitly synthetic legacy transport supplies that historical
        # grammar; the production ExecuteQueries route cannot and must refuse.
        from investigator.adapters.microsoft_self_report import SCALARS
        def legacy_report(query):
            return 'EVALUATE ADDCOLUMNS('+query.removeprefix('EVALUATE ')+',"surface_identity",USERPRINCIPALNAME(),"surface_engine",'+SCALARS[0]+',"surface_object",'+SCALARS[1]+')'
        self.enterContext(patch('investigator.adapters.microsoft_process.semantic_self_report',side_effect=legacy_report))
        self.enterContext(patch('investigator.adapters.form_candidate_values.semantic_self_report',side_effect=legacy_report))
        self.enterContext(patch.dict('investigator.adapters.microsoft_process.SEMANTIC_REPORT',
            {'identity':'surface_identity','engine':'surface_engine','object':'surface_object'},clear=True))
        self.f=fixture.DeclaredPredicateAdapterTests();self.f.setUp();self.addCleanup(self.f.doCleanups)
        f=self.f;f.parts[:]=[f.report_doc,f.page,f.visual]
        f.modify(f.page,lambda doc:doc.update(displayName='Overview',filterConfig={'filters':[]},visualInteractions=[]))
        f.modify(f.visual,lambda doc:doc.update(filterConfig={'filters':[]}))
        other=copy.deepcopy(json.loads(f.visual['metadata']['content']));other['name']='second'
        self.second=f.part('definition/pages/p/visuals/second/visual.json',other)
        f.model['name']='Revenue model';f.model['context']['measures']=[{'id':f.measure['id'],'name':'Revenue'}]
        f.store.list=lambda enabled:[copy.deepcopy(f.model)]
        self.workspace=Workspace.__new__(Workspace);self.workspace.store=f.store;self.workspace.agent=SimpleNamespace(config=f.config)
        self.service=PageInvestigations(self.workspace)
        self.catalog=self.service._catalog();self.report=f.report['report']['id'];self.page=self.report+'/page/p'
        self.body=confirmed(self.catalog,f.model['id'],f.measure['id'],self.report,self.page)
        self.adapter=f.adapter;self.values=iter([3,3]);self.native_requests=[]
        def execute(request):
            self.native_requests.append(copy.deepcopy(request));value=next(self.values)
            response={'results':[{'tables':[{'rows':[{'quantity':value,'surface_identity':f.reader['account'],
                'surface_engine':'OLAP Server','surface_object':f.model['native_id']}]}]}]}
            response[native_identity.KEY]=native_identity.make(response,request,f.reader)
            return response
        self.adapter.execute_native=execute

    def test_executequeries_identity_only_does_not_satisfy_full_page_attestation(self):
        from investigator.adapters.microsoft_self_report import compose
        def execute(request):
            self.native_requests.append(copy.deepcopy(request))
            response={'results':[{'tables':[{'rows':[{'quantity':next(self.values),
                'surface_identity':self.f.reader['account']}]}]}]}
            response[native_identity.KEY]=native_identity.make(response,request,self.f.reader)
            return response
        self.adapter.execute_native=execute
        with patch('investigator.adapters.microsoft_process.semantic_self_report',side_effect=compose), \
             patch('investigator.adapters.form_candidate_values.semantic_self_report',side_effect=compose), \
             patch.dict('investigator.adapters.microsoft_process.SEMANTIC_REPORT',{'identity':'surface_identity'},clear=True):
            result=self.service.consistency(self.body,self.adapter)
        self.assertEqual(result['outcome'],'NOT_COMPARABLE')
        self.assertEqual(result['coverage']['checked_visual_ids'],[])
        self.assertTrue(all(d['disposition']=='UNAVAILABLE' for d in result['coverage']['dispositions']))
        self.assertTrue(all('INFO.' not in r['query'] for r in self.native_requests))
        self.assertFalse(result['cause_established'])

    def sync(self):
        self.catalog=self.service._catalog();self.body=confirmed(self.catalog,self.f.model['id'],self.f.measure['id'],self.report,self.page)

    def test_real_workspace_catalog_and_native_compiler_produce_sealed_evidence(self):
        result=self.service.consistency(self.body,self.adapter)
        self.assertEqual(result['outcome'],'OBSERVED_AGREEMENT',result)
        self.assertEqual(len(result['evidence']),2)
        self.assertEqual(len(self.native_requests),2)
        for evidence in result['evidence']:
            self.assertEqual(evidence['receipt_seal']['state'],'SEALED')
            self.assertEqual(evidence['surface_report_binding'],'VALUE_QUERY')
            self.assertEqual(evidence['attestation']['consistency'],'MATCHED')
            self.assertIn('Revenue',evidence['query'])
            self.assertEqual(evidence['read_address']['kind'],'CELL')
        self.assertEqual(result['snapshot_status'],'SNAPSHOT_UNVERIFIED')
        self.assertFalse(result['cause_established'])

    def test_different_values_are_observation_not_causal_defect(self):
        self.values=iter([3,5]);result=self.service.consistency(self.body,self.adapter)
        self.assertEqual(result['outcome'],'OBSERVED_DIFFERENCE')
        self.assertFalse(result['cause_established']);self.assertEqual(result['scoring'],'NOT_SCORED_ESTATE_GATE')

    def test_different_declared_filters_do_not_become_defect_or_expected_rule(self):
        self.f.modify(self.second,lambda doc:doc.update(filterConfig=fixture.filter_config(fixture.native_filter(('West',)))))
        self.sync();self.values=iter([3,5]);result=self.service.consistency(self.body,self.adapter)
        self.assertEqual(result['outcome'],'NOT_COMPARABLE',result)
        self.assertEqual(result['comparisons'][0]['reason'],'DIFFERENT_DECLARED_RESTRICTIONS')

    def test_grouped_visual_is_explicit_unassessed_not_implicit_total(self):
        self.f.modify(self.second,lambda doc:doc['visual'].update(visualType='tableEx'))
        self.f.modify(self.second,lambda doc:doc['visual']['query']['queryState']['Values']['projections'].insert(0,{'field':fixture.field()}))
        self.sync();result=self.service.consistency(self.body,self.adapter)
        dispositions=result['coverage']['dispositions']
        self.assertEqual(len(dispositions),2);self.assertEqual(next(d for d in dispositions if d['visual_id']==self.second['id'])['disposition'],'UNRESOLVED_GROUPED_CELL')
        self.assertEqual(len(self.native_requests),1)

    def test_unconfirmed_claim_never_reads(self):
        self.body['status']='AWAITING_CONFIRMATION'
        self.assertEqual(self.service.consistency(self.body,self.adapter)['status'],'HELD');self.assertEqual(self.native_requests,[])

    def test_changed_catalog_or_confirmation_hash_refuses(self):
        self.body['confirmation']['interpretation_hash']='forged'
        self.assertEqual(self.service.prepare(self.body)['reason'],'CONFIRMED_RETAINED_CLAIM_REQUIRED')
        self.sync();self.f.modify(self.f.page,lambda doc:doc.update(displayName='Changed'))
        self.assertEqual(self.service.prepare(self.body)['reason'],'CURRENT_CONFIRMED_CATALOG_REQUIRED')

    def test_uncompiled_time_or_filter_is_not_dropped(self):
        for field,value in [('time','today'),('filters',['North'])]:
            with self.subTest(field=field):
                self.sync();self.body['claim']['settled'][field]=value;self.body['engine_admission']['claim_hash']=digest(self.body['claim'])
                self.assertEqual(self.service.prepare(self.body)['status'],'HELD')
        self.assertEqual(self.native_requests,[])

    def test_screenshot_scope_reloads_server_marker_and_cannot_be_forged_complete(self):
        self.body['captured_context']={'review_id':'review','review_hash':'rh','visible_filter_scope':{'status':'COMPLETE'}}
        loader=Mock(return_value={'id':'review','hash':'rh','visible_filter_scope':{'status':'NOT_COMPILED','unfiltered_scope_established':False}})
        self.workspace._claim_screenshots=SimpleNamespace(load=loader)
        result=self.service.consistency(self.body,self.adapter)
        self.assertEqual(result['reason'],'SCREENSHOT_FILTER_SCOPE_NOT_COMPILED');loader.assert_called_once()
        self.assertEqual(self.native_requests,[])

    def test_target_escape_is_refused(self):
        self.body['claim']['selected_binding']['target_ids']=['other-report-visual']
        self.body['engine_admission']['claim_hash']=digest(self.body['claim'])
        self.assertEqual(self.service.prepare(self.body)['reason'],'CONFIRMED_TARGET_LEAVES_PAGE_SCOPE')

    def test_no_governed_reader_means_no_native_dispatch(self):
        self.adapter.meter_read=None
        result=self.service.consistency(self.body,self.adapter)
        self.assertEqual(result['status'],'PARTIAL');self.assertEqual(self.native_requests,[])

    def test_wrong_query_bound_reader_identity_not_accepted(self):
        old=self.adapter.execute_native
        def wrong(request):
            response=old(request);response['results'][0]['tables'][0]['rows'][0]['surface_identity']='someone-else'
            response[native_identity.KEY]=native_identity.make(response,request,self.f.reader)
            return response
        self.adapter.execute_native=wrong
        result=self.service.consistency(self.body,self.adapter)
        self.assertEqual(result['status'],'PARTIAL');self.assertEqual(result['coverage']['checked_visual_ids'],[])

    def _timing_adapter(self,refresh=None,load=None):
        layers=[{'id':'semantic','name':'Semantic'},{'id':'delivery','name':'Serving','transformation_asset_id':'producer'},
                {'id':'landing','name':'Landing'}]
        adapter=SimpleNamespace(model=self.f.model,config=copy.deepcopy(self.f.config),capabilities=lambda:{'refresh_timing'}if refresh else set(),
            resolve_path=lambda measure:{'layers':layers},freshness_boundaries=lambda path:[{'upper':layers[0],'lower':layers[1],'index':1}],
            refresh_timing=Mock(return_value=refresh),job_history=Mock(return_value=load or{'status':'UNAVAILABLE','reason':'No actual audit row'}))
        adapter.config['fabric']['refresh_timing_reader']={'account':'metadata@example.com'}
        from investigator.adapters.page_observations import refresh as refresh_port,load as load_port
        adapter.read_page_refresh=lambda path:refresh_port(adapter,path)
        adapter.read_page_load=lambda boundary:load_port(adapter,boundary)
        adapter.page_visual_inventory=self.adapter.page_visual_inventory
        adapter.config['layer_roles']=[{'asset_id':'semantic','role':'SEMANTIC','business_name':'Semantic'},
            {'asset_id':'delivery','role':'SERVING','business_name':'Serving'},{'asset_id':'landing','role':'LANDING','business_name':'Landing'}]
        return adapter

    def test_missing_refresh_and_load_timestamp_remain_unknown_not_business_date(self):
        adapter=self._timing_adapter();result=self.service.freshness(self.body,adapter)
        self.assertEqual(result['outcome'],'TIMING_UNAVAILABLE');self.assertFalse(result['freshness_established'])
        self.assertTrue(any(m['reason']=='REFRESH_TIMING_CAPABILITY_UNDECLARED'for m in result['missing']))
        self.assertTrue(all(t['last_load']is None and t['last_refresh']is None for t in result['timings']))

    def test_actual_bound_timestamp_receipts_are_retained_without_age_classification(self):
        refresh={'status':'AVAILABLE','model_id':self.f.model['native_id'],'identity_provenance':{'account':'metadata@example.com','token_identity':'metadata@example.com'},
            'history':[{'status':'Completed','startTime':'2026-10-12T08:00:00Z','endTime':'2026-10-12T08:02:00Z','requestId':'refresh-run'}]}
        load={'status':'CURRENT','run_id':'copy-run','started_at':'2026-10-12T07:00:00Z','completed_at':'2026-10-12T07:01:00Z',
            'evidence':{'id':'audit-native-receipt','tool':'context','completeness':'COMPLETE_RESPONSE','context_version':'ctx','runs':[{'status':'AVAILABLE'}]}}
        adapter=self._timing_adapter(refresh,load);result=self.service.freshness(self.body,adapter)
        self.assertEqual(result['timings'][0]['last_refresh']['timestamp'],'2026-10-12T08:02:00Z')
        self.assertEqual(result['timings'][0]['last_load']['timestamp'],'2026-10-12T07:01:00Z')
        self.assertIsNone(result['timings'][1]['last_load'])
        self.assertFalse(result['freshness_established']);self.assertEqual(adapter.job_history.call_count,1)
        self.assertTrue(any(e['id']=='audit-native-receipt'for e in result['evidence']))

    def test_copy_completion_belongs_to_output_not_application_source(self):
        load={'status':'CURRENT','run_id':'copy-run','started_at':'2026-10-12T07:00:00Z','completed_at':'2026-10-12T07:01:00Z',
            'evidence':{'id':'copy-receipt','tool':'context','completeness':'COMPLETE_RESPONSE','context_version':'ctx','runs':[{'status':'AVAILABLE'}]}}
        adapter=self._timing_adapter(load=load)
        layers=[{'id':'semantic'},{'id':'bronze'},{'id':'application','transformation_asset_id':'copy'}]
        adapter.resolve_path=lambda measure:{'layers':layers}
        adapter.freshness_boundaries=lambda path:[{'upper':layers[1],'lower':layers[2],'index':2}]
        adapter.config['layer_roles']=[{'asset_id':'bronze','role':'LANDING','business_name':'Bronze'},
            {'asset_id':'application','role':'SOURCE','business_name':'Application'}]
        result=self.service.freshness(self.body,adapter)
        bronze=next(r for r in result['timings']if r['layer_id']=='bronze')
        source=next(r for r in result['timings']if r['layer_id']=='application')
        self.assertEqual(bronze['last_load']['timestamp'],'2026-10-12T07:01:00Z')
        self.assertIsNone(source['last_load'])

    def test_unrelated_real_sealed_probe_cannot_be_borrowed_for_other_visual(self):
        original=self.adapter.read_visual_quantity;cache=[]
        def borrowed(candidate):
            if not cache:cache.append(original(candidate))
            return copy.deepcopy(cache[0])
        self.adapter.read_visual_quantity=borrowed
        result=self.service.consistency(self.body,self.adapter)
        self.assertEqual(result['status'],'PARTIAL')
        self.assertEqual(len(result['coverage']['checked_visual_ids']),1)

    def test_summary_contains_scalars_not_serialized_objects_or_duplicate_receipts(self):
        result=self.service.consistency(self.body,self.adapter)
        self.assertIn('3 versus 3',result['technical_summary'])
        self.assertNotIn("{'",result['technical_summary'])
        self.assertNotIn('SNAPSHOT_UNVERIFIED',result['technical_summary'])
        for evidence in result['evidence']:self.assertNotIn(evidence['id'],result['technical_summary'])

    def test_malformed_or_wrong_model_refresh_time_not_accepted(self):
        refresh={'status':'AVAILABLE','model_id':'other','history':[{'status':'Completed','startTime':'2026-10-12T08:00:00Z','endTime':'bad'}],
                 'identity_provenance':{'account':'metadata@example.com','token_identity':'metadata@example.com'}}
        result=self.service.freshness(self.body,self._timing_adapter(refresh))
        self.assertTrue(all(t['last_refresh']is None for t in result['timings']))
        self.assertEqual(result['outcome'],'TIMING_UNAVAILABLE')

    def test_real_claim_submit_confirm_flattens_typed_filters_without_changing_facts(self):
        self.workspace.agent.planner_profile={'adapter':'injected'};self.workspace.clock=lambda:1000;self.workspace._claim_glossary=None
        saved=self.workspace.claims.submit({'text':'','request_key':'actual-form','claim':{'metric_phrase':'Revenue','direction':'DIFFERENT',
            'comparator':'NONE','scope':{'kind':'PAGE','report_id':self.report,'page_id':self.page},
            'filters':[{'column_id':self.f.column['id'],'operator':'EQ','value':'North'}]}})
        self.assertEqual(saved['status'],'AWAITING_CONFIRMATION',saved)
        approved=self.workspace.claims.confirm({'id':saved['id'],'revision':saved['revision'],'accepted':True,'request_key':'confirm'})
        with self.workspace.store.connect()as db:_,body=self.workspace.claims._load(db,approved['id'])
        before=copy.deepcopy(body['claim']['facts']);plan=self.service.prepare(body)
        self.assertEqual(plan['status'],'PLANNED',plan)
        self.assertEqual(plan['candidates'][0]['scope']['filters'],[{'column_id':self.f.column['id'],'values':['North']}])
        result=self.service.consistency(body,self.adapter)
        self.assertEqual(result['outcome'],'OBSERVED_AGREEMENT',result);self.assertEqual(body['claim']['facts'],before)
        self.assertIn('North',self.native_requests[0]['query'])

    def test_forged_value_with_real_seal_is_not_evidence(self):
        original=self.adapter.read_visual_quantity
        def wrong(candidate):
            probe=original(candidate);probe['value']='999';return probe
        self.adapter.read_visual_quantity=wrong
        result=self.service.consistency(self.body,self.adapter)
        self.assertEqual(result['coverage']['checked_visual_ids'],[])
        self.assertEqual(result['evidence'],[])

    def test_forged_statement_with_real_seal_is_not_evidence(self):
        original=self.adapter.read_visual_quantity
        def wrong(candidate):
            probe=original(candidate);probe['query']='EVALUATE ROW("quantity",999)';return probe
        self.adapter.read_visual_quantity=wrong
        result=self.service.consistency(self.body,self.adapter)
        self.assertEqual(result['coverage']['checked_visual_ids'],[])

    def test_numeric_looking_string_is_not_same_as_numeric_value(self):
        self.values=iter(['3',3]);result=self.service.consistency(self.body,self.adapter)
        self.assertEqual(result['status'],'PARTIAL')
        self.assertEqual(len(result['coverage']['checked_visual_ids']),1)

    def test_failed_reader_error_keeps_original_terminal_receipt(self):
        self.adapter.execute_native=lambda request:(_ for _ in()).throw(ValueError('Native query error'))
        result=self.service.consistency(self.body,self.adapter)
        self.assertEqual(result['status'],'PARTIAL');self.assertEqual(len(result['evidence']),2)
        self.assertEqual(result['evidence'][0]['result']['error_type'],'ValueError')
        self.assertEqual(result['evidence'][0]['receipt_seal']['state'],'SEALED')

    def test_non_metric_visuals_are_enumerated_not_hidden(self):
        self.f.part('definition/pages/p/visuals/label/visual.json',{'name':'label','visual':{'visualType':'textbox'}})
        self.sync();result=self.service.consistency(self.body,self.adapter)
        self.assertEqual(len(result['coverage']['requested_visual_ids']),3)
        self.assertTrue(any(d['disposition']=='NON_QUANTITY_VISUAL'for d in result['coverage']['dispositions']))

    def test_partial_multimetric_visual_never_becomes_fully_observed(self):
        second=copy.deepcopy(self.f.measure);second.update(id='resolved/sales/other',name='Other')
        self.f.model['context']['model_assets'].append(second);self.f.model['context']['measures'].append({'id':second['id'],'name':'Other'})
        self.f.modify(self.f.visual,lambda doc:doc['visual']['query']['queryState']['Values']['projections'].append({'field':fixture.field('Sales','Other','Measure')}))
        self.sync();catalog=copy.deepcopy(self.catalog)
        visual=next(v for v in catalog['models'][0]['visuals']if v['target_id']==self.f.visual['id'])
        visual['declared_scopes'][second['id']]={'state':'UNAVAILABLE'}
        self.body['claim']['selected_binding']={'kind':'MULTIPLE','bindings':[self.body['claim']['selected_binding'],
            {'model_id':self.f.model['id'],'measure_id':second['id'],'report_id':self.report,'page_id':self.page,'target_ids':[]}]}
        self.body['catalog_hash']=digest(catalog);self.body['confirmation']['catalog_hash']=digest(catalog)
        self.body['engine_admission'].update(claim_hash=digest(self.body['claim']),confirmation_hash=digest(self.body['confirmation']))
        with patch.object(self.service,'_catalog',return_value=catalog):result=self.service.consistency(self.body,self.adapter)
        row=next(d for d in result['coverage']['dispositions']if d['visual_id']==self.f.visual['id'])
        self.assertEqual(row['disposition'],'INCOMPLETE_DECLARED_SCOPE')
        self.assertTrue(any(m['disposition']=='INCOMPLETE_DECLARED_SCOPE'for m in row['measure_dispositions']))
        self.assertEqual(result['status'],'PARTIAL')

if __name__=='__main__':unittest.main()
