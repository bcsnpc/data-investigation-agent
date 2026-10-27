"""Existing-reader security evidence. No scanner substitution or impersonation."""
import json
from copy import deepcopy
from datetime import datetime,timezone


class Security:
    def __init__(self,*,assets,nodes,http,now=None):
        self.assets={a['id']:a for a in assets};self.nodes={n['id']:n for n in nodes};self.http=http
        self.now=now or (lambda:datetime.now(timezone.utc).isoformat())

    def __call__(self,node):
        if node not in self.nodes:raise ValueError('SECURITY_NODE_OUTSIDE_ESTATE')
        selected=self.nodes[node];native=self.assets.get(selected.get('properties',{}).get('asset_id'))
        result={'node':node,'source':'existing-reader-and-retained-definitions','observed_at':self.now(),
                'no_impersonation':True,'checks':[]}
        if native is None:
            result.update(status='UNAVAILABLE',reason='No discovered native asset binding on this graph node.')
            return result
        parent=native
        while parent and parent.get('kind') not in ('SemanticModel','SqlDatabase','Lakehouse','Warehouse'):
            parent=self.assets.get(parent.get('parent_id'))
        if parent is None:
            result.update(status='UNAVAILABLE',reason='No discovered security container.')
            return result
        if parent['kind']=='SemanticModel':
            for definition in self.assets.values():
                if definition.get('parent_id')!=parent['id'] or definition['kind']!='DefinitionPart':continue
                content=definition.get('metadata',{}).get('content')
                try:model=json.loads(content).get('model',{}) if isinstance(content,str) else {}
                except (ValueError,TypeError):continue
                result['checks'].append({'kind':'RLS_OLS_DEFINITIONS','state':'RETAINED_SNAPSHOT',
                    'source_asset':definition['id'],'content_hash':definition.get('content_hash'),
                    'roles':deepcopy(model.get('roles',[])),
                    'qualification':'Retained model definition; an empty roles list is not a fresh membership or effective-access check.'})
            ws,item=parent['id'].removeprefix('fabric://').split('/')
            path='workspaces/'+ws+'/items/'+item+'/connections'
            try:
                response=self.http(path)
                if response['status_code']==200:
                    payload=response['text'];payload=json.loads(payload) if isinstance(payload,str) else payload
                    # Connection identifiers/types only. Credentials and nested
                    # connection details never cross this evidence boundary.
                    rows=payload.get('value',[]) if isinstance(payload,dict) else []
                    result['checks'].append({'kind':'ITEM_CONNECTIONS','state':'OBSERVED','http_status':200,
                        'truncated':bool(payload.get('continuationToken')),
                        'connections':[{k:r[k] for k in ('id','displayName','connectivityType','connectionType') if k in r} for r in rows]})
                else:
                    result['checks'].append({'kind':'ITEM_CONNECTIONS','state':'BLOCKED_PENDING_OWNER' if response['status_code'] in (401,403) else 'UNAVAILABLE',
                        'http_status':response['status_code'],'operation':'GET '+path})
            except Exception as error:
                status=getattr(error,'http_status',None)
                result['checks'].append({'kind':'ITEM_CONNECTIONS','state':'BLOCKED_PENDING_OWNER' if status in (401,403) else 'UNAVAILABLE',
                                         'http_status':status,'provider_code':getattr(error,'provider_code',None),'error_type':type(error).__name__,
                                         'reason':'The installed reader could not complete the exact connection-list read.'})
            result['checks'].append({'kind':'ROLE_MEMBERSHIPS_AND_EFFECTIVE_USER_ACCESS','state':'BLOCKED_PENDING_OWNER',
                'reason':'No current membership reader is installed. Dataset user-access API requires ReadWriteReshare and does not establish RLS membership; investigator is not elevated.',
                'owner_action':'Provide a dated read-only role-membership/security-mapping export, or approve a separately scoped metadata collection route. No write grant requested.'})
        else:
            result['checks'].append({'kind':'SQL_SECURITY_DEFINITIONS','state':'RETAINED_SNAPSHOT',
                'container':parent['id'],'objects':[{'id':a['id'],'definition':a.get('metadata',{}).get('definition'),
                    'security':deepcopy(a.get('metadata',{}).get('security'))} for a in self.assets.values()
                    if a.get('parent_id')==parent['id'] and a.get('kind')=='SqlObject'],
                'qualification':'Only discovered definitions. Missing policy metadata does not prove that no policy exists.'})
        result['status']='PARTIAL' if result['checks'] else 'UNAVAILABLE'
        return result
