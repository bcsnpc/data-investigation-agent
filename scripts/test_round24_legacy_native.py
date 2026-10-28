import json,unittest,hashlib,copy
import test_estate_graph_static as fixtures
from investigator.adapters.estate_graph_static import extract
class LegacyNativeTests(unittest.TestCase):
 def build(self,duplicate=False):
  assets=fixtures.StaticTests().assets();assets=[a for a in assets if a['kind']not in('ReportVisual','ReportPage') and not(a['kind']=='DefinitionPart' and a['id']not in ('binding',))]
  aliases=[{'Name':'d','Entity':'Data'}]
  if duplicate:aliases.append({'Name':'d','Entity':'DifferentTable'})
  query={'From':aliases,'Select':[{'Column':{'Expression':{'SourceRef':{'Source':'d'}},'Property':'Region'}}]}
  raw=json.dumps({'name':'card','singleVisual':{'visualType':'card','prototypeQuery':query}})
  visual={'config':raw,'filters':'[]','queryBinary':'opaque-native-bytes'};page={'name':'page','displayName':'Page','visualContainers':[visual]};layout={'sections':[page]}
  assets += [fixtures.part('layout','r','report.json',layout),fixtures.asset('r/page/page','ReportPage','Page','r',page),fixtures.asset('r/page/page/visual/card','ReportVisual','card','r/page/page',visual)]
  stored={}
  def sink(value):
   h=hashlib.sha256(value).hexdigest();stored[h]=value;return {'sha256':h,'bytes':len(value),'uri':'cas://'+h}
  graph=extract('estate',assets,sink,observed_at=fixtures.NOW,owner='owner')
  return graph,stored,raw
 def test_exact_native_prototype_reference_is_retained_without_claiming_legacy_scope(self):
  graph,stored,raw=self.build();nodes={n['id']:n for n in graph['nodes']};visual=next(n for n in nodes.values()if n['properties'].get('asset_id')=='r/page/page/visual/card');column=next(n for n in nodes.values()if n['properties'].get('asset_id','').endswith('/t/c'))
  edges=[e for e in graph['edges']if e['source']==visual['id']and e['kind']=='COMPUTED_FROM'and e['target']==column['id']];self.assertEqual(len(edges),1)
  at=edges[0]['provenance'];self.assertEqual(stored[at['definition_hash']],raw.encode());self.assertEqual(at['span']['path'],'/singleVisual/prototypeQuery/Select/0/Column')
  self.assertTrue(any(n['confidence']=='UNKNOWN'and 'filter and interaction'in n['label']for n in nodes.values()))
 def test_conflicting_native_alias_is_not_resolved_by_last_entry(self):
  graph,_,_=self.build(True);nodes={n['id']:n for n in graph['nodes']};visual=next(n for n in nodes.values()if n['properties'].get('asset_id')=='r/page/page/visual/card');self.assertFalse(any(e['source']==visual['id']and e['kind']=='COMPUTED_FROM'and nodes[e['target']]['kind']=='COLUMN'for e in graph['edges']))
if __name__=='__main__':unittest.main()
