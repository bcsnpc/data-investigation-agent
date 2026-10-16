"""Literal cropped labels are useful evidence; missing pixels remain unknown."""
import copy,unittest
from investigator.claim_screenshots import rank,partial_label

def page(identity,anchors):
 return {'candidate_id':identity,'names':{'report':'Report '+identity,'page':'Overview '+identity},'anchors':anchors}
def ocr(*lines):
 return {'lines':[{'text':text,'region':{'x':0,'y':n*30,'width':200,'height':20}}for n,text in enumerate(lines)]}

class Tests(unittest.TestCase):
 def test_unique_literal_partial_label_identifies_candidate_with_region(self):
  pages=[page('one',['Top Accounts by Invoice Value']),page('two',['Recent Collections'])]
  got=rank(ocr('Accounts by Invoice'),pages)
  self.assertEqual([p['candidate_id']for p in got],['one'])
  match=got[0]['matched_fragments'][0];self.assertEqual(match['kind'],'PARTIAL_LABEL')
  self.assertEqual(match['fragment'],'Accounts by Invoice');self.assertEqual(match['region']['height'],20)
 def test_shared_fragment_stays_tied(self):
  got=rank(ocr('Collected Amount'),[page('one',['Collected Amount by Region']),page('two',['Collected Amount by Plan'])])
  self.assertEqual(len(got),2);self.assertEqual(got[0]['score'],got[1]['score'])
 def test_short_exact_label_does_not_beat_compatible_longer_label(self):
  got=rank(ocr('Sales Total'),[page('one',['Sales Total']),page('two',['Gross Sales Total'])])
  self.assertEqual(len(got),2);self.assertEqual(got[0]['score'],got[1]['score'])
 def test_many_possible_anchors_do_not_multiply_one_fragment(self):
  got=rank(ocr('Collected Amount'),[page('one',['Collected Amount by Region','Collected Amount by Plan']),page('two',['Collected Amount by Date'])])
  self.assertEqual(got[0]['score'],got[1]['score'])
 def test_single_generic_word_and_unassociated_numbers_cannot_identify(self):
  pages=[dict(page('one',['Net Revenue']),expected_values=[950]),dict(page('two',['Collected Revenue']),expected_values=[550])]
  self.assertEqual(rank(ocr('950','Revenue'),pages),[])
 def test_numeric_literal_only_matches_when_it_is_in_retained_label(self):
  pages=[page('one',['Revenue target for 2024']),page('two',['Revenue target for 2025'])]
  got=rank(ocr('Revenue target for 2024'),pages)
  self.assertEqual([p['candidate_id']for p in got],['one'])
  self.assertEqual(rank(ocr('2024'),pages),[])
 def test_words_from_separate_regions_are_not_joined_into_partial_label(self):
  pages=[page('one',['Net Revenue Forecast for Plans'])]
  self.assertEqual(rank(ocr('Net','Revenue'),pages),[])
 def test_label_matching_does_not_edit_catalog_or_ocr(self):
  pages=[page('one',['Top Accounts by Invoice Value'])];pixels=ocr('Accounts by Invoice');before=copy.deepcopy((pages,pixels))
  rank(pixels,pages);self.assertEqual((pages,pixels),before)

if __name__=='__main__':unittest.main()
