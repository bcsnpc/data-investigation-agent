"""Hash-pinned owner asset catalogs with atomic graph and manifest revision CAS.

Blob uploads happen before the short shared-state transaction. A competing
refresh leaves an unreferenced immutable blob, never a lost catalog update.
"""
import copy
import hashlib
import json
from .shared_state import encoded,sha,StateConflict
from . import estate_graph_contract as contract
from .planner_recording import _safe

NAMESPACE='graph_asset_catalog'
VERSION=1
MAX_ASSETS=50000
MAX_BYTES=256*1024*1024


class AssetCatalog:
    def __init__(self,repository,sink,partition,owner_for,*,allowed_owners):
        from .privacy_capture import ACTIVE
        import os
        if ACTIVE.get() is not None or os.environ.get('INVESTIGATOR_RECORDING_CLASS','EXACT')!='EXACT':
            raise ValueError('GRAPH_PROJECTED_DEFINITION_CAPTURE_NOT_IMPLEMENTED')
        self.repo,self.sink,self.partition,self.owner_for=repository,sink,partition,owner_for
        if not isinstance(allowed_owners,(list,tuple,set,frozenset)) or not 1<=len(allowed_owners)<=1000:
            raise ValueError('GRAPH_CATALOG_OWNER_ALLOWLIST')
        if any(not isinstance(x,str)or not x for x in allowed_owners):raise ValueError('GRAPH_CATALOG_OWNER_ALLOWLIST')
        self.allowed=set(allowed_owners)

    def _payload(self,owner,payload):
        if set(payload)!={'assets','source_asset_ids'}or not isinstance(payload['assets'],list)or not isinstance(payload['source_asset_ids'],list):
            raise ValueError('GRAPH_CATALOG_PAYLOAD_SHAPE')
        assets=payload['assets'];ids=[a['id']for a in assets]
        if len(ids)>MAX_ASSETS or len(set(ids))!=len(ids)or not set(payload['source_asset_ids'])<=set(ids):
            raise ValueError('GRAPH_CATALOG_ASSET_BOUND_OR_IDENTITY')
        owners=self.owner_for(assets)
        if any(value!=owner for value in owners.values()) or set(owners)!=set(ids):
            raise ValueError('GRAPH_CATALOG_PAYLOAD_LEAVES_OWNER')
        raw=encoded(payload).encode('utf8');_safe(raw)
        return raw

    def snapshot(self,estate):
        try:record=self.repo.state.get(NAMESPACE,estate)
        except KeyError:raise ValueError('GRAPH_RETAINED_ASSET_CATALOG_REQUIRED')from None
        body=record['body']
        if set(body)!={'version','owners'}or body['version']!=VERSION or not isinstance(body['owners'],dict)or len(body['owners'])>1000:
            raise ValueError('GRAPH_CATALOG_MANIFEST_SHAPE')
        assets=[];sources=[];observations={};total=0
        for owner,entry in sorted(body['owners'].items()):
            if set(entry)!={'reference','observed_at','source_observations'}:raise ValueError('GRAPH_CATALOG_OWNER_SHAPE')
            observed=contract.timestamp(entry['observed_at'])
            raw=self.sink.read(entry['reference']);total+=len(raw)
            if total>MAX_BYTES:raise ValueError('GRAPH_CATALOG_TOTAL_BYTE_BOUND')
            payload=json.loads(raw)
            if self._payload(owner,payload)!=raw:raise ValueError('GRAPH_CATALOG_PAYLOAD_NOT_CANONICAL')
            assets.extend(payload['assets']);sources.extend(payload['source_asset_ids'])
            if set(entry['source_observations'])!={a['id']for a in payload['assets']}:raise ValueError('GRAPH_CATALOG_OBSERVATION_ASSETS_DIFFER')
            observations.update({key:contract.timestamp(value) for key,value in entry['source_observations'].items()})
        if len(assets)>MAX_ASSETS or len(observations)!=len(assets):raise ValueError('GRAPH_CATALOG_DUPLICATE_OR_ASSET_BOUND')
        return record,assets,sources,observations

    def _commit(self,estate,at,manifest,partitions,revision,*,existing_graph_only=False,retire_missing=False):
        # One lock and transaction: stale readers cannot overwrite any partition
        # or the owner references after another refresh commits.
        with self.repo.state.transaction()as db:
            try:prior=self.repo.state._get(db,NAMESPACE,estate)
            except KeyError:prior=None
            if (None if prior is None else prior['revision'])!=revision:
                raise StateConflict('GRAPH_ASSET_CATALOG_REVISION_DIFFERS')
            if existing_graph_only:
                actual=dict(self.repo.state.sql(db,'SELECT owner,definition_hash FROM estate_graph_owner_versions WHERE estate=?',(estate,)).fetchall())
                expected={p['owner']:p['definition_hash']for p in partitions}
                if actual!=expected:raise StateConflict('GRAPH_SEED_CURRENT_PARTITION_HASHES_DIFFER')
                result={'status':'UNCHANGED','changed':0}
            else:
                if retire_missing:
                    present={p['owner']for p in partitions}
                    prior_owners={row[0]for row in self.repo.state.sql(db,'SELECT owner FROM estate_graph_owner_versions WHERE estate=?',(estate,)).fetchall()}
                    for owner in (prior_owners & set(manifest['owners']))-present:
                        partitions.append({'estate':estate,'owner':owner,'observed_at':at,'definition_hash':sha({'empty_owner':owner}),'nodes':[],'edges':[]})
                result=self.repo.replace_many(partitions,_db=db)
            if prior is None:
                self.repo.state.sql(db,'INSERT INTO state_documents VALUES(?,?,?,?,?)',(NAMESPACE,estate,0,encoded(manifest),sha(manifest)))
            else:
                self.repo.state.sql(db,'UPDATE state_documents SET revision=?,body=?,body_hash=? WHERE namespace=? AND identity=?',
                    (revision+1,encoded(manifest),sha(manifest),NAMESPACE,estate))
        return result

    def seed(self,estate,assets,*,observed_at,source_asset_ids=(),source_observations=None,existing_graph_only=False):
        at=contract.timestamp(observed_at)
        if not isinstance(assets,list)or not assets or len(assets)>MAX_ASSETS:raise ValueError('GRAPH_CATALOG_ASSET_BOUND')
        if len({a['id']for a in assets})!=len(assets):raise ValueError('GRAPH_CATALOG_DUPLICATE_ASSET')
        if not set(source_asset_ids)<={a['id']for a in assets}:raise ValueError('GRAPH_SOURCE_DECLARATION_NOT_COLLECTED')
        times=source_observations if source_observations is not None else {a['id']:at for a in assets}
        if set(times)!={a['id']for a in assets}:raise ValueError('GRAPH_CATALOG_OBSERVATION_ASSETS_DIFFER')
        times={key:contract.timestamp(value)for key,value in times.items()}
        if any(value>at for value in times.values()):raise ValueError('GRAPH_CATALOG_FUTURE_OBSERVATION')
        owners=self.owner_for(assets);groups={}
        for asset in assets:groups.setdefault(owners[asset['id']],[]).append(asset)
        if not self.allowed<=set(groups):raise ValueError('GRAPH_CONFIGURED_OWNER_NOT_SEEDED')
        if len(groups)>1000:raise ValueError('GRAPH_CATALOG_OWNER_BOUND')
        manifest={'version':VERSION,'owners':{}};total=0
        for owner,values in sorted(groups.items()):
            payload={'assets':sorted(values,key=lambda a:a['id']),'source_asset_ids':sorted(set(source_asset_ids)&{a['id']for a in values})}
            raw=self._payload(owner,payload);total+=len(raw)
            if total>MAX_BYTES:raise ValueError('GRAPH_CATALOG_TOTAL_BYTE_BOUND')
            manifest['owners'][owner]={'reference':self.sink(raw),'observed_at':at,
                'source_observations':{a['id']:times[a['id']] for a in values}}
        def retained_reference(raw):
            return {'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),
                'uri':self.sink.uri_prefix+'/files/'+hashlib.sha256(raw).hexdigest()}
        partitions=self.partition(estate,assets,retained_reference if existing_graph_only else self.sink,observed_at=at,source_asset_ids=source_asset_ids,
            source_observations=times)
        return self._commit(estate,at,manifest,partitions,None,existing_graph_only=existing_graph_only)

    def refresh(self,estate,owner,at,payload,*,retained_asset_ids=()):
        at=contract.timestamp(at)
        if owner not in self.allowed:raise ValueError('GRAPH_REFRESH_OWNER_NOT_APPROVED')
        old,assets,sources,observations=self.snapshot(estate)
        if owner not in old['body']['owners']:raise ValueError('GRAPH_REFRESH_OWNER_NOT_SEEDED')
        if at<=old['body']['owners'][owner]['observed_at']:raise StateConflict('GRAPH_CATALOG_TIME_MUST_ADVANCE')
        retained=set(retained_asset_ids)
        owner_map=self.owner_for(assets)
        original={a['id']:a for a in assets if owner_map[a['id']]==owner}
        proposed={a['id']:a for a in payload['assets']}
        if not retained<=original.keys() or any(proposed.get(key)!=original[key] for key in retained):
            raise ValueError('GRAPH_RETAINED_ASSET_CONTENT_DIFFERS')
        times={a['id']:observations[a['id']] if a['id'] in retained else at for a in payload['assets']}
        raw=self._payload(owner,payload);manifest=copy.deepcopy(old['body'])
        if sum(v['reference']['bytes']for k,v in manifest['owners'].items()if k!=owner)+len(raw)>MAX_BYTES:
            raise ValueError('GRAPH_CATALOG_TOTAL_BYTE_BOUND')
        manifest['owners'][owner]={'reference':self.sink(raw),'observed_at':at,
            'source_observations':times}
        owner_ids={key for key,value in self.owner_for(assets).items()if value==owner}
        assets=[a for a in assets if a['id']not in owner_ids]+payload['assets']
        if len(assets)>MAX_ASSETS or len({a['id']for a in assets})!=len(assets):raise ValueError('GRAPH_CATALOG_DUPLICATE_OR_ASSET_BOUND')
        # Source status is an estate declaration, never overwritten by a
        # collector's empty declaration list. Removed sources remain a refusal.
        if not set(sources)<={a['id']for a in assets}:raise ValueError('GRAPH_DECLARED_SOURCE_REMOVED')
        if not set(payload['source_asset_ids'])<=set(sources):raise ValueError('GRAPH_REFRESH_CANNOT_DECLARE_SOURCE')
        observations={key:value for key,value in observations.items()if key not in owner_ids}
        observations.update(times)
        partitions=self.partition(estate,assets,self.sink,observed_at=at,source_asset_ids=sources,source_observations=observations)
        return self._commit(estate,at,manifest,partitions,old['revision'],retire_missing=True)
