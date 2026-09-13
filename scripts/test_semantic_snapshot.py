import unittest
from semantic_snapshot import alignment_query,validate_alignment
from build_powerbi_model import TABLES


class SemanticSnapshotTests(unittest.TestCase):
    def fixture(self):
        gold={'run_id':'expected','counts':{source:10 for source in TABLES.values()}}
        row={}
        for table in TABLES:
            row.update({f'[{table}:run]':'expected',f'[{table}:rows]':10,f'[{table}:nulls]':None})
        return gold,row

    def test_observed_alignment_does_not_claim_version_proof(self):
        result=validate_alignment(*self.fixture())
        self.assertEqual(result['status'],'SEMANTIC_RUN_ALIGNED')
        self.assertFalse(result['snapshot_comparable'])

    def test_mixed_stale_null_and_wrong_count_rejected(self):
        for suffix,value in [('run','expected,other'),('run','old'),('rows',11),('rows',True),('nulls',1)]:
            gold,row=self.fixture();row[f'[FactOrder:{suffix}]']=value
            with self.assertRaises(ValueError):validate_alignment(gold,row)

    def test_missing_dimension_evidence_rejected(self):
        gold,row=self.fixture();row.pop('[DimDate:nulls]')
        with self.assertRaises(ValueError):validate_alignment(gold,row)

    def test_query_covers_all_tables(self):
        query=alignment_query()
        for table in TABLES:
            self.assertIn(f'COUNTROWS({table})',query)
            self.assertIn(f'ISBLANK({table}[_gold_run_id])',query)


if __name__=='__main__':unittest.main()
