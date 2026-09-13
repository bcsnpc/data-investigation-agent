import ast
import copy
from pathlib import Path
import unittest
from uuid import uuid4
from bronze_publication import validate_verification
from source_snapshot import TABLES


class PublicationTests(unittest.TestCase):
    def fixture(self):
        plan={'status':'PLANNED','source_snapshot_id':str(uuid4()),'source_manifest_sha256':'expected','tables':[]}
        rows=[]
        for name in TABLES:
            table={'source_table':name,'destination':'isolated/'+name,'source_sha256':'source','source_schema_sha256':'schema','expected_rows':10}
            plan['tables'].append(table)
            rows.append(dict(table,rows=10,delta_table_id=str(uuid4()),delta_version=0,content_reconciled=True,delta_schema={'fields':[]}))
        publication=dict(plan,status='COMPLETE',tables=rows,verification_id=str(uuid4()))
        verification=copy.deepcopy(publication);verification.update(mode='VERIFY_ONLY',verification_id=str(uuid4()))
        return plan,publication,verification,{'status':'Completed','id':str(uuid4())}

    def test_exact_pinned_verification(self):
        result=validate_verification(*self.fixture())
        self.assertEqual(result['rows'],100)
        self.assertEqual(result['status'],'SOURCE_TO_BRONZE_VERIFIED')

    def test_replacement_version_schema_and_content_rejected(self):
        for key,value in [('delta_table_id',str(uuid4())),('delta_version',1),('delta_schema',{'fields':['changed']}),('content_reconciled',False)]:
            args=self.fixture();args[2]['tables'][0][key]=value
            with self.assertRaises(ValueError):validate_verification(*args)

    def test_same_execution_or_failed_job_rejected(self):
        args=self.fixture();args[2]['verification_id']=args[1]['verification_id']
        with self.assertRaises(ValueError):validate_verification(*args)
        args=self.fixture();args[3]['status']='Failed'
        with self.assertRaises(ValueError):validate_verification(*args)

    def test_sql_types_fail_closed(self):
        tree=ast.parse((Path(__file__).resolve().parents[1]/'infra/fabric/publish_source_snapshot.py').read_text())
        function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='spark_type')
        namespace={};exec(compile(ast.Module(body=[function],type_ignores=[]),'type_contract','exec'),namespace)
        convert=namespace['spark_type']
        self.assertEqual(convert({'sql_type':'decimal','precision':'19','scale':'4'}),'decimal(19,4)')
        self.assertEqual(convert({'sql_type':'datetime2'}),'timestamp')
        with self.assertRaises(ValueError):convert({'sql_type':'sql_variant'})


if __name__=='__main__':unittest.main()
