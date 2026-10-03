"""Every semantic probe compiles the same answered scalarisation before reads."""
import unittest
from unittest.mock import patch
from investigator import flexible_tools,query_dax
from investigator.adapters.microsoft_process import semantic_self_report,SEMANTIC_REPORT
import test_declared_predicate_adapter as fixture

class CompositionTests(unittest.TestCase):
    setUp=fixture.DeclaredPredicateAdapterTests.setUp
    part=fixture.DeclaredPredicateAdapterTests.part
    def test_shared_composition_projects_every_column_without_generic_metadata_access(self):
        for base in ('EVALUATE ROW("quantity",[Revenue])',
                     'EVALUATE ROW("quantity",COUNTROWS(VALUES(Customers[Region])))',
                     'EVALUATE ROW("quantity",CALCULATE([Revenue],TREATAS({"North"},Customers[Region])))'):
            compiled=query_dax.compile_query(semantic_self_report(base),self.model['context']['model_assets'])
            self.assertTrue(set(SEMANTIC_REPORT.values())<=set(compiled['result_columns']))
            self.assertEqual(compiled['query'].count('USERPRINCIPALNAME()'),1)
            self.assertIn('CONCATENATEX(SELECTCOLUMNS(FILTER(INFO.PROPERTIES()',compiled['query'])
            self.assertNotIn('MAXX(FILTER(INFO.PROPERTIES()',compiled['query'])
    def test_missing_each_report_column_refuses_before_transport_or_receipt(self):
        plan={'model_id':self.model['id'],'revision':self.model['revision'],'context_id':self.model['context_id'],
              'max_rows':20,'surface_report':SEMANTIC_REPORT}
        for missing in SEMANTIC_REPORT.values():
            columns=[('quantity','[Revenue]')]+[(c,'USERPRINCIPALNAME()') for c in SEMANTIC_REPORT.values() if c!=missing]
            query='EVALUATE ROW('+','.join('"'+c+'",'+v for c,v in columns)+')'
            with self.assertRaisesRegex(ValueError,'lacks declared surface-report columns'):
                flexible_tools.run(self.store,dict(plan,query=query),self.config,'bounded_dax',
                                   lambda request:self.fail('No execution allowed'))
        self.assertEqual(self.requests,[]);self.assertEqual(self.meters,[])
        self.assertFalse(self.store.path.exists())
    def test_scalar_label_cannot_impersonate_a_projected_column(self):
        plan={'model_id':self.model['id'],'revision':self.model['revision'],'context_id':self.model['context_id'],
              'max_rows':20,'surface_report':SEMANTIC_REPORT,
              'query':'EVALUATE ROW("quantity",[Revenue],"other","surface_identity surface_engine surface_object")'}
        with self.assertRaisesRegex(ValueError,'lacks declared surface-report columns'):
            flexible_tools.build(self.store,plan,self.config,'bounded_dax')
    def test_adapter_baseline_declared_and_existence_cannot_bypass_shared_compile_path(self):
        with patch('investigator.adapters.microsoft_process.semantic_self_report',side_effect=lambda query:query):
            for call in (lambda:self.adapter.evaluate(self.layer,self.measure['id'],{'filters':[]}),
                         lambda:self.adapter.declared_context(self.layer,self.measure['id'],self.scope),
                         lambda:self.adapter._observe_selection_value(self.layer,self.column['id'],'North',self.scope)):
                with self.assertRaisesRegex(ValueError,'lacks declared surface-report columns'):call()
        self.assertEqual(self.requests,[]);self.assertEqual(self.meters,[])

    def test_executed_adapter_probes_share_the_composition(self):
        self.adapter.evaluate(self.layer,self.measure['id'],{'filters':[]})
        self.adapter.evaluate(self.layer,self.measure['id'],self.scope)
        declaration=self.adapter.declared_context(self.layer,self.measure['id'],self.scope)
        self.adapter.evaluate_declared_context(self.layer,self.measure['id'],{'restrictions':[],'dimension_ids':[]})
        from investigator.declared_reproduction import compose
        self.adapter.evaluate_declared_context(self.layer,self.measure['id'],{'restrictions':compose(declaration['restrictions']),'dimension_ids':[]})
        for request in self.requests:
            self.assertTrue(set(SEMANTIC_REPORT.values())<=set(request['result_columns']))
            self.assertEqual(request['query'].count('USERPRINCIPALNAME()'),1)
            self.assertEqual(request['query'].count('CONCATENATEX('),2)
