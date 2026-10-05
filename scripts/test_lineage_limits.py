import copy,unittest
from investigator.lineage_limits import category,technical,business,validate_outputs
from investigator.lineage_runtime import qualify
import test_lineage_runtime as fixture


class LimitsTests(unittest.TestCase):
    def test_failed_selected_proposal_keeps_count_status_and_reason(self):
        test=fixture.QualificationTests();args=test.setup_path()
        v=args['inferred'][0];v['status']='UNVERIFIED';v['reason']='The source read did not complete.'
        result=qualify(test.path,**args);row=result['unresolved_boundary']
        self.assertEqual(row['lineage_refusal'],{'proposal_count':1,'inventoried_proposal_count':1,'statuses':['UNVERIFIED'],'reason_categories':['READ_FAILED']})
        self.assertIn('treated as unbound',technical(row))
        self.assertEqual(len(result['layers']),2)

    def test_stale_and_different_sample_have_distinct_categories(self):
        test=fixture.QualificationTests();args=test.setup_path();args['current_hashes']={}
        row=qualify(test.path,**args)['unresolved_boundary']
        self.assertEqual(row['lineage_refusal']['reason_categories'],['STALE_CODE'])
        args=test.setup_path();args['cell']={'id':'other'}
        self.assertEqual(qualify(test.path,**args)['unresolved_boundary']['lineage_refusal']['reason_categories'],['SAMPLE_MISMATCH'])

    def test_rendered_limits_required_in_both_outputs(self):
        row={'upper_layer':'upper','lower_layer':'lower','lineage_refusal':{
            'proposal_count':2,'inventoried_proposal_count':7,'statuses':['STALE','UNVERIFIED'],'reason_categories':['READ_FAILED','STALE_CODE']}}
        assessment={'technical_output':{'unverified_boundaries':[row]}}
        payload={'deterministic_process_finding':{'unverified_boundaries':[row]},
            'layer_labels':{'upper':{'role':'SERVING','business_name':'prepared data'},'lower':{'role':'LANDING','business_name':'received entries'}}}
        outputs={'technical_output':{'explanation':{'text':technical(row)}},
                 'business_output':{'explanation':{'text':business(payload)}}}
        self.assertFalse(validate_outputs(assessment,outputs))
        outputs['technical_output']['explanation']['text']='No lineage.'
        self.assertIn('technical_output:UNBOUND_LINEAGE_REASON_MISSING',validate_outputs(assessment,outputs))
        outputs['business_output']['explanation']['text']='Not checked.'
        self.assertIn('business_output:UNBOUND_LINEAGE_LIMIT_MISSING',validate_outputs(assessment,outputs))
        self.assertNotIn('UNVERIFIED',business(payload))

if __name__=='__main__':unittest.main()
