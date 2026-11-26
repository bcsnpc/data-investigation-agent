"""Generic saved-trace repairs; no ticket IDs, expected values or live calls."""
from copy import deepcopy
from unittest.mock import Mock
import unittest
from investigator.guided_intake import Catalog, VERSION, admit


class ParentReferenceTests(unittest.TestCase):
    def setUp(self):
        nodes=[];edges=[]
        for suffix in ('one','two'):
            for kind in ('REPORT','PAGE','VISUAL'):
                identity=kind.lower()+'-'+suffix
                nodes.append({'id':identity,'kind':kind,'label':identity})
            edges.extend([{'source':'report-'+suffix,'target':'page-'+suffix,'kind':'CONTAINS'},
                          {'source':'page-'+suffix,'target':'visual-'+suffix,'kind':'CONTAINS'}])
        self.catalog=Catalog({'nodes':nodes,'edges':edges})
        self.request={'version':VERSION,'report':'unknown-parent','page':'page-one','visual':'visual-one',
                      'issue_type':'NUMBER_LOOKS_WRONG','compared_with':{'kind':'NOTHING'}}

    def test_unknown_parent_uses_exact_explicit_child_without_mutating_submission(self):
        before=deepcopy(self.request);answer=admit(self.request,self.catalog)
        self.assertEqual(answer['report'],'report-one')
        self.assertEqual(answer['visual'],'visual-one')
        self.assertEqual(answer['parent_reference_resolution']['basis'],'UNIQUE_EXACT_NATIVE_CONTAINMENT')
        self.assertEqual(self.request,before)

    def test_primary_and_comparison_are_recovered_independently(self):
        self.request['compared_with']={'kind':'ANOTHER_REPORT','target':
            {'report':'another-unknown','page':'page-two','visual':'visual-two'}}
        answer=admit(self.request,self.catalog)
        self.assertEqual(answer['report'],'report-one')
        self.assertEqual(answer['compared_with']['target']['report'],'report-two')
        self.assertEqual(answer['compared_with']['target']['visual'],'visual-two')

    def test_valid_conflicting_report_is_never_replaced(self):
        self.request['report']='report-two'
        with self.assertRaisesRegex(ValueError,'PAGE_OUTSIDE_REPORT'):admit(self.request,self.catalog)

    def test_valid_conflicting_page_is_never_replaced(self):
        self.request.update(report='report-one',page='page-two')
        with self.assertRaises(ValueError):admit(self.request,self.catalog)

    def test_unknown_visual_does_not_borrow_a_page_to_replace_target(self):
        self.request['visual']='unknown-visual'
        with self.assertRaisesRegex(ValueError,'UNKNOWN_REPORT'):admit(self.request,self.catalog)

    def test_multiple_native_parents_do_not_establish_recovery(self):
        self.catalog.edges.append({'source':'report-two','target':'page-one','kind':'CONTAINS'})
        with self.assertRaisesRegex(ValueError,'UNKNOWN_REPORT'):admit(self.request,self.catalog)

    def test_missing_visual_is_not_filled_from_a_matching_measure(self):
        del self.request['visual']
        answer=admit(self.request,self.catalog)
        self.assertNotIn('visual',answer)


class OpenedSourceSchemaTests(unittest.TestCase):
    def setUp(self):
        from investigator.adapters.ai_native_catalog import NativeCatalog
        from test_round23_native_catalog import asset
        parent='sql://reader-server/source-db';self.table=parent+'/object/17'
        assets=[asset(parent,'SqlDatabase',None,'source-db',{}),
                asset(self.table,'SqlObject',parent,'Events',{'schema_name':'app','name':'Events',
                      'type_desc':'USER_TABLE','columns':[{'name':'amount','data_type':'int'}]})]
        self.original=deepcopy(assets);self.events=[]
        self.read=Mock(return_value={'read_only_verified':True,'rows':[
            {'schema_name':'app','table_name':'Events','column_name':name,
             'data_type':kind,'collation_name':None}
            for name,kind in [('amount','int'),('valid_start','datetime2'),('valid_end','datetime2')]]})
        self.catalog=NativeCatalog(assets=assets,graph_nodes=[{'id':'table-node','properties':{'asset_id':self.table}}],
            configuration={'sql':{'server':'reader-server','database':'source-db'},
                           'fabric':{'sql_reader':{'server':'fabric-reader'}}},
            endpoint=Mock(),sql_read=Mock(),source_read=self.read,record=self.events.append)
        self.identity=next(iter(self.catalog.routes))

    def test_retained_columns_do_not_hide_native_history_schema_changes(self):
        self.read.assert_not_called()
        route=self.catalog.prepare(self.identity,['table-node'])
        meta=route['objects'][0]['metadata']
        self.assertEqual([c['name']for c in meta['columns']],['amount','valid_start','valid_end'])
        self.assertTrue(meta['fresh_native_schema'])
        self.assertEqual(self.read.call_args.args[1]['read_only_objects'],['[app].[Events]'])
        self.assertTrue(self.read.call_args.args[1]['require_read_only'])
        self.catalog.prepare(self.identity,['table-node']);self.read.assert_called_once()
        self.assertEqual(self.original[1]['metadata']['columns'],[{'name':'amount','data_type':'int'}])

    def test_optional_transport_failure_retains_only_known_columns_and_warns_once(self):
        from run_source_diagnostic import SourceReadError
        self.read.side_effect=SourceReadError(40613,'SqlException',[])
        route=self.catalog.prepare(self.identity,['table-node'])
        self.assertEqual([c['name']for c in route['objects'][0]['metadata']['columns']],['amount'])
        self.assertNotIn('fresh_native_schema',route['objects'][0]['metadata'])
        self.assertTrue(any(e['event']=='NATIVE_QUERY_SCHEMA_UNAVAILABLE'for e in self.events))
        self.catalog.prepare(self.identity,['table-node']);self.read.assert_called_once()

    def test_unknown_native_object_is_not_read(self):
        route=self.catalog.prepare(self.identity,['outside-node'])
        self.assertEqual(route['objects'],[]);self.read.assert_not_called()

    def test_malformed_or_unguarded_catalog_is_never_promoted(self):
        self.read.return_value={'read_only_verified':False,'rows':[]}
        with self.assertRaisesRegex(ValueError,'guarded surface'):self.catalog.prepare(self.identity)

    def test_safety_or_budget_refusal_is_never_swallowed_as_metadata_unavailable(self):
        for error in (RuntimeError('budget exhausted'),ValueError('read-only refused')):
            with self.subTest(error=type(error).__name__):
                self.read.side_effect=error
                with self.assertRaises(type(error)):self.catalog.prepare(self.identity)


