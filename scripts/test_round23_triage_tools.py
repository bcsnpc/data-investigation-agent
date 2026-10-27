"""Synthetic path facts, record and screenshot checks; zero estate requests."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock
import unittest
from investigator.path_triage import Triage,CHECKS
from investigator.investigation_read_tools import ReadTools,compare_figure
from investigator.screenshot_record_lookup import ScreenshotLookup
from investigator.guided_intake import Catalog
from investigator.package_completeness import check
from test_round23_intake_queries import graph,request,sql_objects
from investigator.investigative_queries import Queries

NOW='2026-11-01T01:00:00Z'


class TriageTests(unittest.TestCase):
    def test_candidate_lookup_matches_visible_words_to_underscores_and_container_names(self):
        node={'id':'matching','kind':'TABLE','label':'stock_movements','properties':{'native_location':{'container_name':'warehouse_gold_fixture'}}}
        other={'id':'other','kind':'TABLE','label':'stock_other','properties':{}}
        port=ReadTools(graph=Mock(),path={'nodes':[],'edges':[]},queries=Mock(),intake={'report':'report'},
                       job_runs=Mock(),refresh_history=Mock(),candidates={'nodes':[other,node],'edges':[]})
        ranked=port.candidates({'words':'stock movements gold'})['candidates']
        self.assertEqual(ranked[0]['id'],'matching')
        self.assertEqual(ranked[0]['rank']['word_matches'],3)

    def test_current_cache_does_not_issue_live_read(self):
        refresh=Mock();save=Mock()
        triage=Triage(path=['visual','model'],lookup=lambda *a:{'source':'ledger','observed_at':NOW,'value':{'status':'ok'}},
                      refresh=refresh,save=save,now=lambda:NOW)
        result=triage.run();self.assertEqual(result['refresh_operations'],0)
        self.assertEqual(len(result['facts']),10);refresh.assert_not_called()
    def test_invalid_or_unavailable_cache_refreshes_negative_stays_negative(self):
        for value in ({'source':'ledger','observed_at':'bad','value':{}},
                      {'source':'ledger','observed_at':NOW,'value':{},'state':'UNAVAILABLE'}):
            refresh=Mock(return_value={'source':'native','observed_at':NOW,'state':'OBSERVED_NEGATIVE','value':[]})
            result=Triage(path=['model'],lookup=lambda *a:value,refresh=refresh,save=lambda x:None,now=lambda:NOW).run()
            self.assertEqual(result['refresh_operations'],10)
            self.assertTrue(all(f['state']=='OBSERVED_NEGATIVE' for f in result['facts']))

    def test_stale_reads_path_only_and_each_fact_has_source_time(self):
        refresh=Mock(return_value={'source':'native','observed_at':NOW,'value':{'status':'ok'}})
        triage=Triage(path=['only','this'],lookup=lambda *a:None,refresh=refresh,save=lambda x:None,now=lambda:NOW)
        result=triage.run();self.assertEqual(result['refresh_operations'],10)
        for call in refresh.call_args_list:self.assertEqual(call.args[1],['only','this'])
        self.assertTrue(all(f['source']=='native' and f['observed_at']==NOW for f in result['facts']))
    def test_failed_refresh_never_becomes_current_or_observed_empty(self):
        old={'source':'ledger','observed_at':'2026-10-01T00:00:00Z','value':{'status':'old'}}
        triage=Triage(path=['model'],lookup=lambda *a:old,refresh=Mock(side_effect=RuntimeError('offline')),
                      save=lambda x:None,now=lambda:NOW,read_limit=1)
        result=triage.run();self.assertEqual(result['facts'][0]['state'],'UNAVAILABLE')
        self.assertEqual(result['facts'][0]['previous'],old)
        self.assertEqual(result['facts'][1]['reason'],'TRIAGE_READ_LIMIT')


class ToolTests(unittest.TestCase):
    def setUp(self):
        self.layers={'gold':{'dialect':'T-SQL','objects':sql_objects()}}
        self.execute=Mock(return_value={'rows':[{'quantity':7}]})
        self.queries=Queries(self.layers,execute=self.execute,reserve=lambda *a:None,save=lambda x:None)
        self.path=graph()
        self.path['nodes'].extend([{'id':'table','kind':'TABLE','label':'Movements','properties':{'lineage_distance':1}},
                                  {'id':'other_table','kind':'TABLE','label':'Movements','properties':{'lineage_distance':3}}])
        self.tools=ReadTools(graph=Mock(),path=self.path,queries=self.queries,intake=request(),
                             job_runs=Mock(),refresh_history=Mock())
    def test_candidates_proximity_and_explicit_visual_preserved(self):
        result=self.tools.candidates({'words':'Movements'})
        names=[r['id'] for r in result['candidates']]
        self.assertLess(names.index('table'),names.index('other_table'))
        self.assertNotIn('othercard',names)
    def test_candidate_value_check_uses_model_written_query(self):
        self.tools.intake['reported_figure']={'state':'NUMBER','value':'7','precision':'EXACT'}
        result=self.tools.candidates({'words':'Movements','checks':[{'candidate':'table','layer':'gold',
                    'kind':'sql','query':'SELECT quantity FROM dbo.Items'}]})
        self.assertEqual(result['resolution'],'ONE_MATCH')
        self.assertEqual(result['checks'][0]['precision'],'EXACT')
    def test_record_presence_duplicates_and_failure_not_absence(self):
        self.execute.return_value={'rows':[{'id':7},{'id':7}]}
        result=self.tools.record_trace({'key':'7','queries':[{'layer':'gold','kind':'sql',
                   'query':'SELECT id FROM dbo.Items','key_field':'id'}]})
        self.assertTrue(result['layers'][0]['duplicate_observed'])
        self.execute.side_effect=RuntimeError('native failed')
        result=self.tools.record_trace({'key':'8','queries':[{'layer':'gold','kind':'sql',
                   'query':'SELECT id FROM dbo.Items WHERE id=8','key_field':'id'}]})
        self.assertEqual(result['layers'][0]['presence'],'UNAVAILABLE')
    def test_blank_zero_and_reduced_precision(self):
        self.assertTrue(compare_figure({'state':'EMPTY'},None)['matches'])
        self.assertFalse(compare_figure({'state':'EMPTY'},0)['matches'])
        result=compare_figure({'state':'NUMBER','value':'3400000','precision':{'place':5}},'3423000')
        self.assertTrue(result['matches']);self.assertTrue(result['weaker_claim'])
        self.assertIn('weaker',result['qualification'])
    def test_missing_security_reader_is_not_misreported_as_a_permission_refusal(self):
        value=self.tools.security_definitions({'node':'table'})
        self.assertEqual(value['status'],'NOT_INSTALLED')
        self.assertIn('no impersonation',value['operation'])
        self.assertIn('UNESTABLISHED',value['permission_need'])


class ScreenshotTests(unittest.TestCase):
    def test_real_key_is_native_only_image_and_personal_values_not_logged(self):
        personal='Synthetic person example'
        events=[];execute=Mock(return_value={'rows':[{'id':19,'name':personal}]})
        objects=sql_objects();objects[0]['metadata']['columns'].append({'name':'name','data_type':'VARCHAR'})
        queries=Queries({'gold':{'dialect':'T-SQL','objects':objects}},execute=execute,
                        reserve=lambda *a:None,save=lambda x:None)
        plans=[{'layer':'gold','query':'SELECT id,name FROM dbo.Items WHERE id=19','kind':'sql',
                'key_field':'id','display_fields':['name']}]
        lookup=ScreenshotLookup(catalog=Catalog(graph()),queries=queries,
            extract=lambda _: {'titles':{'visual':'Card'},'visible_fields':{'name':personal}},
            plan=lambda *a:plans,audit=events.append)
        result=lookup.resolve(b'synthetic-image-bytes',request())
        self.assertEqual(result['key'],'19');self.assertEqual(result['target']['visual'],'card')
        self.assertNotIn(personal,str(events));self.assertNotIn('synthetic-image-bytes',str(events))
        self.assertEqual(events[0]['field_names'],['name'])
    def test_two_keys_offer_distinguishing_fields_not_guessed_key(self):
        queries=Queries({'gold':{'dialect':'T-SQL','objects':sql_objects()}},
            execute=lambda *a,**kw:{'rows':[{'id':1,'day':'Monday','quantity':7},{'id':2,'day':'Tuesday','quantity':7}]},
            reserve=lambda *a:None,save=lambda x:None)
        lookup=ScreenshotLookup(catalog=Catalog(graph()),queries=queries,
            extract=lambda _: {'titles':{},'visible_fields':{'quantity':'7'}},
            plan=lambda *a:[{'layer':'gold','query':'SELECT id FROM dbo.Items','kind':'sql','key_field':'id',
                             'display_fields':['day','id']}],audit=lambda x:None)
        result=lookup.resolve(b'fixture',request())
        self.assertEqual(result['status'],'KEY_CHOICES');self.assertNotIn('id',result['choices'][0]['display'])
    def test_one_wrong_visible_row_does_not_establish_a_key(self):
        queries=Queries({'gold':{'dialect':'T-SQL','objects':sql_objects()}},
            execute=lambda *a,**kw:{'rows':[{'id':1,'quantity':99}]},reserve=lambda *a:None,save=lambda x:None)
        lookup=ScreenshotLookup(catalog=Catalog(graph()),queries=queries,
            extract=lambda _: {'titles':{},'visible_fields':{'quantity':'7'}},
            plan=lambda *a:[{'layer':'gold','query':'SELECT id,quantity FROM dbo.Items','kind':'sql','key_field':'id','display_fields':[]}],
            audit=lambda x:None)
        self.assertEqual(lookup.resolve(b'fixture',request())['status'],'NO_MATCH')
    def test_no_match_is_not_zero_and_attempts_lower_layers(self):
        execute=Mock(return_value={'rows':[]})
        queries=Queries({'gold':{'dialect':'T-SQL','objects':sql_objects()}},execute=execute,
                        reserve=lambda *a:None,save=lambda x:None)
        lookup=ScreenshotLookup(catalog=Catalog(graph()),queries=queries,
            extract=lambda _: {'titles':{},'visible_fields':{'name':'nobody'}},
            plan=lambda *a:[{'layer':'gold','query':'SELECT id FROM dbo.Items','kind':'sql','key_field':'id','display_fields':[]}],
            audit=lambda x:None)
        self.assertEqual(lookup.resolve(b'fixture',request())['status'],'NO_MATCH')


class PackageTests(unittest.TestCase):
    def test_missing_internal_import_fails_without_executing_modules(self):
        with TemporaryDirectory() as folder:
            source=Path(folder)/'source';staged=Path(folder)/'staged'
            for root in (source,staged):(root/'scripts/pkg').mkdir(parents=True)
            (source/'scripts/pkg/dep.py').write_text('raise AssertionError("do not execute")')
            (staged/'scripts/pkg/main.py').write_text('from .dep import value')
            with self.assertRaisesRegex(ValueError,'INTERNAL_IMPORTS_MISSING'):check(staged,source)
            (staged/'scripts/pkg/dep.py').write_text('raise AssertionError("do not execute")')
            self.assertEqual(check(staged,source)['status'],'PASS')


if __name__=='__main__':unittest.main()
