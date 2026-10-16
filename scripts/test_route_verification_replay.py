import ast, importlib.util, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('replay',ROOT/'acceptance/round_thirteen/route_verification_replay.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Tests(unittest.TestCase):
 def program(self,body):
  d=tempfile.TemporaryDirectory();self.addCleanup(d.cleanup);p=Path(d.name)/'p.py';p.write_text(body);return p
 def test_only_identity_guard_removed_and_current_fingerprint_not_spoofed(self):
  p=self.program("def fingerprint(): return 'current'\ndef perform(i):\n if fingerprint()!=i['engine_fingerprint']:raise ValueError('VERIFIER_ENGINE_DIFFERS')\n if i['value']!=7:raise ValueError('CONTENT_DIFFERS')\n return fingerprint()\n")
  raw=p.read_bytes();module=m.compatibility_program(p)
  self.assertEqual(module.perform({'engine_fingerprint':'old','value':7}),'current')
  with self.assertRaisesRegex(ValueError,'CONTENT_DIFFERS'):module.perform({'engine_fingerprint':'old','value':8})
  self.assertEqual(p.read_bytes(),raw)
 def test_unknown_guard_or_nested_guard_is_refused(self):
  for code in ["def perform(i):\n if fingerprint()!=i['engine_fingerprint']:raise ValueError('OTHER')\n", "def perform(i):\n if True:\n  if fingerprint()!=i['engine_fingerprint']:raise ValueError('VERIFIER_ENGINE_DIFFERS')\n"]:
   with self.assertRaisesRegex(ValueError,'GUARD_NOT_RECOGNIZED'):m.compatibility_program(self.program(code))
if __name__=='__main__':unittest.main()
