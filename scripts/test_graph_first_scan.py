import copy
import tempfile
from pathlib import Path
from unittest.mock import Mock
import pytest
from investigator.shared_state import SharedState
from investigator.artifact_store import Files,LocalObjects
from investigator.graph_definitions import DefinitionSink
from investigator.graph_asset_catalog import AssetCatalog,NAMESPACE
from investigator.estate_graph_repository import GraphRepository
from investigator.adapters.estate_graph_static import extract_partitioned,asset_owners
from test_estate_graph_static import asset
from scan_estate_graph import bootstrap_catalog,require_empty_catalog,validate

@pytest.fixture
def setup():
    with tempfile.TemporaryDirectory() as d:
        state=SharedState.offline(Path(d)/'state.sqlite');repo=GraphRepository(state);repo.migrate()
        sink=DefinitionSink(Files(LocalObjects(Path(d)/'blob')),'cas://definitions',recording_class='EXACT')
        catalog=AssetCatalog(repo,sink,extract_partitioned,asset_owners,allowed_owners=['first','second'])
        source=Mock(configured_owners=('first','second'))
        source.list_changes.return_value={'items':[{'owner':x,'deleted':False,'fingerprint':None}for x in source.configured_owners],'complete':False}
        source.fetch.side_effect=lambda x:{'assets':[asset(x,'Report',x)],'source_asset_ids':[]}
        yield catalog,source,lambda:'2026-10-13T18:00:00Z'

def test_fresh_catalog_collects_only_approved_owners_once_and_keeps_originals(setup):
    cat,source,clock=setup
    result=bootstrap_catalog(cat,source,'sample',clock)
    assert result['bootstrap'] is True
    assert {a['id']for a in cat.snapshot('sample')[1]}=={'first','second'}
    assert source.fetch.call_count==2
    source.reset_mock()
    with pytest.raises(ValueError,match='ALREADY_EXISTS'):bootstrap_catalog(cat,source,'sample',clock)
    source.list_changes.assert_not_called()

def test_failure_never_creates_partial_catalog_or_graph(setup):
    cat,source,clock=setup
    def fetch(owner):
        if owner=='second':raise PermissionError('denied')
        return {'assets':[asset(owner,'Report',owner)],'source_asset_ids':[]}
    source.fetch.side_effect=fetch
    with pytest.raises(PermissionError):bootstrap_catalog(cat,source,'sample',clock)
    with pytest.raises(KeyError):cat.repo.state.get(NAMESPACE,'sample')
    assert cat.repo.records('sample')['nodes']==[]

def test_missing_owner_stops_before_fetch_and_foreign_owner_refused(setup):
    cat,source,clock=setup
    source.list_changes.return_value['items'].pop()
    with pytest.raises(ValueError,match='NOT_VISIBLE'):bootstrap_catalog(cat,source,'sample',clock)
    source.fetch.assert_not_called()

def test_empty_requirement_is_atomic_not_only_preflight(setup):
    cat,source,clock=setup
    assets=[asset('first','Report','first'),asset('second','Report','second')]
    graph=extract_partitioned('sample',assets,cat.sink,observed_at=clock())
    cat.repo.replace_many(graph)
    with pytest.raises(ValueError,match='EMPTY_GRAPH'):require_empty_catalog(cat.repo,'sample')
    from investigator.shared_state import StateConflict
    with pytest.raises(StateConflict,match='EMPTY_GRAPH'):
        cat.seed('sample',assets,observed_at=clock(),require_empty_graph=True)
    with pytest.raises(KeyError):cat.repo.state.get(NAMESPACE,'sample')

def test_gateway_violation_stops_before_next_owner(setup):
    cat,source,clock=setup
    from investigator.live_gateway import GatewayDenied
    source.fetch.side_effect=GatewayDenied('DENIED')
    with pytest.raises(GatewayDenied):bootstrap_catalog(cat,source,'sample',clock)
    assert source.fetch.call_count==1
