import unittest
from investigator.adapters.report_listing import ReportLists

W='11111111-1111-4111-8111-111111111111'
R='22222222-2222-4222-8222-222222222222'
OTHER='33333333-3333-4333-8333-333333333333'


class LiveReportListsTests(unittest.TestCase):
    def test_live_names_never_bind_equal_named_other_objects(self):
        models=[{'id':'model','reports':[{'id':'fabric://'+W+'/'+OTHER,'name':'Sales'}],
                 'visuals':[]}]
        result=self.lists.bound_catalog(models)
        self.assertEqual(result['models'][0]['reports'],[])
        self.assertEqual(len(result['unbound_reports']),1)

    def test_live_page_titles_bind_native_page_ids_not_equal_titles(self):
        report='fabric://'+W+'/'+R
        models=[{'id':'model','reports':[{'id':report,'name':'Sales'}],
            'visuals':[{'report_id':report,'page_id':report+'/page/another-page'}]}]
        result=self.lists.bound_pages(report,models)
        self.assertEqual(result['pages'][0]['id'],report+'/page/page-one')
        self.assertFalse(result['pages'][0]['executable'])

    def test_exact_live_report_binding_changes_label_not_approved_identity(self):
        report='fabric://'+W+'/'+R
        models=[{'id':'model','reports':[{'id':report,'name':'Old label'}],
                 'visuals':[{'report_id':report,'page_id':report+'/page/page-one'}]}]
        result=self.lists.bound_catalog(models)
        self.assertEqual(result['models'][0]['reports'],[{'id':report,'name':'Sales'}])
        self.assertEqual(models[0]['reports'][0]['name'],'Old label')
        self.assertTrue(self.lists.bound_pages(report,models)['pages'][0]['executable'])

    def test_partial_paginated_list_refuses_instead_of_omitting_reports(self):
        self.lists.read=lambda endpoint:{'status_code':200,'body':{'value':[], '@odata.nextLink':'next'}}
        with self.assertRaisesRegex(ValueError,'incomplete'):self.lists.reports()

    def setUp(self):
        self.now=0;self.calls=[];self.status=200
        def read(endpoint):
            self.calls.append(endpoint)
            body=([{'id':R,'name':'Sales','reportType':'PowerBIReport'}] if endpoint.endswith('/reports')
                  else [{'name':'page-one','displayName':'Customers','order':0}])
            return {'status_code':self.status,'body':{'value':body}}
        self.read=read
        self.lists=ReportLists([W],'reader-one',read,clock=lambda:self.now)

    def test_values_come_from_live_transport_not_configuration(self):
        self.assertEqual(self.lists.reports()['reports'][0]['name'],'Sales')
        self.assertEqual(self.calls,['groups/'+W+'/reports'])
        self.assertEqual(self.lists.pages(W,R)['pages'][0]['name'],'Customers')

    def test_cache_expires_at_default_five_minutes(self):
        self.assertFalse(self.lists.reports()['cached'])
        self.now=299;self.assertTrue(self.lists.reports()['cached'])
        self.now=300;self.assertFalse(self.lists.reports()['cached'])
        self.assertEqual(len(self.calls),2)

    def test_manual_refresh_forces_physical_request(self):
        self.lists.reports();self.assertFalse(self.lists.reports(refresh=True)['cached'])
        self.assertEqual(len(self.calls),2)

    def test_no_global_workspace_listing_or_out_of_scope_request(self):
        with self.assertRaisesRegex(ValueError,'outside estate'):self.lists.pages(OTHER,R)
        self.assertEqual(self.calls,[])

    def test_arbitrary_report_id_is_not_sent_to_provider(self):
        with self.assertRaisesRegex(ValueError,'absent'):self.lists.pages(W,OTHER)
        self.assertEqual(self.calls,['groups/'+W+'/reports'])

    def test_identity_caches_are_separate(self):
        self.lists.reports()
        second=ReportLists([W],'reader-two',self.read)
        self.assertFalse(second.reports()['cached']);self.assertEqual(len(self.calls),2)

    def test_caller_cannot_change_cached_metadata(self):
        self.lists.reports()['reports'][0]['name']='Invented'
        self.assertEqual(self.lists.reports()['reports'][0]['name'],'Sales')

    def test_refusal_does_not_relabel_expired_data_as_live(self):
        self.lists.reports();self.now=301;self.status=403
        with self.assertRaisesRegex(ValueError,'HTTP 403'):self.lists.reports()

    def test_invalid_scope_ttl_and_refresh_are_rejected(self):
        for ttl in (0,True,3601):
            with self.assertRaises(ValueError):ReportLists([W],'reader',self.read,ttl_seconds=ttl)
        with self.assertRaises(ValueError):ReportLists([],'reader',self.read)
        with self.assertRaises(ValueError):self.lists.reports(refresh='yes')

    def test_page_cache_is_keyed_by_report_and_workspace(self):
        self.lists.pages(W,R);self.lists.pages(W,R)
        self.assertEqual(len(self.calls),2)
        self.lists.pages(W,R,refresh=True);self.assertEqual(len(self.calls),3)

    def test_unknown_report_type_stays_visible_and_cannot_be_opened(self):
        lists=ReportLists([W],'reader',lambda endpoint:{'status_code':200,'body':{'value':[
            {'id':R,'name':'Future report','reportType':'UnfamiliarReport'}]}})
        rows=lists.reports()['reports']
        self.assertEqual(len(rows),1);self.assertFalse(rows[0]['supported'])
        with self.assertRaisesRegex(ValueError,'UnfamiliarReport'):lists.pages(W,R)
