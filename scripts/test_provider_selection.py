import concurrent.futures
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from investigator.provider_selection import DEPLOYMENT, agent_selection
from investigator.agent_provider import GovernedDecision
from investigator.model_spend import SpendBudget
from ticket_planner import provider_body

class ProviderSelectionTests(unittest.TestCase):
    def runtime(self, mode='HYBRID', deployment='investigator-intake-f-55'):
        return SimpleNamespace(config={'_estate':{'investigation':{'mode':mode,'agent_deployment':deployment}}})

    def test_agent_selects_stronger_pipeline_stays_default(self):
        decision=object.__new__(GovernedDecision);decision.runtime=self.runtime()
        with patch.dict(os.environ,AZURE_OPENAI_DEPLOYMENT='investigator-quality-54'):
            def call(*args,**kwargs):
                return provider_body({},'instructions',{},'decision')['model']
            decision._call=call
            self.assertEqual(decision({},instructions='',schema={}),'investigator-intake-f-55')
            self.assertEqual(call(),'investigator-quality-54')
        self.assertIsNone(DEPLOYMENT.get())

    def test_selection_restored_on_exception_and_isolated_between_threads(self):
        with self.assertRaises(RuntimeError):
            with agent_selection(self.runtime()):raise RuntimeError('failure')
        self.assertIsNone(DEPLOYMENT.get())
        import threading
        barrier=threading.Barrier(2)
        def call(name):
            with agent_selection(self.runtime(deployment=name)):
                barrier.wait();return DEPLOYMENT.get()
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            self.assertEqual(list(pool.map(call,['one','two'])),['one','two'])
        self.assertIsNone(DEPLOYMENT.get())

    def test_pipeline_cannot_configure_agent_override(self):
        with self.assertRaisesRegex(ValueError,'AGENT_DEPLOYMENT_CONFIGURATION'):
            with agent_selection(self.runtime(mode='PIPELINE')):pass

    def test_deployment_price_survives_process_boundary_and_legacy_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'spend.sqlite'
            b=SpendBudget(p,1000000)
            ident=b.reserve({'model':'investigator-intake-f-55','input':'x','max_output_tokens':8000})
            later=SpendBudget(p,1000000)
            later.settle(ident,{'input_tokens':1000,'output_tokens':1000})
            self.assertEqual(later.snapshot()['charged_usd'],.035)
            legacy=b.reserve({'input':'x','max_output_tokens':8000})
            with b.connect() as db:db.execute('DELETE FROM model_spend_deployments WHERE id=?',(legacy,))
            later.settle(legacy,{'input_tokens':1000,'output_tokens':1000})
            self.assertEqual(later.snapshot()['charged_usd'],.0525)

    def test_stronger_reservation_is_higher_and_long_context_is_priced(self):
        self.assertEqual(SpendBudget.price(1000,1000,model='investigator-intake-f-55'),35000)
        self.assertEqual(SpendBudget.price(300000,1000,model='investigator-intake-f-55'),3045000)
        with tempfile.TemporaryDirectory() as directory:
            b=SpendBudget(Path(directory)/'spend.sqlite',1000000)
            b.reserve({'model':'investigator-intake-f-55','input':'x','max_output_tokens':8000})
            self.assertGreater(b.snapshot()['charged_usd'],.24)

    def test_protected_margin_does_not_change_ceiling_or_counters(self):
        from investigator.model_spend import SpendHold
        with tempfile.TemporaryDirectory() as directory:
            b=SpendBudget(Path(directory)/'spend.sqlite',1000000)
            with patch.dict(os.environ,INVESTIGATOR_MODEL_SPEND_MARGIN_MICRODOLLARS='900000'):
                with self.assertRaises(SpendHold):
                    b.reserve({'model':'investigator-intake-f-55','input':'x','max_output_tokens':8000})
            self.assertEqual(b.snapshot()['ceiling_usd'],1)
            self.assertEqual(b.snapshot()['charged_usd'],0)
