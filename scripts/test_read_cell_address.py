import copy
import unittest
from investigator import declared_reproduction
import test_report_cells as fixture


class ReadCellAddressTests(unittest.TestCase):
    setUp=fixture.CellTests.setUp
    part=fixture.CellTests.part
    modify=fixture.CellTests.modify
    grouped=fixture.CellTests.grouped

    def run_cells(self):
        self.grouped()
        return declared_reproduction.run(self.adapter,self.layer,self.measure['id'],self.scope)

    def test_two_explicit_cell_requests_validate_against_their_own_definition_and_reads(self):
        result=self.run_cells()
        from investigator.visual_target import resolve
        from investigator.adapters.report_cells import catalog
        previous=self.scope['target_visual']
        self.scope['target_visual']=resolve({'source':previous['source'],'mode':'TOTAL',
            'mode_source':{'start':0,'end':5,'quote':'TOTAL'}},ticket=None,candidates=catalog(self.model),
            report_id=previous['report_id'],measure_id=previous['measure_id'])
        total=declared_reproduction.run(self.adapter,self.layer,self.measure['id'],self.scope)
        findings=[c['finding'] for c in result['cells']+total['cells']]
        self.assertEqual(len(findings),2)
        self.assertNotEqual(findings[0]['definition_evidence_id'],findings[1]['definition_evidence_id'])
        self.assertNotEqual(findings[0]['lower_evidence_id'],findings[1]['lower_evidence_id'])
        observations={o['id']:o for o in result['observations']+total['observations']}
        definition=observations[findings[0]['definition_evidence_id']]
        self.assertEqual(definition['cell_definition'],observations[findings[1]['definition_evidence_id']]['cell_definition'])
        self.assertNotIn('cell',definition)
        for f in findings:
            read=observations[f['lower_evidence_id']]
            self.assertEqual(read['cell_address'],f['cell'])
            declared_reproduction.validate(f,observations)
        self.assertEqual(len(self.requests),3)  # two cells, one shared baseline

    def test_missing_read_address_is_a_refusal_not_a_default(self):
        result=self.run_cells();f=result['cells'][0]['finding']
        obs={o['id']:copy.deepcopy(o) for o in result['observations']}
        del obs[f['lower_evidence_id']]['cell_address']
        with self.assertRaisesRegex(ValueError,'Cell identity differs'):
            declared_reproduction.validate(f,obs)

    def test_cell_grouping_must_match_definition_even_if_read_and_marker_agree(self):
        from investigator.onboarding import digest
        result=self.run_cells();f=copy.deepcopy(result['cells'][0]['finding'])
        obs={o['id']:copy.deepcopy(o) for o in result['observations']}
        c=f['cell'];c['grouping_columns']=['different'];c['key_restrictions'][0]['field_id']='different'
        c['id']=digest({k:v for k,v in c.items() if k!='id'})
        obs[f['lower_evidence_id']]['cell_address']=copy.deepcopy(c)
        with self.assertRaisesRegex(ValueError,'Cell identity differs'):
            declared_reproduction.validate(f,obs)

    def test_refused_walk_keeps_proven_link_in_technical_evidence_only(self):
        from investigator.refusal_synthesis import render
        from investigator.process_receipts import refusal
        from investigator.ticket_inputs import document
        from investigator.onboarding import digest
        self.scope['reported_figure']={'state':'UNSPECIFIED'}
        result=self.run_cells()
        request={'text':'Explain the selected row.','request_key':'link',
                 'structured':{'report_link':'https://example.com/report/page'}}
        derived=document(request);part=derived['provenance']['parts'][-1]
        state={'envelope':{'symptom':derived['text'],'report_binding':{
            'resolution_kind':'DECLARED_REFERENCE','reference':{'request_hash':digest(derived['text']),
            'source':{'start':part['start'],'end':part['end'],'quote':request['structured']['report_link']}}}},
            'observations':result['observations']+[refusal('WALK_REFUSED','TOOL_UNAVAILABLE','walk-stop')]}
        outputs=render(state)
        self.assertIn('Explain the selected row.',outputs['business_output']['explanation']['text'])
        self.assertNotIn('https://',outputs['business_output']['explanation']['text'])
        self.assertIn(request['structured']['report_link'],outputs['technical_output']['explanation']['text'])

    def test_refused_walk_delivers_validated_cell_values_without_inventing_verdict(self):
        from investigator.refusal_synthesis import render
        from investigator.process_receipts import refusal
        self.scope['reported_figure']={'state':'UNSPECIFIED'}
        result=self.run_cells()
        state={'envelope':{'symptom':'Explain the selected row.'},'observations':result['observations']+[
            refusal('WALK_REFUSED','TOOL_UNAVAILABLE','walk-stop')]}
        outputs=render(state)
        self.assertIn('selected row produced 3',outputs['business_output']['explanation']['text'])
        self.assertIn('No reported figure supplied',outputs['business_output']['explanation']['text'])
        self.assertIn('KEYED',outputs['technical_output']['explanation']['text'])
        self.assertNotIn('(TOTAL)',outputs['technical_output']['explanation']['text'])
        self.assertEqual(outputs['provenance'],'DETERMINISTIC_REFUSAL_RENDERING')


if __name__=='__main__':unittest.main()
