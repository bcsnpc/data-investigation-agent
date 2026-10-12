import base64,json
import unittest
from unittest.mock import Mock,patch
from investigator.claim_screenshots import ClaimScreenshots,rank
from investigator.onboarding import Conflict
from investigator.local_screenshot_ocr import validate
from test_screenshot_intake import image_bytes
import test_investigator_workspace as fixture

def ocr(*texts):
    return {'engine':'Windows.Media.Ocr','language':'en-US','width':1000,'height':500,'lines':[
        {'text':t,'region':{'x':10,'y':10+i*30,'width':500,'height':25},'words':[]} for i,t in enumerate(texts)]}
def page(identity='a',anchor='Revenue'):
    return {'candidate_id':identity,'model_id':'m','report_id':'r'+identity,'page_id':'p'+identity,'label':'Billing / '+identity,
            'names':{'report':'Billing','page':'Overview'},'anchors':[anchor],'definition_hash':'h'+identity,
            'targets':[{'target_id':'v'+identity,'labels':[anchor]}]}

class Tests(unittest.TestCase):
    def setUp(self):
        self.h=fixture.WorkspaceTests();self.h.setUp();self.addCleanup(self.h.doCleanups)
        self.w=self.h.workspace;self.w.claim_screenshot_catalog=lambda:[page()]
        self.w.claim_screenshot_ocr=Mock(return_value=ocr('Revenue: 950'))
        raw=image_bytes();self.image=self.w.screenshots.upload({'name':'x.png','mime':'image/png','base64':base64.b64encode(raw).decode(),'request_key':'upload'})
        self.s=ClaimScreenshots(self.w);self.request={'image_id':self.image['id'],'request_key':'identify'}
    def test_actual_local_ocr_regions_and_bad_coordinates(self):
        value=ocr('Revenue');self.assertEqual(validate(value),value)
        value['lines'][0]['region']['x']=float('nan')
        with self.assertRaises(ValueError):validate(value)
    def test_retained_body_loader_and_anchored_figure(self):
        result=self.s.identify(self.request);self.assertEqual(result['status'],'IDENTIFIED')
        self.assertEqual([f['field'] for f in result['facts']],['metric','observation'])
        self.assertEqual(result['facts'][1]['value']['figure']['value'],'950')
        self.assertEqual(result['facts'][0]['source']['review_hash'],result['hash'])
        self.assertEqual(self.s.identify(self.request),result);self.w.claim_screenshot_ocr.assert_called_once()
        self.assertEqual(self.s.load(result['id'])['hash'],result['hash'])
    def test_unlabelled_number_has_no_observation(self):
        value=ocr('Revenue','950');value['lines'][1]['region']['y']=300
        self.w.claim_screenshot_ocr.return_value=value
        value=self.s.identify(self.request)
        self.assertEqual([f['field'] for f in value['facts']],['metric'])
    def test_card_label_value_positional_pair_has_both_regions(self):
        self.w.claim_screenshot_ocr.return_value=ocr('Revenue','950')
        value=self.s.identify(self.request)
        observation=next(f for f in value['facts']if f['field']=='observation')
        self.assertEqual(observation['value']['figure']['value'],'950')
        self.assertNotEqual(observation['source']['region'],observation['source']['label_region'])
    def test_positional_number_with_two_competing_labels_is_not_assigned(self):
        self.w.claim_screenshot_catalog=lambda:[dict(page(),anchors=['Revenue','Collections'],targets=[{'target_id':'v','labels':['Revenue','Collections']}])]
        value=ocr('Revenue','950','Collections');value['lines'][2]['region']['y']=50
        self.w.claim_screenshot_ocr.return_value=value
        result=self.s.identify(self.request)
        self.assertFalse(any(f['field']=='observation'for f in result['facts']))
    def test_tie_is_named_question_not_guess_or_probe(self):
        self.w.claim_screenshot_catalog=lambda:[page(),page('b')]
        value=self.s.identify(self.request);self.assertEqual(value['status'],'NEEDS_INPUT')
        self.assertEqual([x['label'] for x in value['question']['choices']],['Billing / a','Billing / b'])
        self.assertEqual(value['facts'],[]);self.h.native.assert_not_called()
    def test_confirmation_is_append_only_and_portal_mapping_stales(self):
        value=self.s.identify(self.request);oldhash=value['hash']
        confirmed=self.s.confirm({'review_id':value['id'],'candidate_id':'a','request_key':'confirm','portal':{'portal':'Ops','tab':'Sales'}})
        self.assertEqual(confirmed['hash'],oldhash);self.assertEqual(confirmed['candidate_bindings'][0]['status'],'CONFIRMED')
        mapped=self.s.identify(dict(self.request,request_key='mapped',portal={'portal':'Ops','tab':'Sales'}))
        self.assertEqual(mapped['identification_method'],'USER_CONFIRMED_PORTAL_MAPPING')
        self.w.claim_screenshot_catalog=lambda:[page('new','Other')]
        stale=self.s.identify(dict(self.request,request_key='stale',portal={'portal':'Ops','tab':'Sales'}))
        self.assertNotEqual(stale['identification_method'],'USER_CONFIRMED_PORTAL_MAPPING')
    def test_portal_mapping_isolated_by_approved_manifest_hash(self):
        self.w.agent.config['_estate']={'manifest_hash':'estate-a'}
        value=self.s.identify(self.request);portal={'portal':'Ops','tab':'Sales'}
        self.s.confirm({'review_id':value['id'],'candidate_id':'a','request_key':'confirm','portal':portal})
        self.w.agent.config['_estate']={'manifest_hash':'estate-b'}
        other=self.s.identify(dict(self.request,request_key='other-estate',portal=portal))
        self.assertEqual(other['identification_method'],'RETAINED_DEFINITION_TEXT')
    def test_forged_candidate_and_corrupt_review_refused(self):
        value=self.s.identify(self.request)
        with self.assertRaises(Conflict):self.s.confirm({'review_id':value['id'],'candidate_id':'forged','request_key':'c'})
        with self.w.store.connect() as db:db.execute("UPDATE claim_screenshot_reviews SET body='{}' WHERE id=?",(value['id'],))
        with self.assertRaises((Conflict,KeyError)):self.s.load(value['id'])
    def test_projection_refused_before_ocr_and_raw_image_access(self):
        self.w.agent.config['_estate']={'recording':{'tape_class':'PRIVACY_PROJECTED'}}
        with patch.object(self.w.screenshots,'image') as image:
            from investigator.process_tape import TapeError
            with self.assertRaises((Conflict,TapeError)):self.s.identify(self.request)
        image.assert_not_called();self.w.claim_screenshot_ocr.assert_not_called()
    def test_unknown_image_is_not_read_or_written(self):
        with self.assertRaises(KeyError):self.s.identify(dict(self.request,image_id='none'))
        self.w.claim_screenshot_ocr.assert_not_called()
    def test_unknown_client_facts_are_never_accepted(self):
        with self.assertRaises(ValueError):self.s.identify(dict(self.request,facts=[{'figure':950}]))
        self.w.claim_screenshot_ocr.assert_not_called()
    def test_loader_rejects_changed_candidate_definitions(self):
        value=self.s.identify(self.request);self.w.claim_screenshot_catalog=lambda:[page('changed')]
        with self.assertRaisesRegex(Conflict,'catalog changed'):self.s.load(value['id'])
    def test_catalog_bound_refuses_not_truncates_ambiguity(self):
        self.w.claim_screenshot_catalog=lambda:[page(str(i))for i in range(101)]
        with self.assertRaisesRegex(Conflict,'rather than truncate'):self.s.identify(self.request)
    def test_crop_uses_distinct_visual_anchor_across_catalog(self):
        ranked=rank(ocr('Revenue'),[page(),page('b','Collections')])
        self.assertEqual(ranked[0]['candidate_id'],'a')

if __name__=='__main__':unittest.main()
