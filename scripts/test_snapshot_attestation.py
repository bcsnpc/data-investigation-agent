import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,Mock
from dataclasses import replace
from investigator import snapshot_attestation as snapshot,process_outcomes
from investigator.process_debugging import vertical,OPTIONAL_CAPABILITIES,REQUIRED_CAPABILITIES
from investigator.synthesis_digest import _process_evidence
from test_process_debugging import Adapter


def report(probe,version='v1',dataset='dataset-1'):
    return {'status':'AVAILABLE','binding':'QUERY_BOUND','quantity_receipt_id':probe.evidence['id'],
            'evidence_id':'snapshot-'+probe.evidence['id'],'surface':dict(probe.execution_surface),
            'dataset_id':dataset,'version':version,
            'identity_provenance':{'account':'metadata@example.com','execution_reader':False}}


class SnapshotAdapter(Adapter):
    def __init__(self,mode='bound',equal=True):
        super().__init__(['top','lower'],{'top':10,'lower':10 if equal else 11},explain=True)
        self.mode=mode;self.read_order=[]
    def capabilities(self):return super().capabilities()|{'snapshot_identity'}
    def evaluate(self,*args):
        self.read_order.append('quantity');return super().evaluate(*args)
    def snapshot_identity(self,probe):
        self.read_order.append('snapshot')
        if self.mode=='error':raise RuntimeError('unavailable')
        if self.mode=='absent':return None
        r=report(probe)
        if self.mode=='metadata':r['binding']='METADATA_ONLY'
        if self.mode=='wrong_receipt':r['quantity_receipt_id']='another-query'
        if self.mode=='wrong_surface':r['surface']['connection']='other'
        if self.mode=='different_version' and probe.layer=='lower':r['version']='v2'
        if self.mode=='different_dataset' and probe.layer=='lower':r['dataset_id']='dataset-2'
        return r


