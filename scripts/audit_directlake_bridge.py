"""Hash-pinned, offline before/after extraction; never queries the estate."""
import argparse,hashlib,json
from pathlib import Path
from unittest.mock import patch
from collections import Counter
from datetime import datetime,timezone
from investigator.adapters.estate_graph_static import StaticGraph,extract_partitioned,retained_lakehouse_endpoint_assets
from graph_coverage_report import coverage


def digest(raw):return hashlib.sha256(raw).hexdigest()
def audit(workspace,catalog_root,baseline_root,endpoints,output):
    workspace,catalog_root,baseline_root,output=map(Path,(workspace,catalog_root,baseline_root,output))
    output.mkdir(parents=True,exist_ok=True)
    endpoint_raw=Path(endpoints).read_bytes()
    report={'estate_reads':0,'model_calls':0,'endpoint_receipt_sha256':digest(endpoint_raw),
        'at':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'endpoint_time_basis':'Retained receipt observed during offline audit; native response has no service-observation timestamp.',
        'estates':{}}
    for estate in ('fixture','billing'):
        index_raw=(catalog_root/estate/'index.json').read_bytes();index=json.loads(index_raw)
        assets=[];sources=[];observations={};pins=[]
        for owner in index['owners']:
            raw=(workspace/owner['path']).read_bytes()
            if digest(raw)!=owner['sha256'] or len(raw)!=owner['bytes']:raise ValueError('OWNER_PAYLOAD_PIN_DIFFERS')
            payload=json.loads(raw);assets.extend(payload['assets']);sources.extend(payload['source_asset_ids'])
            observations.update({a['id']:owner['observed_at'] for a in payload['assets']})
            pins.append({'owner':owner['owner'],'sha256':owner['sha256'],'bytes':len(raw)})
        baseline_raw=(baseline_root/(estate+'-graph.json')).read_bytes();baseline=json.loads(baseline_raw)
        at=report['at']
        def sink(raw):return {'sha256':digest(raw),'bytes':len(raw),
            'uri':'https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/'+digest(raw)}
        def build(more=()):
            parts=extract_partitioned(estate,assets+list(more),sink,observed_at=at,source_asset_ids=sources,source_observations=observations)
            return {'nodes':[n for p in parts for n in p['nodes']], 'edges':[e for p in parts for e in p['edges']],
                    'truncated':False,'unavailable_owners':baseline.get('unavailable_owners',{})}
        with patch.object(StaticGraph,'entity_partition',lambda *a:None):before=build()
        parser=build()
        # The native endpoint receipt is only applicable to its own workspace.
        more=retained_lakehouse_endpoint_assets(endpoint_raw,observed_at=at)
        known={a['id'] for a in assets};more=[a for a in more if a['parent_id'] in known]
        enriched=build(more)
        stages={}
        for name,graph in [('before',before),('parser_only',parser),('with_retained_endpoints',enriched)]:
            nodes={n['id']:n for n in graph['nodes']}
            edges=[e for e in graph['edges'] if e['properties'].get('binding_kind')=='DIRECTLAKE_ENTITY']
            counts=coverage(graph,baseline)
            if counts['new_start_ids'] or counts['removed_start_ids']:raise ValueError('START_IDENTITY_CHANGED')
            stages[name]={'graph_sha256':digest(json.dumps(graph,sort_keys=True,separators=(',',':')).encode()),
                'bindings_by_source_kind':dict(Counter(nodes[e['source']]['kind'] for e in edges)),
                'coverage':counts}
            (output/(estate+'-'+name+'-graph.json')).write_text(json.dumps(graph,indent=2))
        report['estates'][estate]={'index_sha256':digest(index_raw),'source_manifest_sha256':index['source_manifest_sha256'],
            'baseline_graph_sha256':digest(baseline_raw),'owner_payloads':pins,'stages':stages}
    (output/'audit.json').write_text(json.dumps(report,indent=2))
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('workspace','catalog-root','baseline-root','endpoints','output'):parser.add_argument('--'+name,required=True)
    a=parser.parse_args();r=audit(a.workspace,a.catalog_root,a.baseline_root,a.endpoints,a.output)
    print(json.dumps({e:{k:{'bindings':v['bindings_by_source_kind'],'cohort':v['coverage']['baseline_cohort']} for k,v in x['stages'].items()} for e,x in r['estates'].items()},indent=2))
