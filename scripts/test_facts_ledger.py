"""Facts-ledger, migration and collector integration; no network or model calls."""
import copy
from pathlib import Path
import tempfile
import os
import unittest
from unittest.mock import Mock, patch
from investigator.shared_state import SharedState, StateConflict
from investigator.estate_graph_repository import GraphRepository
from investigator.estate_graph_api import GraphAPI
from investigator.facts_ledger import FactLedger, fact
from investigator.facts_collectors import observation, derived_runs, IncrementalFactCollector, refresh_facts
from investigator.facts_migration import sql
from test_estate_graph import graph, T0, T1

T2='2026-10-13T02:00:00Z'


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.state=SharedState.offline(Path(self.tmp.name)/'facts.sqlite')
        self.repo=GraphRepository(self.state);self.repo.migrate();self.repo.replace(graph())
        self.ledger=FactLedger(self.state)

    def value(self,subject='visual',at=T0,**kwargs):
        return observation(subject,'REFRESH_STATE',{'state':'IDLE'},at,['retained-read'],'test',**kwargs)

    def test_migration_hash_pinned_idempotent_and_same_migration_grants(self):
        self.state.migrate()
        with self.state.transaction() as db:
            self.assertEqual(db.execute('SELECT MAX(version) FROM state_schema_versions').fetchone()[0],4)
        pg=sql('postgresql')
        self.assertIn('GRANT SELECT, INSERT ON TABLE estate_node_facts TO "id-dia-worker"',pg)
        self.assertIn('GRANT SELECT, INSERT, UPDATE ON TABLE estate_fact_cursors TO "id-dia-worker"',pg)
        self.assertNotIn('DELETE',pg);self.assertNotIn('state_accounts',pg)

    def test_graph_subject_membership_and_fact_hash(self):
        self.ledger.append('estate',[self.value()])
        with self.assertRaises(Exception):self.ledger.append('estate',[self.value('absent')])
        with self.state.transaction() as db:db.execute("UPDATE estate_node_facts SET body_hash='wrong'")
        with self.assertRaisesRegex(StateConflict,'FACT_HASH'):self.ledger.read('estate',['visual'])

    def test_graph_replacement_and_node_retirement_preserve_fact_history(self):
        self.ledger.append('estate',[self.value()])
        changed=copy.deepcopy(graph());changed.update(definition_hash='b'*64,observed_at=T1)
        changed['nodes']=[n for n in changed['nodes'] if n['id']!='visual']
        changed['edges']=[e for e in changed['edges'] if e['source']!='visual' and e['target']!='visual']
        self.repo.replace(changed)
        self.assertEqual(len(self.ledger.read('estate',['visual'])['facts']),1)
        with self.assertRaisesRegex(ValueError,'SUBJECT_NOT_IN_GRAPH'):self.ledger.append('estate',[self.value(at=T2)])

    def test_as_of_excludes_future_collection_even_if_observed_earlier(self):
        first=self.value();second=self.value(at=T2);second['observed_at']=T0
        self.ledger.append('estate',[first,second])
        result=self.ledger.read('estate',['visual'],as_of=T1)
        self.assertEqual(len(result['facts']),1)
        self.assertEqual(result['facts'][0]['collected_at'],'2026-10-13T00:00:00.000000Z')

    def test_stale_unavailable_negative_and_missing_do_not_collapse(self):
        unavailable=self.value('measure');unavailable.update(state='UNAVAILABLE',value=None,reason='permission denied')
        negative=observation('column','OVERDUE',{'overdue':False},T0,['listing'],'test',state='OBSERVED_NEGATIVE')
        self.ledger.append('estate',[self.value(),unavailable,negative])
        result=self.ledger.read('estate',['visual','measure','column','page'],now=T2)
        self.assertEqual({v['state'] for v in result['facts']},{'OBSERVED','UNAVAILABLE','OBSERVED_NEGATIVE'})
        self.assertTrue(all(v['freshness']=='STALE' for v in result['facts']))
        self.assertEqual(result['missing_subjects'],['page'])

    def test_inferred_not_a_fact_and_exact_counts_not_estimates(self):
        bad=self.value();bad['source']='INFERRED'
        with self.assertRaisesRegex(ValueError,'NOT_OBSERVED'):fact(bad)
        run=observation('visual','JOB_RUN',{'run_id':'r1','status':'SUCCEEDED','rows_read':None,'rows_written':7},T0,['copy-output'],'adapter')
        self.assertIsNone(fact(run)['value']['rows_read'])
        run['value']['rows_read']=7.0
        with self.assertRaisesRegex(ValueError,'EXACT_COUNT'):fact(run)

    def test_profile_requires_both_actual_count_and_checksum_not_substitution(self):
        value=observation('visual','TABLE_PROFILE',{'load_marker':'r1','row_count':0,'checksum':'e3b0','checksum_method':'SHA256_CANONICAL_ROWS'},T0,['query'],'adapter')
        self.assertEqual(fact(value)['value']['row_count'],0)
        value['value']['checksum']=None
        with self.assertRaisesRegex(ValueError,'COUNTS_CHECKSUM'):fact(value)

    def test_coverage_has_explicit_missing_and_unavailable(self):
        value=self.value();value.update(state='UNAVAILABLE',value=None,reason='403')
        self.ledger.append('estate',[value])
        report=self.ledger.coverage('estate',{'visual':'VISUAL','page':'PAGE'},{'VISUAL':['REFRESH_STATE'],'PAGE':['REFRESH_STATE']},now=T1)
        self.assertEqual({v['status'] for v in report},{'MISSING','UNAVAILABLE'})

    def test_graph_gateway_and_as_of_facts(self):
        self.ledger.append('estate',[self.value()])
        gateway=Mock();gateway.graph_objects.side_effect=lambda estate,nodes,identity:nodes
        api=GraphAPI(self.repo,gateway,identity='reader',estate='estate',allowed_objects=['visual','measure','column'])
        result=api.as_of(T1).freshness('visual')
        self.assertEqual(result['runtime_facts'][0]['subject'],'visual')
        with self.assertRaises(PermissionError):api.node_facts('report')
        with self.assertRaisesRegex(ValueError,'HISTORICAL'):api.as_of(T1).refresh_facts(['visual'],Mock(),now=T2)

    def test_freshness_never_loads_unrelated_historical_bodies(self):
        self.ledger.append('estate',[self.value()])
        with self.state.transaction() as db:
            # If this unrelated report were decoded its hash would fail.
            db.execute("UPDATE estate_graph_history SET body='not-json' WHERE identity='report'")
        gateway=Mock();gateway.graph_objects.side_effect=lambda estate,nodes,identity:nodes
        api=GraphAPI(self.repo,gateway,identity='reader',estate='estate',allowed_objects=['visual','measure','column'])
        with patch.object(self.repo,'records',side_effect=AssertionError('whole catalog forbidden')):
            result=api.freshness('visual',now=T1)
        self.assertEqual(result['runtime_facts'][0]['subject'],'visual')

    def test_all_agent_graph_reads_are_path_scoped(self):
        gateway=Mock();gateway.graph_objects.side_effect=lambda estate,nodes,identity:nodes
        api=GraphAPI(self.repo,gateway,identity='reader',estate='estate',allowed_objects=['report','page','visual','measure','column'])
        with patch.object(self.repo,'records',side_effect=AssertionError('whole catalog forbidden')):
            self.assertEqual(api.definition_of('measure')['node'],'measure')
            self.assertTrue(api.path_to_source('visual')['nodes'])
            self.assertTrue(api.visual_context('report','page','visual')['nodes'])
            self.assertTrue(api.filters_on('page')['nodes'])

    def test_top_up_only_missing_or_stale_path_nodes(self):
        self.ledger.append('estate',[self.value('visual',T1),self.value('report',T0)])
        collector=Mock()
        result=refresh_facts(self.ledger,'estate',['visual','measure'],collector,now=T1)
        self.assertEqual(result['refreshed_subjects'],['measure'])
        self.assertEqual(collector.run.call_args.args[1],['measure'])


