"""Owner control-plane adapter. Credentials never leave memory except Key Vault.

No method from this module is registered with the investigator tool registry.
"""
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import subprocess
from uuid import UUID

import requests


class ControlFailure(RuntimeError):
    pass


def validate(config):
    required = {'version', 'owner_approval', 'cli', 'home_tenant', 'resource_tenant',
                'admin_profile', 'application_id', 'application_object_id',
                'vault_url', 'secret_name', 'old_key_id', 'targets', 'checkpoint'}
    if set(config) != required or config['version'] != 1 or not config['owner_approval']:
        raise ValueError('ROTATION_CONFIG')
    for key in ('home_tenant','resource_tenant','application_id','application_object_id','old_key_id'):
        UUID(config[key])
    if not re.fullmatch(r'https://[a-zA-Z0-9-]+\.vault\.azure\.net', config['vault_url']):
        raise ValueError('ROTATION_EXISTING_VAULT_REQUIRED')
    if not re.fullmatch(r'[a-zA-Z0-9-]{1,127}', config['secret_name']):
        raise ValueError('ROTATION_SECRET_NAME')
    cli = config['cli']
    if not (cli == ['az'] or isinstance(cli,list) and len(cli)==3 and cli[1:]==['-m','azure.cli']
            and re.fullmatch(r'python(?:[0-9.]*)?(?:\.exe)?',Path(cli[0]).name,re.I)):
        raise ValueError('ROTATION_CLI')
    if len(config['targets']) != 2:
        raise ValueError('ROTATION_TWO_APPROVED_CONNECTIONS_REQUIRED')
    for target in config['targets'].values():
        if set(target) != {'connection_id','workspace_id','model_id','verification'}:
            raise ValueError('ROTATION_TARGET_SCHEMA')
        for key in ('connection_id','workspace_id','model_id'): UUID(target[key])
    return config


