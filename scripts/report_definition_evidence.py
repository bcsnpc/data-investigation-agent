"""Evidence bundle from one retained native metadata scan; never executes definitions."""
from contextlib import closing
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from uuid import UUID


def bundle(database, scan_id, report_id):
    scan_id = str(UUID(scan_id))
    with closing(sqlite3.connect(Path(database).resolve().as_uri()+'?mode=ro', uri=True)) as db:
        db.execute('BEGIN')
        scan = db.execute('SELECT status FROM scans WHERE id=?', (scan_id,)).fetchone()
        if not scan or scan[0] not in ('COMPLETE', 'PARTIAL'):
            raise ValueError('Finished metadata scan required')
        rows = db.execute('SELECT id,parent_id,kind,name,source,collected_at,content_hash,metadata FROM assets WHERE scan_id=?', (scan_id,)).fetchall()
    assets = {}
    for aid,parent,kind,name,source,collected,sha,raw in rows:
        if hashlib.sha256(raw.encode()).hexdigest() != sha:
            raise ValueError('Stored metadata hash differs')
        assets[aid] = {'id':aid,'parent_id':parent,'kind':kind,'name':name,'source':source,
                       'collected_at':collected,'content_hash':sha,'metadata':json.loads(raw)}
    report = assets.get(report_id)
    if not report or report['kind'] != 'Report':
        raise ValueError('Selected report unavailable in scan')
    parts = [a for a in assets.values() if a['parent_id']==report_id and a['kind']=='DefinitionPart']
    definitions = {a['name']:a for a in parts}
    if len(definitions)!=len(parts): raise ValueError('Ambiguous definition paths')
    gaps = []; model = None
    pbir = definitions.get('definition.pbir')
    if pbir:
        reference = json.loads(pbir['metadata']['content']).get('datasetReference',{})
        connection = reference.get('byConnection',{}).get('connectionString','')
        ids = re.findall(r'(?:^|;)\s*semanticmodelid\s*=\s*([^;]+)',connection,re.I)
        if len(ids)==1 and 'byPath' not in reference:
            try:
                model_id = str(UUID(ids[0].strip()))
                candidate = assets.get(report['parent_id']+'/'+model_id)
                if candidate and candidate['kind']=='SemanticModel': model=candidate
            except ValueError: pass
    if model is None: gaps.append('Explicit unique semanticmodelid could not be resolved within the same workspace and scan')
    filters = []
    for path,part in sorted(definitions.items()):
        if path=='definition/report.json' or path.endswith('/page.json') or path.endswith('/visual.json'):
            content = json.loads(part['metadata']['content'])
            filters.append({'path':path,'asset_id':part['id'],'content_hash':part['content_hash'],
                            'filter_config_present':'filterConfig' in content,'filter_config':content.get('filterConfig'),
                            'query':content.get('visual',{}).get('query')})
    if 'definition/report.json' not in definitions: gaps.append('Native report definition missing')
    if not any(p.endswith('/page.json') for p in definitions): gaps.append('Native page definitions missing')
    model_assets=[]
    if model:
        selected={model['id']}
        while True:
            children={a['id'] for a in assets.values() if a['parent_id'] in selected}
            if children<=selected: break
            selected|=children
        model_assets=[assets[k] for k in sorted(selected)]
        if not any(a['kind']=='DefinitionPart' and a['name']=='model.bim' for a in model_assets):
            gaps.append('Native model.bim missing')
    result={'schema_version':1,'scan_id':scan_id,'scan_status':scan[0],'report':report,
            'binding_status':'RESOLVED_EXPLICIT_ID' if model else 'UNRESOLVED',
            'binding_reference':pbir['id'] if pbir else None,'model_id':model['id'] if model else None,
            'report_definitions':parts,'filter_context':filters,'model_assets':model_assets,'gaps':gaps,
            'root_cause_verified':False,'snapshot_comparable':False,'automatic_defect_routing':False,
            'limitation':'Retained native definition evidence only. Filters are not evaluated or combined; absent filterConfig does not establish unfiltered runtime state. Slicers, bookmarks, RLS, relationships and DAX require separate evaluation. Hashes detect local changes, not Microsoft provenance signatures.'}
    result['bundle_hash']=hashlib.sha256(json.dumps(result,sort_keys=True).encode()).hexdigest()
    return result


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database',type=Path,required=True)
    parser.add_argument('--scan',required=True)
    parser.add_argument('--report',required=True,help='Full retained fabric:// report asset ID')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=bundle(args.database,args.scan,args.report)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8') as output: json.dump(result,output,indent=2)
    print(json.dumps({'binding_status':result['binding_status'],'gaps':result['gaps'],'bundle_hash':result['bundle_hash']}))
