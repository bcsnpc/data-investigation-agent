"""Worker-owned controls and explicit normalization, without estate requests."""
import ast
import hashlib
from contextlib import closing
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from sqlglot import exp, parse_one
from investigator.control_contract import PATH, bounds, sql_request, finish
from investigator.process_tape import Tape
from investigator.string_semantics import normalization
from investigator.transformation_sql import compile_quantity
from investigator.query_sql import compile_query
import test_string_semantics as fixtures
BINARY=fixtures.BINARY


class ControlTests(unittest.TestCase):
    def test_spark_control_requires_explicit_execution_flag_and_one_statement(self):
        from investigator.adapters.microsoft_string_semantics import spark_control
        with self.assertRaises(PermissionError):spark_control()
        code=spark_control(execution_authorized=True)
        self.assertEqual(code.count('spark.sql('),1)
        self.assertIn('spark.version',code)
        self.assertIn('session_collation_settings',code)
        compile(code,'synthetic-livy-statement','exec')

    def test_every_sql_worker_control_consumes_worker_owned_minimum(self):
        scripts=PATH.parent
        names={'SOURCE_SQL':'Read-CatalogAggregate.ps1','FABRIC_SQL':'Read-FabricSqlAggregate.ps1'}
        self.assertEqual(set(json.loads(PATH.read_text())),set(names))
        for worker,name in names.items():
            request=sql_request(worker,'SELECT 1 AS x',['x'],['dbo.items'])
            contract=bounds(worker)
            self.assertLessEqual(contract['minimum_rows'],request['max_rows'])
            self.assertLessEqual(request['max_rows'],contract['maximum_rows'])
            text=(scripts/name).read_text()
            self.assertIn("'WorkerResponseBounds.json'",text)
            self.assertIn('.'+worker,text)
            self.assertLess(text.index('Invalid record budget'),text.index('$command.ExecuteReader()'))

    def test_control_finishes_real_recorder_once_and_replays(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'control.json'
            tape=Tape(path,{'entry_point':'synthetic','context_identity':'synthetic',
                'config':{},'profile':{},'usage_policy':{},'engine_hash':'synthetic','state':{}})
            finish(tape,{'status':'COMPLETED'})
            before=path.read_bytes()
            finish(tape,{'status':'COMPLETED'})
            self.assertEqual(path.read_bytes(),before)
            Tape(path)
        # Compare every Tape self-attribute read to attributes its class owns.
        import inspect
        tree=ast.parse(inspect.getsource(Tape))
        accesses=[n for n in ast.walk(tree) if isinstance(n,ast.Attribute)
                  and isinstance(n.value,ast.Name) and n.value.id=='self']
        owned={n.attr for n in accesses if isinstance(n.ctx,ast.Store)}
        owned.update(n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef))
        self.assertEqual({n.attr for n in accesses}-owned,set())

    def test_explicit_target_normalization_overrides_execution_engine_padding(self):
        fixture=fixtures.StringSemanticsTests();fixture.setUp()
        for trim,expected in ((False,2),(True,1)):
            declared={**BINARY,'collation':'observed-synthetic','trim':trim}
            statement=compile_quantity(fixture.scan,'v',fixture.catalog,profile='STRING',
                sample=fixture.sample,string_semantics=declared,source_string_semantics=BINARY)
            compile_query(statement,list(fixture.catalog.values()),max_rows=1)
            self.assertEqual('RTRIM(' in statement,trim)
            self.assertNotIn('UPPER(',statement)
            tree=parse_one(statement,read='tsql')
            def primitives(node):
                if (isinstance(node,exp.Add) and isinstance(node.this,exp.Cast)
                    and isinstance(node.this.this,exp.Anonymous)
                    and node.this.this.name.upper()=='DATALENGTH'):
                    return exp.Anonymous(this='exact_key',expressions=[node.this.this.expressions[0].copy()])
                if (isinstance(node,exp.Cast) and isinstance(node.this,exp.Substring)
                    and isinstance(node.this.this,exp.SHA2)):
                    return exp.Anonymous(this='hash_word',expressions=[node.this.this.this.copy()])
                return node
            tree=tree.transform(primitives).transform(primitives)
            tree=tree.transform(lambda n:n.this.copy() if isinstance(n,exp.Cast) and n.to.this==exp.DataType.Type.NVARCHAR else n)
            for ambient in ('BINARY','NOCASE'):
                with closing(sqlite3.connect(':memory:')) as db:
                    db.executescript("ATTACH DATABASE ':memory:' AS dbo; CREATE TABLE dbo.items(key INT,v TEXT COLLATE "+ambient+");")
                    db.executemany('INSERT INTO dbo.items VALUES (1,?)',[('a',),('a ',)])
                    def encode(value):
                        raw=value.encode('utf-16le');return len(raw).to_bytes(8,'big')+raw
                    db.create_function('exact_key',1,encode)
                    db.create_function('hash_word',1,lambda value:int.from_bytes(hashlib.sha256(value).digest()[:4],'big'))
                    row=db.execute(tree.sql(dialect='sqlite')).fetchone()
                    self.assertEqual(row[1],expected)
            self.assertEqual(normalization(declared)['trailing_space_trim'],trim)

    def test_fold_is_explicit_only_when_declared(self):
        fixture=fixtures.StringSemanticsTests();fixture.setUp()
        statement=compile_quantity(fixture.scan,'v',fixture.catalog,profile='STRING',
            sample=fixture.sample,string_semantics={**BINARY,'collation':'synthetic','case_fold':True})
        self.assertIn('UPPER(',statement)
        compile_query(statement,list(fixture.catalog.values()),max_rows=1)