class SnapshotTests(unittest.TestCase):
    def comparison(self,result):return next(o for o in result['_observations'] if o.get('comparison_status')=='CROSS_SURFACE_VERIFIED')
    def test_default_no_report_is_unverified_and_both_outputs_have_specific_limit(self):
        a=Adapter(['top','lower'],{'top':10,'lower':10});r=vertical(a,'measure',{})
        c=self.comparison(r);self.assertEqual(c['snapshot_attestation']['status'],snapshot.UNVERIFIED)
        for key in ('business_output','technical_output'):
            self.assertTrue(any('agreement does not establish that either value is current' in t for t in r[key]['mandatory_limits']))
            self.assertEqual(r[key]['snapshot_attestations'][0]['status'],snapshot.UNVERIFIED)
    def test_bound_reports_can_verify_without_changing_outcome(self):
        for equal in (True,False):
            expected=None
            for mode in ('bound','absent','error','metadata','wrong_receipt','wrong_surface','different_version','different_dataset'):
                a=SnapshotAdapter(mode,equal);r=vertical(a,'measure',{});c=self.comparison(r)
                if expected is None:expected=r['classification']
                self.assertEqual(r['classification'],expected)
                self.assertEqual(c['snapshot_attestation']['status'],snapshot.VERIFIED if mode=='bound' else snapshot.UNVERIFIED)
                self.assertEqual(a.read_order[:2],['quantity','quantity'])
                process_outcomes.validate(r,{o['id']:o for o in r['_observations']})
    def test_mismatch_does_not_infer_alignment_from_equal_version_numbers(self):
        r=vertical(SnapshotAdapter('different_dataset'),'measure',{})
        self.assertEqual(self.comparison(r)['snapshot_attestation']['reason'],'DATASET_OR_VERSION_DIFFERS')
    def test_limit_cannot_be_dropped_and_status_cannot_be_forged(self):
        r=vertical(SnapshotAdapter('metadata',False),'measure',{});c=self.comparison(r)
        limit=snapshot.limitation(c,1);self.assertIn('timing was not excluded',limit)
        r['limits'].remove(limit)
        with self.assertRaisesRegex(ValueError,'specific limitation'):process_outcomes.validate(r,{o['id']:o for o in r['_observations']})
        c['snapshot_attestation']['status']=snapshot.VERIFIED
        with self.assertRaisesRegex(ValueError,'query-bound'):snapshot.checked(c)
    def test_digest_preserves_all_snapshot_fields_and_provenance(self):
        r=vertical(SnapshotAdapter(),'measure',{});c=self.comparison(r)
        result=_process_evidence(c,{o['id']:o for o in r['_observations']})
        self.assertEqual(result['snapshot_attestation'],c['snapshot_attestation'])
        self.assertFalse(result['snapshot_attestation']['upper']['identity_provenance']['execution_reader'])
        self.assertEqual(result['referenced_evidence_ids'],[c['upper_evidence_id'],c['lower_evidence_id']])
        for side in ('upper','lower'):
            self.assertEqual(result[side+'_execution_surface'],c[side+'_execution_surface'])
    def test_historical_comparisons_default_unverified_without_mutation(self):
        r=vertical(SnapshotAdapter(),'measure',{});c=self.comparison(r);c.pop('snapshot_attestation')
        before=copy.deepcopy(c);self.assertEqual(snapshot.checked(c)['status'],snapshot.UNVERIFIED);self.assertEqual(c,before)
    def test_synthesis_projection_and_both_rendered_outputs(self):
        from investigator import synthesis_narrative as narrative
        from investigator.evidence_synthesis import validate
        from investigator.onboarding import Conflict
        from test_synthesis_narrative import NarrativeContractTests
        for outcome in ('CONSISTENT_TO_BOUNDARY','TRANSFORMATION_LOGIC'):
            helper=NarrativeContractTests();state,payload=helper.source(outcome)
            original=next(o for o in state['observations'] if o['id']=='comparison')
            original['snapshot_attestation']=snapshot.comparison(original)
            state['assessment']['limits'].append(snapshot.limitation(original,1))
            entry=next(e for e in payload['evidence'] if e['id']=='comparison')
            entry.update(tool='process',result={'comparison_status':'CROSS_SURFACE_VERIFIED',
                'values_equal':original['values_equal'],'snapshot_attestation':copy.deepcopy(original['snapshot_attestation'])})
            _,outputs=narrative.assemble(narrative.Response(helper.response(payload)),payload,state)
            for key in ('business_output','technical_output'):
                self.assertEqual(outputs[key]['snapshot_attestations'][0]['status'],snapshot.UNVERIFIED)
            technical=outputs['technical_output']['explanation']['text']
            self.assertIn('agreement does not prove currency',technical)
            self.assertIn('timing was not excluded',technical)
            business=outputs['business_output']['explanation']['text']
            self.assertTrue(any(t in business for t in ('update timing','different update times')))
            self.assertNotIn('Comparison 1',business)
            for field in original['snapshot_attestation']:
                changed=copy.deepcopy(payload)
                next(e for e in changed['evidence'] if e['id']=='comparison')['result']['snapshot_attestation'].pop(field)
                with self.assertRaisesRegex(Conflict,'snapshot attestation'):
                    validate(copy.deepcopy(state['assessment']),changed,source_state=state)

    def test_inline_surface_report_and_identity_distinction(self):
        a=Adapter(['top','lower'],{'top':10,'lower':10})
        evaluate=a.evaluate
        def evaluate_with_snapshot(*args):
            p=evaluate(*args);r=report(p)
            r['identity_provenance']={'account':p.execution_surface['identity'],'execution_reader':True}
            return replace(p,evidence=dict(p.evidence,snapshot_identity=r))
        a.evaluate=evaluate_with_snapshot
        r=vertical(a,'measure',{});c=self.comparison(r)
        self.assertEqual(c['snapshot_attestation']['status'],snapshot.VERIFIED)
        wrong=copy.deepcopy(c['snapshot_attestation']['upper'])
        wrong['identity_provenance']['execution_reader']=False
        self.assertFalse(snapshot.bound(wrong,c['upper_evidence_id'],c['upper_execution_surface']))

    def test_optional_not_required(self):
        self.assertIn('snapshot_identity',OPTIONAL_CAPABILITIES);self.assertNotIn('snapshot_identity',REQUIRED_CAPABILITIES)
    def test_plain_business_limit_agreement_and_divergence(self):
        from investigator.business_vocabulary import validate_text
        for equal in (True,False):
            r=vertical(SnapshotAdapter('absent',equal),'measure',{});c=self.comparison(r)
            text=snapshot.business_limit({'evidence':[{'tool':'process','result':c}]})
            validate_text(text,text)
            self.assertIn('up to date' if equal else 'timing was not excluded',text)


