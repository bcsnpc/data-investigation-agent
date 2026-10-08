import unittest
from investigator.intake_field_scores import score


class FieldScoresTests(unittest.TestCase):
    def test_diagnostics_do_not_upgrade_invalid_whole_record_or_invent_spans(self):
        case={'id':'a','should_hold':True,'expected':{'status':'HELD','error':'TARGET_AMBIGUOUS',
            'nominated_question_kind':'FRESHNESS','target_id':None,'cell_mode':None,
            'model_id':None,'measure_id':None,'ticket_shape':None,'comparison_mode':None,
            'figure_state':'UNSPECIFIED','figure_value':None,'figure_precision':None,
            'filters':[],'selection_value':None,'dimension_ids':[]}}
        row={'case_id':'a','model_version':'model','nominated_question_kind':'FRESHNESS',
             'intake':{'status':'HELD','error':'PROVIDER_FAILURE','proposal':None}}
        result=score({'cases':[case]},[row],'model')
        self.assertEqual(result['field_accuracy']['kind'],1)
        self.assertEqual(result['full_matches'],0)
        self.assertEqual(result['field_accuracy']['target'],0)
        self.assertEqual(set(result['unscored_fields']),{'primary_span','comparison_spans'})
        row['intake']['error']='TARGET_AMBIGUOUS'
        self.assertEqual(score({'cases':[case]},[row],'model')['full_matches'],1)


if __name__=='__main__':unittest.main()
