"""Quoted values have a role; asking about a code cannot restrict the walk."""
import copy
import unittest
from unittest.mock import patch
from investigator.question_intake import azure_resolve, wire_contract
from investigator import value_roles


class ValueRoleTests(unittest.TestCase):
    def extract(self, ticket, roles, kind='FIGURE_DIFFERENCE', filters=None):
        payload={'text':ticket,'models':[{'id':'model','measures':[{'id':'measure','name':'Revenue'}],
                    'columns':[{'column_id':'region','name':'Region'}]}]}
        response={'value_mentions':[{'role':role,'source':{'quote':quote}} for role,quote in roles],
            'question_kind':{'kind':kind,'source':{'quote':ticket}},'action':'PROPOSE',
            'model_id':'m0','measure_id':'m0v0','metric_quote':'Revenue','question':None,
            'report_quote':None,'target_request':None,'reported_candidates':[],
            'triage':'BUSINESS_QUESTION:NONE' if kind=='BUSINESS_MEANING' else 'MISMATCH_COMPLAINT:VERTICAL',
            'filters':filters or [],'dimension_ids':[]}
        with patch('ticket_planner.azure_generate',return_value=(response,{})):
            return azure_resolve(payload)[0]

    def test_explicit_selection_can_enter_scope(self):
        result=self.extract('Revenue: I selected North.', [('SELECTION','North')],
            filters=[{'column_id':'m0c0','operator':'in','values':['North'],'quote':'North'}])
        self.assertEqual(result['filters'][0]['values'],['North'])
        self.assertEqual(result['value_mentions'][0]['role'],'SELECTION')

    def test_business_subject_is_preserved_and_scope_is_empty(self):
        result=self.extract('What does Q49 mean for Revenue?', [('SUBJECT','Q49')], 'BUSINESS_MEANING')
        self.assertEqual(result['filters'],[])
        self.assertEqual(result['dimension_ids'],[])
        self.assertEqual(result['value_mentions'][0]['source']['quote'],'Q49')

    def test_mixed_ticket_preserves_both_roles_without_business_scope(self):
        result=self.extract('Revenue: I selected North; what does Q49 mean?',
                            [('SELECTION','North'),('SUBJECT','Q49')], 'BUSINESS_MEANING')
        self.assertEqual([r['role'] for r in result['value_mentions']],['SELECTION','SUBJECT'])
        self.assertEqual(result['filters'],[])

    def test_mixed_comparison_scopes_only_the_selected_value(self):
        result=self.extract('Revenue: I selected North; Q49 is a code I want explained.',
                            [('SELECTION','North'),('SUBJECT','Q49')], filters=[
                            {'column_id':'m0c0','operator':'in','values':['North'],'quote':'North'}])
        self.assertEqual(result['filters'][0]['values'],['North'])
        self.assertEqual(len(result['filters']),1)

    def test_subject_and_incidental_mention_cannot_supply_filter(self):
        for role in ('SUBJECT','MENTION'):
            with self.subTest(role=role),self.assertRaisesRegex(ValueError,'Only a quoted SELECTION'):
                self.extract('Revenue for North.',[(role,'North')],filters=[
                    {'column_id':'m0c0','operator':'in','values':['North'],'quote':'North'}])

    def test_business_meaning_rejects_even_a_declared_selection_filter(self):
        with self.assertRaisesRegex(ValueError,'Business-meaning subjects'):
            self.extract('Revenue: I selected North; what does Q49 mean?',
                [('SELECTION','North'),('SUBJECT','Q49')], 'BUSINESS_MEANING',
                [{'column_id':'m0c0','operator':'in','values':['North'],'quote':'North'}])

    def test_schema_and_consumer_share_closed_vocabulary(self):
        _,schema,_=wire_contract({'text':'Revenue','models':[]})
        self.assertIn('value_mentions',schema['required'])
        self.assertEqual(schema['properties']['value_mentions']['items']['properties']['role']['enum'],list(value_roles.ROLES))
        source={'start':0,'end':3,'quote':'Q49'}
        for entries in ([{'role':'FILTER','source':source}],
                        [{'role':'SUBJECT','source':source},{'role':'SELECTION','source':source}]):
            with self.assertRaises(ValueError):value_roles.validate(copy.deepcopy(entries),'Q49')

    def test_repeated_same_role_does_not_create_a_conflicting_value_role(self):
        result=self.extract('What does Q49 mean for Revenue?',
                            [('SUBJECT','Q49'),('SUBJECT','Q49')], 'BUSINESS_MEANING')
        self.assertEqual(result['filters'],[])



if __name__=='__main__':unittest.main()
