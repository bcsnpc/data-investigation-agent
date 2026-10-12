import copy
import unittest
from investigator.adapters.microsoft_copy_mapping import infer_column_mapping


class CopyAutoMappingTests(unittest.TestCase):
    def setUp(self):
        self.activity = {'name':'Load','type':'Copy','typeProperties':{
            'source':{'type':'AzureSqlSource','sqlReaderQuery':'SELECT [id], CAST(stamp AS bigint) AS stamp FROM app.events',
                      'datasetSettings':{'typeProperties':{'schema':'app','table':'events'}}},
            'sink':{'type':'LakehouseTableSink','tableActionOption':'OverwriteSchema','datasetSettings':{'table':'events'}}}}
        self.src = [{'name':'id','data_type':'int','computed_definition':None},{'name':'stamp','data_type':'timestamp','computed_definition':None}]
        self.dst = [{'name':'id','data_type':'int'},{'name':'stamp','data_type':'bigint'}]

    def test_each_inferred_mapping_is_unverified_and_cast_is_not_identity(self):
        before = copy.deepcopy(self.activity)
        result = infer_column_mapping(self.activity,self.src,self.dst)
        self.assertEqual(self.activity,before)
        self.assertEqual(result['verification'],'UNVERIFIED')
        self.assertEqual([m['unchanged_column'] for m in result['mappings']],[True,False])
        self.assertTrue(all(m['provenance']=='INFERRED_FROM_CODE' and m['verification']=='UNVERIFIED' for m in result['mappings']))
        self.assertEqual(result['mappings'][1]['source_type'],'timestamp')
        self.assertEqual(result['mappings'][1]['destination_type'],'bigint')

    def test_predicate_wrong_object_duplicate_missing_extra_and_unknown_expression_refuse(self):
        for query in ('SELECT id,stamp FROM app.events WHERE id=1',
                      'SELECT id,stamp FROM app.other','SELECT id,id FROM app.events',
                      'SELECT id FROM app.events','SELECT id,stamp+1 AS stamp FROM app.events',
                      'SELECT * FROM app.events','SELECT id,stamp FROM app.events; SELECT 1'):
            with self.subTest(query=query):
                self.activity['typeProperties']['source']['sqlReaderQuery']=query
                with self.assertRaises(ValueError):infer_column_mapping(self.activity,self.src,self.dst)

    def test_proposals_preserve_cast_exclusion_and_refuse_append(self):
        import json
        from investigator.adapters.microsoft_copy_mapping import column_proposals
        mapping=infer_column_mapping(self.activity,self.src,self.dst)
        part={'parent_id':'pipeline','metadata':{'path':'pipeline-content.json','content':json.dumps({'activities':[self.activity]},indent=2)}}
        kwargs={'source_asset':{'id':'source'},'destination_asset':{'id':'destination'},'part':part,'boundary':{'from_layer':'input','to_layer':'output'}}
        result=column_proposals(mapping,**kwargs)
        self.assertEqual(len(result['proposals']),1)
        self.assertEqual(result['excluded'][0]['column'],'stamp')
        self.assertEqual(result['verification'],'UNVERIFIED')
        mapping['row_delivery']='Append'
        with self.assertRaises(ValueError):column_proposals(mapping,**kwargs)

    def test_explicit_translator_never_treated_as_auto(self):
        self.activity['typeProperties']['translator']={}
        with self.assertRaises(ValueError):infer_column_mapping(self.activity,self.src,self.dst)

    def test_ambiguous_case_and_unmatched_destination_refuse(self):
        for dst in (self.dst+[{'name':'Id','data_type':'int'}], self.dst+[{'name':'new','data_type':'int'}]):
            with self.assertRaises(ValueError):infer_column_mapping(self.activity,self.src,dst)


if __name__=='__main__':unittest.main()
