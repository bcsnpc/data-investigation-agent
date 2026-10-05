import copy,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from investigator.transformation_service import run,select
from investigator.lineage_binding import Ledger
import test_lineage_binding as fixture


class ServiceTests(unittest.TestCase):
    def rows(self):
        return fixture.BindingTests().verification()[0]

    def params(self):
        v=self.rows()
        return dict(declared=[],inferred=[v],current_hashes={('code-item','unit.py'):'a'*64},
                    boundary=v['proposal']['boundary'],target_column='amount',
                    context=v['context'],cell=v['cell'],precision=v['precision'])

    def test_declared_first_and_no_inferred_fallback_around_failed_declaration(self):
        p=self.params();p['declared']=[self.rows()]
        self.assertEqual(select(**p)['provenance'],'DECLARED_BY_CONFIGURATION')
        p['declared'][0]['status']='FALSIFIED'
        self.assertEqual(select(**p)['status'],'UNBOUND')

    def test_stale_or_different_sample_is_unbound_never_confidence_override(self):
        p=self.params();self.assertEqual(select(**p)['status'],'RESOLVED')
        p['current_hashes'][('code-item','unit.py')]='b'*64
        result=select(**p);self.assertEqual(result['status'],'UNBOUND')
        p=self.params();p['cell']={'id':'other-cell'}
        self.assertEqual(select(**p)['status'],'UNBOUND')

    def test_distinct_verified_expressions_refuse_ambiguity(self):
        p=self.params();other=copy.deepcopy(p['inferred'][0])
        other['proposal']['expression']['relation']={'kind':'DEDUPE',
            'input':other['proposal']['expression']['relation'],'keys':['amount']}
        p['inferred'].append(other)
        self.assertEqual(select(**p)['status'],'AMBIGUOUS')

    def test_later_falsification_cannot_reuse_earlier_matching_sample(self):
        p=self.params();later=copy.deepcopy(p['inferred'][0]);later['status']='FALSIFIED'
        p['inferred'].append(later)
        self.assertEqual(select(**p)['status'],'UNBOUND')

    def test_service_retains_each_verifier_result_in_ledger(self):
        v=self.rows()
        with tempfile.TemporaryDirectory() as d:
            ledger=Ledger(Path(d)/'lineage.jsonl')
            with patch('investigator.transformation_service.read',return_value=({}, {'content_hash':'a'*64})),\
                 patch('investigator.transformation_service.propose',return_value={'proposals':[v['proposal']]}),\
                 patch('investigator.transformation_service.verify',return_value=v):
                result=run(source={},path='unit.py',meter=None,root=d,schemas={},boundary=v['proposal']['boundary'],
                    item='code-item',target_table='output-table',layers=[],context=v['context'],cell=v['cell'],
                    precision=v['precision'],compiler=None,execute=None,ledger=ledger)
            self.assertEqual(result['verifications'],[v])
            self.assertEqual(ledger.view({('code-item','unit.py'):'a'*64})[0]['status'],'VERIFIED')

if __name__=='__main__':unittest.main()
