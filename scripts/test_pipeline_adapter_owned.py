"""Prepared test: run after applying the private collector patch."""
import copy
import json
from pathlib import Path
import unittest
from investigator.adapters.microsoft_load_declarations import declared_source_connections

class PipelineDeclaredConnectionTests(unittest.TestCase):
    def test_retained_pipeline_source_connections_are_native_declarations(self):
        raw=Path('fixture-code/billing/published-20261009/pipeline-content.json').read_text()
        value=json.loads(raw)
        expected={activity['typeProperties']['source']['datasetSettings']['externalReferences']['connection']
            for activity in value['properties']['activities'] if activity['type']=='Copy'}
        self.assertEqual(expected, declared_source_connections('pipeline-content.json', value))
    def test_sinks_and_script_connections_cannot_become_source_provenance(self):
        document={'properties':{'activities':[{'type':'Script','externalReferences':{'connection':'not-source'}},
            {'type':'Copy','typeProperties':{'source':{'type':'Other'},'sink':{'externalReferences':{'connection':'not-source'}}}}]}}
        self.assertEqual(set(), declared_source_connections('pipeline-content.json', document))
    def test_unknown_definition_does_not_invent_a_connection(self):
        self.assertEqual(set(), declared_source_connections('unknown.json', {'externalReferences':{'connection':'not-source'}}))
    def test_sql_source_missing_connection_is_not_complete(self):
        document={'properties':{'activities':[{'type':'Copy','typeProperties':{'source':{'type':'AzureSqlSource',
            'datasetSettings':{'type':'AzureSqlTable','externalReferences':{}}}}}]}}
        with self.assertRaisesRegex(ValueError,'connection declaration unavailable'):
            declared_source_connections('pipeline-content.json', document)
    def test_nested_copy_source_retains_declared_connection_only(self):
        ref='12345678-1234-1234-1234-123456789abc'
        copy_activity={'type':'Copy','typeProperties':{'source':{'type':'AzureSqlSource','datasetSettings':{
            'type':'AzureSqlTable','externalReferences':{'connection':ref}}}}}
        value={'properties':{'activities':[{'type':'IfCondition','typeProperties':{'ifTrueActivities':[copy_activity]}}]}}
        self.assertEqual({ref},declared_source_connections('pipeline-content.json',value))
