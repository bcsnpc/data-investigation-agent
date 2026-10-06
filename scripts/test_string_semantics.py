"""Binary renderer never borrows SQL's padded or case-insensitive equality."""
import copy
import hashlib
import sqlite3
from contextlib import closing
import unittest
from jsonschema.exceptions import ValidationError
from investigator.string_semantics import validate, binary
from investigator.transformation_sql import compile_quantity
from investigator.query_sql import compile_query

BINARY={'collation':'BINARY','case_fold':False,'trim':False,'accent_fold':False}


class StringSemanticsTests(unittest.TestCase):
    def setUp(self):
        self.catalog={'t':{'id':'t','metadata':{'schema_name':'dbo','name':'items',
            'type_desc':'USER_TABLE','columns':[{'name':'key','data_type':'bigint'},
                                              {'name':'v','data_type':'nvarchar'}]}}}
        self.scan={'kind':'SCAN','table':'t','columns':['key','v']}
        self.sample={'kind':'KEY_RANGE','column':'key','lower':1,'upper':20,'provenance':'synthetic'}

    def test_closed_declaration_unknown_and_contradictory_fail_closed(self):
        self.assertEqual(validate(BINARY),BINARY)
        for value in ({**BINARY,'extra':True},{k:v for k,v in BINARY.items() if k!='accent_fold'}):
            with self.assertRaises(ValidationError):validate(value)
        with self.assertRaises(ValueError):validate({**BINARY,'case_fold':True})
        with self.assertRaises(NotImplementedError):binary({**BINARY,'collation':'unknown'})

    def test_complete_dedup_and_profile_use_length_prefixed_binary_keys(self):
        relation={'kind':'DEDUPE','input':self.scan,'keys':['key','v']}
        text=compile_quantity(relation,'v',self.catalog,profile='STRING',sample=self.sample,
                              string_semantics=BINARY,source_string_semantics=BINARY)
        self.assertIn('GROUP BY',text)
        self.assertIn('DATALENGTH',text)
        self.assertIn('BINARY(8)',text)
        self.assertIn('VARBINARY(MAX)',text)
        self.assertIn('NVARCHAR(MAX)',text)
        self.assertIn("HASHBYTES('SHA2_256'",text)
        compiled=compile_query(text,list(self.catalog.values()),max_rows=1)
        self.assertIn("'SHA2_256'",compiled['query'])

    def test_numeric_profile_still_obeys_whole_row_string_dedup(self):
        relation={'kind':'DEDUPE','input':self.scan,'keys':['key','v']}
        text=compile_quantity(relation,'key',self.catalog,profile='NUMERIC',sample=self.sample,
                              string_semantics=BINARY,source_string_semantics=BINARY)
        self.assertIn('DATALENGTH',text)
        self.assertIn('SUM(',text)
        with self.assertRaises(ValueError):
            compile_quantity({**relation,'keys':['key']},'key',self.catalog,profile='NUMERIC',
                             sample=self.sample,string_semantics=BINARY,source_string_semantics=BINARY)

    def test_hash_allowlist_does_not_enable_arbitrary_functions_or_algorithms(self):
        for expression in ('evil(v)',"HASHBYTES('MD5',v)"):
            with self.assertRaises(ValueError):compile_query('SELECT '+expression+' AS h FROM dbo.items',list(self.catalog.values()))

    def test_compiled_binary_dedup_preserves_case_space_null_and_content(self):
        # Execute the compiled relational structure; substitute only the two
        # SQL Server-specific binary/hash scalar primitives in this test engine.
        from sqlglot import parse_one,exp
        relation={'kind':'DEDUPE','input':self.scan,'keys':['key','v']}
        sql=compile_quantity(relation,'v',self.catalog,profile='STRING',sample=self.sample,
                             string_semantics=BINARY,source_string_semantics=BINARY)
        tree=parse_one(sql,read='tsql')
        def key(node):
            if isinstance(node,exp.Add) and isinstance(node.this,exp.Cast) and isinstance(node.this.this,exp.Anonymous) and node.this.this.name.upper()=='DATALENGTH':
                value=node.this.this.expressions[0].this.copy()
                return exp.Anonymous(this='exact_key',expressions=[value])
            return node
        tree=tree.transform(key)
        def hash_word(node):
            if isinstance(node,exp.Cast) and isinstance(node.this,exp.Substring) and isinstance(node.this.this,exp.SHA2):
                return exp.Anonymous(this='hash_word',expressions=[node.this.this.this.copy()])
            return node
        tree=tree.transform(hash_word)
        with closing(sqlite3.connect(':memory:')) as db:
            db.executescript("ATTACH DATABASE ':memory:' AS dbo; CREATE TABLE dbo.items(key INT,v TEXT);")
            values=['Sales','sales','Sales ','Sales\u0000',None,'Sales']
            db.executemany('INSERT INTO dbo.items VALUES (1,?)',[(v,) for v in values])
            def encoded(value):
                if value is None:return None
                raw=value.encode('utf-16le');return len(raw).to_bytes(8,'big')+raw
            db.create_function('exact_key',1,encoded)
            db.create_function('hash_word',1,lambda value:None if value is None else int.from_bytes(hashlib.sha256(value).digest()[:4],'big'))
            row=db.execute(tree.sql(dialect='sqlite')).fetchone()
            expected=sum(int.from_bytes(hashlib.sha256(encoded(v)).digest()[:4],'big') for v in set(values) if v is not None)
            self.assertEqual(row,(5,4,expected))


if __name__=='__main__':unittest.main()
