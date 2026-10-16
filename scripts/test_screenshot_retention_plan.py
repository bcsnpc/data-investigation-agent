import copy
import hashlib
import unittest
from screenshot_retention_plan import plan


class Tests(unittest.TestCase):
    def test_default_and_override_are_disjoint_and_unrelated_rules_stay_exact(self):
        original={'rules':[{'name':'old','type':'Lifecycle','enabled':True,'definition':{
            'filters':{'blobTypes':['blockBlob'],'prefixMatch':['archive/']},
            'actions':{'baseBlob':{'delete':{'daysAfterModificationGreaterThan':300}}}}}]}
        before=copy.deepcopy(original);result=plan(original,{'one':30,'two':7})
        self.assertEqual(original,before);self.assertEqual(result['rules'][0],before['rules'][0])
        for estate,days in [('one',30),('two',7)]:
            prefix='screenshots/images/'+hashlib.sha256(estate.encode()).hexdigest()+'/'
            rule=next(r for r in result['rules']if prefix in r['definition']['filters']['prefixMatch'])
            self.assertEqual(rule['definition']['actions'],{'baseBlob':{'delete':{'daysAfterCreationGreaterThan':days}}})
        self.assertEqual(result,plan(result,{'one':30,'two':7}))
        changed=plan(result,{'two':14})
        self.assertEqual(changed['rules'][0],before['rules'][0])

    def test_overlapping_existing_deletion_rule_is_not_silently_replaced(self):
        for prefixes in ([],['screenshots/']):
            current={'rules':[{'name':'broad','enabled':True,'definition':{'filters':{'prefixMatch':prefixes},'actions':{'baseBlob':{'delete':{'daysAfterModificationGreaterThan':1}}}}}]}
            with self.assertRaisesRegex(ValueError,'OVERLAPS'):plan(current,{'one':30})

    def test_bad_retention_and_owned_name_collision_refuse(self):
        for days in (0,False,36600,'30'):
            with self.assertRaises(ValueError):plan({'rules':[]},{'one':days})
        current=plan({'rules':[]},{'one':30});current['rules'][0]['definition']['filters']['prefixMatch']=['archive/']
        with self.assertRaisesRegex(ValueError,'COLLISION'):plan(current,{'one':30})


if __name__=='__main__':unittest.main()
