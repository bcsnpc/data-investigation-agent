from urllib.parse import urlencode
import unittest
from investigator.adapters.report_link import parse, predicates, LinkRefused


REPORT='11111111-1111-4111-8111-111111111111'
WORKSPACE='22222222-2222-4222-8222-222222222222'
LINK=f'https://app.powerbi.com/groups/{WORKSPACE}/reports/{REPORT}/ReportSectionA'


class ReportLinkTests(unittest.TestCase):
    def test_shared_declaration_is_not_attestation_of_user_state(self):
        value=parse(LINK)
        self.assertEqual(value['report_id'],REPORT)
        self.assertEqual(value['workspace_id'],WORKSPACE)
        self.assertEqual(value['page_id'],'ReportSectionA')
        self.assertEqual(value['provenance'],'SHARED_URL')
        self.assertFalse(value['claims_active_user_state'])

    def test_encoded_apostrophe_and_keyword_in_value_are_literals(self):
        expression="Customers/Name eq 'O''Brien and Sons' and Sales_x0020_Data/Count in (5, 6.5)"
        value=parse(LINK+'?'+urlencode({'filter':expression}))
        self.assertEqual(value['predicates'][0]['values'],[{'kind':'STRING','value':"O'Brien and Sons"}])
        self.assertEqual(value['predicates'][1]['table'],'Sales Data')
        self.assertEqual(value['predicates'][1]['values'][1],{'kind':'NUMBER','value':'6.5'})

    def test_literal_types_and_identifier_case_remain_explicit(self):
        self.assertEqual(predicates("Sales/Count eq '5'")[0]['values'][0]['kind'],'STRING')
        self.assertEqual(predicates('sales/Count eq 5')[0]['table'],'sales')

    def test_unsupported_predicate_never_preserves_only_a_supported_prefix(self):
        for expression in ("Sales/Count eq 5 or Sales/Count eq 6",'Sales/Count eq 5 and Customers/Age gt 20',
                           'Sales/Count eq 5 and','Sales/Count eq 5 garbage',"Sales/Count in (5, '6')"):
            with self.subTest(expression=expression),self.assertRaises(LinkRefused):predicates(expression)

    def test_conflicting_or_unknown_state_refuses(self):
        for query in (f'reportId={WORKSPACE}','pageName=Other','filter=Sales/Count eq 5&$filter=Sales/Count eq 6',
                      'filter=Sales/Count eq 5&filter=Sales/Count eq 6','unrecognised=state',
                      'filter=Sales/Count eq 5&bookmarkGuid=BookmarkA'):
            with self.subTest(query=query),self.assertRaises(LinkRefused):parse(LINK+'?'+query)

    def test_bookmark_is_a_reference_not_invented_predicates(self):
        result=parse(LINK+'?bookmarkGuid=BookmarkA')
        self.assertEqual(result['bookmark_reference'],'BookmarkA')
        self.assertEqual(result['predicates'],[])

    def test_embedded_report_and_dollar_filter(self):
        link='https://app.powerbi.com/reportEmbed?'+urlencode({'reportId':REPORT,'pageName':'ReportSectionA',
            '$filter':"Sales/Region eq 'North'",'autoAuth':'true'})
        result=parse(link);self.assertIsNone(result['workspace_id'])
        self.assertEqual(result['predicates'][0]['values'][0]['value'],'North')

    def test_origin_userinfo_fragments_and_opaque_share_routes_never_open(self):
        for link in ('javascript:alert(1)',LINK.replace('app.powerbi.com','app.powerbi.com.evil'),
                     LINK.replace('https://','https://user@'),LINK+'#filter=Sales/Count eq 5',
                     LINK.replace('app.powerbi.com','app.powerbi.com:bad'),
                     'https://app.powerbi.com/view?r=opaque'):
            with self.subTest(link=link),self.assertRaises(LinkRefused):parse(link)


if __name__=='__main__':unittest.main()
