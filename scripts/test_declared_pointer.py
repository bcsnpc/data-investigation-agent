import unittest
from investigator.declared_pointer import resolve


class DeclaredPointerTests(unittest.TestCase):
    def assets(self):
        return [
          {'id':'scope-a','parent_id':None,'kind':'Container','name':'A','availability':'CURRENT'},
          {'id':'scope-b','parent_id':None,'kind':'Container','name':'B','availability':'CURRENT'},
          {'id':'a/table','parent_id':'scope-a','kind':'Table','name':'dbo.events','availability':'CURRENT'},
          {'id':'b/table','parent_id':'scope-b','kind':'Table','name':'dbo.events','availability':'CURRENT'}]

    def test_same_name_outside_declared_scope_is_ignored(self):
        result=resolve(self.assets(),{'scope_ids':['scope-a'],'target_labels':['dbo.events'],'target_kinds':['Table']})
        self.assertEqual(result['status'],'RESOLVED');self.assertEqual(result['asset']['id'],'a/table')

    def test_ambiguity_names_every_in_scope_candidate_and_selects_none(self):
        assets=self.assets()+[{'id':'a/other','parent_id':'scope-a','kind':'Table','name':'DBO.EVENTS','availability':'CURRENT'}]
        result=resolve(assets,{'scope_ids':['scope-a'],'target_labels':['dbo.events'],'target_kinds':['Table']})
        self.assertEqual(result['status'],'AMBIGUOUS');self.assertNotIn('asset',result)
        self.assertEqual([x['id'] for x in result['candidates']],['a/other','a/table'])

    def test_missing_scope_never_falls_back_to_global_name_search(self):
        result=resolve(self.assets(),{'scope_ids':['absent'],'target_labels':['dbo.events'],'target_kinds':['Table']})
        self.assertEqual(result['status'],'SCOPE_NOT_DISCOVERED');self.assertEqual(result['candidates'],[])

    def test_no_exact_in_scope_target_is_unresolved(self):
        result=resolve(self.assets(),{'scope_ids':['scope-a'],'target_labels':['dbo.missing'],'target_kinds':['Table']})
        self.assertEqual(result['status'],'NO_MATCH_IN_SCOPE');self.assertEqual(result['candidates'],[])

    def test_resolution_carries_definition_provenance(self):
        result=resolve(self.assets(),{'scope_ids':['scope-a'],'target_labels':['dbo.events'],
            'target_kinds':['Table'],'definition_asset_id':'definition','definition_offset':42,
            'declared_connection_asset_id':'connection'})
        self.assertEqual(result['provenance'],'DECLARED_BY_DEFINITION')
        self.assertEqual(result['definition_asset_id'],'definition')
        self.assertEqual(result['definition_offset'],42)
        self.assertEqual(result['declared_connection_asset_id'],'connection')

    def test_parent_only_scope_is_an_explicit_scope(self):
        assets=[{'id':'table','parent_id':'scope-a','kind':'Table','name':'dbo.events','availability':'CURRENT'}]
        result=resolve(assets,{'scope_ids':['scope-a'],'target_labels':['dbo.events'],'target_kinds':['Table']})
        self.assertEqual(result['status'],'RESOLVED');self.assertEqual(result['asset']['id'],'table')

    def test_denied_scope_is_distinct_from_absence(self):
        result=resolve(self.assets(),{'scope_ids':['scope-a'],'denied_scope_ids':['scope-a'],
            'target_labels':['dbo.events'],'target_kinds':['Table']})
        self.assertEqual(result['status'],'ACCESS_DENIED');self.assertEqual(result['candidates'],[])

if __name__=='__main__':unittest.main()
