import base64,hashlib,json
from unittest.mock import Mock
import pytest
from metadata_inventory import expand_definition
from investigator.adapters.graph_change_collector import Assets,FabricChanges,failure_definition_reference
from investigator.adapters.estate_graph_static import extract

W='11111111-1111-1111-1111-111111111111';R='22222222-2222-2222-2222-222222222222';OWNER='fabric://'+W+'/'+R

def layout():return {'sections':[{'name':'P','displayName':'Overview','filters':'[]','visualContainers':[{'config':json.dumps({'name':'V','singleVisual':{'visualType':'slicer'}}),'filters':'[]','query':'{"Commands":[]}'}]}]}
def parts(doc):return {'report.json':json.dumps(doc)}
def test_legacy_pages_visuals_keep_raw_content_and_real_parent_identity():
    doc=layout();raw=parts(doc);store=Assets()
    expand_definition(store,OWNER,'Report',raw,'read')
    assert next(a for a in store.values if a['kind']=='ReportPage')['metadata']==doc['sections'][0]
    visual=next(a for a in store.values if a['kind']=='ReportVisual')
    assert visual['parent_id']==OWNER+'/page/P'
    assert visual['metadata']==doc['sections'][0]['visualContainers'][0]
    assert [a['name']for a in store.values if a['kind']=='DefinitionPart']==['report.json']

def test_legacy_graph_provenance_points_into_original_and_semantics_remain_unknown():
    doc=layout();raw=parts(doc);store=Assets();store.asset(OWNER,'Report','Report','read',{})
    expand_definition(store,OWNER,'Report',raw,'read');retained={}
    def sink(raw):
        h=hashlib.sha256(raw).hexdigest();retained[h]=raw
        return {'sha256':h,'bytes':len(raw),'uri':'cas://definitions/files/'+h}
    graph=extract('test',store.values,sink,observed_at='2026-10-13T00:00:00Z')
    visual=next(n for n in graph['nodes']if n['kind']=='SLICER')
    assert visual['provenance']['span']['path']=='/sections/0/visualContainers/0'
    assert retained[visual['provenance']['definition_hash']].decode()==raw['report.json']
    assert visual['properties']['native_format']=='PBIR_LEGACY'
    assert any(e['source']==visual['id'] and e['confidence']=='UNKNOWN'for e in graph['edges'])
    assert not any(e['kind']=='FILTERED_BY'for e in graph['edges'])

def test_ambiguous_mixed_and_malformed_legacy_refuse():
    bad=layout();bad['sections'][0]['visualContainers']*=2
    with pytest.raises(ValueError,match='IDENTITY'):expand_definition(Assets(),OWNER,'Report',parts(bad),'read')
    with pytest.raises(ValueError,match='Mixed'):expand_definition(Assets(),OWNER,'Report',{**parts(layout()),'definition/pages/P/page.json':'{}'},'read')
    with pytest.raises(ValueError,match='Mixed'):expand_definition(Assets(),OWNER,'Report',{**parts(layout()),'definition/report.json':'{}'},'read')
    with pytest.raises(ValueError,match='PAGE_BOUND'):expand_definition(Assets(),OWNER,'Report',{'report.json':'{}'},'read')

def test_failed_expansion_retains_native_envelope_before_interpreting_and_binds_owner():
    returned={'unknown.json':'{"opaque":true}'}
    http=Mock(return_value={'status_code':200,'text':{'definition':{'parts':[{'path':k,'payloadType':'InlineBase64','payload':base64.b64encode(v.encode()).decode()}for k,v in returned.items()]}}})
    retained=[]
    def retain(raw):
        retained.append(raw);h=hashlib.sha256(raw).hexdigest();return {'sha256':h,'bytes':len(raw),'uri':'cas://definitions/files/'+h}
    c=FabricChanges(W,[R],http,retain_definition=retain);c.items={R:{'id':R,'type':'Report','displayName':'Report'}}
    with pytest.raises(ValueError,match='Native PBIR pages unavailable')as err:c.fetch(OWNER)
    assert json.loads(retained[0])['parts']==returned
    assert failure_definition_reference(err.value,OWNER)['sha256']==hashlib.sha256(retained[0]).hexdigest()
    assert failure_definition_reference(err.value,'another-owner') is None
    forged=ValueError();forged._graph_definition_failure={'owner':OWNER,'reference':'forged'}
    assert failure_definition_reference(forged,OWNER) is None


@pytest.mark.parametrize('bootstrap',[True,False])
def test_failed_native_decode_health_keeps_reference_without_current_publication(tmp_path,bootstrap):
    from investigator.shared_state import SharedState,encoded
    from investigator.artifact_store import Files,LocalObjects
    from investigator.graph_definitions import DefinitionSink
    from investigator.graph_asset_catalog import AssetCatalog,NAMESPACE
    from investigator.estate_graph_repository import GraphRepository
    from investigator.adapters.estate_graph_static import extract_partitioned,asset_owners
    from investigator.estate_graph_incremental import IncrementalScanner
    from scan_estate_graph import bootstrap_catalog
    state=SharedState.offline(tmp_path/'state.sqlite');repo=GraphRepository(state);repo.migrate()
    sink=DefinitionSink(Files(LocalObjects(tmp_path/'blob')),'cas://definitions',recording_class='EXACT')
    cat=AssetCatalog(repo,sink,extract_partitioned,asset_owners,allowed_owners=[OWNER])
    returned={'unknown.json':'{"opaque":true}'}
    http=Mock(return_value={'status_code':200,'text':{'definition':{'parts':[{'path':k,'payloadType':'InlineBase64','payload':base64.b64encode(v.encode()).decode()}for k,v in returned.items()]}}})
    source=FabricChanges(W,[R],http,retain_definition=sink)
    source.items={R:{'id':R,'type':'Report','displayName':'Report'}}
    source.list_changes=lambda:{'items':[{'owner':OWNER,'deleted':False,'fingerprint':None}],'complete':False}
    if bootstrap:
        with pytest.raises(ValueError,match='Native PBIR pages unavailable'):
            bootstrap_catalog(cat,source,'sample',lambda:'2026-10-13T18:00:00Z')
    else:
        result=IncrementalScanner(repo,source,Mock()).run('sample','2026-10-13T18:00:00Z')
        assert result['owners'][0]['status']=='UNAVAILABLE'
    event=state.get('graph_owner_collection',encoded(['sample',OWNER]))['body']['events'][-1]
    assert event['status']=='UNAVAILABLE'
    assert event['payload_reference']['sha256']==hashlib.sha256(encoded({'owner':OWNER,'kind':'Report',
        'endpoint':'workspaces/'+W+'/items/'+R+'/getDefinition','parts':returned}).encode()).hexdigest()
    assert repo.records('sample')['nodes']==[]
    with pytest.raises(KeyError):state.get(NAMESPACE,'sample')
    assert http.call_count==1
