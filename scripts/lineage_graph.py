"""Build and traverse evidence-backed lineage from one captured metadata scan."""
import argparse, hashlib, json, re, sqlite3, uuid
from collections import deque
from contextlib import closing
from datetime import datetime, timezone
from urllib.parse import unquote, urlsplit
from pathlib import Path
from metadata_config import ROOT
from lineage_notebook import StaticNotebook
from publication_lineage_contract import resolve as publication_scope

DEFAULT_KINDS={'data','binding','presentation','context'}


def walk(value,path='$'):
    yield path,value
    if isinstance(value,dict):
        for key,item in value.items(): yield from walk(item,path+'.'+key)
    elif isinstance(value,list):
        for i,item in enumerate(value): yield from walk(item,f'{path}[{i}]')


class Graph:
    def __init__(self,assets):
        self.assets={a['id']:a for a in assets}; self.edges={}; self.gaps=[]; self.resolved_gaps=[]
    def edge(self,source,target,kind,evidence,detail):
        if source not in self.assets or target not in self.assets:
            self.gap(target,'Asset reference not resolved',detail); return
        if source==target: return
        key=(source,target,kind)
        proof={'asset':evidence,'hash':self.assets.get(evidence,{}).get('hash'), 'detail':detail}
        if proof not in self.edges.setdefault(key,[]): self.edges[key].append(proof)
    def gap(self,asset,reason,detail):
        value={'asset':asset,'reason':reason,'detail':detail}
        if value not in self.gaps:self.gaps.append(value)
    def find(self,kind,name,parent=None):
        matches=[a['id'] for a in self.assets.values() if a['kind']==kind and a['name'].casefold()==name.casefold() and (parent is None or a['parent']==parent)]
        return matches[0] if len(matches)==1 else None
    def table_path(self,path):
        if not isinstance(path,str) or '/Tables/' not in path:return None
        url=urlsplit(path); prefix,table=url.path.split('/Tables/',1)
        workspace=url.netloc.split('@')[0] if url.scheme=='abfss' else prefix.strip('/').split('/')[0]
        lakehouse=prefix.strip('/').split('/')[-1]
        parent=f'fabric://{workspace}/{lakehouse}'
        return self.find('LakehouseTable',unquote(table).replace('/','.'),parent)
    def traverse(self,start,direction='upstream',kinds=None):
        if start not in self.assets: raise ValueError('Unknown asset ID')
        kinds=DEFAULT_KINDS if kinds is None else set(kinds)
        seen={start}; queue=deque([start]); selected=[]
        while queue:
            current=queue.popleft()
            for (source,target,kind),proof in self.edges.items():
                if kind not in kinds:continue
                origin,next_id=(target,source) if direction=='upstream' else (source,target)
                if origin==current:
                    selected.append({'source':source,'target':target,'kind':kind,'evidence':proof})
                    if next_id not in seen:seen.add(next_id);queue.append(next_id)
        return {'assets':[self.assets[x] for x in sorted(seen)],'edges':selected,
                'unresolved':[x for x in self.gaps if x['asset'] in seen]}


