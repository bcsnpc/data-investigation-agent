import copy
import unittest
from investigator.adapters.microsoft_process import MicrosoftProcessAdapter
from investigator.process_debugging import attest, _answer, IDENTITY_REPORTING_WARNING
from investigator.surface_difference import grade, UNESTABLISHED

class NativeTenantIdentityWarningTests(unittest.TestCase):
    def probe(self,**changes):
        reader={'mode':'federated_reader','tenant_id':'tenant','principal_id':'principal','account':'reader'}
        adapter=MicrosoftProcessAdapter(None,{'fabric':{'native_reader':reader}},None,None,None)
        identity={**reader,'workspace_id':'workspace','model_id':'model'}
        body={'execution_identity':identity,'surface_report':{'identity':' tenant'}}
        for key,value in changes.items():
            if key=='identity':body['execution_identity']=value
            elif key=='report':body['surface_report']=value
        return adapter._semantic_probe({'status':'COMPLETED','result':body},'OBSERVED','semantic',
            evidence={'id':'quantity','tool':'bounded_dax'},value={'quantity':'8765'},
            execution_surface={'identity':'reader','connection':'workspace','object':'model','engine':'OLAP Server'},
            surface_report=body['surface_report'],surface_reportable=('identity',),surface_report_binding='VALUE_QUERY')
    def test_tenant_only_native_identity_is_warning_not_unavailable_or_false_match(self):
        probe=attest(self.probe())
        self.assertEqual(probe.status,'OBSERVED')
        self.assertEqual(probe.value,{'quantity':'8765'})
        self.assertEqual(probe.evidence['surface_report'],{'identity':' tenant'})
        self.assertEqual(probe.evidence['surface_attestation']['consistency'],'CONTRADICTED')
        self.assertEqual(probe.evidence['attestation_warning'],IDENTITY_REPORTING_WARNING)
        self.assertEqual(grade(probe.evidence,probe.evidence)['grade'],UNESTABLISHED)
        result=_answer('TRANSFORMATION_LOGIC',4,[probe.evidence],'refined')
        self.assertIn(IDENTITY_REPORTING_WARNING,result['limits'])
    def test_other_principal_or_object_mismatch_and_missing_transport_do_not_get_exception(self):
        for changes in ({'report':{'identity':'administrator'}},{'identity':{}},
                        {'report':{'identity':' tenant','object':'wrong-database'}}):
            with self.subTest(changes=changes):
                probe=attest(self.probe(**changes))
                self.assertEqual(probe.status,'UNAVAILABLE')
                self.assertNotIn('attestation_warning',probe.evidence)
    def test_warning_does_not_stop_walk_to_independently_attested_divergence(self):
        from test_process_debugging import Adapter
        from investigator.process_debugging import vertical
        original=self.probe()
        class Estate(Adapter):
            def evaluate(self,layer,measure,scope):
                if layer['id']=='semantic':return original
                return super().evaluate(layer,measure,scope)
        adapter=Estate(['semantic','gold','refined'],
            {'semantic':{'quantity':'8765'},'gold':{'quantity':'8765'},'refined':{'quantity':'7661'}},explain=True)
        result=vertical(adapter,'measure',{})
        self.assertEqual(result['classification'],'TRANSFORMATION_LOGIC')
        self.assertIn(IDENTITY_REPORTING_WARNING,result['limits'])
        self.assertEqual(adapter.evaluated,['gold','refined'])
    def test_warning_is_rendered_in_both_outputs_without_model_caveats(self):
        from test_synthesis_narrative import NarrativeContractTests
        from investigator.synthesis_narrative import assemble
        state,payload=NarrativeContractTests().source('TRANSFORMATION_LOGIC')
        state['assessment']['limits'].append(IDENTITY_REPORTING_WARNING)
        assessment,outputs=assemble(None,payload,state)
        for key in ('business_output','technical_output'):
            self.assertIn(IDENTITY_REPORTING_WARNING,str(outputs[key]))

if __name__=='__main__':unittest.main()
