import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch,Mock
from investigator import estate_manifest as manifest


ROOT=Path(__file__).resolve().parents[1]


class ManifestTests(unittest.TestCase):
    def fixture(self):return json.loads((ROOT/'infra/estates/fixture.json').read_text())

    def test_fixture_and_unimplemented_estate_validate_without_transport(self):
        for name in ('fixture','databricks'):
            with self.subTest(name=name):manifest.load(ROOT/'infra/estates'/f'{name}.json')
        text=(ROOT/'infra/estates/databricks.json').read_text().lower()
        for word in ('microsoft','fabric','azure','power bi','onelake'):
            self.assertNotIn(word,text)
        from investigator.adapters.estate_installation import configuration
        with self.assertRaisesRegex(ValueError,'not installed'):
            configuration(manifest.load(ROOT/'infra/estates/databricks.json'))

    def test_closed_keys_missing_roles_audits_scopes_and_references_fail_named(self):
        mutations=[('environment_override',lambda m:m.update(environment_override='elsewhere')),
            ('layers',lambda m:m['layers'][0].pop('role')),
            ('audit',lambda m:m['pipelines'][0]['audit'].pop('resource')),
            ('reader',lambda m:m['identities'][0]['scopes'].clear()),
            ('system_of_record',lambda m:m.update(system_of_record='missing')),
            ('reach',lambda m:m['layers'][0]['reach'].update(extra=True)),
            ('code_resources',lambda m:m['lineage']['inference'].update(enabled=True)),
            ('restoration_reserved',lambda m:m['budgets']['round'].update(restoration_reserved=401))]
        for field,edit in mutations:
            m=self.fixture();edit(m)
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,field):manifest.validate(m)

    def test_no_second_config_read_in_projection_or_installation(self):
        m=self.fixture()
        from investigator.adapters.estate_installation import configuration
        with patch.object(Path,'read_text',side_effect=AssertionError('No second config read')):
            c=configuration(manifest.validate(m));p=manifest.policy(m)
        self.assertEqual(c['system_of_record']['asset_id'],m['layers'][-1]['asset_id'])
        self.assertEqual(c['load_audits'][0]['audit_asset_id'],m['resources'][0]['asset_id'])
        self.assertEqual(p['daily_limits']['cloud_calls'],m['budgets']['rolling_physical_requests'])
        # Build uses exactly the manifest file; DB/credential evidence access is
        # distinct from another configuration file and is mocked here.
        from investigator.estate_installation import build
        with patch('investigator.estate_installation.load',return_value=m) as reader,\
             patch('investigator.onboarding.ModelStore'),patch('investigator.runtime.Runtime'),\
             patch('investigator.adaptive_runtime.AdaptiveRuntime'),patch('investigator.workspace.Workspace') as workspace,\
             patch('metadata_config.load_config',side_effect=AssertionError('Legacy config read')),\
             patch('json.load',side_effect=AssertionError('Other JSON config read')),\
             patch.object(Path,'read_text',side_effect=AssertionError('Other text config read')):
            loaded,_=build('estate.json')
        reader.assert_called_once_with('estate.json')
        self.assertEqual(loaded,m)
        self.assertEqual(workspace.call_args.kwargs['dynamic_read_limit'],12)

    def test_adapter_cannot_redeclare_scope_or_pipeline_config(self):
        from investigator.adapters.estate_installation import configuration
        m=self.fixture();m['adapters'][0]['options']['load_audits']=[]
        with self.assertRaisesRegex(ValueError,'options'):configuration(manifest.validate(m))
        m=self.fixture();m['identities'][0]['principal']='different-reader'
        with self.assertRaisesRegex(ValueError,'account differs'):configuration(manifest.validate(m))

    def test_unreachable_is_declared_without_destroying_reader_scope(self):
        from investigator.adapters.estate_installation import configuration
        m=self.fixture();m['layers'][-1]['reachable']=False
        c=configuration(manifest.validate(m))
        self.assertFalse(c['system_of_record']['reachable'])
        self.assertEqual(len(m['identities'][1]['scopes']),1)

    def test_generation_bounds_are_also_checked_by_the_consumer(self):
        m=self.fixture();m['model']['generation_options']['max_output_tokens']=16001
        with self.assertRaisesRegex(ValueError,'max_output_tokens'):manifest.validate(m)

    def test_manifest_cannot_emit_workspace_rejected_bounds(self):
        from investigator.workspace import DYNAMIC_READ_BOUNDS,DYNAMIC_INPUT_BOUNDS
        for key,bounds in [('diagnostic_reads_per_run',DYNAMIC_READ_BOUNDS),('input_characters_per_run',DYNAMIC_INPUT_BOUNDS)]:
            for value in (bounds[0]-1,bounds[1]+1):
                m=self.fixture();m['budgets'][key]=value
                with self.subTest(key=key,value=value),self.assertRaisesRegex(ValueError,key):manifest.validate(m)

    def test_adapter_address_and_credential_cannot_be_silent_parallel_config(self):
        from investigator.adapters.estate_installation import configuration
        m=self.fixture();m['layers'][0]['reach']['address']='different-address'
        with self.assertRaisesRegex(ValueError,'reach.address'):configuration(manifest.validate(m))
        m=self.fixture();m['identities'][1]['credential_reference']='different-secret'
        with self.assertRaisesRegex(ValueError,'credential reference'):configuration(manifest.validate(m))

    def test_declared_lineage_is_evidence_and_conflicts_refuse_without_inventing_quantity(self):
        from investigator.estate_lineage import apply
        estate={'layers':[{'id':x,'asset_id':x} for x in ('upper','lower','other')],
            'lineage':{'bindings':[{'from_layer':'lower','to_layer':'upper','provenance':'DECLARED_BY_CONFIGURATION'}]}}
        path={'layers':[{'id':'upper'},{'id':'lower'}]}
        good=apply(path,estate)
        self.assertEqual(good['layers'],path['layers'])
        self.assertEqual(good['estate_lineage_declarations'][0]['provenance'],'DECLARED_BY_CONFIGURATION')
        bad=apply({'layers':[{'id':'upper'},{'id':'other'}]},estate)
        self.assertEqual(bad['layers'],[{'id':'upper'}]);self.assertIn('conflicts',bad['unresolved_boundary']['reason'])
        missing=apply({'layers':[{'id':'upper'}],'unresolved_boundary':{'reason':'no quantity'}},estate)
        self.assertEqual(missing['layers'],[{'id':'upper'}]);self.assertIn('not a comparison proof',missing['unresolved_boundary']['reason'])


