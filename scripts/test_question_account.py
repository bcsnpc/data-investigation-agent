import copy,unittest
from investigator import question_account as account
from investigator.onboarding import Conflict

class QuestionAccountTests(unittest.TestCase):
    def test_no_reported_figure_category_requires_the_explicit_procedure_receipt(self):
        from investigator.declared_reproduction import NO_FIGURE
        s=self.state('Explain the selected quantity.')
        s['envelope']['question_kind']={'kind':'VISUAL_CONTENT'}
        s['assessment']['classification']='NO_COMPARABLE_PATH'
        s['observations']=[{'id':'no-figure','status':'COMPLETED',
            'check_kind':'DECLARED_CONTEXT_REPRODUCTION_UNAVAILABLE','reason':NO_FIGURE}]
        result=account.build(s)
        self.assertEqual(result['status'],'NO_REPORTED_FIGURE')
        self.assertEqual(result['subjects'][0]['evidence_ids'],['no-figure'])
        self.assertIn('Answer to your question: No verdict',account.render(result))
        s['observations'][0]['reason']='The declared selection is unsupported.'
        self.assertEqual(account.build(s)['status'],'NOT_ANSWERED')
        s['observations'][0]['reason']=NO_FIGURE
        s['observations'][0]['status']='UNAVAILABLE'
        self.assertEqual(account.build(s)['status'],'NOT_ANSWERED')
    def state(self,question='Could the reported quantity be stale? Inspect freshness and processing history.'):
        return {'envelope':{'symptom':question},'observations':[],
                'assessment':{'classification':'TRANSFORMATION_LOGIC','limits':['Snapshot unknown.'],
                    'technical_output':{'skipped_steps':[{'capability':'presentation_freshness','reason':'Reader denied.'}]}}}
    def outputs(self):
        return {key:{'explanation':{'text':'A documented join can repeat entries.'},'mandatory_limits':['Snapshot unknown.']}
                for key in ('business_output','technical_output')}
    def test_freshness_subject_and_unanswered_status_are_required_in_each_output(self):
        state=self.state();outputs=self.outputs();original=copy.deepcopy(state)
        account.attach(outputs,state)
        for key in outputs:
            text=outputs[key]['explanation']['text']
            self.assertIn(state['envelope']['symptom'],text)
            self.assertIn('Not answered',text)
            self.assertIn('currency',text)
            self.assertIn('Refresh history was unavailable',text)
            self.assertLess(text.index('You asked:'),text.index('What was found instead:'))
            broken=copy.deepcopy(outputs);broken[key]['explanation']['text']='A documented join can repeat entries.'
            with self.assertRaises(Conflict):account.validate(broken,state)
        self.assertEqual(state,original)
    def test_same_finding_different_question_has_different_account(self):
        a=self.outputs();b=self.outputs();account.attach(a,self.state());account.attach(b,self.state('Explain the observed difference.'))
        self.assertNotEqual(a['business_output']['explanation']['text'],b['business_output']['explanation']['text'])
        self.assertEqual(a['business_output']['mandatory_limits'],b['business_output']['mandatory_limits'])
    def test_outcome_or_optional_timestamp_does_not_establish_currency(self):
        for outcome in ('REFRESH_LATENCY','CONSISTENT_TO_BOUNDARY','TRANSFORMATION_LOGIC'):
            s=self.state();s['assessment']['classification']=outcome
            self.assertEqual(account.build(s)['status'],'NOT_ANSWERED')
        s['observations']=[{'id':'timing','status':'COMPLETED','process_roles':['freshness']}]
        self.assertEqual(account.build(s)['status'],'PARTLY_ANSWERED')
    def test_unrecognised_and_multiple_requests_never_silently_close(self):
        self.assertEqual(account.build(self.state('Investigate this for me.'))['status'],'NOT_ANSWERED')
        s=self.state('Explain the difference and its business meaning.')
        s['observations']=[{'id':'equal','status':'COMPLETED','comparison_status':'CROSS_SURFACE_VERIFIED'}]
        value=account.build(s)
        self.assertEqual(value['status'],'PARTLY_ANSWERED')
        self.assertEqual({x['subject'] for x in value['subjects']},{'meaning','comparison'})
        self.assertIn('No authoritative business meaning',account.render(value))
    def test_tampered_question_or_completion_status_fails_closed(self):
        state=self.state();outputs=self.outputs();account.attach(outputs,state)
        for field,value in (('status','ANSWERED'),('question','Another question')):
            broken=copy.deepcopy(outputs);broken['business_output']['question_account'][field]=value
            with self.assertRaises(Conflict):account.validate(broken,state)

    def test_freshness_header_renders_actual_attempts_and_reasons_not_a_not_assessed_placeholder(self):
        s=self.state('Inspect the latest movements.');s['envelope']['question_kind']={'kind':'FRESHNESS'}
        marker={'id':'attempt','status':'COMPLETED','check_kind':'FRESHNESS_ATTEMPT',
            'freshness_attempt':{'checks':{'job_history':{'status':'UNAVAILABLE','reason':'No successful run covers this job.'},
                'source_delivery':{'status':'UNAVAILABLE','reason':'The source is configured unreachable.'}}}}
        s['observations']=[marker];outputs=self.outputs();account.attach(outputs,s)
        for output in outputs.values():
            text=output['explanation']['text']
            self.assertIn('No successful run covers this job.',text)
            self.assertIn('source is configured unreachable',text)
            self.assertNotIn('not assessed',text)
        marker['freshness_attempt']['checks']['job_history']={'status':'CURRENT','accounting_observed':True}
        self.assertIn('load accounting was read',account.render(account.build(s)))

    def test_every_declared_kind_owns_its_answer_subject_not_ticket_keywords(self):
        from investigator.question_kind import KINDS
        self.assertEqual(set(account.KIND_SUBJECTS),set(KINDS))
        for kind in KINDS:
            s=self.state('Inspect this.');s['envelope']['question_kind']={'kind':kind}
            value=account.build(s)
            self.assertEqual(value['subjects'][0]['subject'],account.KIND_SUBJECTS[kind])
            self.assertEqual(value['subject_provenance'],'DECLARED_QUESTION_KIND')
            self.assertEqual(value['status'],'NOT_ANSWERED')

    def test_kind_outcome_and_completed_evidence_determine_answer_for_each_kind(self):
        cases={
            'SOURCE_CORRECTNESS':('INGESTION_GAP',{'check_kind':'SOURCE_DELIVERY','delivery_result':{'status':'GAP'}},'ANSWERED'),
            'FIGURE_DIFFERENCE':('LOAD_LATENCY',{'check_kind':'SOURCE_DELIVERY','delivery_result':{'status':'LATENT'}},'ANSWERED'),
            'FRESHNESS':('LOAD_LATENCY',{'process_roles':['job_history']},'PARTLY_ANSWERED'),
            'TRANSFORMATION_MECHANISM':('TRANSFORMATION_LOGIC',{'process_roles':['mechanism']},'PARTLY_ANSWERED'),
            'METRIC_COMPONENTS':('TRANSFORMATION_LOGIC',{'process_roles':['left_definition']},'PARTLY_ANSWERED'),
            'DERIVED_CALCULATION':('TRANSFORMATION_LOGIC',{'process_roles':['transformation_definition']},'PARTLY_ANSWERED'),
            'EXPECTED_BEHAVIOR':('CONSISTENT_TO_BOUNDARY',{'comparison_status':'CROSS_SURFACE_VERIFIED'},'PARTLY_ANSWERED'),
            'BUSINESS_MEANING':('BUSINESS_QUESTION',{'process_roles':['flow_consistency']},'NOT_ANSWERED'),
            'VISUAL_CONTENT':('NO_COMPARABLE_PATH',{'process_roles':['established']},'NOT_ANSWERED')}
        for kind,(outcome,observation,status) in cases.items():
            with self.subTest(kind=kind):
                s=self.state('Inspect this.');s['envelope']['question_kind']={'kind':kind}
                s['assessment']['classification']=outcome
                s['observations']=[dict(observation,id='receipt',status='COMPLETED')]
                self.assertEqual(account.build(s)['status'],status)
                wording={'ANSWERED':'Answered within the checked scope','PARTLY_ANSWERED':'Partly answered','NOT_ANSWERED':'Not answered'}[status]
                self.assertIn('Answer to your question: '+wording,account.render(account.build(s)))
                s['observations'][0]['status']='UNAVAILABLE'
                self.assertEqual(account.build(s)['status'],'NOT_ANSWERED')

    def test_gap_answer_does_not_require_comparison_keywords_and_stays_qualified(self):
        s=self.state('Did the completed load leave anything out?');s['envelope']['question_kind']={'kind':'FIGURE_DIFFERENCE'}
        s['assessment']['classification']='INGESTION_GAP'
        s['observations']=[{'id':'delivery','status':'COMPLETED','check_kind':'SOURCE_DELIVERY','delivery_result':{'status':'GAP'}}]
        text=account.render(account.build(s))
        self.assertIn('Answered within the checked scope',text)
        self.assertIn('precise point of loss were not established',text)
        self.assertNotIn('Not answered',text)

    def test_visual_kind_takes_answer_from_reproduction_even_without_text_marker(self):
        from test_reproduction_composition import CompositionTests
        fixture=CompositionTests();s=fixture.state(fixture.rows())
        s['envelope'].update(symptom='Inspect this.',question_kind={'kind':'VISUAL_CONTENT'})
        self.assertIn('Yes',account.render(account.build(s)))
        s['observations']=fixture.rows('NOT_REPRODUCED')
        self.assertIn('No —',account.render(account.build(s)))

if __name__=='__main__':unittest.main()
