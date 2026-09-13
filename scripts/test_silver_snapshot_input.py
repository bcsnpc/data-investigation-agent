import hashlib
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import MagicMock

from bronze_publication import validate_verification
from silver_snapshot_input import bind
from source_snapshot import canonical
import test_bronze_publication

spec = importlib.util.spec_from_file_location('pinned', Path(__file__).resolve().parents[1] / 'infra/fabric/read_pinned_bronze.py')
pinned = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pinned)


class SilverInputTests(unittest.TestCase):
    def fixture(self):
        expected, publication, verification, job = test_bronze_publication.PublicationTests().fixture()
        proof = dict(publication=publication, verification=verification, job=job,
                     result=validate_verification(expected, publication, verification, job))
        return expected, proof, hashlib.sha256(canonical(proof).encode()).hexdigest()

    def test_bind_retains_exact_versions(self):
        args = self.fixture()
        binding = bind(*args)
        self.assertEqual(len(binding['tables']), 10)
        self.assertEqual(binding['source_snapshot_id'], args[0]['source_snapshot_id'])
        self.assertTrue(all(t['delta_version'] == 0 for t in binding['tables']))

    def test_tampered_or_failed_evidence_rejected(self):
        expected, proof, digest = self.fixture()
        proof['job']['status'] = 'Failed'
        with self.assertRaises(ValueError): bind(expected, proof, digest)
        with self.assertRaises(ValueError):
            bind(expected, proof, hashlib.sha256(canonical(proof).encode()).hexdigest())

    def reader(self):
        binding = bind(*self.fixture())
        spark, delta = MagicMock(), MagicMock()
        rows = binding['tables']
        delta.forPath.return_value.detail.return_value.select.return_value.first.side_effect = [
            [row['delta_table_id']] for row in rows for _ in range(2)]
        spark.read.format.return_value.option.return_value.load.return_value.schema.jsonValue.return_value = rows[0]['delta_schema']
        spark.read.format.return_value.option.return_value.load.return_value.count.return_value = 10
        return binding, spark, delta

    def test_reads_only_pinned_versions(self):
        binding, spark, delta = self.reader()
        self.assertEqual(len(pinned.read_pinned_bronze(spark, delta, binding)), 10)
        self.assertEqual(spark.read.format.return_value.option.call_count, 10)
        for call in spark.read.format.return_value.option.call_args_list:
            self.assertEqual(call.args, ('versionAsOf', 0))

    def test_replaced_identity_fails_before_data_read(self):
        binding, spark, delta = self.reader()
        delta.forPath.return_value.detail.return_value.select.return_value.first.side_effect = [['replacement']]
        with self.assertRaises(ValueError): pinned.read_pinned_bronze(spark, delta, binding)
        spark.read.format.assert_not_called()

    def test_unavailable_version_never_falls_back(self):
        binding, spark, delta = self.reader()
        spark.read.format.return_value.option.return_value.load.side_effect = RuntimeError('vacuumed')
        with self.assertRaises(RuntimeError): pinned.read_pinned_bronze(spark, delta, binding)
        self.assertEqual(spark.read.format.return_value.option.call_count, 1)

    def test_incomplete_binding_and_schema_or_count_changes_fail(self):
        for failure in ('missing', 'schema', 'count'):
            binding, spark, delta = self.reader()
            frame = spark.read.format.return_value.option.return_value.load.return_value
            if failure == 'missing': binding['tables'].pop()
            if failure == 'schema': frame.schema.jsonValue.return_value = {'changed': True}
            if failure == 'count': frame.count.return_value = 11
            with self.assertRaises(ValueError): pinned.read_pinned_bronze(spark, delta, binding)


if __name__ == '__main__': unittest.main()
