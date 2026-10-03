import copy
import unittest
from investigator.process_debugging import vertical
from investigator import process_outcomes
from investigator.system_of_record import declaration
from investigator.output_contract import action, business_text
from test_process_debugging import Adapter


class SourceAdapter(Adapter):
    def __init__(self, *args, source='application', ceiling=8, **kwargs):
        super().__init__(*args, **kwargs)
        self.source=source
        self.ceiling=ceiling

    def resolve_path(self, measure):
        path=super().resolve_path(measure)
        path['max_boundaries']=self.ceiling
        if self.source is not None:path['system_of_record']={'asset_id':self.source}
        return path

    def evaluate(self, *args):
        from dataclasses import replace
        p=super().evaluate(*args)
        if p.evidence:
            p=replace(p,evidence=dict(p.evidence,declared_context={'filters':[], 'dimension_ids':[]}))
        return p


class SystemOfRecordTests(unittest.TestCase):
    def adapter(self, **kwargs):
        return SourceAdapter(['report','delivery','application','beyond'],
            dict(report=12,delivery=12,application=12,beyond=99),**kwargs)

    def test_equal_chain_stops_at_explicit_source_and_keeps_snapshot_limits(self):
        adapter=self.adapter()
        result=vertical(adapter,'measure',{})
        self.assertEqual(result['classification'],'CONSISTENT_TO_SOURCE')
        self.assertEqual(adapter.evaluated,['report','delivery','application'])
        self.assertEqual(result['support']['process']['recommended_action'],'ASK_APPLICATION_OWNER')
        self.assertTrue(any('SNAPSHOT_UNVERIFIED' in x for x in result['limits']))
        process_outcomes.validate(result,{o['id']:o for o in result['_observations']})
        self.assertIn('application owner',action(result['classification'])['text'])
        text=business_text(result['classification'])
        self.assertIn('same moment',text)
        self.assertIn('every expected entry',text)

    def test_no_declaration_no_source_outcome(self):
        a=SourceAdapter(['report','application'],dict(report=12,application=12),source=None)
        self.assertEqual(vertical(a,'m',{})['classification'],'CONSISTENT_TO_BOUNDARY')

    def test_depth_ceiling_is_not_source_reach(self):
        self.assertNotEqual(vertical(self.adapter(ceiling=1),'m',{})['classification'],'CONSISTENT_TO_SOURCE')

    def test_source_divergence_cannot_be_misclassified_before_delivery_producers_exist(self):
        a=self.adapter();a.values['application']=13
        result=vertical(a,'m',{})
        self.assertEqual(result['classification'],'NO_KNOWN_PATTERN')
        self.assertIn('source delivery',result['support']['process']['missing_capability'])

    def test_comparison_context_cannot_override_original_receipts(self):
        result=vertical(self.adapter(),'m',{})
        originals={o['id']:copy.deepcopy(o) for o in result['_observations']}
        originals['read-application']['declared_context']={'filters':['unmatched']}
        with self.assertRaisesRegex(ValueError,'original quantity receipts'):
            process_outcomes.validate(result,originals)

    def test_unknown_or_top_asset_is_not_a_terminal_proof(self):
        for source in ('absent','report'):
            self.assertNotEqual(vertical(self.adapter(source=source),'m',{})['classification'],'CONSISTENT_TO_SOURCE')

    def test_failed_application_attestation_and_disconnected_chain_do_not_qualify(self):
        for options in ({'reports':{'application':{'identity':'someone else'}}},
                        {'not_comparable':('delivery',)}):
            self.assertNotEqual(vertical(self.adapter(**options),'m',{})['classification'],'CONSISTENT_TO_SOURCE')

    def test_validator_rejects_deleted_boundary_divergence_scope_and_inferred_binding(self):
        result=vertical(self.adapter(),'m',{})
        originals={o['id']:o for o in result['_observations']}
        for change in ('deleted','divergent','context','inferred','declaration'):
            a=copy.deepcopy(result);obs=copy.deepcopy(originals)
            c=obs['boundary-2-comparison']
            if change=='deleted':a['support']['process']['evidence_by_role']['comparison'].remove(c['id'])
            elif change=='divergent':c['values_equal']=False
            elif change=='context':c['lower_declared_context']={'filters':['different']}
            elif change=='inferred':c['lower_binding_provenance']='INFERRED_FROM_CODE'
            else:obs['path']['resolved_source_path'].pop('system_of_record')
            with self.subTest(change=change), self.assertRaises(ValueError):process_outcomes.validate(a,obs)

    def test_declaration_never_defaults_or_accepts_names_and_extra_fields(self):
        for value in (None,{}, {'name':'application'}, {'asset_id':'x','inferred':True}, {'asset_id':' '}):
            with self.assertRaises(ValueError):declaration(value)

    def test_source_declaration_is_exposed_without_reconstructing_it_for_synthesis(self):
        from investigator.synthesis_digest import _definition_evidence
        path={'layers':[{'id':'report'},{'id':'application'}],
              'system_of_record':{'asset_id':'application'},'max_boundaries':1}
        observation={'metadata':{},'resolved_source_path':path}
        projected=_definition_evidence(observation)['resolved_source_path']
        self.assertEqual(projected,path)
        self.assertIsNot(projected,path)

    def test_config_loading_accepts_only_closed_declaration_and_retains_it(self):
        import json,tempfile
        from pathlib import Path
        from metadata_config import load_config
        config={'version':1,'sql':{'server':'test.example','database':'test',
            'visibility_schema':'scope','auth':{'mode':'dpapi_file','credential_file':'.local/test.xml'}},
            'fabric':{'workspace_id':'00000000-0000-0000-0000-000000000001',
                'auth':{'mode':'fabric_cli','tenant_id':'00000000-0000-0000-0000-000000000002','python':'python.exe'}},
            'storage':{'database':'.local/test.db'},'system_of_record':{'asset_id':'application'}}
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'config.json';path.write_text(json.dumps(config))
            self.assertEqual(load_config(path)['system_of_record'],{'asset_id':'application'})
            config['system_of_record']['guess']=True;path.write_text(json.dumps(config))
            with self.assertRaises(ValueError):load_config(path)


if __name__=='__main__':unittest.main()