def build(assets,supplement):
    graph=Graph(assets)
    for mapping in supplement.get('snapshot_mappings',[]):
        source=graph.find('SqlObject',mapping['sql_table'],mapping['sql_parent'])
        target=graph.table_path(mapping['destination'])
        if source and target:
            graph.edge(source,target,'data',target,{'verified_snapshot_mapping':mapping})
        else:
            graph.gap(target or mapping['destination'],'Verified snapshot mapping unresolved',mapping)
    parts=[a for a in assets if a['kind']=='DefinitionPart']
    endpoints={}; connections={}
    for record in supplement['records']:
        if record['status']!='AVAILABLE':continue
        data=record['data']
        if 'connectionDetails' in data:connections[data['id']]=record
        if 'sqlEndpointProperties' in data:endpoints[data['sqlEndpointProperties'].get('id')]=record
    # Explicit copy source connection and destination workspace/lakehouse identifiers.
    for part in parts:
        if part['name']=='copyjob-content.json':
            doc=json.loads(part['meta']['content']); prop=doc['properties']
            settings=prop['source']['connectionSettings']; cid=settings.get('externalReferences',{}).get('connection')
            record=connections.get(cid); database=None
            if record:
                pair=record['data']['connectionDetails'].get('path','').split(';')
                if len(pair)==2 and settings.get('typeProperties',{}).get('database',pair[1])==pair[1]: database='sql://'+pair[0]+'/'+pair[1]
            dest=prop['destination']['connectionSettings']['typeProperties']
            parent=f"fabric://{dest['workspaceId']}/{dest['artifactId']}"
            for activity in doc['activities']:
                p=activity['properties']; src=p['source']['datasetSettings']; dst=p['destination']['datasetSettings']
                target=graph.find('LakehouseTable',dst['schema']+'.'+dst['table'],parent)
                source=graph.find('SqlObject',src['schema']+'.'+src['table'],database) if database else None
                if source and target:
                    graph.edge(source,target,'data',part['id'],{'activity':activity['id'],'mapping':p,'connection_evidence':record})
                    graph.edge(part['parent'],target,'produces',part['id'],{'activity':activity['id']})
                else:graph.gap(target or part['parent'],'Copy mapping unresolved',{'source':src,'destination':dst,'connection_id':cid})
        if part['name']=='pipeline-content.json':
            for _,node in walk(json.loads(part['meta']['content'])):
                if isinstance(node,dict) and node.get('type')=='InvokeCopyJob':
                    p=node['typeProperties']; target=f"fabric://{p['workspaceId']}/{p['copyJobId']}"
                    graph.edge(part['parent'],target,'orchestration',part['id'],node)
        if part['name']=='notebook-content.py':
            try: writes,gaps=StaticNotebook(part['meta']['content']).analyze()
            except Exception as exc:
                graph.gap(part['parent'],'Notebook parsing failed',type(exc).__name__);continue
            contract=publication_scope(part['meta']['content'],supplement.get('snapshot_mappings',[]))
            if contract and all(graph.table_path(path) for path in contract['verified_table_dependencies']):
                for line,reason in gaps:
                    graph.resolved_gaps.append({'asset':part['parent'],'reason':reason,'detail':{'line':line},
                        'definition_asset':part['id'],'definition_hash':part['hash'],'evidence':contract})
                for path in contract['possible_table_writes']:
                    graph.edge(part['parent'],graph.table_path(path),'produces',part['id'],contract)
                for path in contract['verified_table_dependencies']:
                    graph.edge(graph.table_path(path),part['parent'],'verification_input',part['id'],contract)
                continue
            for line,reason in gaps: graph.gap(part['parent'],reason,{'line':line})
            for write in writes:
                target=graph.table_path(write['destination'])
                if not target:graph.gap(part['parent'],'Write destination unresolved',write['destination']);continue
                graph.edge(part['parent'],target,'produces',part['id'],{'line':write['line']})
                for line,reason in gaps: graph.gap(target,reason,{'notebook':part['parent'],'line':line})
                if not write['sources']:graph.gap(target,'No statically proven inputs',write)
                for path in write['sources']:
                    source=graph.table_path(path)
                    if source:graph.edge(source,target,'data',part['id'],write)
                    else:graph.gap(target,'Notebook input unresolved',{'input':path,'line':write['line']})
    # Resolve Direct Lake entity partitions through their M expression endpoint ID.
    models={}
    for part in parts:
        if part['name']=='model.bim':models[part['parent']]=(json.loads(part['meta']['content'])['model'],part)
    for model_id,(model,part) in models.items():
        expressions={x['name']:x['expression'] for x in model.get('expressions',[])}
        for table in model['tables']:
            tid=graph.find('SemanticTable',table['name'],model_id)
            for partition in table.get('partitions',[]):
                source=partition.get('source',{}); expression=expressions.get(source.get('expressionSource'),'')
                if isinstance(expression,list):expression='\n'.join(expression)
                match=re.search(r'Sql\.Database\(\s*"([^"]+)"\s*,\s*"([^"]+)"',expression)
                record=endpoints.get(match.group(2)) if match else None
                origin=None
                if record and match.group(1)==record['data']['sqlEndpointProperties'].get('connectionString'):
                    e=record['data']; parent=f"fabric://{e['workspaceId']}/{e['id']}"
                    origin=graph.find('LakehouseTable',source.get('entityName',''),parent) or graph.find('LakehouseTable',source.get('schemaName','')+'.'+source.get('entityName',''),parent)
                if origin:graph.edge(origin,tid,'data',part['id'],{'partition':partition,'expression':expression,'endpoint_evidence':record})
                else:graph.gap(tid,'Semantic partition unresolved',partition)
    for asset in assets:
        if asset['kind']=='SemanticColumn':graph.edge(asset['parent'],asset['id'],'data',asset['id'],{'sourceColumn':asset['meta'].get('sourceColumn')})
        if asset['kind']=='Measure':
            table=graph.assets[asset['parent']]; model=table['parent']; expression=asset['meta'].get('expression','')
            if isinstance(expression,list):expression='\n'.join(expression)
            # Ignore DAX string literals and comments before binding identifiers.
            clean=re.sub(r'"(?:""|[^"])*"|/\*.*?\*/|//[^\n]*|--[^\n]*',' ',expression,flags=re.S)
            pattern=r"(?:(?:'((?:''|[^'])+)'|([A-Za-z_][\w]*))\s*)?\[((?:\]\]|[^\]])+)\]"
            for match in re.finditer(pattern,clean):
                tname=(match.group(1) or match.group(2) or '').replace("''", "'"); name=match.group(3).replace(']]',']')
                t=graph.find('SemanticTable',tname,model) if tname else None
                candidates=[x['id'] for x in assets if x['kind']=='Measure' and x['name'].casefold()==name.casefold() and graph.assets[x['parent']]['parent']==model]
                source=graph.find('SemanticColumn',name,t) if t else (candidates[0] if len(candidates)==1 else None)
                if t and not source:source=graph.find('Measure',name,t)
                if source:graph.edge(source,asset['id'],'data',asset['id'],{'expression':expression,'reference':match.group(0)})
                else:graph.gap(asset['id'],'DAX reference unresolved',match.group(0))
            for t in [x for x in assets if x['kind']=='SemanticTable' and x['parent']==model]:
                if re.search(r'\b(?:COUNTROWS|FILTER|ALL|VALUES)\s*\(\s*'+re.escape(t['name'])+r'\s*[,)]',clean,re.I):
                    graph.edge(t['id'],asset['id'],'data',asset['id'],{'expression':expression,'table':t['name']})
        if asset['kind']=='SemanticRelationship':
            rel=asset['meta']; model=asset['parent']
            a=graph.find('SemanticTable',rel['fromTable'],model);b=graph.find('SemanticTable',rel['toTable'],model)
            graph.edge(b,a,'filter',asset['id'],rel)
    # Report definitions supply model IDs. Do not infer a model from matching names.
    report_models={}
    for part in parts:
        if part['name']=='definition.pbir':
            doc=json.loads(part['meta']['content']); text=json.dumps(doc)
            match=re.search(r'semanticmodelid=([0-9a-f-]+)',text,re.I)
            candidates=[a['id'] for a in assets if a['kind']=='SemanticModel' and match and a['meta']['id'].lower()==match.group(1).lower()]
            if len(candidates)==1:report_models[part['parent']]=candidates[0]
            else:graph.gap(part['parent'],'Report model unresolved',doc)
    for asset in assets:
        if asset['kind'] not in ('ReportVisual','ReportPage'):continue
        graph.edge(asset['id'],asset['parent'],'presentation',asset['id'],{'parent':asset['parent']})
        report=asset['parent'] if asset['kind']=='ReportPage' else graph.assets[asset['parent']]['parent']
        model=report_models.get(report)
        for path,node in walk(asset['meta']):
            if not isinstance(node,dict):continue
            for key,kind in [('Measure','Measure'),('Column','SemanticColumn')]:
                if key not in node or not isinstance(node[key],dict):continue
                reference=node[key]; entity=reference.get('Expression',{}).get('SourceRef',{}).get('Entity'); prop=reference.get('Property')
                table=graph.find('SemanticTable',entity,model) if entity and model else None
                source=graph.find(kind,prop,table) if prop and table else None
                if source:graph.edge(source,asset['id'],'binding',asset['id'],{'path':path,'reference':reference})
                else:graph.gap(asset['id'],'Visual binding unresolved',{'path':path,'reference':reference})
    # Persist static page/report filter dependencies on each affected visual.
    scopes=[(a['id'],a['parent'],a['meta'],a['id']) for a in assets if a['kind']=='ReportPage']
    for part in parts:
        if part['name']=='definition/report.json':scopes.append((part['parent'],part['parent'],json.loads(part['meta']['content']),part['id']))
    for scope,report,metadata,evidence in scopes:
        model=report_models.get(report)
        targets=[a['id'] for a in assets if a['kind']=='ReportVisual' and
                 (a['parent']==scope or graph.assets[a['parent']]['parent']==scope)]
        for path,node in walk(metadata.get('filterConfig',{})):
            if not isinstance(node,dict):continue
            for key,kind in [('Column','SemanticColumn'),('Measure','Measure')]:
                reference=node.get(key)
                if not isinstance(reference,dict):continue
                entity=reference.get('Expression',{}).get('SourceRef',{}).get('Entity')
                table=graph.find('SemanticTable',entity,model) if entity and model else None
                source=graph.find(kind,reference.get('Property',''),table) if table else None
                for target in targets:
                    if source:graph.edge(source,target,'context',evidence,{'filter_path':path,'reference':reference})
                    else:graph.gap(target,'Inherited filter unresolved',reference)
    return graph