class ManifestAdmissionTests(unittest.TestCase):
    def test_manifest_does_not_reduce_planner_directory_coverage(self):
        import test_flexible_investigation as fixture
        from investigator.adaptive_runtime import AdaptiveRuntime
        from investigator.adaptive_candidates import catalog
        from investigator.process_tape import bytes_of
        helper=fixture.DynamicTests();helper.setUp();self.addCleanup(helper.doCleanups)
        agent=AdaptiveRuntime(helper.runtime,lambda _:None)
        state=agent.get(agent.create(helper.envelope,'manifest-context')['id'])
        choices,_=catalog(helper.store,helper.config,helper.envelope)
        before=agent.payload(state,choices)
        helper.config['_estate']={'manifest_hash':'synthetic','layers':[],
            'lineage':{'bindings':[],'inference':{'enabled':False,'code_resources':[]}}}
        after=agent.payload(state,choices)
        def coverage(payload):
            entries=payload['context_entry_points']
            return {'entries':len(entries),'sql_entries':sum(a['kind']=='SqlObject' for a in entries),
                'payload_characters':len(bytes_of(payload).decode())}
        self.assertEqual(coverage(before),coverage(after))
        self.assertEqual(bytes_of(before),bytes_of(after))
        print('MANIFEST_CONTEXT_COVERAGE '+json.dumps({'before':coverage(before),'after':coverage(after)}))

    def test_round_pot_reserves_restoration_and_never_refunds(self):
        import test_flexible_investigation as fixture
        from investigator.usage_governance import UsageGovernor,UsageHold
        helper=fixture.DynamicTests();helper.setUp();self.addCleanup(helper.doCleanups)
        helper.runtime.config['_estate']={'round':{'starts_at_epoch':0,'physical_requests':3,'restoration_reserved':2}}
        policy={'environment':helper.store.environment,'daily_limits':{'planner_calls':50,'cloud_calls':50,
            'input_characters':1000000,'output_tokens':100000},'max_inflight_planners':1,'no_progress_limit':3}
        gov=UsageGovernor(helper.runtime,policy,lambda:1000)
        gov.metered_read('investigation','read',lambda:'value')
        with self.assertRaisesRegex(UsageHold,'round physical'):gov.metered_read('investigation','second',lambda:self.fail('No request'))
        gov.grant_batch({'batch_id':'restore','environment':helper.store.environment,'approved_by':'human',
            'approval_reference':'test-only','expires_at':2000,'runs':[{'session_id':'restoration','purpose':'RESTORATION','reads':2}]})
        for i in range(2):gov.restoration_read('restoration',str(i),lambda:'restored')
        with self.assertRaisesRegex(UsageHold,'round physical'):gov.metered_read('investigation','third',lambda:self.fail('No request'))

    def test_manifest_ceiling_blocks_undeclared_and_unreachable_layer_before_read(self):
        from test_system_of_record import SourceAdapter
        from investigator.process_debugging import vertical,REQUIRED_CAPABILITIES,OPTIONAL_CAPABILITIES
        for mode in ('unreachable','undeclared'):
            adapter=SourceAdapter(['report','delivery','application'],dict(report=12,delivery=12,application=12))
            rows=[{'id':k,'asset_id':k,'reachable':True} for k in ('report','delivery','application')]
            if mode=='unreachable':rows[-1]['reachable']=False
            else:rows.pop()
            adapter.config={'_estate':{'capability_ceiling':sorted(REQUIRED_CAPABILITIES|OPTIONAL_CAPABILITIES),
                'layers':rows,'resources':[],'lineage':{'inference':{'enabled':False,'code_resources':[]}},'accepted_limits':[]}}
            result=vertical(adapter,'m',{})
            self.assertNotIn('application',adapter.evaluated)
            self.assertNotEqual(result['classification'],'CONSISTENT_TO_SOURCE')
