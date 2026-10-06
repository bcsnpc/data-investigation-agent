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

    def test_fixture_arithmetic_never_enters_runtime_configuration(self):
        from investigator.adapters.estate_installation import configuration
        configured=self.fixture();bare=copy.deepcopy(configured);bare.pop('fixture_states')
        actual=configuration(manifest.validate(configured));before=configuration(manifest.validate(bare))
        self.assertNotEqual(actual['_estate'].pop('manifest_hash'),before['_estate'].pop('manifest_hash'))
        self.assertEqual(actual,before)
        bad=copy.deepcopy(configured);bad['fixture_states'].append(copy.deepcopy(bad['fixture_states'][0]))
        with self.assertRaisesRegex(ValueError,'duplicate'):manifest.validate(bad)

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
        helper.config['_estate']['layers']=[{'id':'synthetic','string_semantics':{
            'collation':'BINARY','case_fold':False,'trim':False,'accent_fold':False}}]
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

class InstallationEntrypointTests(unittest.TestCase):
    def test_historical_entrypoints_cannot_execute_from_scattered_configuration(self):
        import run_investigation_v2,serve_investigations
        for module,extra in [(run_investigation_v2,['--config','legacy.json','--approve']),
                             (serve_investigations,['--enable-worker','--estate','legacy.json'])]:
            with self.subTest(module=module.__name__),patch('sys.argv',[module.__name__,*extra]),\
                 patch('metadata_config.load_config',side_effect=AssertionError('No legacy config')):
                with self.assertRaises(SystemExit) as refused:module.main()
                self.assertEqual(refused.exception.code,2)

    def test_historical_status_is_read_only_and_uses_only_manifest(self):
        import run_investigation_v2
        workspace=Mock();workspace.agent.runtime.get.return_value={'status':'SAVED'}
        with patch('sys.argv',['historical','--manifest','estate.json','--run-id','saved','--status-only']),\
             patch.object(run_investigation_v2,'build',return_value=({},workspace)) as build:
            self.assertEqual(run_investigation_v2.main(),0)
        build.assert_called_once_with(Path('estate.json'),execution_enabled=False)
        workspace.agent.runtime.get.assert_called_once_with('saved')
        workspace.agent.runtime.execute.assert_not_called()

class ManifestDiscoveryBudgetTests(unittest.TestCase):
    def test_metadata_http_admission_precedes_the_actual_request(self):
        import io
        from types import SimpleNamespace
        from metadata_auth import MetadataHttp
        class Reply(io.BytesIO):
            status=200;headers={}
        opener=Mock();opener.open.return_value=Reply(b'{"value":[]}')
        calls=[]
        def admit(send):calls.append('admitted');return send()
        client=MetadataHttp(SimpleNamespace(get_token=lambda _: 'synthetic-token'),opener,meter=admit)
        self.assertEqual(client('workspaces')['text'],{'value':[]});self.assertEqual(calls,['admitted'])
        client.meter=lambda _: (_ for _ in ()).throw(RuntimeError('budget boundary'))
        with self.assertRaisesRegex(RuntimeError,'budget boundary'):client('workspaces')
        self.assertEqual(opener.open.call_count,1)

    def test_multi_request_metadata_worker_counts_physical_requests_and_stops_at_pot(self):
        import sys,sqlite3
        import test_flexible_investigation as fixture
        from investigator.usage_governance import UsageGovernor,UsageHold
        from investigator.physical_reads import run
        helper=fixture.DynamicTests();helper.setUp();self.addCleanup(helper.doCleanups)
        helper.runtime.config['_estate']={'round':{'starts_at_epoch':0,'physical_requests':2,'restoration_reserved':0}}
        policy={'environment':helper.store.environment,'daily_limits':{'planner_calls':50,'cloud_calls':50,
            'input_characters':1000000,'output_tokens':100000},'max_inflight_planners':1,'no_progress_limit':3}
        gov=UsageGovernor(helper.runtime,policy,lambda:1000)
        raw='''import json,sys
json.loads(sys.stdin.readline())
for _ in range(2):
 print(json.dumps({'physical_read':'REQUEST','kind':'metadata_read'}),flush=True)
 if sys.stdin.readline().strip()!='ALLOW':raise RuntimeError('not admitted')
 print(json.dumps({'physical_read':'DONE','kind':'metadata_read','status':'AVAILABLE'}),flush=True)
print(json.dumps({'value':[]}),flush=True)
'''
        reply=gov.metered_read('scan','catalog',lambda:run([sys.executable,'-c',raw],input='{}',text=True,timeout=10))
        self.assertEqual(json.loads(reply.stdout),{'value':[]})
        with helper.runtime.db() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM adaptive_usage WHERE kind='cloud'").fetchone()[0],2)
        with self.assertRaises(UsageHold):gov.metered_read('scan','next',lambda:self.fail('No worker after cap'))

    def test_synthetic_worker_raw_acknowledgement_cannot_be_omitted(self):
        import io
        from metadata_worker import metered_request
        for raw,allowed in [('ALLOW\n',True),('DENY\n',False),('',False)]:
            called=[];output=io.StringIO()
            with patch('sys.stdin',io.StringIO(raw)),patch('sys.stdout',output):
                if allowed:self.assertEqual(metered_request(lambda:called.append(True) or {'value':[]} ),{'value':[]})
                else:
                    with self.assertRaisesRegex(RuntimeError,'not admitted'):metered_request(lambda:called.append(True))
            events=[json.loads(x) for x in output.getvalue().splitlines()]
            self.assertEqual(events[0],{'physical_read':'REQUEST','kind':'metadata_read'})
            self.assertEqual(bool(called),allowed)
            self.assertEqual(len(events),2 if allowed else 1)

class ManifestProseContractTests(unittest.TestCase):
    def test_configuration_prefix_cannot_exceed_the_consumer_or_hide_an_unfinished_sentence(self):
        from investigator.estate_limits import PREFIX,STATEMENT_BOUND,render
        from investigator.proposal_limits import ASSESSMENT_DETAIL
        self.assertEqual(STATEMENT_BOUND+len(PREFIX),ASSESSMENT_DETAIL)
        m=ManifestTests().fixture()
        for bad in ['x'*(STATEMENT_BOUND+1), 'A limitation ending without punctuation']:
            m['accepted_limits'][0]['statement']=bad
            with self.assertRaisesRegex(ValueError,'accepted_limits.*statement'):manifest.validate(m)
        valid='This is '+('x'*(STATEMENT_BOUND-len('This is ')-1))+'.'
        self.assertEqual(len(render(valid)),ASSESSMENT_DETAIL)
