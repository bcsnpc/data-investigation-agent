import copy
import unittest
from unittest.mock import patch
from investigator import reported_figure as figure, declared_reproduction
from investigator.process_debugging import Probe,NoValue,attest,attest_surface,vertical
from investigator.process_quantity import quantity
from test_process_debugging import Adapter
from test_declared_reproduction import NeutralAdapter,SCOPE


class ProbeAbsenceTests(unittest.TestCase):
    def test_omitted_observed_value_is_unconstructable(self):
        with self.assertRaisesRegex(ValueError,'explicit measured'):Probe('OBSERVED','x')
        with self.assertRaises(ValueError):Probe('OBSERVED','x',value=NoValue())

    def test_blank_zero_failure_and_not_obtained_are_distinct(self):
        blank=Probe('OBSERVED','x',evidence={'id':'blank'},value=None)
        zero=Probe('OBSERVED','x',evidence={'id':'zero'},value=0)
        failed=Probe('UNAVAILABLE','x',failure={'specificity':'SPECIFIC'})
        absent=Probe('NOT_COMPARABLE','x')
        self.assertEqual([p.value_state for p in (blank,zero,failed,absent)],['BLANK','MEASURED','FAILED','NOT_OBTAINED'])
        self.assertNotEqual(blank.value,zero.value)
        self.assertNotEqual(blank.value,failed.value)
        self.assertNotEqual(failed.value,absent.value)
        with self.assertRaises(ValueError):Probe('UNAVAILABLE','x',value=None)
        with self.assertRaisesRegex(ValueError,'receipt'):Probe('OBSERVED','x',value=0)

    def test_cell_omission_is_not_blank_and_blank_is_not_zero(self):
        with self.assertRaisesRegex(ValueError,'omitted'):quantity([{'q':{'type':'decimal'}}])
        self.assertEqual(quantity([{'q':{'value':None}}]),{'quantity':None})
        self.assertEqual(quantity([{'q':{'value':0}}]),{'quantity':'0'})
        self.assertEqual(quantity([]),[]) # No scalar was returned, not BLANK.


class FigureTests(unittest.TestCase):
    def make(self,text,quote):
        start=text.index(quote)
        return figure.from_candidates([{'start':start,'end':start+len(quote),'quote':quote}],text)

    def test_all_three_explicit_states_and_omission(self):
        with self.assertRaises(ValueError):figure.validate(None)
        with self.assertRaises(ValueError):figure.validate({})
        self.assertEqual(figure.label({'state':'UNSPECIFIED'},'0'),None)
        empty=self.make('The visual is empty.','empty')
        zero=self.make('The visual shows 0.','0')
        self.assertEqual(figure.label(empty,None),'REPRODUCED')
        self.assertEqual(figure.label(empty,'0'),'NOT_REPRODUCED')
        self.assertEqual(figure.label(zero,None),'NOT_REPRODUCED')
        self.assertEqual(figure.label(zero,'0'),'REPRODUCED')

    def test_multiple_numerals_one_reported_span_has_provenance(self):
        text='On 2026-09-14, order 712 exceeds threshold 400; the visual shows 123.'
        reported=self.make(text,'123')
        self.assertEqual(reported['value'],'123')
        self.assertEqual(text[reported['source']['start']:reported['source']['end']],'123')
        bad=copy.deepcopy(reported);bad['source']['start']=0
        with self.assertRaises(ValueError):figure.validate(bad,text)

    def test_two_plausible_candidates_are_a_named_refusal(self):
        text='The visual shows 123 or 124.'
        candidates=[self.make(text,q)['source'] for q in ('123','124')]
        with self.assertRaisesRegex(figure.AmbiguousFigure,'more than one'):figure.from_candidates(candidates,text)

    def test_reduced_precision_is_derived_never_widened(self):
        f=self.make('It shows about 3.4M.','about 3.4M')
        self.assertEqual(f['precision'],{'state':'STATED_PLACE','place':5})
        self.assertEqual(self.make('about 3M','about 3M')['precision'],{'state':'STATED_PLACE','place':6})
        self.assertEqual(figure.label(f,'3412345'),'REPRODUCED')
        self.assertEqual(figure.label(f,'3512345'),'NOT_REPRODUCED')
        bad=copy.deepcopy(f);bad['precision']['place']=6
        with self.assertRaises(ValueError):figure.validate(bad)
        with self.assertRaisesRegex(ValueError,'precision'):self.make('about 3400000','about 3400000')

    def test_reduced_precision_qualification_in_both_outputs(self):
        scope={**SCOPE,'reported_figure':self.make('about 3.4M','about 3.4M')}
        result=declared_reproduction.run(NeutralAdapter('3412345'),{'id':'top'},'measure',scope)
        self.assertEqual(result['finding']['label'],'REPRODUCED')
        for name in ('business_output','technical_output'):
            self.assertIn('weaker than an exact match',result[name])
            self.assertIn('No tolerance was inferred',result[name])

    def test_unspecified_reason_precedes_inventory_and_target(self):
        with patch.object(NeutralAdapter,'declared_context',side_effect=AssertionError('Must not extract')):
            result=declared_reproduction.run(NeutralAdapter(),{'id':'top'},'m',{'reported_figure':{'state':'UNSPECIFIED'}})
        self.assertEqual(result['reason'],declared_reproduction.NO_FIGURE)
        self.assertEqual(result['observations'],[])


