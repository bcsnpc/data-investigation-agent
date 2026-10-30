"""Owner-only hospital provisioning; no DIA imports or permission changes.

Uses the existing Fabric CLI owner's cache. Never persists access tokens.
Receipts contain resource metadata only. Local journal makes creates resumable.
"""
import argparse
import contextlib
import io
import json
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request
import urllib.parse

CAPACITY='ec15bc07-8e88-436e-8dbe-485b9a7f4533'


class OwnerFabric:
    def __init__(self, journal, cli_packages):
        sys.path.insert(0,str(cli_packages))
        from fabric_cli.core.fab_auth import FabAuth
        with contextlib.redirect_stdout(io.StringIO()):
            self.token=FabAuth().get_access_token(['https://api.fabric.microsoft.com/.default'],interactive_renew=False)
        self.path=Path(journal)
        self.state=json.loads(self.path.read_text())if self.path.exists()else {'receipts':[]}

    def save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.path.write_text(json.dumps(self.state,indent=2)+'\n',encoding='utf8')

    def call(self,path,body=None):
        if path.startswith('https://'):
            parsed=urllib.parse.urlparse(path)
            if parsed.hostname and parsed.hostname.endswith('.analysis.windows.net')and parsed.path.startswith('/v1/operations/'):
                path='https://api.fabric.microsoft.com'+parsed.path
        url=path if path.startswith('https://api.fabric.microsoft.com/')else'https://api.fabric.microsoft.com/v1/'+path
        if not url.startswith('https://api.fabric.microsoft.com/'):raise ValueError('Unexpected API host')
        data=None if body is None else json.dumps(body).encode()
        req=urllib.request.Request(url,data=data,headers={'Authorization':'Bearer '+self.token,'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(req,timeout=90)as r:
                raw=r.read();result=json.loads(raw)if raw else{}
                receipt={'path':path,'method':req.get_method(),'status':r.status,'response':result}
                self.state['receipts'].append(receipt);self.save()
                if r.status==202:
                    location=r.headers['Location']
                    self.state['pending_operation']=location;self.save()
                    for _ in range(60):
                        time.sleep(5)
                        status=self.call(location)
                        if status.get('status')=='Failed':raise RuntimeError(json.dumps(status))
                        if status.get('status')=='Succeeded':
                            self.state.pop('pending_operation',None);self.save()
                            return self.call(location+'/result')
                    raise TimeoutError('Creation pending; saved operation must be inspected before retrying')
                return result
        except urllib.error.HTTPError as e:
            error={'path':path,'method':req.get_method(),'status':e.code,'error':e.read().decode(errors='replace')}
            self.state['receipts'].append(error);self.save()
            raise RuntimeError(json.dumps(error))from None

    def provision(self):
        if self.state.get('pending_operation'):raise RuntimeError('Inspect saved pending operation before further creates')
        capacities=self.call('capacities')['value']
        capacity=next(c for c in capacities if c['id']==CAPACITY)
        if capacity['state']!='Active':raise RuntimeError('Existing capacity inactive; no capacity change approved')
        workspaces=self.call('workspaces')['value']
        matches=[w for w in workspaces if w['displayName']=='HealthNet Analytics']
        if len(matches)>1:raise RuntimeError('Ambiguous workspace; refuses adoption by name')
        if 'workspace'not in self.state:
            if matches:raise RuntimeError('Unjournaled existing workspace; inspect ownership first')
            self.state['workspace']=self.call('workspaces',{'displayName':'HealthNet Analytics','description':'Fully synthetic HealthNet estate. Owner build only; no DIA access granted.','capacityId':CAPACITY})
            self.save()
        ws=self.state['workspace']['id']
        after=self.call('workspaces/'+ws)
        if after.get('capacityId')!=CAPACITY:raise RuntimeError('Capacity binding mismatch')
        self.state['workspace_after']=after;self.save()
        for kind,name in [('Lakehouse','hn_raw'),('Warehouse','hn_dw')]:
            if name not in self.state:
                self.state[name]=self.call(f'workspaces/{ws}/items',{'displayName':name,'type':kind,'description':'Synthetic HealthNet only'})
                self.save()
        self.state['items_after']=self.call(f'workspaces/{ws}/items');self.save()
        return {k:self.state[k]for k in('workspace','hn_raw','hn_dw')}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--journal',required=True)
    p.add_argument('--cli-packages',required=True)
    args=p.parse_args()
    print(json.dumps(OwnerFabric(args.journal,args.cli_packages).provision(),indent=2))

