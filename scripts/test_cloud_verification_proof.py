import copy,hashlib,json,shutil,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
from investigator.process_tape import Tape
from investigator.onboarding import digest
from investigator.estate_manifest import policy
from investigator.adapters.estate_installation import configuration
from test_process_tape import bootstrap
import test_binding_sample as samples
from test_microsoft_readiness import fixture
import test_estate_manifest as manifests
from cloud_verification_proof import validate,reference,validate_form_scope,require_exact_snapshot


class FreshProofTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.prepared=self.root/'prepared';self.capture=self.root/'capture';self.prepared.mkdir();self.capture.mkdir()
        self.manifest,self.scan,self.route=fixture();self.manifest['layers']+=manifests.ManifestTests().fixture()['layers'][2:];self.manifest['lineage']['source_delivery']=None;self.manifest['lineage']['code_locations']=[];self.manifest_path=self.root/'estate.json';self.manifest_path.write_text(json.dumps(self.manifest))
        self.config=configuration(self.manifest);self.context={'version':'approved-scan',**self.scan}
        self.model={'id':'selected-model','enabled':True,'context_id':'synthetic','context':{'id':'synthetic','model_id':'selected-model','scan_id':self.context['version']}}
        self.witness=samples.BindingSampleTests().trial('NUMERIC',[2,4],[4,2]);self.spec={'proposals':[self.witness['proposal']]}
        self.spec_path=self.root/'spec.json';self.spec_path.write_text(json.dumps(self.spec))
        self.patches=[patch('investigator.runtime.fingerprint',return_value='engine'),patch('investigator.source_revision.committed_revision',return_value='1'*40),
            patch('cloud_binding_verifier.preflight',return_value={'admissible':True,'verification_reads_needed':5,'verification_cap':40})]
        for p in self.patches:p.start();self.addCleanup(p.stop)
        approval={'manifest_sha256':self.sha(self.manifest_path),'config_hash':digest(self.config),'engine_hash':'engine',
                  'context_id':self.context['version'],'context_hash':digest(self.scan)}
        (self.prepared/'approval.json').write_text(json.dumps(approval))
        for n,value in [('context.json',self.context),('model.json',self.model),('endpoints.json',{})]:
            (self.prepared/n).write_text(json.dumps(value));shutil.copyfile(self.prepared/n,self.capture/n)
        for n in ('catalog.sqlite','inventory.sqlite'):
            (self.capture/n).write_bytes(b'synthetic sealed fixture');shutil.copyfile(self.capture/n,self.prepared/n)
        for stored,installed in [('verification_program.py','cloud_binding_verifier.py'),('code_verifier_capture.py','cloud_verification_capture.py')]:
            shutil.copyfile(Path(__file__).with_name(installed),self.capture/stored)
        definition=next(a for a in self.scan['assets']if a['kind']=='DefinitionPart')
        source={'id':'native-path','declared_source_binding':{'asset':{'id':self.route['selected_observations'][-1]['lower_layer']},
            'unchanged_connection':{'definition_hash':hashlib.sha256(definition['metadata']['content'].encode()).hexdigest()}}}
        obs=copy.deepcopy(self.route['selected_observations']);obs[-1]['comparison_status']='CROSS_SURFACE_VERIFIED'
        self.result={'status':'VERIFIED','profile_published':False,'verification_reads':5,'plan':{'verification_reads_needed':5,'verification_cap':40},
            'witnesses':[self.witness],'native_route':{'id':'native-session','observations':obs+[source],'process_read_receipts':self.route['read_receipts']}}
        self.seal()
    def sha(self,p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def seal(self):
        # Each changed synthetic case gets its own immutable capture directory.
        if (self.capture/'tape.json').exists():
            new=self.root/('capture-'+str(len(list(self.root.glob('capture*')))));new.mkdir()
            for p in self.capture.iterdir():
                if p.name not in ('tape.json','tape.events.jsonl'):shutil.copyfile(p,new/p.name)
            self.capture=new
        b=bootstrap();b.update(entry_point='code_verifier',config=self.config,engine_hash='engine',usage_policy=policy(self.manifest))
        b['state']={'environment':self.manifest['environment'],'engine_revision':'1'*40,'capture_contract':'code-verifier-dependencies-v1',
            'members':{p.name:self.sha(p)for p in self.capture.iterdir()},
            'inputs':{'context_hash':digest(self.context),'engine_fingerprint':'engine','model_context_id':'synthetic',
                      'native_route_contract':'declared-native-pair-v1','verification_spec':self.spec}}
        Tape(self.capture/'tape.json',b).finish({'status':'COMPLETED','result':self.result,'accounting':{'pending_reservations':0}})
        self.proof=reference(self.prepared,self.capture,self.spec_path)
    def test_real_witness_and_native_consumers_revalidate_without_replay_or_ready(self):
        with patch('cloud_verification_capture.replay',side_effect=AssertionError('no replay-before-live')):
            result=validate(self.manifest_path,self.proof)
        self.assertEqual('PROOF_REVALIDATED',result['status']);self.assertEqual(1,result['witness_count'])
        self.assertEqual('NOT_ASSESSED',result['readiness']);self.assertFalse(result['profile_published'])
        self.assertEqual(self.route['selected_observations'][0]['measure_id'],result['constraints']['measure_ids'][0])
    def test_missing_witness_refuses_despite_verified_label(self):
        self.result['witnesses']=[];self.seal()
        with self.assertRaisesRegex(ValueError,'WITNESS_COVERAGE'):validate(self.manifest_path,self.proof)
    def test_forged_witness_quantities_refuse_in_existing_consumer(self):
        self.result['witnesses'][0]['observations'][1]['quantities']['count']=99;self.seal()
        with self.assertRaises(ValueError):validate(self.manifest_path,self.proof)
    def test_changed_context_or_spec_or_dependency_refuses(self):
        for member in ('context.json','model.json','inventory.sqlite'):
            path=self.prepared/member;before=path.read_bytes();path.write_bytes(before+b' ')
            with self.subTest(member=member),self.assertRaises(ValueError):validate(self.manifest_path,self.proof)
            path.write_bytes(before)
        self.spec_path.write_text('{}')
        with self.assertRaisesRegex(ValueError,'SOURCE_HASH'):validate(self.manifest_path,self.proof)
    def test_native_attestation_is_recomputed_not_trusted_by_label(self):
        self.result['native_route']['observations'][0]['surface_report']['identity']='different-reader'
        self.seal()
        with self.assertRaises(ValueError):validate(self.manifest_path,self.proof)

    def test_wrong_current_image_fingerprint_refuses(self):
        with patch('investigator.runtime.fingerprint',return_value='different'):
            with self.assertRaisesRegex(ValueError,'PIN_DIFFERS'):validate(self.manifest_path,self.proof)
    def demo_workspace(self):
        from investigator.form_intake import VERSION as form_version
        measure=self.route['selected_observations'][0]['measure_id']
        models=[{'id':self.model['id'],'reports':[{'id':'report'}],'visuals':[{'target_id':'card','report_id':'report','page_id':'page',
            'measure_ids':[measure],'grouping_columns':[],'declared_scopes':{measure:{'state':'COMPLETE','restrictions':[]}}}]}]
        form={'version':form_version,'request_key':'demo','report_id':'report','page_id':'page','target_id':'card',
              'cell_mode':'UNGROUPED','value_seen':'17','comparison':'LOOKS_WRONG','description':''}
        path=self.root/'form.json';path.write_text(json.dumps(form))
        workspace=SimpleNamespace(store=SimpleNamespace(shared_catalog=object(),get=Mock(return_value=self.model)),
            agent=SimpleNamespace(governor=SimpleNamespace(shared=object())),intake_configuration=None,preview=Mock())
        return workspace,models,path

    def test_standalone_typed_handoff_consumes_real_proof_then_normal_form(self):
        from contextlib import nullcontext
        from investigator.unified_runner import handlers
        workspace,models,path=self.demo_workspace();ctx=SimpleNamespace(root=self.root,record=Mock(),step=lambda n,f:f())
        plan={'manifest':str(self.manifest_path),'run_id':'demo-only','options':{'ticket':str(path),'verification_proof':self.proof}}
        with patch('cloud_runner_context.install_private_snapshots',return_value={}), \
             patch('investigator.estate_installation.build',return_value=(self.manifest,workspace)), \
             patch('investigator.question_intake.snapshot',return_value={'models':models}), \
             patch('run_adaptive_investigation.local_azure_key',return_value=nullcontext()), \
             patch('cloud_form_worker.run_form',return_value={'ticket':{'state':'FINDINGS_SHARED'}}) as run:
            result=handlers()['investigation'](plan,ctx)
        self.assertEqual('DEMO_FINISHED',result['status']);self.assertEqual('NOT_ASSESSED',result['proof']['readiness'])
        run.assert_called_once_with(workspace,json.loads(path.read_bytes()))

    def test_forged_summary_cannot_admit_provider_or_workspace(self):
        from cloud_runner_context import demo_from_proof
        ctx=SimpleNamespace(record=Mock(),step=lambda n,f:f())
        plan={'manifest':str(self.manifest_path),'options':{'ticket':'form.json','verification_proof':{'status':'VERIFIED'}}}
        with patch('investigator.estate_installation.build') as build:
            with self.assertRaisesRegex(ValueError,'REFERENCE_REQUIRED'):demo_from_proof(plan,ctx)
        build.assert_not_called()

    def test_changed_current_model_or_filtered_form_stops_before_model_admission(self):
        from cloud_runner_context import demo_from_proof
        workspace,models,path=self.demo_workspace();ctx=SimpleNamespace(record=Mock(),step=lambda n,f:f())
        plan={'manifest':str(self.manifest_path),'options':{'ticket':str(path),'verification_proof':self.proof}}
        for changed in ('model','scope'):
            workspace.store.get.return_value={**self.model,'unexpected':'changed'} if changed=='model' else self.model
            if changed=='scope':
                next(iter(models[0]['visuals'][0]['declared_scopes'].values()))['restrictions']=[{'field_id':'field','operator':'IN','values':[1]}]
            with self.subTest(changed=changed),patch('cloud_runner_context.install_private_snapshots',return_value={}), \
                 patch('investigator.estate_installation.build',return_value=(self.manifest,workspace)), \
                 patch('investigator.question_intake.snapshot',return_value={'models':models}), \
                 patch('run_adaptive_investigation.local_azure_key') as model,patch('cloud_form_worker.run_form') as run:
                with self.assertRaisesRegex(ValueError,'MODEL_CHANGED|SCOPE_DIFFERS'):demo_from_proof(plan,ctx)
                model.assert_not_called();run.assert_not_called()

    def test_prepared_inventory_accepts_only_exact_audited_sqlite_backup(self):
        from contextlib import closing
        import sqlite3
        from cloud_verification_capture import snapshot
        source=self.prepared/'inventory.sqlite';source.unlink()
        with closing(sqlite3.connect(source)) as db:
            db.execute('CREATE TABLE inventory(value TEXT)');db.execute('INSERT INTO inventory VALUES(?)',('retained fixture',));db.commit()
            # Advance source header counters without changing its logical data.
            db.execute('UPDATE inventory SET value=value');db.commit()
            db.execute('PRAGMA user_version=7');db.commit()
        target=self.capture/'inventory.sqlite';target.unlink();expected=snapshot(source,target)
        self.assertNotEqual(self.sha(source),expected)
        before=self.sha(source);self.seal()
        result=validate(self.manifest_path,self.proof)
        self.assertEqual('PROOF_REVALIDATED',result['status']);self.assertEqual(before,self.sha(source))
        with closing(sqlite3.connect(source)) as db:
            db.execute('UPDATE inventory SET value=?',('changed data',));db.commit()
        with self.assertRaisesRegex(ValueError,'SNAPSHOT_DIFFERS'):validate(self.manifest_path,self.proof)

    def test_inventory_backup_reconstruction_retains_secret_audit(self):
        from contextlib import closing
        import sqlite3
        source=self.root/'unsafe-inventory.sqlite'
        with closing(sqlite3.connect(source)) as db:
            db.execute('CREATE TABLE inventory(value TEXT)');db.execute('INSERT INTO inventory VALUES(?)',('password=synthetic_credential_123',));db.commit()
        before=self.sha(source)
        from investigator.planner_recording import RecordingError
        with self.assertRaises(RecordingError):require_exact_snapshot(source,'0'*64)
        self.assertEqual(before,self.sha(source))

    def test_summary_strings_cannot_stand_in_for_proof(self):
        with self.assertRaisesRegex(ValueError,'REFERENCE_REQUIRED'):validate(self.manifest_path,{'status':'COMPLETED','verification_status':'VERIFIED'})


if __name__=='__main__':unittest.main()