def persist(database,scan,graph,supplement):
    run=str(uuid.uuid4())
    with closing(sqlite3.connect(database)) as db:
        db.executescript('''CREATE TABLE IF NOT EXISTS lineage_runs(id TEXT PRIMARY KEY,scan_id TEXT,created TEXT,status TEXT,supplement TEXT);
        CREATE TABLE IF NOT EXISTS lineage_edges(run_id TEXT,source TEXT,target TEXT,kind TEXT,evidence TEXT,PRIMARY KEY(run_id,source,target,kind));
        CREATE TABLE IF NOT EXISTS lineage_gaps(run_id TEXT,asset TEXT,reason TEXT,detail TEXT);''')
        retained=dict(supplement,resolved_parser_gaps=graph.resolved_gaps)
        db.execute('INSERT INTO lineage_runs VALUES(?,?,?,?,?)',(run,scan,datetime.now(timezone.utc).isoformat(),'PARTIAL' if graph.gaps else 'COMPLETE',json.dumps(retained)))
        db.executemany('INSERT INTO lineage_edges VALUES(?,?,?,?,?)',[(run,*key,json.dumps(proof)) for key,proof in graph.edges.items()])
        db.executemany('INSERT INTO lineage_gaps VALUES(?,?,?,?)',[(run,x['asset'],x['reason'],json.dumps(x['detail'])) for x in graph.gaps]);db.commit()
    return run


