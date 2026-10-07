import copy
import unittest
import test_translation_proposer as witnesses
from investigator.adapters.translation_scope import apply
from investigator import query_sql


class ScopedTranslationTests(unittest.TestCase):
    def setUp(self):
        self.request, _ = witnesses.case('MEASURE')
        self.request['metadata']['normalization'] = {'encoding':'typed-json-utf8','case_fold':False,'trim':False}
        proof = witnesses.TranslationTests().binding(self.request)
        self.request['metadata'].update(key_binding=proof, key_definition_hashes=copy.deepcopy(proof['declaration']['definition_hashes']))
        self.objects = {'table': {'catalog': {'id':'table', 'metadata': {'schema_name':'dbo', 'name':'Source',
            'type_desc':'USER_TABLE','columns':[{'id':'proposed.k','name':'Key','data_type':'int'},
                                              {'id':'value','name':'Value','data_type':'bigint'}]}}}}
        self.query = 'SELECT SUM(s.[Value]) AS quantity FROM dbo.Source AS s'
        self.scope = [{'field_id':'native.k','operator':'IN','values':[1,2]}]

    def test_scope_is_compiled_and_parameterised_through_exact_verified_column(self):
        sql = apply(self.query, self.scope, self.request, self.objects)
        compiled = query_sql.compile_query(sql, [self.objects['table']['catalog']])
        self.assertIn('WHERE', compiled['query'])
        self.assertEqual([parameter['value'] for parameter in compiled['parameters']], ['1','2'])

    def test_empty_intersection_is_a_false_predicate_not_missing_scope(self):
        sql = apply(self.query, [{**self.scope[0], 'values':[]}], self.request, self.objects)
        self.assertIn('1 = 0', sql)

    def test_missing_stale_falsified_or_quantity_binding_refuses(self):
        for kind in ('missing','stale','falsified','quantity'):
            request = copy.deepcopy(self.request)
            if kind == 'missing': request['metadata'].pop('key_binding')
            elif kind == 'stale': request['metadata']['key_definition_hashes']['native'] = '0'*64
            elif kind == 'falsified': request['metadata']['key_binding']['status'] = 'FALSIFIED'
            else: request['metadata']['key_binding'] = {'status':'VERIFIED','quantity':3}
            with self.subTest(kind=kind), self.assertRaises((ValueError, KeyError, NotImplementedError)):
                apply(self.query, self.scope, request, self.objects)

    def test_unknown_alias_self_join_or_nested_scope_never_guesses(self):
        for query in ('SELECT SUM(x.Value) AS quantity FROM dbo.Other x',
                      'SELECT SUM(s.Value) AS quantity FROM dbo.Source s JOIN dbo.Source t ON s.[Key]=t.[Key]',
                      'SELECT (SELECT SUM(s.Value) FROM dbo.Source s) AS quantity FROM dbo.Source t'):
            with self.subTest(query=query), self.assertRaises(NotImplementedError):
                apply(query, self.scope, self.request, self.objects)

    def test_unseen_keys_and_undeclared_string_semantics_refuse(self):
        with self.assertRaisesRegex(NotImplementedError, 'outside'):
            apply(self.query, [{**self.scope[0], 'values':[99]}], self.request, self.objects)
        self.objects['table']['catalog']['metadata']['columns'][0]['data_type'] = 'varchar'
        with self.assertRaisesRegex(NotImplementedError, 'collation'):
            apply(self.query, self.scope, self.request, self.objects)


if __name__ == '__main__': unittest.main()
