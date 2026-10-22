"""Retain served item-list metadata separately from calculation definitions.

No API client lives here. The existing scanner supplies its already received
item and approved CAS sink; the history reader uses only shared state/proofs.
"""
from copy import deepcopy
import hashlib
from urllib.parse import urlsplit

from ..estate_graph_contract import timestamp
from ..shared_state import encoded,sha,StateConflict

NAMESPACE='graph_item_metadata_history'
VERSION='served-item-metadata-v1'
TIME_FIELDS=('lastModifiedDateTime','modifiedDateTime','modifiedTime')
ACTOR_FIELDS=('lastModifiedBy','modifiedBy','lastModifiedByUserName','modifiedByUserName',
              'lastModifiedByUserPrincipalName','modifiedByUserPrincipalName')
VOLATILE_FIELDS=frozenset((*TIME_FIELDS,*ACTOR_FIELDS))


def projection(item):
    time_field=next((k for k in TIME_FIELDS if item.get(k)),None)
    actor_field=next((k for k in ACTOR_FIELDS if item.get(k)),None)
    at=item.get(time_field) if time_field else None
    actor=item.get(actor_field) if actor_field else None
    if isinstance(actor,dict):actor=actor.get('displayName') or actor.get('userPrincipalName') or actor.get('id')
    if not isinstance(actor,str) or not actor.strip():actor=None
    reason=None
    if at is not None:
        try:at=timestamp(at)
        except ValueError:at=None;reason='MODIFIED_TIME_NOT_PARSEABLE'
    if at is None and reason is None:reason='MODIFIED_TIME_NOT_RETURNED'
    return {'modified_at':at,'modified_by':actor,'reason':reason,
            'metadata_fields':{'modified_at':time_field,'modified_by':actor_field}}


class ItemMetadataHistory:
    def __init__(self,state,sink=None,*,limit=32):
        if type(limit) is not int or not 1<=limit<=100:raise ValueError('ITEM_METADATA_HISTORY_BOUND')
        self.state,self.sink,self.limit=state,sink,limit

    def observe(self,estate,owner,item,*,collected_at):
        collected_at=timestamp(collected_at)
        if self.sink is None:raise ValueError('ITEM_METADATA_IMMUTABLE_SINK_REQUIRED')
        if not isinstance(item,dict) or not owner.endswith('/'+str(item.get('id'))):
            raise ValueError('ITEM_METADATA_OWNER_BINDING_DIFFERS')
        # The source is the parsed item from a successful existing listing. This
        # canonical envelope is explicitly not the original HTTP byte stream.
        envelope={'version':VERSION,'recording_class':'CANONICAL_ITEM_METADATA_PROJECTION',
                  'estate':estate,'owner':owner,'item':deepcopy(item)}
        raw=encoded(envelope).encode('utf8')
        if len(raw)>65536:raise ValueError('ITEM_METADATA_PROJECTION_BOUND')
        from ..planner_recording import _safe
        _safe(raw)
        identity=hashlib.sha256(raw).hexdigest()
        reference=self.sink(raw)
        parsed=urlsplit(reference.get('uri','')) if isinstance(reference,dict) else None
        if (not isinstance(reference,dict) or set(reference)!={'sha256','bytes','uri'}
                or reference['sha256']!=identity or reference['bytes']!=len(raw)
                or not parsed.scheme or parsed.username or parsed.password or parsed.query):
            raise ValueError('ITEM_METADATA_REFERENCE_DIFFERS')
        key=encoded([estate,owner])
        try:saved=self.state.get(NAMESPACE,key)
        except KeyError:saved={'revision':None,'body':{'version':VERSION,'estate':estate,'owner':owner,'observations':[],'truncated':False}}
        body=deepcopy(saved['body'])
        if body['version']!=VERSION or body['estate']!=estate or body['owner']!=owner:
            raise StateConflict('ITEM_METADATA_INDEX_BINDING_DIFFERS')
        if any(r['item_sha256']==identity for r in body['observations']):return reference
        body['observations'].append({'item_sha256':identity,'collected_at':collected_at,
            **projection(item),'provenance':{'source':'SERVED_ITEM_LISTING','evidence_id':identity,
                'reference':reference,'observed_at':collected_at,'span':{'kind':'JSON_POINTER','path':'/item'}}})
        if len(body['observations'])>self.limit:
            body['observations']=body['observations'][-self.limit:];body['truncated']=True
        self.state.put(NAMESPACE,key,body,revision=saved['revision'])
        return reference

    def read(self,estate,node):
        owner=node['owner'];key=encoded([estate,owner])
        try:body=self.state.get(NAMESPACE,key)['body']
        except KeyError:return {'observations':[],'coverage_gaps':[{'source':'ITEM_METADATA','reason':'NO_RETAINED_ITEM_LISTING_OBSERVATION'}]}
        if (body['version']!=VERSION or body['estate']!=estate or body['owner']!=owner
                or not isinstance(body['observations'],list) or len(body['observations'])>100):
            raise StateConflict('ITEM_METADATA_INDEX_BINDING_DIFFERS')
        rows=[];gaps=[]
        if body['truncated']:gaps.append({'source':'ITEM_METADATA','reason':'Older observations remain in immutable CAS; this index is bounded'})
        for observation in reversed(body['observations']):
            if observation['provenance']['evidence_id']!=observation['item_sha256']:
                raise StateConflict('ITEM_METADATA_REFERENCE_DIFFERS')
            if observation['modified_at'] is None:
                gaps.append({'source':'ITEM_METADATA','reason':observation['reason'],
                             'provenance':observation['provenance']});continue
            rows.append({'subject':node['id'],'source':'ITEM_METADATA','actor':observation['modified_by'],
                         'at':observation['modified_at'],'reason':None,'provenance':observation['provenance']})
        return {'observations':rows,'coverage_gaps':gaps}