class LiteralCandidateTests(unittest.TestCase):
    def setUp(self):
        from test_round23_intake_queries import graph,request
        self.raw=graph();self.catalog=Catalog(self.raw);self.proposal=request()
        self.proposal['reported_figure']={'state':'NUMBER','value':'1234','precision':'EXACT'}
        self.raw['nodes'].append({'id':'header','kind':'VISUAL','label':'page annotation',
                                  'properties':{'asset_id':'native-header'}})
        self.raw['edges'].append({'source':'page','target':'header','kind':'CONTAINS'})
        self.catalog=Catalog(self.raw)
        self.asset={'id':'native-header','kind':'ReportVisual','metadata':{
            'visual':{'visualType':'textbox','objects':{'general':[{'properties':{'paragraphs':[
                {'textRuns':[{'value':'Current selections: region 2'}]}]}}]}}}}

    def inventory(self,**kwargs):
        from investigator.intake_candidates import enumerate_targets
        return enumerate_targets(self.catalog,text='quantity',proposal=self.proposal,
            explicit=kwargs.pop('explicit',{'report':'report'}),native_assets=kwargs.pop('native_assets',[self.asset]),**kwargs)

    def text(self,value):
        self.asset['metadata']['visual']['objects']['general'][0]['properties']['paragraphs'][0]['textRuns'][0]['value']=value

    def test_proven_nonmatching_literal_does_not_require_a_numeric_query(self):
        before=deepcopy(self.asset);inventory=self.inventory()
        self.assertEqual([c['id']for c in inventory['candidates']],['card'])
        proof=inventory['excluded_native_literals'][0]
        self.assertEqual(proof['asset_id'],'native-header');self.assertEqual(len(proof['metadata_sha256']),64)
        self.assertEqual(self.asset,before)

    def test_numeric_annotations_are_static_not_measured_candidates(self):
        for text in ('1,234','1.234K','1.234e3','total 1234'):
            with self.subTest(text=text):
                self.text(text);self.assertEqual(len(self.inventory()['candidates']),1)
        paragraph=self.asset['metadata']['visual']['objects']['general'][0]['properties']['paragraphs'][0]
        paragraph['textRuns']=[{'value':'12'},{'value':'34'}]
        self.assertEqual(len(self.inventory()['candidates']),1)

    def test_explicit_literal_is_never_dropped(self):
        inv=self.inventory(explicit={'report':'report','page':'page','visual':'header'})
        self.assertEqual([c['id']for c in inv['candidates']],['header'])

    def test_missing_native_or_dynamic_or_unknown_visual_stays_ambiguous(self):
        self.assertEqual(len(self.inventory(native_assets=[])['candidates']),2)
        self.asset['metadata']['visual']['query']={'unread':True}
        self.assertEqual(len(self.inventory()['candidates']),2)
        del self.asset['metadata']['visual']['query']
        self.asset['metadata']['visual']['objects']['general'][0]['properties']['dynamic']={'expr':{'Measure':{'Property':'quantity'}}}
        self.assertEqual(len(self.inventory()['candidates']),2)

    def test_exclusion_precedes_limit_but_real_unread_visuals_still_truncate(self):
        self.assertTrue(self.inventory(limit=1)['exhaustive'])
        self.asset['metadata']['visual']['visualType']='card'
        self.assertFalse(self.inventory(limit=1)['exhaustive'])

    def test_static_annotation_is_excluded_without_an_exact_figure(self):
        self.proposal.pop('reported_figure')
        self.assertEqual(len(self.inventory()['candidates']),1)
        self.proposal['reported_figure']={'state':'NUMBER','value':'1234','precision':0}
        self.assertEqual(len(self.inventory()['candidates']),1)

    def test_missing_or_malformed_native_metadata_remains_a_candidate(self):
        for metadata in (None,[],{}, {'visual':None}, {'visual':{'visualType':'textbox'}}):
            with self.subTest(metadata=metadata):
                self.asset['metadata']=metadata
                self.assertEqual(len(self.inventory()['candidates']),2)


if __name__=='__main__':unittest.main()
