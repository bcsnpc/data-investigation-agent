import hashlib
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from prepare_live_enrichment import prepare
from enrich_estate import tasks_from_graph


class FullRetainedPreparation(unittest.TestCase):
    def node(self,identity,kind='REPORT',definition='{"expression":"SUM(units)"}'):
        return {'id':identity,'kind':kind,'label':identity,'properties':{'definition':definition},
            'provenance':{'definition_hash':hashlib.sha256(definition.encode()).hexdigest(),'source_id':'retained:'+identity}}
    def test_every_visual_includes_slicer_and_only_configured_key_tables(self):
        nodes=[self.node('slicer','SLICER'),self.node('key','TABLE'),self.node('other','TABLE')]
        repository=SimpleNamespace(records=lambda *args,**kwargs:{'nodes':nodes,'edges':[],'truncated':False})
        tasks=tasks_from_graph(repository,'fixture',key_tables=['key'])
        self.assertEqual({task['subject'] for task in tasks},{'slicer','key'})
    def test_all_nodes_chunked_without_truncation_with_missing_definition_gap(self):
        with tempfile.TemporaryDirectory() as root:
            nodes=[self.node('report'+str(index)) for index in range(51)]
            nodes.append(self.node('slicer','SLICER'));nodes.append(self.node('key','TABLE'))
            nodes.append(self.node('not-key','TABLE'));missing=self.node('missing','MEASURE')
            missing['properties']['definition']={'bytes':5,'sha256':'a'*64,'uri':'https://fixture/files/'+('a'*64)};nodes.append(missing)
            result=prepare({'fixture':{'nodes':nodes,'edges':[]}},root,Path(root)/'out',key_tables={'fixture':['key']})
            self.assertEqual(result['estates'][0]['candidate_count'],54)
            self.assertEqual(result['estates'][0]['ready_tasks'],53)
            self.assertEqual([batch['tasks'] for batch in result['batches']],[50,3])
            self.assertEqual(result['estates'][0]['gaps'][0]['reason'],'DEFINITION_BYTES_NOT_LOCAL')
            self.assertEqual(result['estates'][0]['other_tables_not_selected'],1)
            self.assertEqual(result['provider_calls'],0)
    def test_oversized_definition_is_coverage_gap_not_truncated(self):
        with tempfile.TemporaryDirectory() as root:
            result=prepare({'fixture':{'nodes':[self.node('large','REPORT','x'*24001)],'edges':[]}},root,Path(root)/'out')
            self.assertEqual(result['estates'][0]['ready_tasks'],0)
            self.assertEqual(result['estates'][0]['gaps'][0]['reason'],'ENRICHMENT_DEFINITION_BOUND')


if __name__=='__main__':unittest.main()
