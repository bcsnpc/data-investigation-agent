import copy,unittest
from investigator import question_account as account
from investigator.onboarding import Conflict

class QuestionAccountTests(unittest.TestCase):
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

if __name__=='__main__':unittest.main()
