"""Provisional typed-profile reuse never becomes a ticket-cell or snapshot proof."""
import copy
import unittest
from investigator.transformation_service import select
from investigator.lineage_runtime import qualify
from investigator.lineage_limits import business
import test_binding_sample as samples


class ProfileActivationTests(unittest.TestCase):
    def test_runtime_lineage_callback_runs_after_execution_admission_and_is_metered(self):
        from unittest.mock import patch
        import test_flexible_investigation as fixture
        from investigator.adaptive_runtime import AdaptiveRuntime
        from investigator.process_debugging import VERSION
        helper=fixture.DynamicTests();helper.setUp();self.addCleanup(helper.doCleanups)
        envelope=copy.deepcopy(helper.envelope);envelope['strategy']=VERSION
        seen=[]
        def lineage(adapter,path,scope,meter):
            seen.append(scope['measure_id'])
            meter('code_source',lambda:{'status':'AVAILABLE'},True)
            return path
        agent=AdaptiveRuntime(helper.runtime,lambda _:self.fail('No planner'),process_lineage=lineage)
        identity=agent.create(envelope,'profile-lineage-test')['id']
        with patch('investigator.process_debugging.vertical',side_effect=ValueError('after lineage')):
            state=agent.run(identity)
        self.assertEqual(seen,[envelope['measure_id']])
        self.assertEqual(state['cloud_calls'],0)
        self.assertEqual(state['physical_calls'],1)
        self.assertTrue(any(e['kind']=='PROCESS_READ_RECORDED' for e in state['events']))

    def arguments(self):
        helper=samples.BindingSampleTests();helper.setUp()
        proof=helper.trial('NUMERIC',[2,4],[4,2])
        return dict(declared=[],inferred=[proof],current_hashes={('code-item','unit.py'):'a'*64},
            boundary=proof['proposal']['boundary'],target_column='amount',context='synthetic',
            cell=None,precision=None,binding_profiles=True)

    def test_explicit_opt_in_recomputes_original_profile_and_preserves_caveat(self):
        args=self.arguments()
        result=select(**args)
        self.assertEqual(result['status'],'RESOLVED')
        self.assertTrue(result['verification']['requires_reverification'])
        self.assertEqual(result['verification']['snapshot_status'],'SNAPSHOT_UNVERIFIED')
        self.assertEqual(select(**{**args,'binding_profiles':False})['status'],'UNBOUND')

    def test_changed_code_context_column_or_later_failure_never_reuses_old_success(self):
        for change in ('hash','context','column','later'):
            args=self.arguments()
            if change=='hash':args['current_hashes'][('code-item','unit.py')]='b'*64
            elif change=='context':args['context']='another'
            elif change=='column':args['target_column']='another'
            else:
                failed=copy.deepcopy(args['inferred'][0]);failed['status']='UNVERIFIED';failed['reason']='Read failed'
                args['inferred'].append(failed)
            self.assertEqual(select(**args)['status'],'UNBOUND')

    def test_producer_status_cannot_replace_profile_receipts(self):
        args=self.arguments();args['inferred'][0]['observations'][1]['quantities']['count']=900
        with self.assertRaises(ValueError):select(**args)

    def test_engine_business_qualification_is_not_model_composed(self):
        text=business({'deterministic_process_finding':{'profile_verified_boundaries':['receipt']}})
        self.assertIn('lineage was verified on value, not on snapshot',text)
        self.assertIn('sampled agreement',text)

    def test_qualification_preserves_original_input_read_expression(self):
        args=self.arguments();args.pop('target_column');args.pop('boundary');args.pop('binding_profiles')
        estate={'layers':[{'id':'input','asset_id':'input-asset'},{'id':'output','asset_id':'output-asset'}],
            'lineage':{'inference':{'enabled':True},'code_locations':[{'from_layer':'input','to_layer':'output',
                'may_infer_from_code':True,'locations':[{'source':'fixture','path':'unit.py'}]}]}}
        path={'layers':[{'id':'output-asset','source_column':'amount'},
                        {'id':'input-asset','source_column':'amount','compiled':{'query':'untransformed input'}}]}
        result=qualify(path,estate=estate,addresses={'input-asset':'input-table','output-asset':'output-table'},**args)
        self.assertEqual(result['layers'][1]['compiled'],path['layers'][1]['compiled'])
        self.assertEqual(result['layers'][1]['binding']['provenance'],'INFERRED_FROM_CODE')
