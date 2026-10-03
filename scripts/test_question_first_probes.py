"""Read caps preserve question-first evidence and name every stopped probe."""
import json,unittest
import test_report_cells as fixture
from investigator import declared_reproduction,narrative_form

class QuestionFirstTests(unittest.TestCase):
    setUp=fixture.CellTests.setUp
    part=fixture.CellTests.part
    modify=fixture.CellTests.modify
    def three(self):
        doc=json.loads(self.visual['metadata']['content'])
        for name in ('second','third'):
            doc['name']=name
            self.part('definition/pages/p/visuals/'+name+'/visual.json',doc)
            self.modify(self.page,lambda d:d['visualInteractions'].append({'source':'s','target':name,'type':'DataFilter'}))
    def check(self):return declared_reproduction.run(self.adapter,self.layer,self.measure['id'],self.scope)
    def test_three_candidates_share_declared_and_baseline_reads(self):
        self.three();result=self.check()
        self.assertEqual(len(result['cells']),3)
        self.assertEqual(len(self.requests),2)
        self.assertIn('TREATAS',self.requests[0]['query'])
        self.assertNotIn('TREATAS',self.requests[1]['query'])
        self.assertEqual(len(self.adapter.duplicate_read_events),4)
        self.assertTrue(all(e['diagnostic_reads']==0 for e in self.adapter.duplicate_read_events))
    def test_one_slot_records_declared_value_and_names_stopped_baseline_in_both_outputs(self):
        self.adapter.remaining_diagnostic_reads=lambda:1-len(self.requests)
        result=self.check()
        self.assertEqual(len(self.requests),1);self.assertIn('TREATAS',self.requests[0]['query'])
        self.assertNotIn('finding',result)
        read=next(o for o in result['observations'] if o.get('applied_restrictions'))
        self.assertEqual(read['reproduction_quantity'],'3')
        stopped=result['unevaluated_cells'][0]
        self.assertEqual(stopped['purpose'],'UNDECLARED_CONTEXT')
        for key in ('business_output','technical_output'):
            self.assertIn('check without report declarations',result[key])
            self.assertIn('would establish',result[key])
    def test_cap_names_all_remaining_jobs_without_a_verdict(self):
        self.adapter.remaining_diagnostic_reads=lambda:0
        result=self.check();self.assertEqual(self.requests,[])
        self.assertEqual([s['purpose'] for s in result['unevaluated_cells']],['DECLARED_CONTEXT','UNDECLARED_CONTEXT'])
        self.assertNotIn('finding',result)
    def test_existence_and_baseline_reads_use_the_same_run_cache(self):
        from test_report_scoped_cells import ScopedTests
        ScopedTests.native(self)
        binding=self.scope['report_binding']
        self.adapter._observe_selection_value(self.layer,self.column['id'],'North',binding)
        self.adapter._observe_selection_value(self.layer,self.column['id'],'North',binding)
        self.adapter.evaluate(self.layer,self.measure['id'],{'filters':[],'report_binding':binding})
        self.adapter.evaluate(self.layer,self.measure['id'],{'filters':[],'report_binding':binding})
        self.assertEqual(len(self.requests),2)
    def test_cap_refusal_is_rendered_in_final_narratives(self):
        self.adapter.remaining_diagnostic_reads=lambda:1-len(self.requests)
        result=self.check();payload={'evidence':[{'id':o['id'],'result':o} for o in result['observations']]}
        text=narrative_form.business('The question remains unanswered.',payload)
        self.assertIn('check without report declarations',text)
        self.assertIn('would establish',text)
