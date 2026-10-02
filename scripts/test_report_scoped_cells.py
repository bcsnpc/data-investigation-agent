"""Report scope, original value receipts, complete lookup, and exact-query reuse."""
import copy
import json
import unittest
from unittest.mock import patch
from investigator import report_resolution,declared_reproduction,native_identity,report_scope
from investigator.adapters import report_predicates
import test_report_cells as cell_fixture
from test_declared_predicate_adapter import native_filter,filter_config,field


class ScopedTests(unittest.TestCase):
    setUp=cell_fixture.CellTests.setUp
    part=cell_fixture.CellTests.part
    modify=cell_fixture.CellTests.modify
    grouped=cell_fixture.CellTests.grouped

    def no_predicates(self):
        self.modify(self.page,lambda d:d.pop('filterConfig'))
        self.modify(self.visual,lambda d:d.pop('filterConfig'))
        self.modify(self.slicer,lambda d:d['visual']['objects'].pop('general'))
        self.parts.remove(self.bookmark)

    def request(self,column=None):
        self.scope['filters']=[]
        self.scope['selection_request']={'state':'REQUESTED','report_binding':self.scope['report_binding'],
            'value_source':{'start':0,'end':5,'quote':'North'},
            'column_source':{'start':0,'end':len(column),'quote':column} if column else None}

    def native(self,exists=1):
        def execute(request):
            self.requests.append(copy.deepcopy(request))
            value=exists if 'COUNTROWS' in request['query'] else 3
            response={'results':[{'tables':[{'rows':[{'quantity':value,
                'surface_identity':self.reader['account'],'surface_engine':'OLAP Server','surface_object':self.model['native_id']}]}]}]}
            response[native_identity.KEY]=native_identity.make(response,request,self.reader)
            return response
        self.adapter.execute_native=execute

    def prepare(self):
        return report_resolution.prepare(self.adapter,self.layer,self.measure['id'],self.scope)

    def test_compiled_fingerprint_ignores_text_formatting_but_not_distinct_reads(self):
        from investigator.flexible_tools import build
        from investigator.adapters.report_predicates import quantity_query
        from investigator.adapters.microsoft_process import semantic_self_report,SEMANTIC_REPORT
        query=semantic_self_report(quantity_query(self.model,self.measure['id'],[]))
        plan={'model_id':self.model['id'],'revision':self.model['revision'],'context_id':self.model['context_id'],
            'query':query,'max_rows':20,'surface_report':SEMANTIC_REPORT}
        first=build(self.store,plan,self.config,'bounded_dax')
        formatted=build(self.store,{**plan,'query':query.replace('EVALUATE ','EVALUATE  ').replace(',',', ')},self.config,'bounded_dax')
        self.assertNotEqual(first['scope_hash'],formatted['scope_hash'])
        self.assertEqual(self.adapter._compiled_quantity_fingerprint(first),self.adapter._compiled_quantity_fingerprint(formatted))
        changed=build(self.store,{**plan,'query':semantic_self_report(quantity_query(self.model,self.measure['id'],
            [{'field_id':self.column['id'],'operator':'IN','values':['North']}]))},self.config,'bounded_dax')
        self.assertNotEqual(self.adapter._compiled_quantity_fingerprint(first),self.adapter._compiled_quantity_fingerprint(changed))

    def test_report_inventory_cannot_leak_a_second_reports_matching_value(self):
        self.no_predicates();self.grouped();self.request();self.native()
        other=copy.deepcopy(self.report);other['report']={'id':'foreign/report','name':'Other report'}
        other['report_definitions']=copy.deepcopy(self.parts)
        for part in other['report_definitions']:
            part['id']='foreign/'+part['id']
            if part['name'].endswith('/page.json'):
                document=json.loads(part['metadata']['content']);document['filterConfig']=filter_config(native_filter())
                part['metadata']['content']=json.dumps(document)
        self.model['context']['reports'].append(other)
        scope,obs=self.prepare()
        self.assertEqual(scope['selection_resolution']['resolution_kind'],'OBSERVED')
        self.assertEqual(len(self.requests),1)
        self.assertTrue(all(o.get('report_id',self.report['report']['id'])==self.report['report']['id'] for o in obs))

    def test_no_saved_slicer_selection_is_active_full_domain_and_conserved(self):
        self.no_predicates()
        options=report_predicates.scoped_options(self.model,self.measure['id'],self.scope['report_binding'])
        d=options[0];entries=report_scope.validate_inventory(d['inventory'],d['restrictions'],binding=self.scope['report_binding'],reports=self.adapter.report_catalog())
        self.assertEqual(len(entries),1)
        self.assertEqual(entries[0]['disposition'],'ACTIVE');self.assertEqual(entries[0]['effect'],'FULL_DOMAIN')
        self.assertEqual(d['restrictions'],[])

    def test_full_domain_does_not_skip_an_unknown_saved_selection_container(self):
        self.no_predicates()
        self.modify(self.slicer,lambda d:d['visual']['objects'].update(opaqueSelection={'value':'unknown'}))
        result=declared_reproduction.run(self.adapter,self.layer,self.measure['id'],self.scope)
        self.assertEqual(result['status'],'UNDECLARED');self.assertEqual(self.requests,[])
        self.assertIn('Unsupported declarations',result['reason'])

    def test_new_engine_never_falls_back_to_model_wide_report_declarations(self):
        scope={k:v for k,v in self.scope.items() if k!='report_binding'}
        result=declared_reproduction.run(self.adapter,self.layer,self.measure['id'],scope)
        self.assertEqual(result['unsupported_form'],'REPORT_BINDING_ABSENT')
        self.assertEqual(self.requests,[])

    def test_observed_value_reaches_keyed_and_total_cells_with_original_receipt(self):
        self.no_predicates();self.grouped();self.request();self.native()
        scope,obs=self.prepare();scope['selection_observations']=obs
        target=scope['selection_resolution'];self.assertEqual(target['resolution_kind'],'OBSERVED')
        lookup=next(o for o in obs if o['id']==target['receipt_id'])
        self.assertEqual(lookup['surface_report_receipt_id'],lookup['id'])
        self.adapter.remaining_diagnostic_reads=lambda:4-len(self.requests)
        result=declared_reproduction.run(self.adapter,self.layer,self.measure['id'],scope)
        self.assertEqual([r['cell']['mode'] for r in result['cells']],['KEYED','TOTAL'])
        self.assertEqual(len(self.requests),3)
        self.assertIn('no declared report filter',result['business_output'])
        self.assertIn('OBSERVED',result['technical_output'])
        self.assertTrue(all(r['finding']['unavailability'] is None for r in result['cells']))

    def test_no_reported_figure_computes_cells_and_totals_without_verdict(self):
        self.no_predicates();self.grouped();self.request();self.native()
        self.scope['reported_figure']={'state':'UNSPECIFIED'}
        scope,obs=self.prepare();scope['selection_observations']=obs
        result=declared_reproduction.run(self.adapter,self.layer,self.measure['id'],scope)
        self.assertEqual(result['reason'],declared_reproduction.NO_FIGURE)
        self.assertEqual(len(result['cells']),2)
        self.assertTrue(all(r['finding']['label'] is None and r['finding']['reproduced_value']=='3' for r in result['cells']))

    def test_none_or_multiple_matching_columns_is_a_named_refusal(self):
        self.no_predicates();self.grouped();self.request();self.native(0)
        with self.assertRaisesRegex(report_resolution.ResolutionRefused,'no grouping column'):self.prepare()
        self.assertEqual(len(self.requests),1)
        another={**self.column,'id':'resolved/customers/channel','name':'Channel'}
        self.model['context']['model_assets'].append(another)
        self.modify(self.visual,lambda d:d['visual']['query']['queryState']['Values']['projections'].insert(0,{'field':field(column='Channel')}))
        self.requests.clear();self.native(1)
        with self.assertRaisesRegex(report_resolution.ResolutionRefused,'multiple grouping columns'):self.prepare()
        self.assertEqual(len(self.requests),2)

    def test_lookup_cap_never_selects_from_partial_column_coverage(self):
        self.no_predicates();self.grouped();self.request();self.native()
        self.adapter.remaining_diagnostic_reads=lambda:0
        with self.assertRaisesRegex(report_resolution.ResolutionRefused,'cannot cover every grouping'):self.prepare()
        self.assertEqual(self.requests,[])

    def test_stated_column_is_exact_and_still_tests_value_existence(self):
        self.no_predicates();self.grouped();self.request('Region');self.native()
        scope,obs=self.prepare();self.assertEqual(scope['selection_resolution']['resolution_kind'],'STATED')
        self.assertEqual(scope['selection_resolution']['lookup']['status'],'MATCH');self.assertEqual(len(self.requests),1)
        self.requests.clear();self.native(0)
        with self.assertRaisesRegex(report_resolution.ResolutionRefused,'MISMATCH receipt'):self.prepare()
        self.assertEqual(len(self.requests),1)
        self.request('region')
        with self.assertRaisesRegex(report_resolution.ResolutionRefused,'exactly one'):self.prepare()

    def test_evidence_resolution_precedes_lookup_and_candidate_addressing(self):
        self.modify(self.visual,lambda d:d.pop('filterConfig'))
        self.modify(self.slicer,lambda d:d['visual']['objects'].pop('general'))
        self.request();self.native()
        order=[]
        original=self.adapter.report_selection_inventory
        def inventory(*args):order.append('inventory');return original(*args)
        with patch.object(self.adapter,'report_selection_inventory',side_effect=inventory):scope,obs=self.prepare()
        self.assertEqual(order,['inventory']);self.assertEqual(self.requests,[])
        self.assertEqual(scope['selection_resolution']['resolution_kind'],'EVIDENCE')
        self.assertNotIn('cell',obs[0])
        self.assertEqual(len(self.adapter.declared_cells(self.layer,self.measure['id'],scope)['cells']),1)

    def test_missing_second_key_names_it_and_total_remains_evaluable(self):
        self.grouped()
        another={**self.column,'id':'resolved/customers/product','name':'Product'}
        self.model['context']['model_assets'].append(another)
        self.modify(self.visual,lambda d:d['visual']['query']['queryState']['Values']['projections'].insert(0,{'field':field(column='Product')}))
        batch=self.adapter.declared_cells(self.layer,self.measure['id'],self.scope)
        self.assertIn('MISSING_CELL_KEYS: Product',batch['refusals'][0]['reason'])
        self.assertEqual(batch['cells'][0]['cell']['mode'],'TOTAL')

    def test_unsupported_unfamiliar_selection_visual_is_blocked_by_consumer(self):
        self.part('definition/pages/p/visuals/alien/visual.json',{'visual':{'visualType':'unfamiliarSelectionBearingThing'}})
        result=declared_reproduction.run(self.adapter,self.layer,self.measure['id'],self.scope)
        self.assertEqual(self.requests,[]);self.assertEqual(result['status'],'UNDECLARED')
        self.assertIn('UNKNOWN_VISUAL_KIND:unfamiliarSelectionBearingThing',result['reason'])

    def test_exact_read_reuse_records_event_and_original_result_without_budget(self):
        result=declared_reproduction.run(self.adapter,self.layer,self.measure['id'],self.scope)
        self.assertEqual(len(self.requests),2)
        declaration=self.adapter.declared_cells(self.layer,self.measure['id'],self.scope)['cells'][0]
        self.assertEqual(self.adapter.declared_cell_cost(self.measure['id'],declaration),0)
        result=declared_reproduction.run(self.adapter,self.layer,self.measure['id'],self.scope)
        self.assertEqual(len(self.requests),2);self.assertEqual(len(self.meters),2)
        events=[o for o in result['observations'] if o.get('check_kind')=='COMPILED_DUPLICATE_REFUSED']
        self.assertTrue(events);self.assertTrue(all(e['diagnostic_reads']==0 and e['prior_result']=={'quantity':'3'} for e in events))

    def test_distinct_compiled_read_is_never_refused_even_if_results_equal(self):
        self.modify(self.page,lambda d:d.pop('filterConfig'));self.parts.remove(self.slicer)
        document=json.loads(self.visual['metadata']['content']);document['name']='other'
        document['filterConfig']=filter_config(native_filter(('West',)))
        self.part('definition/pages/p/visuals/other/visual.json',document)
        result=declared_reproduction.run(self.adapter,self.layer,self.measure['id'],self.scope)
        self.assertEqual(len(self.requests),3)
        self.assertEqual(len({r['query'] for r in self.requests}),3)
        self.assertEqual(len(result['cells']),2)

    def test_original_resolution_receipt_is_required_by_marker_validation(self):
        self.no_predicates();self.grouped();self.request();self.native()
        scope,obs=self.prepare();scope['selection_observations']=obs
        result=declared_reproduction.run(self.adapter,self.layer,self.measure['id'],scope)
        marker=result['cells'][0]['finding']; originals={o['id']:o for o in obs+result['observations']}
        declared_reproduction.validate(marker,originals)
        del originals[scope['selection_resolution']['receipt_id']]
        with self.assertRaisesRegex(ValueError,'coverage is incomplete'):declared_reproduction.validate(marker,originals)


if __name__=='__main__':unittest.main()
