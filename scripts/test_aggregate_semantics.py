import unittest
from copy import deepcopy

from investigator.aggregate_semantics import describe, dependency_shapes, assess_mapping
from investigator.proof_requirements import readiness
from investigator.semantic_graph import analyze
from investigator.onboarding import digest


def model(expressions, table_name='Unfamiliar table', column_name='Amount'):
    assets=[{'id':'t','name':table_name,'kind':'SemanticTable','metadata':{'partitions':[{'mode':'directLake'}]},'parent_id':'m','content_hash':'t'},
            {'id':'c','name':column_name,'kind':'SemanticColumn','metadata':{'dataType':'decimal'},'parent_id':'t','content_hash':'c'}]
    for identity,expression in expressions.items():
        assets.append({'id':identity,'name':identity,'kind':'Measure','parent_id':'t',
                       'metadata':{'expression':expression},'content_hash':digest(expression)})
    return {'id':'m','context_id':'ctx','context':{'measures':[{'id':i} for i in expressions],
        'reports':[{'model_assets':assets}],'semantic_graph':analyze(assets)}}


class AggregateTests(unittest.TestCase):
    def test_unseen_names_do_not_change_direct_operator_support(self):
        for table_name,column_name in [('Unfamiliar table','Amount'),("Owner's facts",'Cost] basis')]:
            expression="SUM('"+table_name.replace("'","''")+"'["+column_name.replace(']',']]')+'])'
            m=model({'Never registered metric':expression},table_name,column_name)
            result=describe(m,'Never registered metric')
            self.assertEqual(result['state'],'SUPPORTED');self.assertEqual(result['input_id'],'c')

    def test_countrows_table_binding(self):
        result=describe(model({'Rows':"COUNTROWS('Unfamiliar table')"}),'Rows')
        self.assertEqual(result['operation'],'count_rows');self.assertEqual(result['input_id'],'t')

    def test_context_operations_and_distinct_are_not_flat_sums(self):
        for expression in ["CALCULATE(SUM('Unfamiliar table'[Amount]))","SUMX('Unfamiliar table',[Amount])",
                           "DISTINCTCOUNT('Unfamiliar table'[Amount])","SUM('Unfamiliar table'[Amount])+1",
                           "IF(TRUE(),SUM('Unfamiliar table'[Amount]),BLANK())"]:
            self.assertEqual(describe(model({'Metric':expression}),'Metric')['state'],'UNSUPPORTED')

    def test_complex_parent_preserves_supported_children_without_local_evaluation(self):
        m=model({'Revenue':"SUM('Unfamiliar table'[Amount])",'Costs':"SUM('Unfamiliar table'[Amount])",
                 'Margin':'DIVIDE([Revenue]-[Costs],[Revenue])'})
        tree=dependency_shapes(m,'Margin');nodes={n['measure_id']:n for n in tree['nodes']}
        self.assertEqual(set(nodes),{'Margin','Revenue','Costs'})
        self.assertEqual(nodes['Margin']['aggregate']['state'],'UNSUPPORTED')
        self.assertEqual(nodes['Revenue']['aggregate']['state'],'SUPPORTED')
        self.assertTrue(tree['native_evaluation_required'])

    def test_calculated_and_float_columns_stay_unsupported(self):
        for change in [{'expression':'1','type':'calculated'},{'dataType':'double'}]:
            m=model({'Metric':"SUM('Unfamiliar table'[Amount])"})
            m['context']['reports'][0]['model_assets'][1]['metadata'].update(change)
            self.assertEqual(describe(m,'Metric')['state'],'UNSUPPORTED')

    def test_mapping_input_is_explicit_and_operation_mismatch_held(self):
        m=model({'Rows':"COUNTROWS('Unfamiliar table')"})
        contract={'measure_id':'Rows','source_operation':'count_rows','native_input_id':'t'}
        source={'request':{'plan':{'operation':'count_rows'}}}
        result=assess_mapping(m,contract,source)
        self.assertEqual(result['state'],'SUPPORTED_DECLARED_SHAPE');self.assertFalse(result['semantic_equivalence_verified'])
        contract['native_input_id']='wrong';self.assertIn('NATIVE_INPUT_MAPPING_REQUIRED',assess_mapping(m,contract,source)['gaps'])
        contract['source_operation']='sum';self.assertIn('AGGREGATE_OPERATIONS_DIFFER',assess_mapping(m,contract,source)['gaps'])

    def test_definition_change_changes_shape_and_hash(self):
        a=describe(model({'Metric':"SUM('Unfamiliar table'[Amount])"}),'Metric')
        b=describe(model({'Metric':"COUNTROWS('Unfamiliar table')"}),'Metric')
        self.assertNotEqual(a['definition_hash'],b['definition_hash']);self.assertNotEqual(a['operation'],b['operation'])

    def test_retained_metadata_and_directlake_are_not_generation_proof(self):
        result=readiness(model({'Metric':"COUNTROWS('Unfamiliar table')"}))
        self.assertEqual(result['observed_partition_modes'],['directLake'])
        self.assertFalse(result['live_acceptance_ready'])
        states={r['id']:r['state'] for r in result['requirements']}
        self.assertEqual(states['retained_definition'],'AVAILABLE')
        self.assertEqual(states['exclusive_remote_write_boundary'],'MISSING')


if __name__=='__main__':unittest.main()