class CoverageTests(unittest.TestCase):
    surface={'engine':'synthetic','connection':'c','object':'o','identity':'reader'}

    def test_identity_only_is_consistent_but_partial_not_matched(self):
        a=attest_surface(self.surface,{'identity':'reader'})
        self.assertEqual((a['status'],a['consistency'],a['coverage']),('PARTIAL','MATCHED','PARTIAL'))
        self.assertEqual(a['unattested_fields'],['connection','engine','object'])
        self.assertEqual(attest_surface(self.surface,None)['coverage'],'NONE')
        self.assertEqual(attest_surface(self.surface,self.surface)['status'],'MATCHED')

    def test_partial_can_reproduce_but_cannot_verify_cross_surface(self):
        reproduced=declared_reproduction.run(NeutralAdapter(),{'id':'top'},'measure',SCOPE)
        self.assertEqual(reproduced['finding']['upper_surface_attestation']['status'],'PARTIAL')
        self.assertEqual(reproduced['finding']['label'],'REPRODUCED')
        adapter=Adapter(['top','lower'],{'top':0,'lower':0},reports={'top':{'identity':'reader'}},reportable={'top':('identity',)})
        result=vertical(adapter,'m',{})
        self.assertEqual(result['classification'],'NO_COMPARABLE_PATH')
        self.assertFalse(any(o.get('comparison_status')=='CROSS_SURFACE_VERIFIED' for o in result['_observations']))

    def test_missing_or_contradictory_identity_does_not_get_partial_eligibility(self):
        for report in ({},{'identity':'different'}):
            p=attest(Probe('OBSERVED','x',{'id':'receipt'},0,execution_surface=self.surface,surface_report=report))
            self.assertEqual(p.status,'UNAVAILABLE')
            self.assertEqual(p.value_state,'FAILED')


class CompletionAbsenceTests(unittest.TestCase):
    def test_missing_active_set_is_not_an_explicit_empty_active_set(self):
        class Missing(NeutralAdapter):
            def declared_context(self,*args):
                d=super().declared_context(*args);del d['restrictions'];return d
        a=Missing();result=declared_reproduction.run(a,{'id':'top'},'m',SCOPE)
        self.assertEqual(result['unsupported_form'],'DECLARATION_INVENTORY_CONTRACT')
        self.assertIn('requires a list',result['reason'])
        self.assertEqual(a.read_scopes,[])

    def test_commit_availability_without_commit_content_is_not_an_observation(self):
        from investigator.adapters.microsoft_process import MicrosoftProcessAdapter
        a=MicrosoftProcessAdapter.__new__(MicrosoftProcessAdapter)
        a.config={'fabric':{'workspace_id':'w'}}
        path={'layers':[{'kind':'declared_source','binding':{'asset':{'id':'a','parent_id':'w/l','name':'t'}}}]}
        for result in ({},{'status':'AVAILABLE'},{'status':'AVAILABLE','latest_commit':None,'commit_info':{}}):
            a.read_ingestion=lambda _,r=result:r
            self.assertEqual(a.ingestion(path,{})['status'],'UNAVAILABLE')
        a.read_ingestion=lambda _:{'status':'AVAILABLE','latest_commit':'00000000000000000000.json','commit_info':{'timestamp':0}}
        result=a.ingestion(path,{})
        self.assertEqual(result['status'],'COMMIT_OBSERVED')
        self.assertEqual(result['evidence']['delta_commit']['commit_info']['timestamp'],0)

    def test_omitted_definition_status_never_explains_or_excludes(self):
        for explains in (False,True,None):
            for response in ({'explains':explains},{'status':'COMPLETED','explains':explains}):
                class Hostile(Adapter):
                    def transformation_definition(self,b):return response
                result=vertical(Hostile(['top','lower'],{'top':0,'lower':1}),'m',{})
                self.assertNotIn(result['classification'],('DEFECT','TRANSFORMATION_LOGIC'))
                self.assertTrue(any(s['capability']=='transformation_definition' for s in result['support']['process']['skipped_steps']))

    def test_missing_job_status_never_excludes_failed_completion(self):
        for response in ({},{'status':'CURRENT'}):
            class Hostile(Adapter):
                def job_history(self,b):return response
            result=vertical(Hostile(['top','lower'],{'top':0,'lower':1}),'m',{})
            self.assertNotEqual(result['classification'],'DEFECT')
            self.assertTrue(any(s['capability']=='job_history' for s in result['support']['process']['skipped_steps']))
