import base64,copy,hashlib,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'acceptance/known_domain'))
from mechanism_supersession import select
from investigator.process_tape import Tape,bytes_of
from investigator.mechanism_revision import REASON


class SupersessionGateTests(unittest.TestCase):
    def build(self,root):
        source=root/'original';source.write_bytes(b'unchanged original tape')
        source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
        original={'technical_output':{'text':'Original sentence.','evidence_ids':['receipt']},
                  'outcome':'PRESERVED','future':{'quantity':16,'snapshot':None}}
        response=copy.deepcopy(original);response['technical_output']['text']='The join can repeat matching rows.'
        tape=Tape(root/'new.json',{'entry_point':'synthetic','context_identity':'retained',
            'config':{},'profile':{},'usage_policy':{},'engine_hash':'synthetic','state':{
                'supersedes_tape_sha256':source_hash,'supersedes_provider_event_sha256':'source-event','reason':REASON}})
        body={'output':[{'type':'message','content':[{'type':'output_text','text':json.dumps({'text':response['technical_output']['text']})}]}]}
        tape.event('PROVIDER_REQUEST',bytes_of({'input':json.dumps({'mechanism':{
            'spine':{'layer_tokens':{}},'previous_mechanism':'Original sentence.','reason':REASON}})}))
        tape.event('PROVIDER_RESPONSE',bytes_of({'status':200,'body':base64.b64encode(bytes_of(body)).decode()}))
        event_hash=tape.events[-1]['sha256']
        tape.finish({'status':'ACCEPTED','result':{'response':response}})
        records=[{'case_id':'test','tape_sha256':source_hash,'attempts':[{'payload':{'layer_tokens':{}},
            'provider_event_sha256':'source-event','response':original}]}]
        revision={'case_id':'test','source_tape_sha256':source_hash,'source_provider_event_sha256':'source-event',
            'superseded_text':original['technical_output']['text'],'response':response,
            'revision_tape_member':'new.json','revision_tape_sha256':hashlib.sha256(tape.path.read_bytes()).hexdigest(),
            'revision_provider_event_sha256':event_hash}
        return source,{'provider_event_sha256':'source-event','response':original,'text':'Original sentence.',
            'payload':{'layer_tokens':{}}},records,{'version':1,'reason':REASON,'revisions':[revision]}

    def test_private_provider_body_and_all_structured_fields_are_checked(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);path,source,records,revisions=self.build(root)
            before=path.read_bytes();original=copy.deepcopy(records)
            result=select(path,source,root=root,records=records,revisions=revisions)
            self.assertTrue(result['structured_fields_byte_identical']);self.assertTrue(result['original_rendered_outputs_unchanged'])
            self.assertEqual(path.read_bytes(),before);self.assertEqual(records,original)
            bad=copy.deepcopy(revisions);bad['revisions'][0]['response']['future']['quantity']=17
            with self.assertRaisesRegex(ValueError,'STRUCTURED_FIELDS'):select(path,source,root=root,records=records,revisions=bad)
            bad=copy.deepcopy(revisions);bad['revisions'][0]['revision_provider_event_sha256']='forged'
            with self.assertRaisesRegex(ValueError,'PROVIDER_EVENT_DIFFERS'):select(path,source,root=root,records=records,revisions=bad)
            bad_source=copy.deepcopy(source);bad_source['payload']['new_context']='different'
            with self.assertRaisesRegex(ValueError,'PROVIDER_CONTEXT_DIFFERS'):
                select(path,bad_source,root=root,records=records,revisions=revisions)

    def test_no_cross_column_substitution_or_unproved_amendment(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);path,source,records,revisions=self.build(root)
            with self.assertRaisesRegex(ValueError,'PRIVATE_TAPE_REQUIRED'):
                select(path,source,root=None,records=records,revisions=revisions)
            other=root/'other-column';other.write_bytes(b'different original tape')
            self.assertIsNone(select(other,source,root=root,records=records,revisions=revisions))
            source=copy.deepcopy(source);source['response']['future']['quantity']=17
            with self.assertRaisesRegex(ValueError,'ORIGINAL_RESPONSE_DIFFERS'):
                select(path,source,root=root,records=records,revisions=revisions)


if __name__=='__main__':unittest.main()
