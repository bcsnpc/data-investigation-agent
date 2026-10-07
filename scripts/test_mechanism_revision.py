import copy,unittest
from investigator.mechanism_revision import revise,unchanged_structure,effective_records,require_unused_retry,REASON
from investigator.path_narrative import RepeatedHedge


class MechanismRevisionTests(unittest.TestCase):
    def attempt(self):
        return {'payload':{'layer_tokens':{}},'response':{'technical_output':{'text':'Old sentence.','evidence_ids':['r1']},
            'outcome':'UNCHANGED','comparison':{'upper':'16','lower':None,'snapshot':'UNVERIFIED'},'future_field':{'retained':True}}}

    def test_only_sentence_changes_even_future_evidence_is_preserved(self):
        original=self.attempt();saved=copy.deepcopy(original)
        changed=revise(original,'The join can repeat matching rows.')
        unchanged_structure(original['response'],changed)
        self.assertEqual(original,saved);self.assertEqual(changed['comparison'],original['response']['comparison'])

    def test_quantity_citation_outcome_and_future_field_changes_refuse(self):
        original=self.attempt()['response']
        for key,value in [('outcome','OTHER'),('comparison',{'upper':'17'}),('future_field',{}),
                          ('technical_output',{'text':'New sentence.','evidence_ids':['r2']})]:
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'STRUCTURED_FIELDS'):
                unchanged_structure(original,{**copy.deepcopy(original),key:value})

    def test_checker_rejection_is_not_a_valid_amendment(self):
        with self.assertRaises(RepeatedHedge):revise(self.attempt(),'The join may repeat rows and can raise the quantity.')
        with self.assertRaises(ValueError):revise(self.attempt(),'The lower-layer operation repeats rows.')

    def test_supersession_is_bound_to_original_tape_and_keeps_original(self):
        attempt={**self.attempt(),'provider_event_sha256':'event'}
        records=[{'case_id':'test','tape_sha256':'original','attempts':[attempt]}]
        revision={'case_id':'test','source_tape_sha256':'original','source_provider_event_sha256':'event',
            'superseded_text':'Old sentence.','response':revise(attempt,'The join can repeat matching rows.')}
        envelope={'version':1,'reason':REASON,'revisions':[revision]}
        effective=effective_records(records,envelope)
        self.assertEqual(records[0]['attempts'][0]['response']['technical_output']['text'],'Old sentence.')
        unchanged_structure(attempt['response'],effective[0]['attempts'][0]['response'])
        for field,value in [('source_tape_sha256','other-column'),('source_provider_event_sha256','other-event'),
                            ('superseded_text','Different original.')]:
            with self.subTest(field=field),self.assertRaises(ValueError):
                effective_records(records,{**envelope,'revisions':[{**revision,field:value}]})

    def test_second_rejection_cannot_be_resumed_as_a_third_call(self):
        row={'status':'BLOCKED','attempts':[{'number':1,'response':{'text':'Rejected.'}}]}
        require_unused_retry(row)
        row['attempts'][0]['number']=2
        with self.assertRaisesRegex(ValueError,'No unused composition retry'):require_unused_retry(row)


if __name__=='__main__':unittest.main()
