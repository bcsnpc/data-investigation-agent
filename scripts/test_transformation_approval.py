import copy,json,tempfile,unittest
from pathlib import Path
from investigator.transformation_approval import approve,read_approval
from investigator.lineage_binding import Ledger,seal
import test_lineage_binding as fixture

class ApprovalTests(unittest.TestCase):
    def setup_approval(self,d,values=('7','7')):
        result,_=fixture.BindingTests().verification(values)
        self.manifest={'lineage':{'bindings':[dict(result['proposal']['boundary'],provenance='DECLARED_BY_CONFIGURATION')]}}
        self.sample={k:result[k] for k in ('proposal','context','cell','precision')}
        observations=iter(result['observations']);self.calls=[]
        def execute(side,plan):
            self.calls.append(side);return next(observations)
        return dict(samples=[self.sample],compiler=lambda *args:None,execute=execute,
            ledger=Ledger(Path(d)/'lineage.jsonl'),destination=Path(d)/'approval.json',now='2026-10-05T00:00:00Z')

    def test_approval_executes_verifier_and_leaves_manifest_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            options=self.setup_approval(d);original=copy.deepcopy(self.manifest)
            approve(self.manifest,**options)
            record=read_approval(options['destination'],self.manifest)
            self.assertEqual(self.calls,['TARGET','SOURCE'])
            self.assertEqual(record['declared_verifications'][0]['status'],'VERIFIED')
            self.assertEqual(self.manifest,original)
            with self.assertRaises(FileExistsError):
                # No re-execution when an immutable destination already exists.
                approve(self.manifest,**options)

    def test_falsified_declaration_blocks_and_retains_values_in_ledger(self):
        with tempfile.TemporaryDirectory() as d:
            options=self.setup_approval(d,('7','8'))
            with self.assertRaisesRegex(ValueError,'Declared binding falsified'):
                approve(self.manifest,**options)
            self.assertFalse(options['destination'].exists())
            row=json.loads(options['ledger'].path.read_text())['verification']
            self.assertEqual(row['status'],'FALSIFIED')
            self.assertEqual([o['quantity']['value'] for o in row['observations']],['7','8'])

    def test_uncompilable_declaration_blocks_without_reads_and_retains_reason(self):
        with tempfile.TemporaryDirectory() as d:
            options=self.setup_approval(d)
            def compiler(*args):raise NotImplementedError('Faithful source expression unavailable')
            options['compiler']=compiler
            with self.assertRaisesRegex(ValueError,'not verified'):
                approve(self.manifest,**options)
            self.assertEqual(self.calls,[])
            row=json.loads(options['ledger'].path.read_text())['verification']
            self.assertEqual(row['status'],'UNVERIFIED')
            self.assertIn('Faithful source expression unavailable',row['reason'])
            self.assertFalse(options['destination'].exists())

    def test_missing_or_unconfigured_declaration_refuses_before_read(self):
        with tempfile.TemporaryDirectory() as d:
            options=self.setup_approval(d);options['samples']=[]
            with self.assertRaisesRegex(ValueError,'no executable sample'):
                approve(self.manifest,**options)
            self.assertEqual(self.calls,[])
            options['samples']=[copy.deepcopy(self.sample)]
            options['samples'][0]['proposal']['boundary']['from_layer']='invented'
            with self.assertRaisesRegex(ValueError,'not a configured'):
                approve(self.manifest,**options)
            self.assertEqual(self.calls,[])

    def test_changed_manifest_and_forged_verdict_cannot_reuse_approval(self):
        with tempfile.TemporaryDirectory() as d:
            options=self.setup_approval(d);approve(self.manifest,**options)
            changed=copy.deepcopy(self.manifest);changed['extra']='changed'
            with self.assertRaisesRegex(ValueError,'different manifest'):
                read_approval(options['destination'],changed)
            wrapped=json.loads(options['destination'].read_text())
            wrapped['approval']['declared_verifications'][0]['observations'][1]['quantity']['value']='8'
            wrapped['sha256']=seal(wrapped['approval'])
            options['destination'].write_text(json.dumps(wrapped))
            with self.assertRaisesRegex(ValueError,'falsified'):
                read_approval(options['destination'],self.manifest)

if __name__=='__main__':unittest.main()
