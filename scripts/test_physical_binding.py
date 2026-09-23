import json
from pathlib import Path
import unittest
from unittest.mock import patch
from sqlglot import parse_one, exp
from sqlglot.optimizer.qualify import qualify
from investigator.query_sql import compile_query,QueryRejection
from investigator.physical_binding import describe,object_feedback


class ParameterBindingTests(unittest.TestCase):
    def test_recorded_g_candidate_preserves_group_expression(self):
        fixture=json.loads((Path(__file__).parent/'fixtures/sql_group_binding.json').read_text())
        objects=[{'id':name,'metadata':{'schema_name':'app','name':name,
                 'type_desc':'USER_TABLE','columns':[{'name':c,'data_type':'int'} for c in columns]}}
                 for name,columns in fixture['tables'].items()]
        compiled=compile_query(fixture['query'],objects,max_rows=20)
        bound=parse_one(compiled['query'],read='tsql')
        cases=list(bound.find_all(exp.Case))
        self.assertEqual(len(cases),2)
        self.assertEqual(cases[0],cases[1])
        self.assertEqual(len(compiled['parameters']),4)
        # Restore literal nodes solely in this test to compare against qualification
        # of the untouched proposal; no semantic rewriting/equivalence engine.
        values={p['name'][1:]:p['value'] for p in compiled['parameters']}
        restored=cases[0].copy()
        for parameter in list(restored.find_all(exp.Parameter)):
            value=values[parameter.name]
            if isinstance(parameter.parent,exp.Cast):
                parameter.parent.replace(exp.Literal.number(value))
            else:parameter.replace(exp.Literal.string(value))
        schema={'app':{name:{c:'int' for c in cols} for name,cols in fixture['tables'].items()}}
        original=qualify(parse_one(fixture['query'],read='tsql'),dialect='tsql',schema=schema)
        self.assertEqual(restored,next(original.find_all(exp.Case)))

    def test_literal_type_and_value_remain_distinct(self):
        objects=[{'id':'x','metadata':{'schema_name':'s','name':'t','type_desc':'USER_TABLE',
                    'columns':[{'name':'n','data_type':'int'}]}}]
        result=compile_query("SELECT '1' AS a, 1 AS b, 1.0 AS c, '1' AS d, 2 AS e FROM s.t",objects)
        self.assertEqual([p['value'] for p in result['parameters']],['1','1','1.0','2'])
        tree=parse_one(result['query'],read='tsql')
        self.assertEqual(tree.expressions[0].this,tree.expressions[3].this)


class PhysicalFeedbackTests(unittest.TestCase):
    def test_complexity_names_measured_counts_and_unchanged_caps(self):
        query='SELECT '+','.join('(SELECT COUNT(*) FROM z.t) AS v'+str(i) for i in range(8))+' FROM z.t'
        with self.assertRaises(QueryRejection) as caught:compile_query(query,[])
        self.assertEqual(caught.exception.feedback['measured'],{'selects':9,'joins':0})
        self.assertEqual(caught.exception.feedback['caps'],{'selects':8,'joins':4})

    def test_scoped_hints_never_rebind_or_invent_schema(self):
        sql={'id':'sql://host/db/object/1','parent_id':'sql://host/db','kind':'SqlObject',
             'name':'inventory.rows','metadata':{'name':'rows','schema_name':'inventory'}}
        fabric={'id':'fabric://workspace/lake/table/rows','kind':'LakehouseTable','name':'rows','metadata':{}}
        config={'sql':{'server':'host','database':'db','visibility_schema':'inventory'}}
        error=QueryRejection('unavailable',reason_code='SQL_OBJECT_UNAVAILABLE',object_name='rows',requested_schema='other')
        with patch('investigator.context_search.latest',return_value={'assets':[sql,fabric]}):
            feedback=object_feedback(None,config,{sql['id']:sql},error)
        self.assertEqual(feedback['searched_connection'],'sql://host/db')
        self.assertEqual(feedback['requested_schema'],'other')
        self.assertEqual(len(feedback['catalog_targets']),2)
        self.assertIn('cannot be joined',feedback['binding_notice'])
        self.assertEqual(describe(sql)['schema'],'inventory')
        self.assertIsNone(describe(fabric)['schema'])
        self.assertEqual(describe(fabric)['sql_endpoint_binding'],'NOT_ESTABLISHED')
        self.assertNotIn('query',feedback)

    def test_members_inherit_schema_only_from_actual_parent(self):
        parent={'id':'sql://host/db/object/1','metadata':{'schema_name':'private_schema'}}
        child={'id':'sql://host/db/object/1/column/x','parent_id':parent['id']}
        self.assertEqual(describe(child,{parent['id']:parent})['schema'],'private_schema')
        self.assertIsNone(describe(child)['schema'])

    def test_rejection_targets_and_binding_survive_compaction_and_wire(self):
        from investigator.dynamic_reasoning import compact_context,wire_contract
        target={'id':'sql://h/d/object/1','kind':'SqlObject','name':'s.t',
                'physical_binding':{'system':'SQL','connection':'sql://h/d','schema':'s'}}
        payload={'observations':[{'id':'r','tool':'context','status':'REJECTED','metadata':{
            'reason':'unavailable','reason_code':'SQL_OBJECT_UNAVAILABLE','catalog_targets':[target],
            'binding_notice':'Inspect exact endpoint','unused':'x'*2000}},
            {'id':'last','tool':'context','metadata':{}}], 'candidates':[], 'hypotheses':[],
            'context':[{'id':'optional-'+str(i)} for i in range(130)]}
        compact_context(payload)
        self.assertEqual(payload['observations'][0]['metadata']['catalog_targets'],[target])
        wire,_,handles=wire_contract(payload)
        item=wire['observations'][0]['metadata']['catalog_targets'][0]
        self.assertEqual(handles[item['id']],target['id'])
        self.assertEqual(item['physical_binding'],target['physical_binding'])


if __name__=='__main__':unittest.main()
