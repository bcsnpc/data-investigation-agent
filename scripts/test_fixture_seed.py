import ast,json,tempfile,unittest
from pathlib import Path
from fixture.seed import load,insert_plan,notebook_template,NOTEBOOK


class FixtureSeedTests(unittest.TestCase):
    def test_committed_seed_is_literal_and_derivation_is_independent_of_engine(self):
        tables=load()['tables']
        movements=next(t for t in tables if t['name'].startswith('stock_movements_'))
        rates=next(t for t in tables if t['name'].startswith('product_rates_'))
        mi={name:i for i,(name,_) in enumerate(movements['columns'])}
        ri={name:i for i,(name,_) in enumerate(rates['columns'])}
        joined=[m for m in movements['rows'] for rate in rates['rows'] if m[mi['product_id']]==rate[ri['product_id']]]
        self.assertEqual(len(movements['rows']),360)
        self.assertEqual(sum(r[mi['units']] for r in movements['rows']),7661)
        self.assertEqual(len(joined),406)
        self.assertEqual(sum(r[mi['units']] for r in joined),8765)

    def test_notebook_code_is_never_executed_and_nonliteral_seed_refuses(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'seed.py';marker=Path(d)/'executed'
            tables=load()['tables']
            p.write_text('import json\nsource_rows=json.loads('+repr(json.dumps(tables))+')\nopen('+repr(str(marker))+',"w").write("bad")')
            self.assertEqual(load(p)['tables'],tables);self.assertFalse(marker.exists())
            p.write_text('source_rows=fetch_from_cloud()')
            with self.assertRaises(ValueError):load(p)
            p.write_text('import json\nsource_rows=json.loads("[]")\nsource_rows=json.loads("[]")')
            with self.assertRaises(ValueError):load(p)

    def test_insert_parameters_are_not_sql_literals_and_identifiers_fail_closed(self):
        table={'name':'synthetic_people','columns':[['name','string']],'rows':[["O'Brien"]]}
        plan=insert_plan(table)
        self.assertNotIn("O'Brien",plan['insert']);self.assertEqual(plan['parameters'],table['rows'])
        self.assertEqual(plan['precondition'],'OBJECT_MUST_NOT_EXIST')
        with self.assertRaises(ValueError):insert_plan(table,'dbo];drop_table')

    def test_notebook_rebinds_only_container_declaration_against_recorded_code(self):
        lakes={k:'00000000-0000-0000-0000-'+str(i).zfill(12) for i,k in enumerate(('bronze','silver','gold'),1)}
        result=notebook_template('11111111-1111-1111-1111-111111111111',lakes)
        before=ast.parse(NOTEBOOK.read_bytes());after=ast.parse(result['source'])
        def without_paths(tree):
            return [ast.dump(n) for n in tree.body if not (isinstance(n,ast.Assign)
                and any(isinstance(t,ast.Name) and t.id=='paths' for t in n.targets))]
        self.assertEqual(without_paths(before),without_paths(after))
        self.assertEqual(set(result['containers']),set(lakes))
        for key,value in lakes.items():self.assertIn(value,result['containers'][key])
        with self.assertRaises(ValueError):notebook_template('11111111-1111-1111-1111-111111111111',{k:list(lakes.values())[0] for k in lakes})


if __name__=='__main__':unittest.main()
