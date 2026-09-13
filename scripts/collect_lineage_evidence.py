"""Capture non-secret connection/endpoint evidence for a specific inventory scan."""
import argparse, json, sqlite3
from datetime import datetime, timezone
from contextlib import closing
from pathlib import Path
from metadata_config import ROOT, load_config
from metadata_auth import WorkerTransport


def collect(database, scan, transport):
    with closing(sqlite3.connect(database)) as db:
        state=db.execute('SELECT status FROM scans WHERE id=?',(scan,)).fetchone()
        if not state or state[0]!='COMPLETE':raise ValueError('Complete inventory scan required')
        rows=db.execute('SELECT id,kind,metadata FROM assets WHERE scan_id=?',(scan,)).fetchall()
    connections=set(); lakehouses=[]
    for aid,kind,raw in rows:
        data=json.loads(raw)
        if kind=='Lakehouse': lakehouses.append(data)
        if kind=='DefinitionPart' and data['path'].endswith('copyjob-content.json'):
            definition=json.loads(data['content'])
            ref=definition['properties']['source']['connectionSettings'].get('externalReferences',{}).get('connection')
            if ref: connections.add(ref)
    records=[]
    for endpoint in [f'connections/{id}' for id in sorted(connections)]+[f"workspaces/{x['workspaceId']}/lakehouses/{x['id']}" for x in lakehouses]:
        try:
            data=transport(endpoint)['text']
            if endpoint.startswith('connections/'):
                # Explicit allowlist: never retain credentialDetails or credentials.
                details=data.get('connectionDetails',{})
                safe={'id':data['id'],'connectionDetails':{k:details[k] for k in ('type','path') if k in details}}
            else:
                safe={'id':data['id'],'workspaceId':data.get('workspaceId'),
                      'sqlEndpointProperties':data.get('properties',{}).get('sqlEndpointProperties',{})}
            records.append({'source':endpoint,'status':'AVAILABLE','data':safe,'collected_at':datetime.now(timezone.utc).isoformat()})
        except Exception as exc:
            records.append({'source':endpoint,'status':'UNAVAILABLE','error_type':type(exc).__name__})
    return {'scan_id':scan,'records':records}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=ROOT/'infra/metadata/development.json')
    parser.add_argument('--scan');parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    config=load_config(args.config)
    database=config['storage']['database']
    with closing(sqlite3.connect(database)) as db:
        scan=args.scan or db.execute("SELECT id FROM scans WHERE status='COMPLETE' ORDER BY started DESC LIMIT 1").fetchone()[0]
    auth=config['fabric']['auth']
    transport=WorkerTransport(auth['python'],auth['tenant_id'],ROOT/'scripts/metadata_worker.py')
    data=collect(database,scan,transport)
    output=args.output or Path(database).parent/'lineage-evidence.json'
    output.write_text(json.dumps(data,indent=2))
    print([(r['source'],r['status']) for r in data['records']])
