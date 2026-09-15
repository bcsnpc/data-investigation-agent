import unittest
from investigator.semantic_graph import analyze, affected


def assets(expressions):
    return [{'id':'t','name':'Sales','kind':'SemanticTable','parent_id':'model','metadata':{},'content_hash':'t'},
            {'id':'amount','name':'amount','kind':'SemanticColumn','parent_id':'t','metadata':{},'content_hash':'c'}]+[
        {'id':name,'name':name,'kind':'Measure','parent_id':'t','metadata':{'expression':expression},'content_hash':name}
        for name,expression in expressions.items()]


class SemanticTests(unittest.TestCase):
    def test_recursive_dependencies_operations_and_impacted_closure(self):
        g=analyze(assets({'Revenue':'SUM(Sales[amount])','COGS':'SUM(Sales[amount])',
                         'Margin':'DIVIDE([Revenue] - [COGS], [Revenue])'}))
        self.assertEqual(g['measures']['Margin']['dependencies'],['COGS','Revenue'])
        self.assertIn('RATIO',g['measures']['Margin']['operations'])
        self.assertEqual(g['dependency_state'],'SUPPORTED')
        self.assertEqual(affected(['amount'],g),['COGS','Margin','Revenue'])
        self.assertEqual(g['measures']['Margin']['native_queryability'],'UNKNOWN')

    def test_strings_comments_escaped_names_and_table_reference(self):
        g=analyze(assets({'Base] value':'COUNTROWS(Sales)',
                         'Parent':'IF(HASONEVALUE(Sales[amount]), [Base]] value], "[Not a reference]") // [ignored]'}))
        self.assertEqual(g['measures']['Parent']['dependencies'],['Base] value'])
        self.assertIn('t',g['measures']['Base] value']['references'])
        self.assertNotIn('Unresolved',str(g['measures']['Parent']['gaps']))

    def test_cycles_unknown_references_and_unsupported_functions(self):
        g=analyze(assets({'A':'[B]','B':'[A]','C':'[A]+[Missing]','D':'SUMX(Sales,Sales[amount])'}))
        self.assertEqual(g['dependency_state'],'PARTIAL')
        self.assertIn('Cyclic measure dependency',g['measures']['A']['gaps'])
        self.assertEqual(g['measures']['C']['dependency_state'],'PARTIAL')
        self.assertIn('Operation analysis unavailable',str(g['measures']['D']['gaps']))

    def test_ambiguous_reference_is_not_guessed_and_input_is_bounded(self):
        a=assets({'amount':'1','Other':'[amount]'});g=analyze(a)
        self.assertTrue(g['measures']['Other']['gaps'])
        self.assertTrue(analyze(assets({'Huge':'x'*100001}))['measures']['Huge']['gaps'])


if __name__=='__main__':unittest.main()
