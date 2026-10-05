import copy,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import test_lineage_binding as fixture
from investigator.adapters.code_lineage import Installation
from investigator.lineage_binding import Ledger

class InstallationTests(unittest.TestCase):
    def setup_installation(self,d):
        self.v,_=fixture.BindingTests().verification()
        self.v['proposal']['location']['item']='source'
        self.manifest={'layers':[{'id':'input','asset_id':'input-asset'},{'id':'output','asset_id':'output-asset'}],
            'lineage':{'bindings':[],'inference':{'enabled':True},
                'code_sources':[{'id':'source'}], 'code_locations':[{'from_layer':'input','to_layer':'output',
                    'may_infer_from_code':True,'locations':[{'source':'source','path':'unit.py'}]}]}}
        self.path={'layers':[{'id':'report'}, {'id':'output-asset','source_column':'amount'},
            {'id':'input-asset','source_column':'amount','compiled':{'query':'original input'},
                'binding':{'provenance':'DECLARED_BY_DEFINITION'}}], 'evidence':{'id':'path'}}
        adapter=SimpleNamespace(store=None,model={'context_id':self.v['context']})
        context={'assets':[{'id':'input-asset','availability':'CURRENT','metadata':{'location':'input-table'}},
            {'id':'output-asset','availability':'CURRENT','metadata':{'location':'output-table'}}]}
        installed=Installation(self.manifest,Path(d)/'estate.json',d)
        self.context=context;self.adapter=adapter
        installed.ledger.append(self.v)
        return installed

    def execute(self,installed,hash='a'*64):
        unit={'item_identity':{'logical_id':'code-item'},'content_hash':hash}
        receipt={'content_hash':hash,'kind':'LOCAL_PATH'}
        self.meters=[]
        def read(source,path,*,meter,**kwargs):
            meter(lambda:None);return unit,receipt
        def meter(tool,execute,physical_only=False):
            self.meters.append((tool,physical_only));return execute()
        with patch('investigator.context_search.latest',return_value=self.context),             patch('investigator.adapters.code_lineage.read',side_effect=read),             patch.object(installed,'approval',return_value={'declared_verifications':[]}):
            return installed(self.adapter,self.path,{},meter)

    def test_real_ledger_records_reach_the_runtime_without_lossy_projection(self):
        with tempfile.TemporaryDirectory() as d:
            installed=self.setup_installation(d)
            self.assertEqual(installed.ledger.records(),[self.v])
            result=self.execute(installed)
            self.assertEqual(len(result['layers']),3)
            self.assertEqual(result['layers'][-1]['binding']['lineage_verification'],self.v)
            self.assertEqual(self.meters,[('code_source',True)])
            self.assertEqual(result['layers'][-1]['compiled'],{'query':'original input'})

    def test_changed_hash_is_recorded_and_unbound_without_rewriting_ledger(self):
        with tempfile.TemporaryDirectory() as d:
            installed=self.setup_installation(d);before=installed.ledger.path.read_bytes()
            result=self.execute(installed,hash='b'*64)
            self.assertEqual(len(result['layers']),2)
            self.assertEqual(result['evidence']['lineage_qualification'][0]['selection']['excluded'][0]['status'],'STALE')
            self.assertEqual(installed.ledger.path.read_bytes(),before)

    def test_no_recorded_sample_cannot_manufacture_verification(self):
        with tempfile.TemporaryDirectory() as d:
            installed=self.setup_installation(d);installed.ledger.path.unlink()
            result=self.execute(installed)
            self.assertEqual(len(result['layers']),2)
            self.assertIn('No unique recorded',result['unresolved_boundary']['reason'])

if __name__=='__main__':unittest.main()
