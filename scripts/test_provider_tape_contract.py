import base64,json,unittest
from investigator.provider_tape_contract import canonical,equal
from investigator.process_tape import Tape,TapeError,bytes_of
from investigator.budget_tape_contract import install

class ProviderCanonicalTests(unittest.TestCase):
 def request(self,value,compact=False):
  return json.dumps({'input':json.dumps(value,separators=(',',':') if compact else None),'model':'model'},separators=(',',':') if compact else None).encode()
 def test_request_key_order_and_whitespace_match(self):
  a=self.request({'names':{'b':'two','a':'one'},'number':16})
  b=self.request({'number':16,'names':{'a':'one','b':'two'}},True)
  self.assertTrue(equal('PROVIDER_REQUEST',a,b))
 def test_one_field_change_fails(self):
  self.assertFalse(equal('PROVIDER_REQUEST',self.request({'number':16}),self.request({'number':17})))
 def test_prose_whitespace_and_array_order_are_content(self):
  for a,b in [({'text':'two words'},{'text':'two  words'}),({'values':[1,2]},{'values':[2,1]})]:
   self.assertFalse(equal('PROVIDER_REQUEST',self.request(a),self.request(b)))
 def response(self,raw):return bytes_of({'status':200,'body':base64.b64encode(raw).decode()})
 def test_response_body_is_canonical_not_base64_text(self):
  a=self.response(b'{"output":[],"usage":{"a":1,"b":2}}')
  b=self.response(b'{ "usage": {"b":2,"a":1}, "output": [] }')
  self.assertTrue(equal('PROVIDER_RESPONSE',a,b))
  self.assertFalse(equal('PROVIDER_RESPONSE',a,self.response(b'{"output":[],"usage":{"a":1,"b":3}}')))
 def test_declared_function_arguments_are_structured_json(self):
  def body(args):return self.response(json.dumps({'output':[{'type':'function_call','arguments':args}]}).encode())
  self.assertTrue(equal('PROVIDER_RESPONSE',body('{"b":2,"a":1}'),body('{ "a":1, "b":2 }')))
  self.assertFalse(equal('PROVIDER_RESPONSE',body('{"a":1}'),body('{"a":2}')))
 def test_non_json_duplicate_keys_and_nan_fail(self):
  for body in (b'not JSON',b'{"a":1,"a":2}',b'{"a":NaN}'):
   with self.subTest(body=body),self.assertRaises(ValueError):canonical('PROVIDER_REQUEST',body)
 def test_tape_provider_matching_is_canonical_and_physical_stays_exact(self):
  tape=object.__new__(Tape);tape.replaying=True;tape.take=lambda kind:b'{"count":1}'
  tape.event('PROVIDER_REQUEST',b'{ "count":1 }')
  with self.assertRaisesRegex(TapeError,'PROVIDER_CONTENT_DIFFERS'):tape.event('PROVIDER_REQUEST',b'{"count":2}')
  with self.assertRaisesRegex(TapeError,'REQUEST_BYTES_DIFFER'):tape.event('BOUNDED_REQUEST',b'{ "count":1 }')
 def test_archived_producer_uses_the_same_canonical_consumer(self):
  class Old:
   class Tape:
    def event(self,kind,body):
     if self.take(kind)!=body:raise TapeError('OLD_BYTES')
   TapeError=TapeError
  install(Old,provider_equal=equal)
  tape=Old.Tape();tape.replaying=True;tape.take=lambda kind:b'{"count":1}'
  tape.event('PROVIDER_REQUEST',b'{ "count":1 }')
  with self.assertRaisesRegex(TapeError,'PROVIDER_CONTENT_DIFFERS'):tape.event('PROVIDER_REQUEST',b'{"count":2}')
if __name__=='__main__':unittest.main()
