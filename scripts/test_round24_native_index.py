import unittest,tempfile
from pathlib import Path
from unittest.mock import Mock
from investigator.shared_state import SharedState
from investigator.estate_graph_repository import GraphRepository
from investigator.estate_graph_api import GraphAPI
from investigator.adapters.ai_native_catalog import NativeCatalog
from test_estate_graph import proof,T0
from investigator import estate_graph_contract as c
class NativeIndexTests(unittest.TestCase):
 def test_column_and_step_survive_native_index_while_form_catalog_stays_small(self):
  with tempfile.TemporaryDirectory()as folder:
   state=SharedState.offline(Path(folder)/'s.sqlite');repo=GraphRepository(state);repo.migrate()
   nodes=[c.node('table','owner','TABLE','Table',proof(),properties={'asset_id':'table'}),c.node('column','owner','COLUMN','quantity',proof(),properties={'asset_id':'column'}),c.node('step','owner','QUERY_STEP','Producer',proof(),properties={})]
   repo.replace({'estate':'estate','owner':'owner','definition_hash':'a'*64,'observed_at':T0,'nodes':nodes,'edges':[]})
   gateway=Mock();gateway.graph_objects.side_effect=lambda estate,ids,**kw:list(ids)
   graph=GraphAPI(repo,gateway,identity='reader',estate='estate',allowed_objects={n['id']for n in nodes})
   self.assertNotIn('column',{n['id']for n in graph.intake_catalog()['nodes']})
   native=graph.native_index();self.assertEqual({n['id']for n in native['nodes']},{'table','column','step'});self.assertFalse(native['definition_bodies_included'])
   with unittest.mock.patch.object(NativeCatalog,'__init__',return_value=None)as create:
    NativeCatalog.from_graph(graph,assets=[],configuration={},endpoint=Mock(),sql_read=Mock(),record=Mock())
   self.assertIn('column',{n['id']for n in create.call_args.kwargs['graph_nodes']})
if __name__=='__main__':unittest.main()
