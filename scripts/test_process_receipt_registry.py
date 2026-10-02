import ast
import copy
from pathlib import Path
import unittest
from unittest.mock import patch
from investigator import process_receipts as receipts, refusal_synthesis
from investigator.onboarding import Conflict
from investigator import synthesis_digest


class ReceiptRegistryTests(unittest.TestCase):
    def test_every_registered_shape_has_a_terminal_display_and_two_refusal_outputs(self):
        for name, spec in receipts.REGISTRY.items():
            with self.subTest(shape=name):
                observation={'id':'original','tool':'process','check_kind':name,
                    'status':'COMPLETED','completeness':'COMPLETE_RESPONSE'}
                self.assertEqual(receipts.summary(observation)['shape'],name)
                if spec.refusal_stage:
                    observation['reason']='The original blocker.'
                    chain=[observation]
                else:
                    chain=[observation,receipts.refusal('WALK_REFUSED','The original blocker.','stop')]
                state={'envelope':{'symptom':'Check the reported figure.'},'observations':chain}
                original=copy.deepcopy(state)
                outputs=refusal_synthesis.render(state)
                for key in ('business_output','technical_output'):
                    self.assertIn('The original blocker.',outputs[key]['explanation']['text'])
                self.assertEqual(state,original)

    def test_earliest_refusal_survives_later_inventory_and_validation_complaints(self):
        stages=['INTAKE_REFUSED','RESOLUTION_REFUSED','INVENTORY_REFUSED',
                'REPRODUCTION_REFUSED','WALK_REFUSED']
        for index, stage in enumerate(stages):
            chain=[receipts.refusal(s,'first refusal' if i==index else 'later complaint',str(i))
                   for i,s in enumerate(stages) if i>=index]
            result=refusal_synthesis.render({'text':'What happened?','observations':chain})
            self.assertEqual(result['refusal']['stage'],receipts.REGISTRY[stage].refusal_stage)
            self.assertIn('first refusal',result['business_output']['explanation']['text'])
            self.assertNotIn('later complaint',result['business_output']['explanation']['text'])

    def test_hostile_unregistered_shape_is_named_before_any_rendering(self):
        hostile={'id':'bad','tool':'process','check_kind':'UNREGISTERED_HOSTILE',
                 'status':'COMPLETED','completeness':'COMPLETE_RESPONSE'}
        with self.assertRaisesRegex(Conflict,'Unregistered process receipt shape: UNREGISTERED_HOSTILE'):
            synthesis_digest.build({'observations':[hostile]},None)
        with self.assertRaisesRegex(Conflict,'UNREGISTERED_HOSTILE'):
            refusal_synthesis.render({'text':'Question','observations':[hostile]})

    def test_producer_check_kind_literals_cannot_outgrow_registry(self):
        root=Path(__file__).parent/'investigator'
        found=set()
        for path in root.rglob('*.py'):
            tree=ast.parse(path.read_text(encoding='utf-8-sig'))
            for node in ast.walk(tree):
                if isinstance(node,ast.Dict):
                    for key,value in zip(node.keys,node.values):
                        if isinstance(key,ast.Constant) and key.value=='check_kind' and isinstance(value,ast.Constant):
                            found.add(value.value)
        self.assertTrue(found)
        self.assertEqual(found-set(receipts.REGISTRY),set())

    def test_registered_resolution_keeps_original_validation(self):
        observation={'id':'resolution','tool':'process','check_kind':'REPORT_SELECTION_RESOLUTION'}
        with patch('investigator.report_resolution.validate',side_effect=ValueError('Missing inventory')):
            with self.assertRaisesRegex(ValueError,'Missing inventory'):
                synthesis_digest._process_evidence(observation,{}, {})

    def test_registry_adds_no_directory_or_model_payload(self):
        from test_evidence_synthesis import SynthesisTests
        fixture=SynthesisTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
        agent,state=fixture.stopped()
        with agent.runtime.db() as db:before=synthesis_digest.build(state,db)
        original=copy.deepcopy(receipts.REGISTRY)
        receipts.REGISTRY['FUTURE_TEST_ONLY']=receipts.Shape('retained')
        try:
            with agent.runtime.db() as db:after=synthesis_digest.build(state,db)
        finally:
            receipts.REGISTRY.clear();receipts.REGISTRY.update(original)
        self.assertEqual(before,after)

    def test_runtime_delivers_refusal_without_provider_or_reclassifying_evidence(self):
        from test_evidence_synthesis import SynthesisTests
        f=SynthesisTests();f.setUp();self.addCleanup(f.doCleanups)
        agent,state=f.stopped()
        with agent.runtime.db() as db:
            original=agent.load(db,state['id'])
            original['observations'].append(receipts.refusal(
                'REPORT_SELECTION_REFUSED','Target ambiguity: no scoped grouping column can test the stated value.','refusal'))
            agent.save(db,original,'TEST_REFUSAL',{})
        result=agent.synthesize(state['id'],lambda *_:self.fail('Refusal must not call provider'))
        self.assertEqual(result['synthesis']['status'],'COMPLETED')
        self.assertEqual(result['synthesis']['calls'],0)
        self.assertIsNone(result['synthesis']['assessment'])
        for key in ('business_output','technical_output'):
            self.assertIn('Target ambiguity:',result['outcome']['synthesis_outputs'][key]['explanation']['text'])
        self.assertEqual(result['observations'],original['observations'])

    def test_saved_intake_refusal_has_both_outputs_without_provider_or_reads(self):
        from test_question_intake import ask
        import test_investigator_workspace as fixture
        from investigator.question_intake import Intake
        f=fixture.WorkspaceTests();f.setUp();self.addCleanup(f.doCleanups)
        intake=Intake(f.workspace,lambda p:(ask(),{}))
        # save() is the common path for ASK, provenance refusals, HELD and user holds.
        body={'id':'refused','status':'NEEDS_INPUT','text':'Which result?',
              'question':'Which metric and exact filters should be checked?','error':None}
        with f.store.connect() as db:
            from investigator.onboarding import encoded,digest
            db.execute('INSERT INTO workspace_intakes VALUES (?,?,?,?)',('refused','refused',encoded(body),digest(body)))
            intake.save(db,body)
        self.assertEqual(intake.get('refused')['refusal_outputs']['refusal']['text'],body['question'])


if __name__=='__main__':unittest.main()
