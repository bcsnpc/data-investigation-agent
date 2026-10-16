import copy
import unittest
from investigator import intake_vocabulary, intake_extraction
from investigator.intake_name_resolution import resolve
from investigator.ticket_clarification import settings, DEFAULTS
from investigator.onboarding import digest


class IntakeVocabularyTests(unittest.TestCase):
    def setUp(self):
        self.models=[{'id':'m','measures':[{'id':'q','name':'Handled quantity','aliases':['Existing synonym']}],
                     'columns':[{'column_id':'c','name':'Location'}]}]
        self.config=copy.deepcopy(DEFAULTS)
        self.config['vocabulary_aliases']=[{'alias':'Work amount','canonical':'Handled quantity'},
                                           {'alias':'Site','canonical':'Location'}]

    def test_declared_aliases_resolve_both_member_kinds_with_provenance(self):
        models=intake_vocabulary.apply(self.models,settings(self.config))
        self.assertEqual(resolve('Work amount',models[0]['measures'],'id')['id'],'q')
        self.assertEqual(resolve('Site',models[0]['columns'],'column_id')['column_id'],'c')
        self.assertEqual(models[0]['measures'][0]['estate_vocabulary']['provenance'],'DECLARED_BY_CONFIGURATION')
        self.assertEqual(models[0]['measures'][0]['aliases'],['Existing synonym','Work amount'])

    def test_configuration_and_original_catalog_are_unchanged(self):
        original=copy.deepcopy(self.models);config=copy.deepcopy(self.config)
        result=intake_vocabulary.apply(self.models,self.config)
        self.assertEqual(self.models,original);self.assertEqual(self.config,config)
        for key,identity in (('measures','id'),('columns','column_id')):
            self.assertEqual([m[identity] for m in result[0][key]],
                             [m[identity] for m in original[0][key]])

    def test_no_declarations_preserve_catalog_bytes(self):
        self.assertEqual(digest(intake_vocabulary.apply(self.models,DEFAULTS)),digest(self.models))

    def test_alias_never_breaks_duplicate_canonical_binding_tie(self):
        self.models[0]['measures'].append({'id':'other','name':'Handled quantity'})
        models=intake_vocabulary.apply(self.models,self.config)
        with self.assertRaisesRegex(ValueError,'Ambiguous declared name'):
            resolve('Work amount',models[0]['measures'],'id')

    def test_canonical_must_be_declared_exactly_not_fuzzily(self):
        self.config['vocabulary_aliases']=[{'alias':'Work amount','canonical':'quantity'}]
        self.assertEqual(intake_vocabulary.apply(self.models,self.config),self.models)

    def test_duplicate_operator_aliases_are_refused(self):
        self.config['vocabulary_aliases'].append({'alias':'WORK AMOUNT','canonical':'Location'})
        with self.assertRaisesRegex(ValueError,'Duplicate estate vocabulary alias'):settings(self.config)

    def test_aliases_reach_model_names_without_rewriting_ticket(self):
        models=intake_vocabulary.apply(self.models,self.config)
        wire=intake_extraction.wire({'text':'Why is Work amount high?','models':models})
        self.assertEqual(wire['ticket'],'Why is Work amount high?')
        self.assertIn('Work amount',wire['names']);self.assertIn('Site',wire['names'])

    def test_aliases_consume_existing_name_bound_without_truncation(self):
        self.config['vocabulary_aliases']=[{'alias':'x'*4001,'canonical':'Handled quantity'}]
        models=intake_vocabulary.apply(self.models,self.config)
        with self.assertRaisesRegex(ValueError,'INTAKE_NAME_LIST_OVERSIZE'):
            intake_extraction.wire({'text':'Question','models':models})

    def test_declared_alias_reaches_original_scope_consumer_with_exact_ticket_span(self):
        from test_intake_extraction import fixture
        from investigator.question_intake import validate
        raw,payload=fixture('In Report, Global card Work amount shows 16 and looks wrong.',
            measures=[{'quote':'Work amount','role':'PRIMARY'}],
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}],
            figures=[{'quote':'16','role':'PRIMARY','state':'NUMBER','precision_quote':None}])
        config=copy.deepcopy(DEFAULTS)
        config['vocabulary_aliases']=[{'alias':'Work amount','canonical':'Quantity'}]
        payload['models']=intake_vocabulary.apply(payload['models'],config)
        proposal=intake_extraction.resolve(raw,payload)
        validate(proposal,payload)
        self.assertEqual(proposal['measure_id'],'measure')
        self.assertEqual(proposal['metric_quote'],'Work amount')
        self.assertEqual(proposal['target_visual']['target_id'],'card')
        self.assertEqual(proposal['extracted_ticket']['response'],raw)

    def test_real_workspace_snapshot_uses_its_estate_configuration(self):
        import test_investigator_workspace as fixtures
        from investigator.question_intake import snapshot
        harness=fixtures.WorkspaceTests();harness.setUp();self.addCleanup(harness.doCleanups)
        workspace=harness.workspace
        original=snapshot(workspace)
        canonical=original['models'][0]['measures'][0]['name']
        config=copy.deepcopy(DEFAULTS)
        config['vocabulary_aliases']=[{'alias':'Estate synonym','canonical':canonical}]
        workspace.intake_configuration=config
        current=snapshot(workspace)
        self.assertIn('Estate synonym',current['models'][0]['measures'][0]['aliases'])
        self.assertNotEqual(digest(current),digest(original))
        workspace.intake_configuration=None
        self.assertEqual(snapshot(workspace),original)


if __name__=='__main__':unittest.main()
