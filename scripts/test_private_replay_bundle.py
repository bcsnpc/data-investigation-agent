import base64
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('private_bundle',Path(__file__).resolve().parents[1]/'acceptance/known_domain/private_bundle.py')
bundle=importlib.util.module_from_spec(spec);spec.loader.exec_module(bundle)


class PrivateReplayBundleTests(unittest.TestCase):
    def test_hash_mismatch_fails_before_decryption(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'cipher';p.write_bytes(b'DIA1'+b'x'*64)
            with patch('cryptography.hazmat.primitives.ciphers.aead.AESGCM',side_effect=AssertionError('Must not decrypt')):
                with self.assertRaisesRegex(ValueError,'BEFORE_DECRYPTION'):
                    bundle.hydrate(p,'0'*64,b'x'*32,Path(d)/'output')
            self.assertFalse((Path(d)/'output').exists())

    def test_separate_mapping_preserves_source_and_refuses_escape(self):
        import json
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);run={'tape_path':'D:\\private\\tape.json'};original=dict(run)
            mapping=root/'replay-paths.json'
            mapping.write_text(json.dumps({run['tape_path']:'process-tapes/id/tape.json'}))
            self.assertEqual(bundle.tape_path(run,root),root/'process-tapes/id/tape.json')
            self.assertEqual(run,original)
            mapping.write_text(json.dumps({run['tape_path']:'../outside/tape.json'}))
            with self.assertRaisesRegex(ValueError,'LEAVES_BUNDLE'):bundle.tape_path(run,root)

    def test_authenticated_ciphertext_rejects_wrong_key(self):
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.exceptions import InvalidTag
        with tempfile.TemporaryDirectory() as d:
            nonce=b'n'*12;raw=b'DIA1'+nonce+AESGCM(b'x'*32).encrypt(nonce,b'private',b'DIA1')
            p=Path(d)/'cipher';p.write_bytes(raw)
            with self.assertRaises(InvalidTag):bundle.hydrate(p,hashlib.sha256(raw).hexdigest(),b'y'*32,Path(d)/'output')

    def test_valid_bundle_extracts_and_unsafe_member_refuses(self):
        import io,tarfile
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        with tempfile.TemporaryDirectory() as d:
            for unsafe in (False,True):
                data=io.BytesIO()
                with tarfile.open(fileobj=data,mode='w:gz') as archive:
                    for i in range(61):
                        name='../escape' if unsafe and i==0 else 'evidence/'+str(i)
                        member=tarfile.TarInfo(name);member.size=1;archive.addfile(member,io.BytesIO(b'x'))
                nonce=b'n'*12;raw=b'DIA1'+nonce+AESGCM(b'x'*32).encrypt(nonce,data.getvalue(),b'DIA1')
                p=Path(d)/'cipher';p.write_bytes(raw);out=Path(d)/str(unsafe)
                if unsafe:
                    with self.assertRaisesRegex(ValueError,'UNSAFE_MEMBER'):bundle.hydrate(p,hashlib.sha256(raw).hexdigest(),b'x'*32,out)
                    self.assertFalse(out.exists())
                else:
                    bundle.hydrate(p,hashlib.sha256(raw).hexdigest(),b'x'*32,out)
                    self.assertEqual(len(list((out/'evidence').iterdir())),61)


if __name__=='__main__':unittest.main()
