from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import datetime,timezone
import unittest
from investigator.shared_state import SharedState
from investigator.anthropic_credit import policy_for,admit
from investigator.model_spend import SpendHold

class ReservedCreditTests(unittest.TestCase):
 def test_explicit_cohort_reserve_blocks_other_steps_without_resetting_usage(self):
  now=datetime(2026,11,2,tzinfo=timezone.utc).timestamp()
  with TemporaryDirectory()as folder:
   state=SharedState.offline(Path(folder)/'s.sqlite');state.migrate()
   with state.transaction()as db:
    state.sql(db,'INSERT INTO state_accounts VALUES(?,?,?,?,?,?)',('model-microdollars:2026-11','MICRODOLLARS',70000000,0,49000000,0))
    p=policy_for(state,db,'2026-11')
   p['allowed_owner_prefixes']=['round26-opus-calibration','round26-held-v5-']
   state.put('anthropic_credit','2026-11',p)
   with state.transaction(_read_only=True)as db:
    for owner in ['round24-guided-smoke','grader','round26-dev03-text',None]:
     with self.subTest(owner=owner),self.assertRaisesRegex(SpendHold,'RESERVED_FOR_APPROVED_COHORTS'):
      admit(state,db,'model-microdollars:2026-11',1,now,purpose='GRADING',owner=owner)
    for owner in ['round26-opus-calibration01-text','round26-held-v5-form']:
     admit(state,db,'model-microdollars:2026-11',1,now,purpose='INVESTIGATOR',owner=owner)
    # The reserve never affects the independently funded OpenAI account.
    admit(state,db,'provider-openai-microdollars:2026-11',1,now,owner='round26-dev03-text')
   self.assertEqual(int(state.totals('model-microdollars:2026-11')['charged']),49000000)

if __name__=='__main__':unittest.main()
