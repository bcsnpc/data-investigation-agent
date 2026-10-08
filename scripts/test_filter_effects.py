import copy,json,unittest
from unittest.mock import patch
from investigator import filter_effects,declared_reproduction,native_identity,process_outcomes,process_budget
from investigator.usage_governance import UsageHold
from investigator.process_debugging import vertical,Probe
from test_declared_predicate_adapter import native_filter,filter_config
from test_report_cells import CellTests


class FilterEffectsTests(unittest.TestCase):
    setUp=CellTests.setUp
    part=CellTests.part
    modify=CellTests.modify

    def prepare(self,full_value=3):
        product=copy.deepcopy(self.column);product.update(id='resolved/customers/product',name='Product')
        self.model['context']['model_assets'].append(product)
        self.modify(self.visual,lambda d:d.update(filterConfig=filter_config(native_filter(('Widget',),column='Product'))))
        def execute(request):
            self.requests.append(copy.deepcopy(request))
            value=full_value if request['query'].count('TREATAS')==2 else 8
            response={'results':[{'tables':[{'rows':[{'quantity':value,'surface_identity':self.reader['account'],
                'surface_engine':'OLAP Server','surface_object':self.model['native_id']}]}]}]}
            response[native_identity.KEY]=native_identity.make(response,request,self.reader)
            return response
        self.adapter.execute_native=execute
        return declared_reproduction.run(self.adapter,self.layer,self.measure['id'],self.scope)

    def check(self):
        checked=self.prepare()
        result=filter_effects.run(self.adapter,self.layer,self.measure['id'],self.scope,checked)
        originals={o['id']:o for o in checked['observations']+result['observations']}
        return checked,result,originals

    def test_one_probe_per_restriction_with_redundant_same_field_predicates_and_reuse(self):
        checked,result,originals=self.check()
        self.assertEqual(len(result['finding']['variants']),3)
        self.assertEqual(sum(v['changed'] for v in result['finding']['variants']),1)
        self.assertEqual(len(self.requests),4)
        self.assertTrue(self.adapter.duplicate_read_events)
        filter_effects.validate(result['finding'],originals)
        self.assertTrue(all(v['quantity'] in ('3','8') for v in result['finding']['variants']))

    def test_business_effects_name_evidence_backed_filter_and_the_changed_value(self):
        _,result,originals=self.check()
        text=filter_effects.render(result['finding'],True)
        self.assertIn('product: Widget',text)
        self.assertIn('produced 8 (changed)',text)
        from investigator.narrative_form import validate
        validate(text,True)
        bad=copy.deepcopy(result['finding']);bad['variants'][0]['removed_restriction']['values']=['Invented']
        with self.assertRaisesRegex(ValueError,'removed restriction'):filter_effects.validate(bad,originals)

    def test_hostile_missing_or_changed_variant_is_refused(self):
        _,result,originals=self.check()
        for mutation in ('drop','quantity','scope'):
            bad=copy.deepcopy(result['finding'])
            if mutation=='drop':bad['variants'].pop()
            elif mutation=='quantity':bad['variants'][0]['quantity']='99'
            else:bad['variants'][0]['applied_restrictions']=[]
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):filter_effects.validate(bad,originals)

    def test_conditional_bookmark_cannot_be_removed_as_an_active_restriction(self):
        checked=self.prepare();definition=next(o for o in checked['observations'] if 'declared_context_definition' in o.get('process_roles',[]))
        entries=declared_reproduction._entries(definition,definition['declaration_inventory'],definition['declared_restrictions'])
        entry=next(e for e in entries if e['disposition']=='CONDITIONAL')
        with self.assertRaisesRegex(ValueError,'active declaration'):filter_effects.variant(entries,entry['id'],0,[])

    def test_empty_intersection_and_cell_keys_survive_single_restriction_removal(self):
        entries=[{'id':'a','disposition':'ACTIVE','restrictions':[{'field_id':'f','operator':'IN','values':['North']}]},
                 {'id':'b','disposition':'ACTIVE','restrictions':[{'field_id':'f','operator':'IN','values':['South']}]}]
        self.assertEqual(declared_reproduction.compose([e['restrictions'][0] for e in entries]),
                         [{'field_id':'f','operator':'IN','values':[]}])
        self.assertEqual(filter_effects.variant(entries,'b',0,[]),entries[0]['restrictions'])
        self.assertEqual(filter_effects.variant(entries,'a',0,entries[0]['restrictions']),
                         [{'field_id':'f','operator':'IN','values':[]}])

    def test_blank_is_compared_as_a_result_and_never_becomes_zero(self):
        from investigator.reported_figure import from_candidates
        self.scope['reported_figure']=from_candidates([{'start':0,'end':5,'quote':'blank'}],'blank')
        checked=self.prepare(None)
        result=filter_effects.run(self.adapter,self.layer,self.measure['id'],self.scope,checked)
        self.assertIsNone(checked['finding']['reproduced_value'])
        self.assertEqual(sum(row['changed'] for row in result['finding']['variants']),1)
        self.assertTrue(any(row['quantity'] is None and not row['changed'] for row in result['finding']['variants']))

    def test_adapter_refuses_an_arbitrary_variant_even_when_the_removal_id_is_valid(self):
        checked=self.prepare();definition=next(o for o in checked['observations'] if 'declared_context_definition' in o.get('process_roles',[]))
        entries=declared_reproduction._entries(definition,definition['declaration_inventory'],definition['declared_restrictions'])
        entry,index=filter_effects.active_restrictions(entries)[0]
        from investigator.onboarding import Conflict
        with self.assertRaisesRegex(Conflict,'scope differs'):
            self.adapter.evaluate_declared_context(self.layer,self.measure['id'],{'restrictions':[],
                'dimension_ids':[],'cell_id':checked['finding']['cell']['id'],'probe_purpose':'WITHOUT_DECLARATION',
                'declaration_id':entry['id'],'restriction_index':index})

    def test_cap_stops_without_extra_read_and_without_a_complete_effect_finding(self):
        checked=self.prepare();before=len(self.requests)
        self.adapter.remaining_diagnostic_reads=lambda:0
        with self.assertRaises(UsageHold):filter_effects.run(self.adapter,self.layer,self.measure['id'],self.scope,checked)
        self.assertEqual(len(self.requests),before)

    def test_non_reproduction_never_attributes_a_filter(self):
        checked=self.prepare();bad=copy.deepcopy(checked);bad['finding']['label']='NOT_REPRODUCED'
        from investigator.question_kind import UnimplementedRoute
        before=len(self.requests)
        with self.assertRaises(UnimplementedRoute):filter_effects.run(self.adapter,self.layer,self.measure['id'],self.scope,bad)
        self.assertEqual(len(self.requests),before)

    def test_unmodified_run_cap_is_split_for_a_filter_only_route(self):
        self.assertEqual(process_budget.allocation(12,{'question_kind':{'kind':'FILTER_EFFECT',
            'source':{'start':0,'end':6,'quote':'Report'}}}),{'WALK':1,'REPRODUCTION':11})

    def vertical_result(self):
        self.prepare()
        scope={**self.scope,'question_kind':{'kind':'FILTER_EFFECT','source':{'start':0,'end':6,'quote':'Report'}}}
        path={'status':'RESOLVED','layers':[self.layer,{'id':'lower','kind':'source'}],
              'evidence':{'id':'path','tool':'context','completeness':'COMPLETE_RESPONSE'}}
        surface={'engine':'OLAP Server','connection':self.model['workspace'],
            'object':self.model['native_id'],'identity':self.reader['account']}
        def baseline(layer,*args):
            self.assertEqual(layer['id'],self.layer['id'])
            return Probe('OBSERVED',layer['id'],value={'quantity':8},execution_surface=surface,
                evidence={'id':'baseline','tool':'context','completeness':'COMPLETE_RESPONSE','metadata':{}},
                surface_report=surface,surface_reportable=('identity','engine','object'))
        with patch.object(self.adapter,'resolve_path',return_value=path),patch.object(self.adapter,'evaluate',side_effect=baseline) as reads:
            result=vertical(self.adapter,self.measure['id'],scope)
        self.assertEqual(reads.call_count,1)
        return result

    def test_vertical_filter_route_finishes_at_the_visual_without_any_lower_read(self):
        result=self.vertical_result()
        self.assertEqual(result['classification'],'DECLARED_FILTER_EFFECTS')
        process_outcomes.validate(result,{o['id']:o for o in result['_observations']})
        self.assertIn(filter_effects.LIMIT,result['limits'])

    def test_new_outcome_does_not_accept_an_unrelated_established_receipt(self):
        from test_process_debugging import OutcomeContractTests
        value,originals=OutcomeContractTests().valid('NO_KNOWN_PATTERN')
        value['classification']='DECLARED_FILTER_EFFECTS'
        with self.assertRaisesRegex(ValueError,'per-restriction'):process_outcomes.validate(value,originals)


if __name__=='__main__':unittest.main()
