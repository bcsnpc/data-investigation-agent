import hashlib,io,tarfile,tempfile,unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'acceptance/known_domain'))
from private_bundle import *
class Tests(unittest.TestCase):
 def test_size_pin_checked_before_extract_and_old_optional_stays_valid(self):
  key=b'K'*32;body=b'synthetic fixture';buf=io.BytesIO()
  with tarfile.open(fileobj=buf,mode='w:gz') as t:
   info=tarfile.TarInfo('fixture');info.size=len(body);t.addfile(info,io.BytesIO(body))
  raw=seal_for_recipient(buf.getvalue(),recipient_public_key(key));digest=hashlib.sha256(raw).hexdigest();inventory={'fixture':hashlib.sha256(body).hexdigest()}
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);cipher=root/'cipher';cipher.write_bytes(raw)
   with self.assertRaisesRegex(ValueError,'SIZE_PIN_DIFFERS'):hydrate(cipher,digest,key,root/'wrong',expected_members=1,inventory=inventory,expected_uncompressed_bytes=1)
   self.assertFalse((root/'wrong').exists())
   hydrate(cipher,digest,key,root/'right',expected_members=1,inventory=inventory,expected_uncompressed_bytes=len(body));self.assertEqual((root/'right/fixture').read_bytes(),body)
   hydrate(cipher,digest,key,root/'old',expected_members=1,inventory=inventory);self.assertEqual((root/'old/fixture').read_bytes(),body)
if __name__=='__main__':unittest.main()
