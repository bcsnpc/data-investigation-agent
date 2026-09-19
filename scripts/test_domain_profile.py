"""Structural inference never invents business semantics or execution permission."""
import unittest
from unittest.mock import patch
from investigator.domain_profile import infer
from investigator import query_sql, query_dax


def asset(identity,kind,name,parent=None,**metadata):
    return dict(id=identity,kind=kind,name=name,parent_id=parent,metadata=metadata,availability='CURRENT')


class DomainProfileTests(unittest.TestCase):
    def test_roles_follow_declared_edges_not_business_names(self):
        items=[asset('a','SemanticTable','Orchid'),asset('b','SemanticTable','Pebble'),
               asset('k','SemanticColumn','opaque','b',dataType='int64'),
               asset('d','SemanticColumn','z','a',dataType='dateTime'),
               asset('r','SemanticRelationship','edge',fromTable='Orchid',toTable='Pebble',
                     fromCardinality='many',toCardinality='one',fromColumn='x',toColumn='opaque')]
        p=infer(items);a,b=p['tables']
        self.assertEqual(a['role_hypotheses'],['LIKELY_FACT_OR_BRIDGE'])
        self.assertEqual(b['candidate_key_columns'],['k'])
        self.assertEqual(a['date_columns'],['d'])
        self.assertEqual(b['data_profile'],'NOT_MEASURED')
        self.assertEqual(b['grain'],'UNKNOWN_UNTIL_TESTED')
        items[-1]['metadata'].pop('toCardinality')
        self.assertEqual(infer(items)['tables'][1]['role_hypotheses'],['UNKNOWN'])

    def test_incomplete_large_profiles_are_explicit_and_removed_assets_ignored(self):
        items=[asset(str(i).zfill(2),'SemanticTable','t'+str(i)) for i in range(15)]
        items[0]['availability']='REMOVED'
        p=infer(items)
        self.assertTrue(p['tables_truncated']);self.assertEqual(len(p['tables']),12)
        self.assertNotIn('00',[t['asset_id'] for t in p['tables']])
        self.assertEqual(infer([])['tables'],[])

    def test_capability_contracts_track_validators(self):
        self.assertEqual(set(query_dax.capabilities()['supported_functions']),query_dax.FUNCTIONS)
        self.assertEqual(set(query_sql.capabilities()['supported_ast_nodes']),query_sql.NODES-{'Offset','Parameter'})
        self.assertIn('Composite grain',query_sql.capabilities()['experiments'])

    def test_missing_connector_permissions_are_not_advertised_as_execution(self):
        from investigator.flexible_tools import capabilities
        with patch('investigator.source_diagnostics.snapshot',side_effect=ValueError('No pinned catalog')):
            tools=capabilities(None,{'enabled':True,'workspace':'w','native_id':'m'},{'fabric':{}})
        self.assertTrue(all(t['eligibility']=='UNAVAILABLE' for t in tools))
        self.assertTrue(all(t['execution_permission']=='UNKNOWN_UNTIL_DISPATCH' for t in tools))

    def test_large_identifiers_have_a_profile_byte_bound(self):
        from investigator.onboarding import encoded
        items=[asset(str(i)+'x'*1900,'SemanticTable','name'+str(i)) for i in range(12)]
        profile=infer(items)
        self.assertLessEqual(len(encoded(profile)),6000)
        self.assertTrue(profile['tables_truncated'])

    def test_profile_tables_are_retrievable_through_real_handles(self):
        from investigator.dynamic_reasoning import wire_contract
        payload={'observations':[],'candidates':[],'hypotheses':[],
                 'domain_profile':infer([asset('opaque-table','SemanticTable','Neutral')])}
        wire,_,handles=wire_contract(payload)
        self.assertEqual(handles[wire['domain_profile']['tables'][0]['asset_id']],'opaque-table')

    def test_planner_projection_preserves_focus_without_mutating_discovered_profile(self):
        from investigator.domain_profile import for_planner
        from investigator.onboarding import encoded
        profile=infer([asset(str(i)+'x'*180,'SemanticTable','t'+str(i)) for i in range(12)])
        before=encoded(profile);focus=profile['tables'][-1]['asset_id']
        projected=for_planner(profile,focus)
        self.assertLessEqual(len(encoded(projected)),2500)
        self.assertEqual(projected['tables'][0]['asset_id'],focus)
        self.assertTrue(projected['tables_truncated']);self.assertEqual(encoded(profile),before)

    def test_dense_scoped_members_do_not_erase_selected_table(self):
        from investigator.domain_profile import for_planner
        from investigator.onboarding import encoded
        identity='workspace/'+'a'*36+'/model/'+'b'*36+'/table/Neutral'
        items=[asset(identity,'SemanticTable','Neutral')]
        for i in range(8):
            items.append(asset(identity+'/column/'+str(i),'SemanticColumn',str(i),identity,dataType='double'))
            items.append(asset(identity+'/measure/'+str(i),'Measure',str(i),identity))
        profile=infer(items);before=encoded(profile)
        projected=for_planner(profile,identity)
        self.assertLessEqual(len(encoded(projected)),2500)
        table=projected['tables'][0]
        self.assertEqual(table['asset_id'],identity)
        self.assertEqual(table['numeric_columns_profile_count'],8)
        self.assertEqual(table['measure_ids_profile_count'],8)
        self.assertTrue(table['numeric_columns'])
        self.assertTrue(table['measure_ids'])
        self.assertTrue(table['truncated'])
        self.assertEqual(encoded(profile),before)

    def test_structural_experiments_use_existing_governed_sql(self):
        obj={'id':'opaque','metadata':{'schema_name':'approved','name':'entities','type_desc':'USER_TABLE',
             'columns':[{'name':n,'data_type':'int'} for n in ('a','b')]}}
        queries=[
            'SELECT COUNT(*) AS rows, COUNT(DISTINCT a) AS distinct_a, COUNT(a) AS nonnull_a FROM approved.entities',
            'SELECT a,b,COUNT(*) AS copies FROM approved.entities GROUP BY a,b HAVING COUNT(*)>1',
            'SELECT a,COUNT(DISTINCT b) AS values_b,COUNT(*)-COUNT(b) AS null_b FROM approved.entities GROUP BY a HAVING COUNT(DISTINCT b)>1',
            'SELECT COUNT(*) AS joined_rows FROM approved.entities x LEFT JOIN approved.entities y ON x.a=y.a']
        for query in queries:
            with self.subTest(query=query):
                result=query_sql.compile_query(query,[obj],max_rows=10)
                self.assertEqual(result['asset_ids'],['opaque'])
                self.assertEqual(result['max_rows'],11)
        with self.assertRaises(ValueError):
            query_sql.compile_query(queries[0].replace('approved.entities','unapproved.entities'),[obj])


if __name__=='__main__':unittest.main()
