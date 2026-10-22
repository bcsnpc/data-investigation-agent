import json
from pathlib import Path
import unittest
from unittest.mock import Mock,patch
from investigator.daily_smoke import _gold_read,run_smoke,validate_gold_payload

class GoldPayloadTests(unittest.TestCase):
    def catalog(self):
        # Exact compiled query/parameters/columns from preserved event16. Public
        # connection coordinates are irrelevant to its control classification.
        value=json.loads((Path(__file__).parent/'fixtures/smoke-rejected-catalog-request.json').read_bytes())
        return {**value,'server':'retained-endpoint.test','database':'warehouse_gold_e1b8e1','authentication':{'principal_id':'reader'}}
    def test_exact_retained_catalog_shape_refuses_before_worker_dispatch(self):
        from investigator.adapters.binding_catalog import compiled_control_objects
        payload=self.catalog();self.assertIsNotNone(compiled_control_objects(payload))
        with patch('investigator.physical_reads.run')as dispatch,self.assertRaisesRegex(ValueError,'SMOKE_GOLD_DATA_QUERY_REQUIRED'):
            _gold_read(payload)
        dispatch.assert_not_called()
    def test_catalog_refuses_before_any_health_check_or_sign_in(self):
        payload=self.catalog();context=Mock();external=Mock()
        config={'version':1,'run_id':'daily','reader_authentication':payload['authentication'],'gold_payload':payload,'platform_blob':{},'demo_earned':False}
        with self.assertRaisesRegex(ValueError,'SMOKE_GOLD_DATA_QUERY_REQUIRED'):
            run_smoke(config,context,state=Mock(),sign_in=external,gold_read=external,blob_roundtrip=external)
        context.step.assert_not_called();external.assert_not_called()
    def test_regular_read_only_sum_is_accepted_but_controls_and_missing_guard_are_not(self):
        payload={'query':'SELECT SUM(units) AS value FROM dbo.movements','read_only_objects':['[dbo].[movements]'],'result_columns':['value'],'max_rows':2,'require_read_only':True}
        self.assertIs(validate_gold_payload(payload),payload)
        for invalid in ({**payload,'require_read_only':False},{**payload,'control_mode':'SELF_REPORT'},{**payload,'control_mode':'PREWARM'}):
            with self.subTest(payload=invalid),self.assertRaisesRegex(ValueError,'SMOKE_GOLD_DATA_QUERY_REQUIRED'):validate_gold_payload(invalid)
    def test_unrecognised_catalog_query_does_not_evade_the_generic_data_check(self):
        payload={'query':'SELECT name FROM sys.columns','read_only_objects':['[dbo].[movements]'],'result_columns':['name'],'max_rows':2,'require_read_only':True}
        with self.assertRaisesRegex(ValueError,'SMOKE_GOLD_DATA_QUERY_REQUIRED'):validate_gold_payload(payload)

if __name__=='__main__':unittest.main()
