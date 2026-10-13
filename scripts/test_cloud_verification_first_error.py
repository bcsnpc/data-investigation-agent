"""The first event error must not be replaced by a fabricated final mismatch."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock, patch

import cloud_verification_capture as capture
from investigator.process_tape import TapeError


class FirstReplayErrorTests(unittest.TestCase):
    def test_clock_error_is_retained_and_same_exception_escapes_without_final(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);source=root/'capture';source.mkdir()
            members={}
            for name in ('catalog.sqlite','verification_program.py','code_verifier_capture.py'):
                body=b'synthetic sealed dependency';(source/name).write_bytes(body)
                members[name]=hashlib.sha256(body).hexdigest()
            bootstrap={'entry_point':'code_verifier','state':{'capture_contract':capture.CONTRACT,
                'members':members,'native_path_identities':{'catalog.sqlite':'/recorded/catalog.sqlite'},'environment':'synthetic'}}
            tape=SimpleNamespace(bootstrap=bootstrap,replaying=True,index=17,finish=Mock())
            original=TapeError('TAPE_EVENT_DIFFERS:CLOCK:BUDGET')
            program=SimpleNamespace(perform=Mock(side_effect=original))
            output=root/'replayed'
            with patch.object(capture.journal,'Tape',return_value=tape), \
                 patch('investigator.budget_checkpoint.prepare'), \
                 patch.object(capture,'load_program',return_value=program), \
                 patch.object(capture,'snapshot') as snapshot, \
                 patch.object(capture,'finalize',side_effect=TapeError('MASKED_FINAL_ERROR')) as finalize:
                with self.assertRaises(TapeError) as raised:capture.replay(source,output)
            self.assertIs(raised.exception,original)
            snapshot.assert_not_called();finalize.assert_not_called();tape.finish.assert_not_called()
            detail=json.loads((root/'replayed-recomputed-final.json').read_bytes())
            self.assertEqual(detail['error']['message'],'TAPE_EVENT_DIFFERS:CLOCK:BUDGET')
            self.assertFalse(detail['exact_final_compared']);self.assertFalse(detail['matched'])
            self.assertEqual(detail['event_index'],17)

    def test_live_capture_keeps_existing_recorded_failure_contract(self):
        program=SimpleNamespace(perform=Mock(side_effect=TapeError('synthetic original failure')))
        result,error,status=capture.perform(program,{},None,None,None)
        self.assertIsNone(result);self.assertEqual(status,'FAILED')
        self.assertEqual(error['error_type'],'TapeError')
        self.assertEqual(error['message'],'synthetic original failure')

if __name__=='__main__':unittest.main()
