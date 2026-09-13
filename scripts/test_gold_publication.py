import hashlib
import unittest
from uuid import uuid4
from gold_publication import TABLES,validate
from gold_snapshot_input import validate_proof
from source_snapshot import canonical
from silver_publication import validate as validate_silver
import test_silver_publication


class GoldPublicationTests(unittest.TestCase):
    def fixture(self):
        binding={'report':{'run_id':str(uuid4()),'bronze_binding':{'source_snapshot_id':str(uuid4())}}}
        report={'status':'READY','run_id':str(uuid4()),'silver_binding':binding,
                'silver_run_id':binding['report']['run_id'],'checks':{'reconciliation':True},'outputs':{},'counts':{}}
        for name in TABLES:
            report['counts'][name]=10
            report['outputs'][name]={'path':'gold/Tables/'+name,'delta_table_id':str(uuid4()),'delta_version':1,
                'rows':10,'content_reconciled':True,'schema':{'fields':[{'name':'key'}]}}
        return binding,report

    def test_complete_gold_includes_dimensions(self):
        self.assertEqual(validate(*self.fixture(),'gold')['tables'],9)

    def test_failed_partial_and_stale_publications_rejected(self):
        for failure in ('failed','dimension','binding','run'):
            binding,report=self.fixture()
            if failure=='failed':report['checks']['reconciliation']=False
            if failure=='dimension':report['outputs'].pop('dim_date')
            if failure=='binding':report['silver_binding']={}
            if failure=='run':report['silver_run_id']=str(uuid4())
            with self.assertRaises(ValueError):validate(binding,report,'gold')

    def test_output_evidence_rejected(self):
        for key,value in [('delta_version',True),('rows',11),('path','wrong'),('schema',{}),('content_reconciled',False)]:
            binding,report=self.fixture();report['outputs']['order_summary'][key]=value
            with self.assertRaises(ValueError):validate(binding,report,'gold')

    def test_silver_proof_revalidated(self):
        binding,report=test_silver_publication.SilverPublicationTests().fixture()
        proof={'report':report,'job':{'status':'Completed'},'result':validate_silver(binding,report,'silver')}
        digest=hashlib.sha256(canonical(proof).encode()).hexdigest()
        self.assertEqual(validate_proof(binding,proof,digest,'silver',report['run_id'])['status'],'BOUND_SILVER')
        proof['job']['status']='Failed'
        with self.assertRaises(ValueError):validate_proof(binding,proof,digest,'silver',report['run_id'])
        digest=hashlib.sha256(canonical(proof).encode()).hexdigest()
        with self.assertRaises(ValueError):validate_proof(binding,proof,digest,'silver',report['run_id'])


if __name__=='__main__':unittest.main()