class CollectorTests(unittest.TestCase):
    setUp=LedgerTests.setUp
    value=LedgerTests.value
    def collector(self):
        adapter=Mock();adapter.identity='recorded-runtime-adapter'
        adapter.list_changes.return_value={'items':[{'subject':'visual','marker':'m1','load_marker':'load1'}],'complete':True,'evidence_ids':['list-read']}
        adapter.fetch.side_effect=lambda subject,now:[self.value(subject,now)]
        adapter.profile.side_effect=lambda subject,load_marker,now:observation(subject,'TABLE_PROFILE',{'load_marker':load_marker,'row_count':4,'checksum':'abc','checksum_method':'canonical-test'},now,['profile-read'],'test')
        budget=Mock();budget.claim.return_value=True
        return IncrementalFactCollector(self.ledger,adapter,budget=budget,key_tables=['visual']),adapter,budget

    def test_due_poll_once_unchanged_marker_no_detail_fanout(self):
        collector,adapter,budget=self.collector()
        collector.run('estate',['visual'],now=T0)
        self.assertEqual(collector.run('estate',['visual'],now=T0)['status'],'NOT_DUE')
        collector.run('estate',['visual'],now=T1)
        self.assertEqual(adapter.list_changes.call_count,2)
        self.assertEqual(adapter.fetch.call_count,1)
        self.assertEqual(adapter.profile.call_count,1)

    def test_new_load_profiles_once_no_counts_from_copy_output(self):
        collector,adapter,budget=self.collector()
        collector.run('estate',['visual'],now=T0)
        adapter.list_changes.return_value['items'][0].update(marker='m2',load_marker='load2')
        collector.run('estate',['visual'],now=T1)
        self.assertEqual(adapter.profile.call_count,2)
        self.assertEqual(self.ledger.read('estate',['visual'])['facts'][0]['value']['row_count'],4)

    def test_unavailable_profile_retries_even_when_runtime_marker_unchanged(self):
        collector,adapter,budget=self.collector()
        adapter.profile.side_effect=lambda subject,load_marker,now:observation(subject,'TABLE_PROFILE',None,now,['failed-profile'],'test',state='UNAVAILABLE',reason='endpoint unavailable')
        collector.run('estate',['visual'],now=T0)
        self.assertIsNone(self.ledger.cursor('estate',adapter.identity,'visual:profile'))
        collector.run('estate',['visual'],now=T1)
        self.assertEqual(adapter.fetch.call_count,1)
        self.assertEqual(adapter.profile.call_count,2)

    def test_exhausted_scan_budget_makes_no_adapter_call(self):
        collector,adapter,budget=self.collector();budget.claim.return_value=False
        self.assertEqual(collector.run('estate',['visual'],now=T0)['status'],'BUDGET_EXHAUSTED')
        adapter.list_changes.assert_not_called();adapter.fetch.assert_not_called()

    def test_out_of_path_listing_and_fetch_refused(self):
        collector,adapter,budget=self.collector()
        adapter.list_changes.return_value['items'][0]['subject']='report'
        with self.assertRaisesRegex(ValueError,'OUTSIDE_PATH'):collector.run('estate',['visual'],now=T0)
        adapter.fetch.assert_not_called()

    def test_incomplete_listing_is_gap_never_negative(self):
        collector,adapter,budget=self.collector()
        adapter.list_changes.return_value.update(items=[],complete=False)
        collector.run('estate',['visual'],now=T0)
        value=self.ledger.read('estate',['visual'])['facts'][0]
        self.assertEqual(value['state'],'UNAVAILABLE');self.assertIsNone(value['value'])

    def test_failed_fetch_does_not_advance_subject(self):
        collector,adapter,budget=self.collector()
        value=self.value();value.update(state='UNAVAILABLE',value=None,reason='403')
        adapter.fetch.side_effect=None;adapter.fetch.return_value=[value]
        collector.run('estate',['visual'],now=T0)
        self.assertIsNone(self.ledger.cursor('estate',adapter.identity,'visual'))

    def test_median_and_overdue_use_real_runs_and_schedule(self):
        runs=[{'run_id':'one','start':T0,'end':'2026-10-13T00:10:00Z','status':'SUCCEEDED'},
              {'run_id':'two','start':T1,'end':'2026-10-13T01:20:00Z','status':'SUCCEEDED'}]
        values=derived_runs('visual',runs,T2,['runs','schedule'],'test',schedule={'next_due':'2026-10-13T01:30:00Z'})
        self.assertEqual(values[0]['value']['median_seconds'],900)
        self.assertTrue(values[1]['value']['overdue'])


@unittest.skipUnless(os.environ.get('DIA_TEST_POSTGRES_FACTS_DSN'),'explicit application PostgreSQL facts test DSN not configured')
class PostgreSQLWorkerFactsTests(unittest.TestCase):
    def test_migrated_schema_as_real_worker_role(self):
        import psycopg
        from investigator.facts_worker_verification import verify_worker_role
        with psycopg.connect(os.environ['DIA_TEST_POSTGRES_FACTS_DSN'],autocommit=True) as connection:
            connection.execute('SET search_path TO dia_state, pg_catalog')
            node=connection.execute('SELECT estate,identity FROM estate_graph_nodes ORDER BY estate,identity LIMIT 1').fetchone()
            self.assertIsNotNone(node,'worker-role test requires a real retained graph subject')
            result=verify_worker_role(connection,estate=node[0],subject=node[1],at=T2)
            self.assertEqual(result['status'],'PASS')
            self.assertEqual(result['role'],'id-dia-worker')
            self.assertEqual(result['writes'],'ROLLED_BACK')


if __name__=='__main__':unittest.main()