class OwnerAdapter:
    def __init__(self, config, *, verify=None, transport=requests.request, execute=subprocess.run):
        self.c = validate(config); self.transport=transport; self.execute=execute
        self.verifier=verify; self.calls=[]; self._tokens={}

    def targets(self): return sorted(self.c['targets'])

    def token(self, resource, *, resource_tenant=False):
        tenant=self.c['resource_tenant' if resource_tenant else 'home_tenant']
        key=(resource,tenant)
        if key not in self._tokens:
            env=os.environ.copy()
            if resource_tenant:env['AZURE_CONFIG_DIR']=str(Path(self.c['admin_profile']).resolve())
            p=self.execute(self.c['cli']+['account','get-access-token','--tenant',tenant,
                '--resource',resource,'-o','json','--only-show-errors'],env=env,capture_output=True,timeout=90)
            if p.returncode:raise ControlFailure('OWNER_SIGN_IN_REQUIRED:'+tenant)
            self._tokens[key]=json.loads(p.stdout)['accessToken']
        return self._tokens[key]

    def request(self, method, url, resource, payload=None, *, resource_tenant=False):
        # Response bodies, headers and request bodies never enter a receipt.
        try:
            result=self.transport(method,url,headers={'Authorization':'Bearer '+self.token(resource,resource_tenant=resource_tenant)},json=payload,timeout=120)
        except Exception:
            raise ControlFailure('CONTROL_TRANSPORT_FAILED') from None
        self.calls.append({'method':method,'url':url,'http_status':result.status_code})
        if not result.ok:
            raise ControlFailure('CONTROL_HTTP_'+str(result.status_code))
        return result.json() if result.content else {}

    def graph(self, method, suffix='', payload=None):
        return self.request(method,'https://graph.microsoft.com/v1.0/applications/'+self.c['application_object_id']+suffix,'https://graph.microsoft.com/',payload)

    def observe(self):
        app=self.graph('GET','?$select=id,appId,passwordCredentials,keyCredentials')
        if app['appId']!=self.c['application_id']:raise ControlFailure('APPLICATION_ID_DIFFERS')
        out={'app_id':app['appId'],'credentials':[{k:v.get(k) for k in ('keyId','displayName','startDateTime','endDateTime')} for v in app.get('passwordCredentials',[])],
             'key_credential_count':len(app.get('keyCredentials',[])),'connections':{}}
        for name,t in self.c['targets'].items():
            f='https://api.fabric.microsoft.com/v1/'
            connection=self.request('GET',f+'connections/'+t['connection_id'],'https://api.fabric.microsoft.com/',resource_tenant=True)
            detail=connection['credentialDetails']
            if detail.get('singleSignOnType')!='None' or detail.get('credentialType')!='ServicePrincipal':
                raise ControlFailure('FIXED_SERVICE_PRINCIPAL_REQUIRED:'+name)
            bindings=self.request('GET',f+'workspaces/'+t['workspace_id']+'/items/'+t['model_id']+'/connections','https://api.fabric.microsoft.com/',resource_tenant=True)
            if not any(x.get('id')==t['connection_id'] for x in bindings.get('value',[])):
                raise ControlFailure('MODEL_BINDING_DIFFERS:'+name)
            users=self.request('GET','https://api.powerbi.com/v1.0/myorg/groups/'+t['workspace_id']+'/datasets/'+t['model_id']+'/users','https://analysis.windows.net/powerbi/api',resource_tenant=True)
            out['connections'][name]={'id':t['connection_id'],'binding':bindings,'users':users,
                'details':connection['connectionDetails'],'connectivity':connection['connectivityType'],
                'credential_type':detail['credentialType'],'sso':detail['singleSignOnType']}
        return out

    def create_and_store(self, days):
        now=datetime.now(timezone.utc); end=now+timedelta(days=days)
        created=self.graph('POST','/addPassword',{'passwordCredential':{
            'displayName':'dia-fixed-readonly-rotation-'+now.strftime('%Y%m%dT%H%M%SZ'),
            'startDateTime':now.isoformat(),'endDateTime':end.isoformat()}})
        secret=created.pop('secretText'); created.pop('hint',None)
        # This method must be checkpointed by the adapter before storing: if
        # the vault fails, the newly created key ID remains recoverable.
        metadata={k:created.get(k) for k in ('keyId','startDateTime','endDateTime')}
        intent=Path(self.c['checkpoint']+'.created-key.json')
        intent.write_text(json.dumps(metadata)+'\n',encoding='utf-8')
        try:
            stored=self.request('PUT',self.c['vault_url']+'/secrets/'+self.c['secret_name']+'?api-version=7.4','https://vault.azure.net',
                {'value':secret,'attributes':{'enabled':True,'exp':int(end.timestamp())},
                 'tags':{'purpose':'fixture-billing-fixed-readonly','ownerApproval':self.c['owner_approval'],'keyId':created['keyId']}})
            if stored.pop('value')!=secret:raise ControlFailure('VAULT_WRITE_READBACK_DIFFERS')
            ref=stored['id']
            read=self.request('GET',ref+'?api-version=7.4','https://vault.azure.net')
            if read.pop('value')!=secret:raise ControlFailure('VAULT_READBACK_DIFFERS')
            return {'key_id':created['keyId'],'store_reference':ref,'expires_at_utc':created['endDateTime']}
        finally:
            secret=None

    def update(self, target, credential):
        t=self.c['targets'][target]
        ref=credential['store_reference']
        if not ref.startswith(self.c['vault_url']+'/secrets/'+self.c['secret_name']+'/'):
            raise ControlFailure('ROTATION_SECRET_REFERENCE_DIFFERS')
        value=self.request('GET',ref+'?api-version=7.4','https://vault.azure.net')['value']
        try:
            self.request('PATCH','https://api.fabric.microsoft.com/v1/connections/'+t['connection_id'],'https://api.fabric.microsoft.com/',
                {'connectivityType':'ShareableCloud','credentialDetails':{'singleSignOnType':'None','connectionEncryption':'Encrypted','skipTestConnection':False,
                    'credentials':{'credentialType':'ServicePrincipal','tenantId':self.c['resource_tenant'],
                    'servicePrincipalClientId':self.c['application_id'],'servicePrincipalSecret':value}}},resource_tenant=True)
        finally:value=None

    def verify(self, target):
        if self.verifier:return self.verifier(target,self.c['targets'][target])
        from .rotation_verification import verify
        return verify(target,self.c['targets'][target],self)

    def assert_unchanged_scope(self,before,after):
        if before['connections']!=after['connections'] or before['key_credential_count']!=after['key_credential_count']:
            raise ControlFailure('CONNECTION_OR_MODEL_SCOPE_CHANGED')

    def remove_old(self):
        current=self.graph('GET','?$select=passwordCredentials')
        if any(x['keyId']==self.c['old_key_id'] for x in current.get('passwordCredentials',[])):
            self.graph('POST','/removePassword',{'keyId':self.c['old_key_id']})


def execute(path, *, apply=False):
    from ..connection_rotation import rotate
    config=validate(json.loads(Path(path).read_bytes()))
    if not apply:return {'status':'PLAN','targets':sorted(config['targets']),'days':30,
        'old_credential_removed_only_after_both_reads':True,'owner_approval':config['owner_approval']}
    checkpoint=Path(config['checkpoint']); checkpoint.parent.mkdir(parents=True,exist_ok=True)
    state=json.loads(checkpoint.read_bytes()) if checkpoint.exists() else {}
    # No silent duplicate when a crash occurred between addPassword and vault.
    if not state.get('new_credential') and Path(config['checkpoint']+'.created-key.json').exists():
        raise ControlFailure('CREATED_KEY_REQUIRES_EXPLICIT_RECOVERY_NO_DUPLICATE')
    adapter=OwnerAdapter(config)
    def save(value):
        value['owner_approval']=config['owner_approval'];value['control_requests']=adapter.calls
        checkpoint.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
    result=rotate(adapter,state,save)
    return {'status':result['status'],'checkpoint':str(checkpoint),'expires_at_utc':result['new_credential']['expires_at_utc'],'permission_grants_changed':False}
