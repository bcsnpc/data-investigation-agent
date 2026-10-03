import copy,unittest
from investigator import reproduction_composition as composition,question_account,narrative_form
from investigator.output_contract import business_text
from investigator.business_vocabulary import validate_identifier_form


class CompositionTests(unittest.TestCase):
    def rows(self,label='REPRODUCED'):
        result=[]
        for i,count,v in [(0,0,'61'),(1,1,'17'),(2,2,None)]:
            result.append({'id':'finding-'+str(i),'check_kind':'DECLARED_CONTEXT_REPRODUCTION','status':'COMPLETED',
                'label':label if i==2 else 'NOT_REPRODUCED','cell':{'id':str(i),'mode':'UNGROUPED'},
                'reported_figure':{'state':'EMPTY','source':{'start':0,'end':5,'quote':'empty'}},'reproduced_value':v,'undeclared_context_value':'61',
                'composed_restrictions':[{'field_id':'opaque/columns/movement_type','operator':'IN','values':['RECEIPT']},
                    {'field_id':'opaque/columns/product_name','operator':'IN','values':['Component 7']}][:count],
                'declarations':[{'disposition':'ACTIVE','assumption':'SAVED_DEFAULT'},
                    {'disposition':'CONDITIONAL','assumption':'INVOCATION_UNKNOWN'}], 'limitations':['Original limit.']})
        return result
    def state(self,rows):
        return {'envelope':{'symptom':'Check whether saved declared context reproduces the visual.'},
            'observations':rows,'assessment':{'classification':'NO_COMPARABLE_PATH'}}
    def payload(self,rows):
        return {'question':self.state(rows)['envelope']['symptom'],'evidence':[{'id':r['id'],'result':r} for r in rows]}
    def test_reproduction_answers_even_when_vertical_path_cannot_compare(self):
        rows=self.rows();a=question_account.build(self.state(rows))
        self.assertEqual(a['status'],'ANSWERED');self.assertIn('Yes',question_account.render(a))
        self.assertEqual(a['answering_cell_receipt_id'],'finding-2')
        self.assertEqual(a['finding_outcome'],'NO_COMPARABLE_PATH')
        rows=self.rows('NOT_REPRODUCED');self.assertIn('No —',question_account.render(question_account.build(self.state(rows))))
    def test_three_cells_one_lead_two_single_line_mentions_no_repeated_hedges(self):
        rows=self.rows();before=copy.deepcopy(rows);text=composition.body(rows)
        self.assertEqual(text.count('The answering visual'),1)
        self.assertEqual(sum(line.startswith('Other visual') for line in text.splitlines()),2)
        self.assertEqual(text.count('saved defaults'),1);self.assertEqual(text.count('invoked bookmark'),1)
        self.assertIn('RECEIPT',text);self.assertEqual(rows,before)
        self.assertEqual(narrative_form.business('Separate vertical probe was 999.',self.payload(rows)),text)
        self.assertNotIn('999',text);self.assertNotIn('resolution EVIDENCE',text)
    def test_action_is_fixed_by_answer_not_missing_vertical_access(self):
        for label,phrase in [('REPRODUCED','enhancement'),('NOT_REPRODUCED','current slicer'),(None,'figure or empty state')]:
            rows=self.rows(label)
            if label is None:
                for row in rows:row.update(label=None,reported_figure={'state':'UNSPECIFIED'})
            lead=composition.select(rows);self.assertIn(phrase,composition.action(lead)['text'])
            self.assertNotIn('access',composition.action(lead)['text'])
            if label is None:self.assertIn('No verdict: no figure supplied',question_account.render(question_account.build(self.state(rows))))
    def test_non_reproduction_open_set_names_moved_slicer_first_once(self):
        text=composition.body(self.rows('NOT_REPRODUCED'))
        self.assertEqual(text.count('A moved slicer'),1)
        self.assertLess(text.index('A moved slicer'),text.index('an invoked bookmark'))
        for term in ('user selection','row-level security','difference further back'):self.assertIn(term,text)
    def test_values_are_content_identifier_forms_still_fail(self):
        validate_identifier_form('RECEIPT Sales Customers silver')
        for text in ('fabric://workspace/report','app.Sales','some_column','receipt-123','C:/file/data','3484a2bc-98c5-4cef-be5c-a6215484075e'):
            with self.subTest(text=text),self.assertRaises(ValueError):validate_identifier_form(text)
        self.assertIn('RECEIPT',business_text('NO_COMPARABLE_PATH',self.payload(self.rows())))
    def test_freshness_question_is_not_closed_by_unrelated_reproduction(self):
        state=self.state(self.rows());state['envelope']['symptom']='Is the number stale?'
        self.assertEqual(question_account.build(state)['status'],'NOT_ANSWERED')
    def test_header_is_first_in_both_outputs_and_tampering_rejected(self):
        state=self.state(self.rows());outputs={k:{'explanation':{'text':composition.body(self.rows())}} for k in ('business_output','technical_output')}
        question_account.attach(outputs,state)
        for k in outputs:self.assertTrue(outputs[k]['explanation']['text'].startswith('You asked:'))
        outputs['business_output']['explanation']['text']='Not answered.'
        with self.assertRaises(ValueError):question_account.validate(outputs,state)
    def test_tested_adapter_ceiling_is_rendered_only_when_declared(self):
        payload={'scope':{'surface_attestation_ceiling':{'layer':{'connection':'NOT_SELF_REPORTABLE_FOR_READER'}}},'evidence':[]}
        source={'limits':[],'technical_output':{'unattested_surface_fields':[{'layer':'layer','field':'connection','evidence_id':'probe'}]}}
        text=narrative_form.technical('The recorded calculation was evaluated.',payload,source,{'text':'Supply the figure.'})
        self.assertIn('not self-reportable on this surface for this reader',text)
        self.assertEqual(text.count('Unattested connection'),1)


if __name__=='__main__':unittest.main()
