import copy,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from investigator.adapters.code_approval import Controller
import test_lineage_binding as fixture


class ControllerTests(unittest.TestCase):
    def setup(self,d):
        result,_=fixture.BindingTests().verification()
        sample={k:result[k] for k in ('proposal','context','cell','precision')}
        edge=sample['proposal']['boundary']
        manifest={'layers':[],'lineage':{'bindings':[dict(edge,provenance='DECLARED_BY_CONFIGURATION')],
            'code_sources':[{'id':'code-item'}],
            'code_locations':[dict(edge,may_infer_from_code=True,
                                   locations=[{'source':'code-item','path':'unit.py'}])]}}
        calls=[]
        class Route:
            def compile(self,*args):return None
            def execute(self,side,plan):
                calls.append(side);return copy.deepcopy(result['observations'][0 if side=='TARGET' else 1])
        controller=Controller(manifest,Path(d)/'estate.json',d,meter=None,route_factory=lambda sample:Route())
        return controller,sample,result,calls

    def test_approval_then_single_fetch_shared_by_multiple_samples(self):
        with tempfile.TemporaryDirectory() as d:
            c,s,v,calls=self.setup(d);c.approve([s])
            request={'boundary':s['proposal']['boundary'],'source':'code-item','path':'unit.py',
                     'target_table':s['proposal']['target']['table'],'schemas':{},
                     **{k:s[k] for k in ('context','cell','precision')}}
            unit={'content_hash':'a'*64,'path':'unit.py'};receipt=copy.deepcopy(unit)
            with patch('investigator.adapters.code_approval.read',return_value=(unit,receipt)) as read,\
                 patch('investigator.transformation_service.propose',return_value={'proposals':[s['proposal']]}):
                output=c.infer([request,copy.deepcopy(request)])
            self.assertEqual(read.call_count,1)
            self.assertEqual(len(output['boundaries']),2)
            self.assertEqual(calls,['TARGET','SOURCE']*3)
            self.assertEqual(len(c.ledger.records()),3)

    def test_missing_declaration_refuses_before_adapter_resolution(self):
        with tempfile.TemporaryDirectory() as d:
            c,s,v,calls=self.setup(d)
            c.route_factory=lambda sample:self.fail('Resolution must not run')
            with self.assertRaisesRegex(ValueError,'cover exactly'):c.approve([])
            self.assertFalse(c.destination.exists())

    def test_failed_approval_cannot_start_reader_or_fetch_code(self):
        with tempfile.TemporaryDirectory() as d:
            c,s,v,calls=self.setup(d)
            with patch('investigator.adapters.code_approval.read') as read:
                with self.assertRaises(FileNotFoundError):c.infer([])
            read.assert_not_called()

    def test_unauthorized_location_refuses_before_fetch(self):
        with tempfile.TemporaryDirectory() as d:
            c,s,v,calls=self.setup(d);c.approve([s])
            request={'boundary':s['proposal']['boundary'],'source':'code-item','path':'other.py',
                     'target_table':s['proposal']['target']['table'],'schemas':{},
                     **{k:s[k] for k in ('context','cell','precision')}}
            with patch('investigator.adapters.code_approval.read') as read:
                with self.assertRaisesRegex(ValueError,'not authorized'):c.infer([request])
            read.assert_not_called()

if __name__=='__main__':unittest.main()
