import base64
import json
from pathlib import Path
import tempfile
import unittest
from investigator.privacy_projection import Projection, ProjectionError, canonical, declaration
from investigator.privacy_tape import PrivacyTape


def policy():
    return {'tape_class': 'PRIVACY_PROJECTED', 'version': 'estate-privacy-projection-v1',
            'estate_id': 'synthetic-estate', 'key_reference': 'secret-store/estate-projection',
            'columns': ['column://synthetic/person_name']}


def projector(key=b'synthetic-in-memory-key-32-bytes!!', value=None):
    return Projection(value or policy(), lambda reference: key)


class PrivacyTests(unittest.TestCase):
    def test_sensitive_key_digest_is_built_from_projected_tuples_not_raw_values(self):
        from investigator.translation_proposer import key_fingerprint
        column=policy()['columns'][0]; keys=[['PRIVATE KEY A'],['PRIVATE KEY B'],[None]]
        normalization={'encoding':'TYPED_JSON','case_fold':False,'trim':False}
        p=projector(); projected=p.key_set([column],keys,normalization)
        self.assertEqual(projected['count'],3)
        self.assertEqual(projected['binary_hash'],key_fingerprint(projected['keys'],normalization)['binary_hash'])
        self.assertNotEqual(projected['binary_hash'],key_fingerprint(keys,normalization)['binary_hash'])
        self.assertEqual(projected,projector().key_set([column],keys,normalization))
        self.assertIsNone(projected['keys'][2][0])
        self.assertNotIn('PRIVATE KEY',canonical(projected).decode())
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'tape.json';tape=PrivacyTape(path,p)
            tape.event('KEY_SET',canonical(projected));outputs=tape.finish({'key_set':projected})
            replay_projection=projector();replay=PrivacyTape(path,replay_projection,replay=True)
            replay.event('KEY_SET',canonical(replay_projection.key_set([column],keys,normalization)))
            self.assertEqual(replay.finish(outputs),outputs)

    def test_sensitive_key_digest_requires_complete_typed_tuple_coverage(self):
        p=projector(); column=policy()['columns'][0]
        for columns,keys in (([column],[['PRIVATE',1]]),([column,column],[['A','B']]),
                             ([],[['A']]),([column],['A'])):
            with self.subTest(columns=columns,keys=keys),self.assertRaises(ProjectionError):
                p.key_set(columns,keys,{'encoding':'TYPED_JSON'})

    def test_sensitive_value_cannot_rename_schema_fields_or_merge_keys(self):
        column=policy()['columns'][0]
        for raw in ('quantity','value','column','private'):
            with self.subTest(raw=raw), tempfile.TemporaryDirectory() as folder:
                tape=PrivacyTape(Path(folder)/'tape.json',projector())
                with self.assertRaisesRegex(ProjectionError,'STRUCTURAL_KEY'):
                    tape.event('RESPONSE',canonical({column:raw,raw:12}))
                self.assertEqual(list(Path(folder).iterdir()),[])

    def test_synthetic_sensitive_column_records_and_replays_without_raw_disk_or_outputs(self):
        raw = 'PRIVATE SYNTHETIC PERSON'
        column = policy()['columns'][0]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'tape.json'
            p = projector()
            tape = PrivacyTape(path, p)
            # The early prose predates the typed result. It must not leak to
            # an append-only raw journal before that later result identifies it.
            request = canonical({'ticket': 'Check ' + raw})
            result = canonical({'columns': [column, 'quantity'], 'rows': [[raw, 12], [None, 0]]})
            tape.event('REQUEST', request)
            self.assertEqual(list(Path(folder).iterdir()), [])
            tape.event('RESPONSE', result)
            outputs = tape.finish({'business': 'Checked ' + raw, 'technical': raw,
                                   'count': 2, 'blank': None, 'zero': 0})
            self.assertNotIn(raw, json.dumps(outputs))
            self.assertEqual(outputs['count'], 2)
            self.assertIsNone(outputs['blank'])
            self.assertEqual(outputs['zero'], 0)
            for file in Path(folder).rglob('*'):
                if file.is_file():
                    self.assertNotIn(raw.encode(), file.read_bytes())
            stored = json.loads(path.read_bytes())
            for event in stored['events']:
                self.assertNotIn(raw.encode(), base64.b64decode(event['body']))
            replay_projection = projector()
            # Request projection uses the same independently supplied typed
            # value; replay never puts an original back into a recorded body.
            replay_projection.bind(column, raw)
            replay = PrivacyTape(path, replay_projection, replay=True)
            replay.event('REQUEST', request)
            replay.event('RESPONSE', result)
            self.assertEqual(replay.finish({'business': 'Checked ' + raw, 'technical': raw,
                                          'count': 2, 'blank': None, 'zero': 0}), outputs)
            self.assertEqual(stored['projection']['comparison'], 'EXACT_AFTER_PROJECTION')

    def test_nested_provider_json_and_base64_are_projected_before_write(self):
        raw = 'SENSITIVE_PROVIDER_NAME'
        p = projector()
        inner = {'output': [{'arguments': canonical({policy()['columns'][0]: raw,
                                                    'text': raw}).decode()}]}
        wrapper = canonical({'status': 200, 'body': base64.b64encode(canonical(inner)).decode()})
        projected = p.body(wrapper, base64_body=True)
        inner_projected = base64.b64decode(json.loads(projected)['body'])
        self.assertNotIn(raw.encode(), projected)
        self.assertNotIn(raw.encode(), inner_projected)
        self.assertIn(b'privacy_v1_', inner_projected)

    def test_keyed_per_estate_stable_distinct_and_not_unkeyed_dictionary_hash(self):
        import hashlib
        p = projector(); column = policy()['columns'][0]
        a = p.bind(column, 'Alice'); b = p.bind(column, 'Bob')
        self.assertEqual(a, projector().bind(column, 'Alice'))
        self.assertNotEqual(a, b)
        other = policy(); other['estate_id'] = 'another-estate'
        self.assertNotEqual(a, projector(value=other).bind(column, 'Alice'))
        self.assertNotIn(hashlib.sha256(b'Alice').hexdigest(), a)
        self.assertEqual(p.bind(column, a), a)

    def test_policy_or_key_change_cannot_reproject_a_tape(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'tape.json'
            PrivacyTape(path, projector()).finish({})
            other = policy(); other['columns'].append('column://synthetic/second')
            for p in (projector(key=b'another-in-memory-key-32-bytes!!!'), projector(value=other)):
                with self.assertRaisesRegex(ProjectionError, 'RE_RECORD_REQUIRED'):
                    PrivacyTape(path, p, replay=True)

    def test_content_change_fails_after_projection(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'tape.json'
            tape = PrivacyTape(path, projector()); tape.event('REQUEST', b'{"count":1}')
            tape.finish({})
            replay = PrivacyTape(path, projector(), replay=True)
            with self.assertRaisesRegex(ProjectionError, 'BYTES_DIFFER'):
                replay.event('REQUEST', b'{"count":2}')

    def test_projected_response_replays_without_reverse_dictionary_or_raw_values(self):
        column=policy()['columns'][0]
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'tape.json';tape=PrivacyTape(path,projector())
            tape.event('RESPONSE',canonical({column:'PRIVATE NAME'}))
            outputs=tape.finish({'technical':'PRIVATE NAME'})
            replay=PrivacyTape(path,projector(),replay=True)
            response=json.loads(replay.take('RESPONSE'))
            self.assertTrue(response[column].startswith('privacy_v1_'))
            self.assertEqual(replay.finish(outputs),outputs)

    def test_forged_projected_token_and_tampered_tape_refuse(self):
        p=projector()
        with self.assertRaisesRegex(ProjectionError,'VERIFIED_PROVENANCE'):
            p.bind(policy()['columns'][0],'privacy_v1_'+'a'*64)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'tape.json';PrivacyTape(path,projector()).finish({})
            value=json.loads(path.read_bytes());value['outputs']={'new':'changed'}
            path.write_bytes(canonical(value))
            with self.assertRaisesRegex(ProjectionError,'TAPE_SEAL'):
                PrivacyTape(path,projector(),replay=True)

    def test_nested_base64_json_is_not_an_escape_hatch(self):
        raw='PRIVATE_BASE64_NAME'
        value={'embedded':base64.b64encode(canonical({policy()['columns'][0]:raw})).decode()}
        result=projector().project(value)
        self.assertNotIn(raw.encode(),base64.b64decode(result['embedded']))

    def test_sensitive_empty_string_does_not_change_unrelated_empty_absent_or_zero_fields(self):
        column=policy()['columns'][0]
        result=projector().project({'columns':[column,'quantity'],'rows':[['',0],[None,0]],
                                   'explanation':'','absent':None,'zero':0})
        self.assertTrue(result['rows'][0][0].startswith('privacy_v1_'))
        self.assertIsNone(result['rows'][1][0])
        self.assertEqual(result['explanation'],'')
        self.assertEqual(result['zero'],0)

    def test_exact_column_identity_never_guesses_from_basename(self):
        p=projector()
        raw='NOT_THE_DECLARED_COLUMN'
        result=p.project({'column_id':'column://other/person_name','value':raw})
        self.assertEqual(result['value'],raw)

    def test_unresolved_column_headers_and_unaccounted_row_fields_refuse_capture(self):
        column=policy()['columns'][0]
        with tempfile.TemporaryDirectory() as folder:
            tape=PrivacyTape(Path(folder)/'tape.json',projector())
            for body in ({'columns':[{'name':'person_name'}],'rows':[['PRIVATE NAME']]},
                         {'columns':[column],'rows':[{'unresolved_alias':'PRIVATE NAME'}]},
                         {'columns':[column,column],'rows':[['A','B']]}):
                with self.assertRaises(ProjectionError):
                    tape.event('RESPONSE',canonical(body))
            self.assertEqual(list(Path(folder).iterdir()),[])

    def test_duplicate_keys_and_nested_ambiguous_json_cannot_hide_a_value(self):
        with tempfile.TemporaryDirectory() as folder:
            tape=PrivacyTape(Path(folder)/'tape.json',projector())
            for body in (b'{"value":"PRIVATE A","value":"PRIVATE B"}',
                         canonical({'input':'{"value":"PRIVATE A","value":"PRIVATE B"}'}),
                         canonical({'embedded':base64.b64encode(
                             b'{"value":"PRIVATE A","value":"PRIVATE B"}').decode()}),
                         b'{"value":NaN}'):
                with self.assertRaises(ProjectionError):
                    tape.event('RESPONSE',body)
            self.assertEqual(list(Path(folder).iterdir()),[])

    def test_manifest_file_cannot_declare_both_classes_with_duplicate_keys(self):
        from investigator.estate_manifest import load
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'estate.json'
            path.write_text('{"recording":{"tape_class":"PRIVACY_PROJECTED"},'
                            '"recording":{"tape_class":"EXACT"}}',encoding='utf8')
            with self.assertRaisesRegex(ValueError,'Duplicate'):
                load(path)

    def test_opaque_bytes_and_untyped_sensitive_numbers_refuse_without_disk_write(self):
        with tempfile.TemporaryDirectory() as folder:
            tape = PrivacyTape(Path(folder) / 'tape.json', projector())
            with self.assertRaisesRegex(ProjectionError, 'OPAQUE_BODY_REFUSED'):
                tape.event('REQUEST', b'unparsed sensitive text')
            with self.assertRaisesRegex(ProjectionError, 'TYPE_UNSUPPORTED'):
                tape.event('RESPONSE', canonical({policy()['columns'][0]: 123}))
            self.assertEqual(list(Path(folder).iterdir()), [])

    def test_policy_cannot_mix_exact_and_projected_columns(self):
        self.assertEqual(declaration({'tape_class': 'EXACT'}), {'tape_class': 'EXACT'})
        for value in ({'tape_class': 'EXACT', 'columns': ['name']},
                      {**policy(), 'columns': ['z', 'a']},
                      {**policy(), 'key': 'must-never-be-in-manifest'}):
            with self.assertRaises(ProjectionError):
                declaration(value)

    def test_manifest_declares_one_class_and_projected_installation_cannot_fall_back_to_raw(self):
        from investigator.estate_manifest import validate
        from investigator.estate_installation import build
        from unittest.mock import patch
        root=Path(__file__).resolve().parents[1]
        value=json.loads((root/'infra/estates/fixture.json').read_text())
        value['recording']=policy()
        validated=validate(value)
        with patch('investigator.estate_installation.load',return_value=validated):
            with self.assertRaisesRegex(ValueError,'LOCAL_SECRET_STORE'):
                build('not-read')
        from types import SimpleNamespace
        from investigator.onboarding import ModelStore
        with tempfile.TemporaryDirectory() as folder:
            temporary=Path(folder)
            config={'storage':{'database':str(temporary/'inventory.sqlite')}}
            def create(*args):return SimpleNamespace(store=ModelStore(temporary/'catalog.sqlite',temporary/'inventory.sqlite','synthetic'))
            validated['storage']['catalog']='catalog.sqlite'
            with patch('investigator.estate_installation.load',return_value=validated), \
                 patch('metadata_config.ROOT',temporary), \
                 patch('investigator.adapters.estate_installation.configuration',return_value=config), \
                 patch('investigator.estate_installation._build_workspace',side_effect=create):
                _,installation=build('not-read',secret_store=lambda _:b'synthetic-in-memory-key-32-bytes!!')
            self.assertEqual(installation._workspace.store.privacy_capture,installation.capture)
            self.assertEqual(list(temporary.iterdir()),[])
            installation.close()
        value['recording']={'tape_class':'EXACT','columns':['secret']}
        with self.assertRaises(ValueError):validate(value)

    def test_secret_reference_resolves_only_from_existing_local_dpapi_store(self):
        from investigator.adapters.windows_privacy_secrets import resolver
        from unittest.mock import patch
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as folder:
            read=resolver(folder)
            key=b'synthetic-key-kept-in-process-only!!'
            with patch('subprocess.run',return_value=SimpleNamespace(
                    returncode=0,stdout=base64.b64encode(key),stderr=b'')) as call:
                self.assertEqual(read('.local/secrets/synthetic.xml'),key)
                self.assertTrue(call.call_args.kwargs['capture_output'])
                self.assertNotIn(key.decode(),str(call.call_args))
            with patch('subprocess.run') as call:
                with self.assertRaisesRegex(ProjectionError,'LOCAL_SECRET_STORE'):
                    read('repo-key.txt')
                call.assert_not_called()

    def test_legacy_tape_class_is_exact_and_source_bytes_stay_unchanged(self):
        from investigator.process_tape import Tape
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'exact.json'
            tape=Tape(path,{'entry_point':'synthetic','context_identity':'synthetic',
                'config':{},'profile':{},'usage_policy':{},'engine_hash':'synthetic','state':{}})
            tape.finish({});before=path.read_bytes()
            replay=Tape(path);replay.finish({})
            self.assertEqual(replay.tape_class,'EXACT')
            self.assertEqual(path.read_bytes(),before)

    def test_projected_estate_cannot_capture_exact_bootstrap_or_copy_raw_artifacts(self):
        from investigator.process_tape import Tape,TapeError
        from investigator.run_recording import operation
        from types import SimpleNamespace
        from unittest.mock import patch
        config={'_estate':{'recording':policy()}}
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(TapeError,'CANNOT_USE_EXACT_CAPTURE'):
                Tape(Path(folder)/'tape.json',{'config':config})
            self.assertEqual(list(Path(folder).iterdir()),[])
        owner=SimpleNamespace(config=config)
        called=[]
        @operation('intake')
        def read(owner):called.append('raw-implementation')
        with patch('investigator.run_recording.backup') as backup:
            with self.assertRaisesRegex(TapeError,'REQUIRES_ATOMIC_INSTALLATION_RUN'):
                read(owner)
            backup.assert_not_called()
        self.assertEqual(called,[])

    def test_recording_declaration_does_not_reduce_directory_or_enter_model_payload(self):
        import test_flexible_investigation as fixture
        from investigator.adaptive_runtime import AdaptiveRuntime
        from investigator.adaptive_candidates import catalog
        helper=fixture.DynamicTests();helper.setUp();self.addCleanup(helper.doCleanups)
        agent=AdaptiveRuntime(helper.runtime,lambda _:None)
        state=agent.get(agent.create(helper.envelope,'privacy-context')['id'])
        choices,_=catalog(helper.store,helper.config,helper.envelope)
        before=agent.payload(state,choices)
        agent.config.setdefault('_estate',{})['recording']=policy()
        after=agent.payload(state,choices)
        self.assertEqual(canonical(before),canonical(after))
        def counts(payload):
            entries=payload['context_entry_points']
            return {'entries':len(entries),'sql_entries':sum(e['kind']=='SqlObject' for e in entries),
                    'payload_characters':len(canonical(payload).decode())}
        self.assertEqual(counts(before),counts(after))
        print('PRIVACY_CONTEXT_COVERAGE '+json.dumps({'before':counts(before),'after':counts(after)}))
