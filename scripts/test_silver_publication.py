import copy
import unittest
from uuid import uuid4
from silver_publication import SOURCES, validate


class SilverPublicationTests(unittest.TestCase):
    def fixture(self):
        binding={'source_snapshot_id':str(uuid4()),'tables':[{'source_table':s,'rows':10} for s in SOURCES.values()]}
        report={'status':'READY','run_id':str(uuid4()),'bronze_binding':binding,'outputs':{}}
        for name in SOURCES:
            report['outputs'][name]={'path':'silver/Tables/'+name,'delta_table_id':str(uuid4()),
                'delta_version':1,'rows':10,'schema':{'fields':[{'name':'key'}]},'content_reconciled':True}
        return binding,report

    def test_complete_publication(self):
        self.assertEqual(validate(*self.fixture(),'silver')['rows'],100)

    def test_partial_or_unrelated_receipt_rejected(self):
        for failure in ('running','missing','binding'):
            binding,report=self.fixture()
            if failure=='running':report['status']='RUNNING'
            if failure=='missing':report['outputs'].pop('fact_order')
            if failure=='binding':report['bronze_binding']={}
            with self.assertRaises(ValueError):validate(binding,report,'silver')

    def test_bad_output_evidence_rejected(self):
        for key,value in [('delta_version',True),('delta_version',-1),('rows',11),
                          ('path','another/Tables/fact_order'),('schema',{}),('content_reconciled',False)]:
            binding,report=self.fixture()
            report['outputs']['fact_order'][key]=value
            with self.assertRaises(ValueError):validate(binding,report,'silver')

    def test_reused_table_identity_rejected(self):
        binding,report=self.fixture()
        report['outputs']['fact_order']['delta_table_id']=report['outputs']['dim_customer']['delta_table_id']
        with self.assertRaises(ValueError):validate(binding,report,'silver')


if __name__=='__main__':unittest.main()
