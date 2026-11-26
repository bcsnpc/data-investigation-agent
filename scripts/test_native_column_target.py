from copy import deepcopy
from unittest.mock import Mock
import unittest
from investigator.guided_intake import Catalog
from investigator.estate_graph_api import GraphAPI
from investigator.regression_features import configured


class ColumnTargetTests(unittest.TestCase):
    def graph(self):
        nodes=[{'id':'lake','kind':'SOURCE','label':'Operations landing','owner':'lake','properties':{}},
               {'id':'orders','kind':'TABLE','label':'dbo.Rows','owner':'lake','properties':{}},
               {'id':'rates','kind':'TABLE','label':'dbo.Prices','owner':'lake','properties':{}},
               {'id':'order-key','kind':'COLUMN','label':'order_id','owner':'lake','properties':{}},
               {'id':'rate-key','kind':'COLUMN','label':'rate_id','owner':'lake','properties':{}}]
        edges=[{'source':a,'target':b,'kind':'CONTAINS'}for a,b in
               [('lake','orders'),('lake','rates'),('orders','order-key'),('rates','rate-key')]]
        return {'nodes':nodes,'edges':edges,'truncated':False}

    def catalog(self, graph=None):
        graph=graph or self.graph()
        repo=Mock();repo.path_records.return_value=deepcopy(graph)
        gateway=Mock();gateway.graph_objects.side_effect=lambda estate,ids,**kwargs:ids
        api=GraphAPI(repo,gateway,identity='read-only',estate='synthetic',
                     allowed_objects=[n['id']for n in graph['nodes']],at='2026-11-21T00:00:00Z')
        return Catalog(api.intake_catalog()),repo

    def test_column_names_come_only_from_admitted_native_containment(self):
        catalog,repo=self.catalog()
        self.assertEqual(catalog.nodes['orders']['properties']['column_names'],['order_id'])
        self.assertNotIn('order-key',catalog.nodes)
        repo.path_records.assert_called_once()
        self.assertEqual(catalog.table_matches('Operations landing is missing order_id 123')[0]['id'],'orders')

    def test_same_key_on_two_tables_stays_ambiguous(self):
        graph=self.graph();graph['nodes'][-1]['label']='order_id'
        catalog,_=self.catalog(graph)
        self.assertEqual({r['id']for r in catalog.table_matches('Operations landing is missing order_id 123')},
                         {'orders','rates'})

    def test_missing_column_or_container_does_not_create_a_binding(self):
        catalog,_=self.catalog()
        self.assertEqual(catalog.table_matches('Operations landing is missing nonexistent_key 123'),[])
        self.assertEqual(catalog.table_matches('A different place is missing order_id 123'),[])

    def test_unlinked_column_is_not_a_schema_witness(self):
        graph=self.graph();graph['edges']=[e for e in graph['edges']if e['target']!='order-key']
        catalog,_=self.catalog(graph)
        self.assertNotIn('column_names',catalog.nodes['orders']['properties'])
        self.assertEqual(catalog.table_matches('Operations landing is missing order_id 123'),[])

    def test_explicit_child_name_wins_over_a_different_schema_hint(self):
        catalog,_=self.catalog()
        self.assertEqual([x['id']for x in catalog.table_matches('Operations landing dbo.Prices order_id 123')],['rates'])

    def test_flag_off_preserves_prior_projection_and_matching(self):
        pass


if __name__=='__main__':unittest.main()
