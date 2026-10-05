import copy,importlib.util,unittest,tempfile
from pathlib import Path
spec=importlib.util.spec_from_file_location('known_acceptance',Path(__file__).resolve().parents[1]/'acceptance/known_domain/check.py')
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)

class AcceptanceGateTests(unittest.TestCase):
    def state(self):
        return {'status':'COMPLETED','envelope':{'context_id':'00000000-0000-4000-8000-000000000001','symptom':'Explain the result.'},'observations':[],
            'assessment':{'classification':'NO_KNOWN_PATTERN'},'synthesis':{'outputs':{k:{'question_account':{'status':'NOT_ANSWERED'},
                'explanation':{'text':'Answer to your question: Not answered.\n\nThe calculation requires business context.'},
                **({'model_mechanism':{'text':'The calculation requires business context.','provenance':'PROVIDER_MECHANISM'}} if k=='technical_output' else {})}
                for k in ('business_output','technical_output')}}}
    def case(self,state=None):
        return {'version':3,'reference_session_id':'reference','model_id':'model','ticket_hash':'a'*64,'context_pin':{'context_id':'00000000-0000-4000-8000-000000000001','hash':'a'*64},
            'expected':gate.project(state or self.state()),'invariants':sorted(gate.INVARIANTS),'acceptance_change_reason':'Structured reference.'}
    def errors(self,state,case=None):return gate.output_checks(case or self.case(),state,pinned_context=self.case()['context_pin'])

    def test_wording_changes_preserving_structure_pass(self):
        s=self.state();self.assertEqual(self.errors(s),[])
        for o in s['synthesis']['outputs'].values():o['explanation']['text']='Answer to your question: Not answered within this evidence scope.\n\nThe available checks leave the business explanation open.'
        self.assertEqual(self.errors(s),[])

    def test_changed_outcome_grade_layer_or_category_fails(self):
        for field,value in [('outcome','CONSISTENT_TO_BOUNDARY'),('answer_category','ANSWERED'),('boundaries',[{'grade':'OBJECT_DISTINCT'}]),('layers_reached',[{'object':'other'}])]:
            case=self.case();case['expected'][field]=value
            self.assertIn('STRUCTURE:'+field,self.errors(self.state(),case))

    def test_mechanism_is_not_guessed_from_rendered_spine(self):
        s=self.state();s['synthesis']['outputs']['technical_output'].pop('model_mechanism')
        self.assertIn('technical_output:MISSING_MODEL_MECHANISM_PROVENANCE',self.errors(s))
        self.assertNotIn('technical_output:MISSING_MODEL_MECHANISM_PROVENANCE',gate.output_checks(self.case(),s,pinned_context=self.case()['context_pin'],provider_mechanism={'text':'The calculation requires business context.','provenance':'SEALED_PROVIDER_MECHANISM'}))

    def test_reproduction_grades_verdict_not_walk_label(self):
        s=self.state();s['observations']=[{'check_kind':'DECLARED_CONTEXT_REPRODUCTION','id':'finding','composed_restrictions':[],'cell':{'id':'cell'},'label':'REPRODUCED','reproduced_value':'16','reported_figure':{'state':'NUMBER','value':'16'}}]
        for o in s['synthesis']['outputs'].values():o['question_account']={'status':'ANSWERED','reproduction_answer':'Yes'};o['explanation']['text']='Answer to your question: Yes, saved selections reproduce it.\n\nThe calculation matches the reported figure.'
        c=self.case(s);c['expected']=gate.project(s,'cell');c['expected'].pop('outcome')
        s['assessment']['classification']='NO_COMPARABLE_PATH';self.assertEqual(self.errors(s,c),[])
        s['observations'][0]['label']='NOT_REPRODUCED';self.assertIn('STRUCTURE:reproduction',self.errors(s,c))

    def test_entity_binding_kind_is_not_a_resolution_kind(self):
        s=self.state();s['envelope']['report_binding']={'resolution_kind':'STATED'}
        baseline=gate.project(s)
        s['envelope']['name_binding']={'kind':'REPORT'}
        self.assertEqual(gate.project(s),baseline)
        s['envelope']['report_binding']['resolution_kind']='EVIDENCE'
        self.assertNotEqual(gate.project(s)['resolutions'],baseline['resolutions'])

    def test_missing_answer_and_wrong_answer_enum_fail(self):
        s=self.state();s['synthesis']['outputs']['business_output']['explanation']['text']='The result remains open.'
        self.assertIn('business_output:ANSWER_CATEGORY_CHANGED',self.errors(s))
        s['synthesis']['outputs']['business_output']['explanation']['text']='Answer to your question: Answered.\n\nThe calculation requires business context.'
        self.assertIn('business_output:ANSWER_CATEGORY_CHANGED',self.errors(s))

    def test_raw_identifier_and_serialization_are_invariants(self):
        for bad in ('app.sales_123abc','{"quantity":1}'):
            s=self.state();s['synthesis']['outputs']['business_output']['explanation']['text']='Answer to your question: Not answered.\n\n'+bad
            self.assertTrue(any(':FORM:' in x for x in self.errors(s)))

    def test_wrong_context_fails(self):
        s=self.state();s['envelope']['context_id']='successor'
        self.assertIn('CONTEXT_ID_CHANGED',self.errors(s))

    def test_required_structure_and_invariants_fail_closed(self):
        for field in ('unknown','missing','reason'):
            c=self.case()
            if field=='unknown':c['invariants'].append('future')
            elif field=='missing':c['expected'].pop('layers_reached')
            else:c['acceptance_change_reason']=''
            with self.assertRaises(ValueError):gate.validate_case(c)

    def test_missing_private_inputs_blocks_without_network(self):
        with tempfile.TemporaryDirectory() as d:
            c={**self.case(),'ticket':'test','reference_session_id':'source'};r=gate.run_case(c,Path(d),Path(d)/'out')
        self.assertEqual(r['status'],'BLOCKED');self.assertEqual(r['network_calls'],0)

if __name__=='__main__':unittest.main()
