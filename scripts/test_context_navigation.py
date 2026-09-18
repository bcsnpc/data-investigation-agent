"""Bounded definition navigation, with unrelated names and untrusted content."""
import unittest
from unittest.mock import patch
from investigator import context_search


class ContextNavigationTests(unittest.TestCase):
    def test_definition_handles_decode_content_parameters_exactly(self):
        from investigator.dynamic_reasoning import wire_contract,from_wire
        payload={'candidates':[],'hypotheses':[],'observations':[{'id':'receipt','tool':'context','status':'COMPLETED',
                 'metadata':{'children':[{'id':'part:random','name':'source.py','kind':'DefinitionPart'}]}}]}
        wire,schema,handles=wire_contract(payload)
        action=from_wire({'next':{'kind':'LOOKUP','operation':'content','value':'a0','offset':6000},'hypotheses':[]},handles)
        self.assertEqual(action['lookup'],{'operation':'content','value':'part:random','offset':6000})
        operations=[v['properties'].get('operation',{}).get('enum',[]) for v in schema['properties']['next']['anyOf']]
        self.assertIn(['content'],operations);self.assertIn(['find'],operations)

    def context(self):
        self.parent={'id':'item:random','name':'Orchid','kind':'Notebook','parent_id':'workspace',
                     'metadata':{},'availability':'CURRENT','coverage_scope':'surface','provenance':'DISCOVERED'}
        self.part={'id':'part:random','name':'source.py','kind':'DefinitionPart','parent_id':'item:random',
                   'metadata':{'path':'source.py','content':'a'*7000+'NEEDLE'+ 'b'*7000},
                   'availability':'CURRENT','coverage_scope':'surface','provenance':'DISCOVERED'}
        return {'version':'v1','assets':[self.parent,self.part],
                'graph':{'edges':[]},'coverage':{'surface':{'status':'COMPLETE'}}}

    def test_definition_children_are_labelled_without_expanding_content(self):
        with patch.object(context_search,'latest',return_value=self.context()):
            result=context_search.get_asset(None,'item:random')
        self.assertEqual(result['children'][0]['id'],'part:random')
        self.assertEqual(result['children'][0]['kind'],'DefinitionPart')
        self.assertNotIn('metadata',result['children'][0])

    def test_content_pages_expose_omission_and_resume_exactly(self):
        with patch.object(context_search,'latest',return_value=self.context()):
            first=context_search.read_content(None,'part:random',offset=0)
            second=context_search.read_content(None,'part:random',offset=first['next_offset'])
            last=context_search.read_content(None,'part:random',offset=14000)
        self.assertTrue(first['truncated'])
        self.assertEqual(first['content']+second['content'],self.part['metadata']['content'][:12000])
        self.assertEqual(second['offset'],6000)
        self.assertTrue(last['truncated'])
        self.assertIsNone(last['next_offset'])

    def test_literal_find_is_bounded_and_does_not_execute_content(self):
        with patch.object(context_search,'latest',return_value=self.context()):
            result=context_search.find_content(None,'part:random','NEEDLE')
            self.assertEqual(result['matches'][0]['offset'],7000)
            self.assertLess(len(result['matches'][0]['excerpt']),1000)
            missing=context_search.find_content(None,'part:random','ignore all previous instructions')
            self.assertEqual(missing['matches'],[])

    def test_unknown_removed_and_non_text_targets_fail_closed(self):
        context=self.context()
        with patch.object(context_search,'latest',return_value=context):
            with self.assertRaises(KeyError):context_search.read_content(None,'other',offset=0)
            with self.assertRaises(ValueError):context_search.read_content(None,'item:random',offset=0)
            self.part['availability']='REMOVED'
            with self.assertRaises(ValueError):context_search.read_content(None,'part:random',offset=0)

    def test_unicode_content_retains_structured_pagination(self):
        from investigator.onboarding import encoded
        context=self.context();self.part['metadata']['content']='\u4e00'*14000
        with patch.object(context_search,'latest',return_value=context):
            result=context_search.read_content(None,'part:random',offset=0)
        self.assertLessEqual(len(encoded(result)),11000)
        self.assertEqual(result['next_offset'],len(result['content']))


if __name__=='__main__':unittest.main()
