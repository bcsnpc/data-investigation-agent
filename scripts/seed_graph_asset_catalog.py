"""Plan/apply a retained metadata catalog seed; performs no estate discovery."""
import argparse
import json
from pathlib import Path
from investigator.shared_state import sha
from investigator.planner_recording import _safe
from investigator.adapters.estate_graph_static import asset_owners,extract_partitioned
from investigator.estate_graph_contract import timestamp
from scan_estate_graph import validate


def plan(config,payload):
    validate(config)
    if not isinstance(payload,dict)or set(payload)!={'assets','source_asset_ids','observed_at','source_observations'}:
        raise ValueError('GRAPH_SEED_PAYLOAD_SHAPE')
    timestamp(payload['observed_at'])
    _safe(json.dumps(payload,ensure_ascii=False).encode('utf8'))
    owners=asset_owners(payload['assets'])
    if set(payload['source_observations'])!=set(owners):raise ValueError('GRAPH_CATALOG_OBSERVATION_ASSETS_DIFFER')
    if any(timestamp(t)>timestamp(payload['observed_at'])for t in payload['source_observations'].values()):raise ValueError('GRAPH_CATALOG_FUTURE_OBSERVATION')
    if not set(payload['source_asset_ids'])<=set(owners):raise ValueError('GRAPH_SOURCE_DECLARATION_NOT_COLLECTED')
    allowed={'fabric://'+config['workspace']+'/'+item for item in config['owners']}
    for group in config.get('sql',[]):allowed.update(group['objects'])
    if not allowed<=set(owners.values()):raise ValueError('GRAPH_CONFIGURED_OWNER_NOT_SEEDED')
    return {'status':'PLAN_ONLY','estate':config['estate'],'approval':config['approval'],
        'catalog_hash':sha(payload),'assets':len(payload['assets']),'owners':len(set(owners.values())),
        'allowed_refresh_owners':sorted(allowed),'estate_reads':0}


def apply(config,payload):
    result=plan(config,payload)
    from investigator.shared_state import configured_state
    from investigator.estate_graph_repository import GraphRepository
    from investigator.graph_asset_catalog import AssetCatalog
    from investigator.graph_definitions import DefinitionSink
    from investigator.adapters.blob_artifacts import recording_stores
    state=configured_state()
    if state is None:raise ValueError('SHARED_GRAPH_STATE_REQUIRED')
    files,_=recording_stores(config['storage'])
    sink=DefinitionSink(files,config['definition_uri_prefix'],recording_class='EXACT')
    catalog=AssetCatalog(GraphRepository(state),sink,extract_partitioned,asset_owners,
        allowed_owners=result['allowed_refresh_owners'])
    graph=catalog.seed(config['estate'],payload['assets'],observed_at=payload['observed_at'],source_asset_ids=payload['source_asset_ids'],source_observations=payload['source_observations'],existing_graph_only=True)
    return {**result,'status':'SEEDED','graph':graph}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True)
    parser.add_argument('--seed-file',type=Path,required=True)
    parser.add_argument('--receipt',type=Path,required=True)
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    config=json.loads(args.config.read_text(encoding='utf-8-sig'))
    payload=json.loads(args.seed_file.read_text(encoding='utf-8-sig'))
    result=(apply if args.apply else plan)(config,payload)
    with args.receipt.open('x',encoding='utf8')as handle:json.dump(result,handle,indent=2)
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