def load_assets(database,scan):
    with closing(sqlite3.connect(database)) as db:
        state=db.execute('SELECT status FROM scans WHERE id=?',(scan,)).fetchone()
        if not state or state[0]!='COMPLETE':raise ValueError('Complete metadata scan required')
        rows=db.execute('SELECT id,parent_id,kind,name,metadata,content_hash FROM assets WHERE scan_id=?',(scan,)).fetchall()
    return [dict(zip(['id','parent','kind','name','meta','hash'],[a,p,k,n,json.loads(m),h])) for a,p,k,n,m,h in rows]


def load_graph(database,run=None):
    with closing(sqlite3.connect(database)) as db:
        if run is None:
            row=db.execute('SELECT id,scan_id FROM lineage_runs ORDER BY created DESC LIMIT 1').fetchone()
        else:row=db.execute('SELECT id,scan_id FROM lineage_runs WHERE id=?',(run,)).fetchone()
        if not row:raise ValueError('Lineage build not found')
        run,scan=row
        graph=Graph(load_assets(database,scan))
        retained=json.loads(db.execute('SELECT supplement FROM lineage_runs WHERE id=?',(run,)).fetchone()[0])
        graph.resolved_gaps=retained.get('resolved_parser_gaps',[])
        for source,target,kind,evidence in db.execute('SELECT source,target,kind,evidence FROM lineage_edges WHERE run_id=?',(run,)):
            graph.edges[(source,target,kind)]=json.loads(evidence)
        graph.gaps=[{'asset':a,'reason':r,'detail':json.loads(d)} for a,r,d in db.execute('SELECT asset,reason,detail FROM lineage_gaps WHERE run_id=?',(run,))]
    return graph


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database',type=Path,default=ROOT/'.local/metadata/inventory.sqlite')
    parser.add_argument('--evidence',type=Path,default=ROOT/'.local/metadata/lineage-evidence.json')
    parser.add_argument('--run');parser.add_argument('--include-filter',action='store_true');parser.add_argument('--asset');parser.add_argument('--direction',choices=['upstream','downstream'],default='upstream')
    args=parser.parse_args()
    if args.asset:
        graph=load_graph(args.database,args.run)
        kinds=DEFAULT_KINDS|{'filter'} if args.include_filter else DEFAULT_KINDS
        print(json.dumps(graph.traverse(args.asset,args.direction,kinds),indent=2))
    else:
        supplement=json.loads(args.evidence.read_text());scan=supplement['scan_id']
        graph=build(load_assets(args.database,scan),supplement)
        run=persist(args.database,scan,graph,supplement)
        result={'run_id':run,'scan_id':scan,'edges':len(graph.edges),'unresolved':len(graph.gaps),'status':'PARTIAL' if graph.gaps else 'COMPLETE'}
        (args.database.parent/'lineage-latest.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
