import unittest
from investigator.transformation_judgment import validate


class TransformationJudgmentTests(unittest.TestCase):
    def test_three_bounded_judgments_map_without_deciding_intent(self):
        for label,expected in [('EXPLAINS',True),('DOES_NOT_EXPLAIN',False),('INDETERMINATE',None)]:
            with self.subTest(label=label):
                result=validate({'judgment':label,'explanation':'The retrieved definition was assessed.',
                                 'limitation':'Business intent remains unknown.'})
                self.assertIs(result['explains'],expected);self.assertEqual(result['status'],'COMPLETED')

    def test_unbounded_or_unknown_output_is_rejected(self):
        with self.assertRaises(ValueError):validate({'judgment':'CORRECT','explanation':'x','limitation':'x'})
        with self.assertRaises(ValueError):validate({'judgment':'EXPLAINS','explanation':'x'*701,'limitation':'x'})

if __name__=='__main__':unittest.main()
