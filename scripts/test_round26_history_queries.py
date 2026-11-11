import unittest
from investigator.investigative_queries import validate
from test_round23_intake_queries import sql_objects


class HistoryQueriesTests(unittest.TestCase):
    def layer(self, dialect):
        return {'dialect': dialect, 'objects': sql_objects()}

    def test_tsql_temporal_reads_preserve_native_clause(self):
        for suffix in ("FOR SYSTEM_TIME AS OF '2026-10-01T00:00:00Z'",
                       "FOR SYSTEM_TIME BETWEEN '2026-10-01' AND '2026-10-02'",
                       'FOR SYSTEM_TIME ALL'):
            result = validate('SELECT SUM(quantity) AS n FROM dbo.Items ' + suffix, self.layer('T-SQL'))
            rendered = result['query']
            for parameter in result['parameters']:
                rendered = rendered.replace(parameter['name'], "'" + parameter['value'] + "'")
            self.assertIn(suffix, rendered)

    def test_delta_reads_preserve_version_and_timestamp(self):
        for suffix in ('VERSION AS OF 2', "TIMESTAMP AS OF '2026-10-01T00:00:00Z'"):
            result = validate('SELECT SUM(quantity) AS n FROM dbo.Items ' + suffix, self.layer('Spark SQL'))
            self.assertIn(suffix, result['query'])

    def test_history_does_not_admit_writes_external_tables_or_expressions(self):
        for dialect, text in (
            ('T-SQL', 'UPDATE dbo.Items SET quantity=2'),
            ('T-SQL', "SELECT * FROM dbo.Unknown FOR SYSTEM_TIME ALL"),
            ('T-SQL', "SELECT * FROM dbo.Items FOR SYSTEM_TIME BETWEEN '2026-10-02' AND '2026-10-01'"),
            ('Spark SQL', 'DELETE FROM dbo.Items'),
            ('Spark SQL', 'SELECT * FROM dbo.Unknown VERSION AS OF 2'),
            ('Spark SQL', 'SELECT * FROM dbo.Items VERSION AS OF -1')):
            with self.subTest(text=text), self.assertRaises(Exception):
                validate(text, self.layer(dialect))