class OptionalReaderTests(unittest.TestCase):
    def test_config_optional_separate_and_no_secret_fields(self):
        from metadata_config import ROOT,load_config
        config=json.loads((ROOT/'infra/metadata/development.json').read_text(encoding='utf-8-sig'))
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'config.json'
            def load():p.write_text(json.dumps(config));return load_config(p)
            self.assertNotIn('snapshot_identity_reader',load()['fabric'])
            config['fabric']['snapshot_identity_reader']={'account':'metadata@example.com','profile':'.local/snapshot-reader'}
            self.assertIn('snapshot_identity_reader',load()['fabric'])
            config['fabric']['sql_reader']={'account':'metadata@example.com','profile':'.local/sql-test','server':'host'}
            with self.assertRaisesRegex(ValueError,'distinct'):load()
            del config['fabric']['sql_reader'];config['fabric']['snapshot_identity_reader']['token']='secret'
            with self.assertRaises(ValueError):load()
    def config(self):
        return {'fabric':{'workspace_id':'workspace','auth':{'tenant_id':'tenant'},
                         'sql_reader':{'server':'host'},
                         'snapshot_identity_reader':{'account':'metadata@example.com','profile':'.local/snapshot-reader'}}}
    def probe(self):
        from investigator.process_debugging import Probe
        return Probe('OBSERVED','layer',{'id':'quantity-1'},execution_surface={'engine':'FABRIC_SQL','connection':'sql://host','object':'db'})
    def test_no_identity_fallback(self):
        import snapshot_identity_reader as reader
        with patch.object(reader,'session_status',return_value={'status':'SIGN_IN_REQUIRED'}),patch.object(reader,'cli') as cli:
            r=reader.read(self.config(),{'workspace':'workspace'},self.probe(),None)
        cli.assert_not_called();self.assertEqual(r['status'],'UNAVAILABLE');self.assertFalse(r['identity_provenance']['execution_reader'])
    def test_metadata_success_is_not_query_bound(self):
        import snapshot_identity_reader as reader
        import base64
        claims={'tid':'tenant','aud':'https://database.windows.net/','upn':'metadata@example.com','oid':'metadata-principal'}
        token='h.'+base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip('=')+'.s'
        run=Mock(return_value=Mock(stdout=json.dumps({'status':'SERVED','rows':[{'latest_log_version':2}]})))
        with patch.object(reader,'session_status',return_value={'status':'READY'}),patch.object(reader,'cli',return_value={'accessToken':token}):
            r=reader.read(self.config(),{'workspace':'workspace'},self.probe(),None,run=run)
        self.assertEqual(r['status'],'AVAILABLE');self.assertEqual(r['binding'],'METADATA_ONLY')
        self.assertEqual(r['identity_provenance']['token_identity'],'metadata@example.com')
        self.assertNotIn(token,json.dumps(r));run.assert_called_once()
        self.assertFalse(snapshot.bound(r,'quantity-1',self.probe().execution_surface))

if __name__=='__main__':unittest.main()
