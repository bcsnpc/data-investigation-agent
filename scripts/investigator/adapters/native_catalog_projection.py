"""Investigation's view of retained assets, independent of inventory bookkeeping.

Identity, native kind, containment and definition metadata describe the asset.
Collector timestamps, scan IDs, hashes and status columns do not establish its
present readability. Optional audit fields never become query prerequisites.
"""
from copy import deepcopy
import hashlib
import json


def project(assets,graph_nodes):
    result={};warnings=[];missing=set()
    proofs_by_asset={}
    for node in graph_nodes:
        proof=node.get('provenance')
        if not isinstance(proof,dict):continue
        for identity in {node.get('properties',{}).get('asset_id'),proof.get('source_id')} - {None}:
            proofs_by_asset.setdefault(identity,[]).append({'node':node['id'],'provenance':proof})
    for raw in assets:
        if raw.get('availability') not in (None,'CURRENT'):
            missing.add('explicitly unavailable retained identities were omitted')
            continue
        asset={key:deepcopy(raw[key]) for key in ('id','kind','name','metadata')}
        asset['parent_id']=raw.get('parent_id')
        # Other top-level bookkeeping fields deliberately never enter the
        # query adapter, so a future collector cannot add a new dependency.
        if raw.get('availability') is not None:asset['availability']=raw['availability']
        else:missing.add('current inventory availability')
        if raw.get('content_hash'):
            asset['content_hash']=raw['content_hash']
        else:
            canonical=json.dumps(asset['metadata'],sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
            asset['content_hash']=hashlib.sha256(canonical).hexdigest()
            asset['content_hash_basis']='DERIVED_RETAINED_METADATA_CANONICAL_JSON'
            missing.add('inventory content hashes (metadata digests are derived and labelled)')
        if raw.get('provenance'):asset['provenance']=deepcopy(raw['provenance'])
        else:
            asset['provenance']={'source':'RETAINED_ASSET_CATALOG','graph_references':deepcopy(proofs_by_asset.get(asset['id'],[])),
                'qualification':'Retained metadata, not a new estate observation or query-bound attestation.'}
            missing.add('inventory provenance')
        if not raw.get('observed_at') and not raw.get('collected_at'):
            missing.add('per-asset collector timestamps')
        result[asset['id']]=asset
    if missing:
        warnings.append('Catalog bookkeeping unavailable: '+', '.join(sorted(missing))+'. This does not block investigation; successful queries establish present readability only.')
    return result,warnings
