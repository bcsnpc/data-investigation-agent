from copy import deepcopy
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from investigator.explain_questions import ask,load,main
from investigator.adapters.explain_history import HistoryPort
from investigator.estate_graph_api import GraphAPI
from investigator.estate_graph_repository import GraphRepository
from investigator.live_gateway import Gateway,GatewayDenied
from investigator.shared_state import SharedState
from investigator.process_debugging import Probe
from test_estate_graph import graph,proof,T0,T1


class ExplainTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.state=SharedState.offline(Path(self.temp.name)/'state.sqlite')
        self.repo=GraphRepository(self.state);self.repo.migrate()
        value=graph()
        value['nodes'][2]['properties']['definition']='visual references Units'
        value['nodes'][3]['properties']['definition']='SUM(Activity[units])'
        value['nodes'][4]['properties'].update(definition='source value',system_of_record=True)
        self.repo.replace(value)
        self.ids=['report','page','visual','measure','column']
        self.gateway=Gateway({'version':1,'live_enabled':False,'identities':{'reader':{'graph':{'estate':self.ids}}}})

    def api(self,allowed=None,at=None):
        return GraphAPI(self.repo,self.gateway,identity='reader',estate='estate',allowed_objects=allowed or self.ids,at=at)

    def test_calculation_walk_cites_exact_definition_and_missing_enrichment(self):
        result=ask('How is Quantity calculated?',self.api(),now=T1)
        self.assertEqual(result['kind'],'CALCULATION_EXPLANATION')
        self.assertEqual(result['status'],'PARTIAL')
        steps=result['technical_evidence']['steps']
        self.assertEqual([s['node'] for s in steps],['visual','measure','column'])
        self.assertEqual(steps[1]['definition']['definition'],'SUM(Activity[units])')
        self.assertEqual(steps[1]['provenance'],proof())
        self.assertIn('As of',result['business_answer'])
        self.assertIn('No current enriched',result['coverage_gaps'][0]['reason'])

    def test_measure_is_a_valid_start_without_becoming_a_visual(self):
        result=ask('How is Units calculated?',self.api(),now=T1)
        self.assertEqual(result['subject'],'measure')
        self.assertEqual([s['node'] for s in result['technical_evidence']['steps']],['measure','column'])

    def test_no_whole_catalog_read_or_unrelated_history_for_explanation(self):
        actual=self.repo.records
        def scoped(*args,**kwargs):
            self.assertIsNotNone(kwargs.get('identities'))
            return actual(*args,**kwargs)
        with patch.object(self.repo,'records',side_effect=scoped):
            result=ask('How is Quantity calculated?',self.api(allowed=['visual','measure','column']),now=T1)
        self.assertEqual(result['subject'],'visual')

    def test_admitted_path_does_not_follow_unauthorized_neighbor(self):
        result=ask('How is Quantity calculated?',self.api(['visual']),now=T1)
        self.assertEqual([s['node'] for s in result['technical_evidence']['steps']],['visual'])
        self.assertTrue(any('outside' in gap['reason'] for gap in result['coverage_gaps']))
        with self.assertRaises(GatewayDenied):self.api().calculation_path('secret-other-node')

    def test_inferred_links_and_prose_are_never_reported_as_verified(self):
        value=graph();value['edges'][2].update(confidence='INFERRED',base_confidence='INFERRED')
        value.update(definition_hash='b'*64,observed_at=T1)
        value['edges'][2]['provenance']['source']='MODEL_PROPOSAL'
        self.repo.replace(value)
        enrichment=[{'subject':'visual','definition_hash':'a'*64,'status':'INFERRED',
                     'calculation_explanation':'Shows the units measure.','synonyms':['shown quantity']}]
        result=ask('How is shown quantity calculated?',self.api(),enrichment=enrichment,now=T1)
        self.assertIn('Inferred explanation',result['business_answer'])
        self.assertIn('inferred links',result['business_answer'])
        self.assertEqual(result['technical_evidence']['inferred_links'][0]['id'],'vm')

    def test_stale_or_stub_enrichment_does_not_supply_an_explanation_or_alias(self):
        for invalid in ({'definition_hash':'b'*64},{'stale_definition':True},{'recording_class':'RECORDED_STUB'}):
            with self.subTest(invalid=invalid):
                entry={'subject':'visual','definition_hash':'a'*64,'status':'INFERRED','calculation_explanation':'Stale description','synonyms':['special label'],**invalid}
                result=ask('How is Quantity calculated?',self.api(),enrichment=[entry],now=T1)
                self.assertNotIn('Stale description',result['business_answer'])

    def test_history_does_not_guess_actor_from_owner_or_graph_scan(self):
        result=ask('Who changed Units?',self.api(),now=T1)
        self.assertEqual(result['kind'],'CHANGE_HISTORY');self.assertEqual(result['status'],'PARTIAL')
        self.assertIn('not established',result['business_answer']);self.assertIn('reason was not recorded',result['business_answer'])
        self.assertNotIn('owner at',result['business_answer'])

    def test_modified_metadata_has_attribution_and_no_invented_reason(self):
        value=graph();value['nodes'][3]['properties']['observed_metadata']={
            'modified_at':T0,'modified_by':'Recorded user','provenance':{'evidence_id':'item-observation','source':'item metadata'}}
        value.update(definition_hash='b'*64,observed_at=T1)
        self.repo.replace(value)
        result=ask('Who changed Units?',self.api(),now=T1)
        self.assertIn('Recorded user',result['business_answer'])
        self.assertIn('reason was not recorded',result['business_answer'])
        self.assertIn('does not identify which calculation changed',result['business_answer'])
        self.assertEqual(result['technical_evidence']['observations'][0]['source'],'ITEM_METADATA')

    def test_activity_and_git_are_explicit_subject_bound_ports(self):
        called=[]
        def activity(subject):
            called.append(subject)
            return [{'subject':subject,'source':'FABRIC_ACTIVITY','actor':'Observed actor','at':T0,
                     'reason':None,'provenance':{'evidence_id':'activity-1'}}]
        def git(subject):
            return [{'subject':subject,'source':'GIT','actor':'Commit author','at':T0,
                     'reason':'Commit message','provenance':{'commit':'sealed-commit'}}]
        result=ask('Who changed Units?',self.api(),now=T1,history_port=HistoryPort(activity=activity,git=git))
        self.assertEqual(called,['measure']);self.assertIn('Commit message',result['business_answer'])
        self.assertIn('Observed actor',result['business_answer'])
        self.assertEqual(len(result['technical_evidence']['observations']),2)

    def test_history_after_as_of_is_excluded(self):
        def activity(subject):
            return [{'subject':subject,'source':'FABRIC_ACTIVITY','actor':'Future actor','at':T1,
                     'reason':None,'provenance':{'evidence_id':'future'}}]
        result=ask('Who changed Units?',self.api(at=T0),now=T1,history_port=HistoryPort(activity=activity))
        self.assertNotIn('Future actor',result['business_answer'])
        self.assertEqual(result['technical_evidence']['observations'],[])

    def test_only_typed_surface_checked_existing_values_are_included(self):
        def value(subject):
            return Probe('OBSERVED','L0',evidence={'id':'query-'+subject},value=None,
                         execution_surface={'identity':'reader','object':'model'},
                         surface_report={'identity':'reader','object':'model'},surface_reportable=('object',),
                         surface_report_binding='VALUE_QUERY')
        result=ask('How is Quantity calculated?',self.api(),now=T1,value_lookup=value)
        observed=result['technical_evidence']['steps'][0]['value']
        self.assertEqual(observed['value_state'],'BLANK');self.assertIsNone(observed['value'])
        refused=ask('How is Quantity calculated?',self.api(),now=T1,value_lookup=lambda _: {'attested':True,'value':0})
        self.assertIsNone(refused['technical_evidence']['steps'][0]['value'])

    def test_unknown_or_conflicting_subject_stays_held(self):
        self.assertEqual(ask('How is Unknown calculated?',self.api(),now=T1)['reason'],'QUESTION_SUBJECT_UNRESOLVED')
        self.assertEqual(ask('How is Quantity calculated?',self.api(),subject='measure',now=T1)['reason'],'QUESTION_AND_BOUND_TARGET_DIFFER')
        self.assertEqual(ask('How are Quantity and Units calculated?',self.api(),now=T1)['reason'],'TIED_CATALOG_CANDIDATES')

    def test_cli_requires_explicit_shared_state_and_no_owner_fallback(self):
        import json
        path=Path(self.temp.name)/'ask.json'
        path.write_text(json.dumps({'version':'dia-graph-ask-v1','estate':'estate','identity':'reader','allowed_objects':['visual']}))
        with patch('investigator.shared_state.configured_state',return_value=None),patch('subprocess.run') as run:
            with self.assertRaisesRegex(ValueError,'CONFIGURED_SHARED_STATE_REQUIRED'):
                main(SimpleNamespace(estate=path,question='How is Quantity calculated?'))
            run.assert_not_called()
        path.write_text(json.dumps({'version':'dia-graph-ask-v1','estate':'estate','identity':'reader','allowed_objects':['visual'],'subject':'measure'}))
        with self.assertRaisesRegex(ValueError,'SUBJECT_OUTSIDE'):load(path)

    def test_dia_ask_dispatches_only_the_typed_explanation_entry(self):
        from dia import main as cli
        with patch('investigator.explain_questions.main',return_value=0) as invoke:
            self.assertEqual(cli(['ask','How is Quantity calculated?','--estate','approved.json']),0)
        args=invoke.call_args.args[0]
        self.assertEqual(args.question,'How is Quantity calculated?')
        self.assertEqual(str(args.estate),'approved.json')


if __name__=='__main__':unittest.main()
