import copy
import json
from pathlib import Path
import tempfile
import unittest

from cloud_value_mapping import directlake, endpoint, load_owners, required_columns, script_projection_upstream
from cloud_value_verifier import Refused, measure_program
from test_cloud_value_verifier import fixture, restriction


class MappingTests(unittest.TestCase):
    def test_required_columns_include_dimension_keys_without_inventing_values(self):
        model,_=fixture()
        fields=required_columns(model,measure_program(model,'measure'),[restriction('Dimension.name',['North'])])
        self.assertEqual(fields,['Dimension.id','Dimension.name','Facts.amount','Facts.dim_id'])

    def test_owner_hash_checked_before_parsing(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'body.json').write_text('{}')
            index=root/'index.json';index.write_text(json.dumps({'owners':[{'path':'body.json','sha256':'0'*64}]}))
            with self.assertRaisesRegex(Refused,'OWNER_PAYLOAD_HASH_DIFFERS'):load_owners(index,root)

    def dataset(self):
        container='fabric://workspace/container'
        native=[{'id':container,'kind':'Warehouse','content_hash':'a'*64,'metadata':{'id':'container','properties':{'connectionString':'declared.example'}}},
            {'id':'physical-table','kind':'WarehouseTable','parent_id':container,'metadata':{'schema_name':'serving','name':'renamed'}},
            {'id':'physical-column','kind':'WarehouseColumn','name':'renamed_amount','parent_id':'physical-table','metadata':{'name':'renamed_amount'}}]
        graph={'nodes':[{'id':'semantic','properties':{'asset_id':'Facts.amount'}},{'id':'physical','properties':{'asset_id':'physical-column'}}],
            'edges':[{'id':'bridge','kind':'COMPUTED_FROM','source':'semantic','target':'physical','provenance':{'definition_hash':'b'*64},
            'properties':{'binding_kind':'DIRECTLAKE_ENTITY','container_asset_id':container,'schema':'serving','entity':'renamed',
                'source_column':'renamed_amount','physical_definition':{'definition_hash':'c'*64}}}]}
        return native,graph

    def test_exact_directlake_edge_allows_renamed_storage_column(self):
        model,_=fixture();native,graph=self.dataset()
        mapping=directlake(model,graph,native,['Facts.amount'],[])
        self.assertEqual(mapping['columns'],{'Facts.amount':{'object_id':'physical-table','column':'renamed_amount'}})
        self.assertEqual(mapping['endpoint']['database'],'container')
        self.assertEqual(mapping['provenance'][0]['edge_id'],'bridge')

    def test_equal_name_in_other_container_is_not_a_binding(self):
        model,_=fixture();native,graph=self.dataset();graph['edges'][0]['properties']['container_asset_id']='fabric://workspace/other'
        with self.assertRaisesRegex(Refused,'DIRECTLAKE_CONTAINER_DISAGREES'):directlake(model,graph,native,['Facts.amount'],[])

    def test_lakehouse_endpoint_requires_exact_receipt_not_name(self):
        native=[{'id':'fabric://workspace/lake','kind':'Lakehouse','metadata':{'displayName':'same name'}}]
        with self.assertRaisesRegex(Refused,'LAKEHOUSE_ENDPOINT_BINDING_UNRESOLVED'):endpoint('fabric://workspace/lake',native,[])

    def test_script_projection_keeps_duplicate_writers_and_cross_catalog_gap(self):
        container='fabric://workspace/container'
        mapping={'endpoint':{'container_asset_id':container,'server':'declared.example','database':'declared_db'},
            'objects':{'physical':{'schema':'serving','table':'result','columns':['amount']}},
            'columns':{'Facts.amount':{'object_id':'physical','column':'amount'}},'relationships':[]}
        native=[]
        for i in range(2):
            document={'properties':{'activities':[{'linkedService':{'properties':{'typeProperties':{'artifactId':'container','endpoint':'declared.example'}}},
                'typeProperties':{'database':'declared_db','scripts':[{'text':'CREATE VIEW input.rows AS SELECT amount FROM [external_catalog].[dbo].[raw];'},
                    {'text':'CREATE TABLE serving.result AS SELECT amount FROM input.rows;'}]}}]}}
            native.append({'id':'part'+str(i),'kind':'DefinitionPart','metadata':{'path':'pipeline-content.json','content':json.dumps(document)}})
        result=script_projection_upstream(mapping,native)
        self.assertEqual(result['objects'][container+'/declared-view/input.rows']['availability'],'DECLARED_IN_RETAINED_SCRIPT_NOT_CATALOG_OBSERVED')
        self.assertEqual(len(result['provenance'][0]['alternatives']),4) # All matching writer/view provenance combinations.
        self.assertIn('exact endpoint/container binding',result['remaining_gap'])
        self.assertTrue(all(not a['projection']['execution_established'] for a in result['provenance'][0]['alternatives']))


if __name__=='__main__':unittest.main()
