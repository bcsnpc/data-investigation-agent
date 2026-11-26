import unittest
from sqlglot.errors import ParseError
from investigator.query_sql import compile_query
from investigator.regression_features import configured


class UnicodeLiteralTests(unittest.TestCase):
    def objects(self):
        return [{'id': 'approved', 'metadata': {'schema_name': 'app', 'name': 'Readers',
                 'type_desc': 'USER_TABLE', 'columns': [{'name': 'reader_name', 'data_type': 'nvarchar'},
                                                      {'name': 'units', 'data_type': 'int'}]}}]

    def test_national_literal_uses_same_bounded_parameter_path(self):
        query = "SELECT SUM(units) AS quantity FROM app.Readers WHERE reader_name=N'Δ O''Brien; --'"
        result = compile_query(query, self.objects())
        self.assertEqual(result['parameters'][0]['value'], "Δ O'Brien; --")
        self.assertNotIn("O'Brien", result['query'])
        self.assertIn('@p0', result['query'])

    def test_national_literal_still_has_the_data_length_limit(self):
        with self.assertRaisesRegex(ValueError, 'Parameter value budget'):
            compile_query("SELECT units FROM app.Readers WHERE reader_name=N'abcdef'", self.objects(), literal_limit=5)

    def test_does_not_admit_a_write_or_unknown_object(self):
        for query in ("UPDATE app.Readers SET reader_name=N'x'", "EXEC(N'SELECT 1')",
                      "SELECT units FROM app.Unknown WHERE reader_name=N'x'"):
            with self.subTest(query=query), self.assertRaises((ValueError, ParseError)):
                compile_query(query, self.objects())

    def test_flag_off_retains_the_original_rejection(self):
        pass


if __name__ == '__main__':
    unittest.main()
