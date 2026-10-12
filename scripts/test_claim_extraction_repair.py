import copy,unittest
from types import SimpleNamespace
from unittest.mock import patch
from investigator import claim_facts as facts
from investigator.claim_provider import extract,ClaimExtractionUnavailable
from investigator.claim_clarification import interpretation
from investigator.intake_span_references import tokens
from investigator.usage_governance import UsageHold


def raw(text,field='observation',symbol='OBSERVED'):
    return {'facts':[{'field':field,'reference':[1,len(tokens(text))],'symbol':symbol,'metric_reference':None}]}


class Decision:
    values=[];calls=0
    def __init__(self,*args,**kwargs):pass
    def _call(self,*args,**kwargs):
        type(self).calls+=1;v=type(self).values.pop(0)
        if isinstance(v,Exception):raise v
        return copy.deepcopy(v)


class ClaimExtractionRepairTests(unittest.TestCase):
    def setUp(self):
        Decision.calls=0
        self.workspace=SimpleNamespace(agent=SimpleNamespace(config={},generation_options={'max_payload_characters':32000}))
    def extract(self,text,values):
        Decision.values=values
        with patch('investigator.claim_provider.GovernedDecision',Decision):return extract(self.workspace,text,'document','session')
    def test_qualitative_observed_expected_keep_exact_statements(self):
        text='I expected some indication of when these cards were last updated.'
        result,audit=self.extract(text,[raw(text,symbol='EXPECTED')])
        value=result[0]['value']
        self.assertEqual(value['figure'],{'state':'UNSPECIFIED'})
        self.assertEqual(value['statement']['quote'],text)
        self.assertEqual(value['quantity_structure']['kind'],'QUALITATIVE')
        self.assertEqual(audit['usable_fields'],['observation'])
        claim={'settled':{'observation':[value]},'selected_binding':None,'facts':result}
        output=interpretation(claim,{'models':[]})['text']
        self.assertIn(text,output);self.assertNotIn('expected not stated',output)
    def test_plural_and_range_never_become_one_scalar_or_two_exact_values(self):
        for text,kind in [('500 collected and 600 invoiced','MULTIPLE_QUANTITIES'),('between 500 and 600','RANGE'),('about 500','PRECISION_UNAVAILABLE')]:
            value=facts.extraction(raw(text),text,'document')[0]['value']
            self.assertEqual(value['quantity_structure']['kind'],kind)
            self.assertEqual(value['figure'],{'state':'UNSPECIFIED'})
            for span in value['quantity_structure']['numerals']:
                self.assertEqual(text[span['start']:span['end']],span['quote'])
            self.assertTrue(value['quantity_structure']['numerals'])
    def test_single_number_and_empty_exact_contract_stays_unchanged(self):
        value=facts.extraction(raw('16'),'16','document')[0]['value']
        self.assertEqual(set(value),{'role','figure','metric_phrase'})
        self.assertEqual(value['figure']['value'],'16')
        self.assertEqual(facts.extraction(raw('blank'),'blank','document')[0]['value']['figure']['state'],'EMPTY')
    def test_near_shape_repairs_only_representation_and_no_missing_role(self):
        record={'field':'METRIC','reference':[1,1],'symbol':'CONTEXT'}
        result,audit=self.extract('Quantity',[{'facts':record}])
        self.assertEqual(result[0]['value'],{'phrase':'Quantity'})
        self.assertTrue(audit['repairs']);self.assertEqual(Decision.calls,1)
        bad=raw('Quantity');bad['facts'][0].pop('symbol')
        with self.assertRaisesRegex(ValueError,'REJECTED_TWICE'):self.extract('Quantity',[bad,bad])
        self.assertEqual(Decision.calls,3)
    def test_non_observation_metric_annotation_is_not_a_new_association(self):
        record=raw('Quantity','metric',None);record['facts'][0]['metric_reference']=[1,1]
        result,audit=self.extract('Quantity',[record])
        self.assertEqual(result[0]['value'],{'phrase':'Quantity'})
        self.assertNotIn('metric_span',result[0]['source'])
        self.assertIn('NON_OBSERVATION_METRIC_REFERENCE:0',audit['repairs'])
    def test_one_retry_for_reference_rejection_not_third(self):
        invalid=raw('16');invalid['facts'][0]['reference']=[99,99]
        _,audit=self.extract('16',[invalid,raw('16')]);self.assertEqual(audit['calls'],2)
        with self.assertRaisesRegex(ValueError,'REJECTED_TWICE'):self.extract('16',[invalid,invalid])
    def test_timeout_is_handled_without_second_provider_call(self):
        with self.assertRaises(ClaimExtractionUnavailable)as seen:self.extract('16',[TimeoutError('transport timeout')])
        self.assertTrue(seen.exception.audit['handled_timeout']);self.assertEqual(Decision.calls,1)
        self.assertEqual(seen.exception.audit['calls'],1)
    def test_retry_admission_refuses_and_authentication_propagates(self):
        invalid=raw('16');invalid['facts'][0]['reference']=[99,99]
        with self.assertRaises(ClaimExtractionUnavailable)as seen:self.extract('16',[invalid,UsageHold('Planner concurrency limit')])
        self.assertEqual(seen.exception.reason,'RETRY_ADMISSION_UNAVAILABLE')
        class AuthenticationError(Exception):pass
        with self.assertRaises(AuthenticationError):self.extract('16',[AuthenticationError('denied')])


if __name__=='__main__':unittest.main()
