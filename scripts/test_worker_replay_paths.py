"""Windows worker descriptors retain the same meaning in Linux replay."""
import importlib.util
import base64
from pathlib import Path, PurePosixPath
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from investigator import tape_worker, process_tape

spec = importlib.util.spec_from_file_location('portable_worker_replay',
    Path(__file__).resolve().parents[1] / 'acceptance/unknown_domain/worker_replay.py')
helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)


class PortableWorkerTests(unittest.TestCase):
    def test_windows_python_path_is_not_recognized_by_posix_basename(self):
        path = r'D:\retained\reader-env\Scripts\python.exe'
        self.assertEqual(PurePosixPath(path).name, path)
        command = [path, '/restored/scripts/run_native_diagnostic.py']
        self.assertEqual(helper.portable_command(command), ['python', 'run_native_diagnostic.py'])
        self.assertEqual(tape_worker.descriptor(command), ['python', 'run_native_diagnostic.py'])

    def test_config_contents_preserved_and_wrong_executable_not_normalized(self):
        for command in ([r'C:\reader\python3.exe', r'D:\engine\reader.py', '--config', '/tmp/profile.json'],
                        ['/usr/bin/python3', '/src/reader.py', '--config', '/tmp/profile.json']):
            self.assertEqual(helper.portable_command(command), ['python', 'reader.py', '--config', '/tmp/profile.json'])
        self.assertEqual(helper.portable_command([r'C:\reader\unexpected.exe'])[0], r'C:\reader\unexpected.exe')

    def test_helper_only_normalizes_replay_and_does_not_consume_events(self):
        command = [r'C:\reader\python.exe', r'D:\engine\reader.py']
        original = Mock(side_effect=lambda value: list(value))
        for replaying in (False, True):
            journal = SimpleNamespace(ACTIVE=Mock())
            journal.ACTIVE.get.return_value = SimpleNamespace(replaying=replaying)
            with patch.object(tape_worker, 'descriptor', original), helper.install(journal):
                value = tape_worker.descriptor(command)
            self.assertEqual(value, ['python', 'reader.py'] if replaying else command)

    def test_absolute_windows_config_paths_preserved_by_real_validator_on_posix_root(self):
        import copy
        import json
        import metadata_config
        config=json.loads((Path(__file__).resolve().parents[1]/'infra/metadata/development.json').read_text(encoding='utf-8-sig'))
        config['sql']['auth']['credential_file']=r'D:\retained\reader.xml'
        config['fabric']['auth']['python']=r'D:\retained\Scripts\python.exe'
        config['storage']['database']=r'D:\retained\inventory.sqlite'
        journal=SimpleNamespace(ACTIVE=Mock())
        journal.ACTIVE.get.return_value=SimpleNamespace(replaying=True)
        with patch.object(metadata_config,'ROOT',PurePosixPath('/isolated/replay')), helper.configuration_paths(journal):
            actual=metadata_config.validate_config(copy.deepcopy(config))
        self.assertEqual(actual['sql']['auth']['credential_file'],config['sql']['auth']['credential_file'])
        self.assertEqual(actual['fabric']['auth']['python'],config['fabric']['auth']['python'])
        self.assertEqual(actual['storage']['database'],config['storage']['database'])

    def test_replay_config_root_preserves_relative_and_posix_absolute_semantics(self):
        root=helper._ReplayConfigRoot(PurePosixPath('/isolated/replay'))
        self.assertEqual(str(root/'relative/file.json'),'/isolated/replay/relative/file.json')
        self.assertEqual(str(root/'/absolute/file.json'),'/absolute/file.json')
        self.assertEqual((root/r'D:\absolute\file.json').resolve(),r'D:\absolute\file.json')
        self.assertEqual((root/r'\\server\share\file.json').resolve(),r'\\server\share\file.json')
        with self.assertRaisesRegex(ValueError,'DRIVE_RELATIVE'):
            root/'D:relative.json'

    def test_configuration_path_helper_does_not_change_live_validation_root(self):
        import metadata_config
        journal=SimpleNamespace(ACTIVE=Mock());journal.ACTIVE.get.return_value=SimpleNamespace(replaying=False)
        root=metadata_config.ROOT
        original=Mock(side_effect=lambda config:metadata_config.ROOT)
        with patch.object(metadata_config,'validate_config',original),helper.configuration_paths(journal):
            self.assertIs(metadata_config.validate_config({}),root)
        self.assertIs(metadata_config.ROOT,root)

    def test_first_mismatch_is_retained_when_error_handling_raises_another(self):
        expected=process_tape.bytes_of({'command':['python','expected.py']})
        tape=process_tape.Tape.__new__(process_tape.Tape)
        tape.replaying=True;tape.index=0
        tape.events=[{'ordinal':1,'kind':'WORKER_START','at':0,'body':base64.b64encode(expected).decode(),
                     'sha256':process_tape.sha(expected)},
                    {'ordinal':2,'kind':'WORKER_SEND','at':0,'body':base64.b64encode(b'payload').decode(),
                     'sha256':process_tape.sha(b'payload')}]
        actual=process_tape.bytes_of({'command':['python','wrong.py']});private=[]
        with helper.first_tape_error(process_tape,private):
            with self.assertRaisesRegex(process_tape.TapeError,'REQUEST_BYTES_DIFFER'):
                tape.event('WORKER_START',actual)
            with self.assertRaisesRegex(process_tape.TapeError,'CLOCK:WORKER_SEND'):
                tape.event('CLOCK',b'irrelevant')
        self.assertEqual(len(private),1)
        self.assertEqual(private[0]['reason'],'TAPE_REQUEST_BYTES_DIFFER')
        self.assertEqual(private[0]['index_before'],0);self.assertEqual(private[0]['index_after'],1)
        self.assertEqual(base64.b64decode(private[0]['actual_body_base64']),actual)
        self.assertEqual(base64.b64decode(private[0]['recorded_body_base64']),expected)

    def test_worker_event_bytes_remain_exact_after_portable_descriptor(self):
        # No comparison policy changes: different commands/queries still fail.
        self.assertNotEqual(process_tape.bytes_of(tape_worker.descriptor(['python', 'a.py'])),
                            process_tape.bytes_of(tape_worker.descriptor(['python', 'b.py'])))
        self.assertNotEqual(process_tape.safe_request('{"query":"SELECT 1"}'),
                            process_tape.safe_request('{"query":"SELECT 2"}'))
        expected = process_tape.bytes_of({'command': ['python', 'a.py', '--literal', 'SELECT 1'], 'mode': 'BOUNDED'})
        for command in ([r'D:\env\python.exe', '/restored/a.py', '--literal', 'SELECT 1'],
                        ['/usr/bin/python', '/restored/a.py', '--literal', 'SELECT 1']):
            self.assertEqual(process_tape.bytes_of({'command': helper.portable_command(command), 'mode': 'BOUNDED'}), expected)
        for command in ([r'D:\env\other.exe', '/restored/a.py', '--literal', 'SELECT 1'],
                        [r'D:\env\python.exe', '/restored/a.py', '--literal', 'SELECT 2']):
            tape = process_tape.Tape.__new__(process_tape.Tape)
            tape.replaying = True; tape.index = 0
            tape.events = [{'ordinal': 1, 'kind': 'WORKER_START', 'at': 0,
                            'body': base64.b64encode(expected).decode(), 'sha256': process_tape.sha(expected)}]
            with self.assertRaisesRegex(process_tape.TapeError, 'TAPE_REQUEST_BYTES_DIFFER'):
                tape.event('WORKER_START', process_tape.bytes_of({'command': helper.portable_command(command), 'mode': 'BOUNDED'}))


if __name__ == '__main__': unittest.main()
