import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from investigator.shared_state import SharedState,StateConflict
from investigator.shared_spend import SharedSpendBudget
from investigator.model_spend import SpendBudget,SpendHold,admission
from export_shared_state import export_spend


class SharedSpendTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.state=SharedState.offline(Path(self.tmp.name)/'shared.sqlite');self.state.migrate()
        self.env=patch.dict(os.environ,{'INVESTIGATOR_WORKER_ID':'worker','INVESTIGATOR_MODEL_SPEND_MICRODOLLARS':'1000000','INVESTIGATOR_MODEL_SPEND_MARGIN_MICRODOLLARS':'100000'})
        self.env.start();self.addCleanup(self.env.stop)
        self.state.import_accounts('spend',{'accounts':[{'identity':'model-microdollars','unit':'MICRODOLLARS','ceiling':1000000,'protected':100000,'opening':234567,'violated':False}]})

    def test_real_admission_path_uses_authority_not_local_dollar_file(self):
        forbidden=Path(self.tmp.name)/'must-not-exist.sqlite'
        with patch('investigator.shared_state.configured_state',return_value=self.state),patch.dict(os.environ,{'INVESTIGATOR_MODEL_SPEND_DB':str(forbidden)}):
            with patch.object(SpendBudget,'price',side_effect=lambda i,o,model=None:i+o):
                with admission({'input':'test','max_output_tokens':500,'model':'synthetic'}) as settle:
                    settle({'input_tokens':10,'output_tokens':20})
        self.assertFalse(forbidden.exists())
        self.assertEqual(self.state.snapshot('model-microdollars')['charged'],'234597')

    def test_direct_constructor_never_falls_back_in_cloud_mode(self):
        with patch('investigator.shared_state.configured_state',return_value=self.state):
            self.assertIsInstance(SpendBudget('unused.sqlite',1000000),SharedSpendBudget)

    def test_shared_policy_cannot_silently_widen(self):
        with self.assertRaisesRegex(SpendHold,'policy differs'):SharedSpendBudget(self.state,2000000)

    def test_unknown_provider_usage_retains_bound(self):
        guard=SharedSpendBudget(self.state,1000000)
        with patch.object(SpendBudget,'price',return_value=1000):key=guard.reserve({'input':'test','max_output_tokens':500})
        guard.settle(key)
        self.assertEqual(self.state.snapshot('model-microdollars')['charged'],'235567')

    def test_export_keeps_original_rows_exact_and_refuses_open_reservation(self):
        db=sqlite3.connect(':memory:');self.addCleanup(db.close)
        db.executescript('CREATE TABLE spend_policy(id,ceiling); INSERT INTO spend_policy VALUES(1,1000000); CREATE TABLE model_spend(id,created,reserved,charged,status,input_tokens,output_tokens); CREATE TABLE model_spend_deployments(id,model);')
        db.execute('INSERT INTO model_spend VALUES(?,?,?,?,?,?,?)',('one',1.25,250,123,'SETTLED',10,20))
        result=export_spend(db,margin_microdollars=100000)
        self.assertEqual(result['accounts'][0]['opening'],123)
        self.assertEqual(result['original_tables']['model_spend']['rows'][0],['one',1.25,250,123,'SETTLED',10,20])
        db.execute("UPDATE model_spend SET status='RESERVED'")
        with self.assertRaisesRegex(ValueError,'DRAINED_WORKERS'):export_spend(db,margin_microdollars=100000)


if __name__=='__main__':unittest.main()
