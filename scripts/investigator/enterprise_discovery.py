"""Environment-owned discovery, versioned graph and automatic model catalog projection."""
from datetime import datetime, timezone
import json
import re
from uuid import UUID, uuid4

from metadata_inventory import Inventory
from .onboarding import Conflict, digest, encoded
from .semantic_graph import analyze, affected


def utc():
    return datetime.now(timezone.utc).isoformat()


def stable(asset):
    metadata = dict(asset['metadata'])
    if asset['kind']=='SqlDatabase': metadata.pop('captured_at',None)
    return digest({'kind':asset['kind'],'name':asset['name'],'parent':asset['parent_id'],'metadata':metadata})


def descendants(assets, root):
    selected={root}
    while True:
        children={a['id'] for a in assets.values() if a['parent_id'] in selected}
        if children<=selected:break
        selected|=children
    return [assets[k] for k in sorted(selected) if k in assets]


def graph(assets, bindings):
    edges=[]; gaps=[]
    def edge(source,target,relation,evidence,provenance='DISCOVERED'):
        if source in assets and target in assets:
            edges.append({'source':source,'target':target,'relation':relation,
                          'evidence':evidence,'provenance':provenance})
    for a in assets.values():
        if a['parent_id']:edge(a['parent_id'],a['id'],'CONTAINS',[a['id']])
    for report,model in bindings.items():edge(report,model,'USES',[report])
    for model in (a for a in assets.values() if a['kind']=='SemanticModel'):
        semantic=analyze(descendants(assets,model['id']))
        for node in semantic['measures'].values():
            for target in node['references']:
                edge(node['id'],target,'DEPENDS_ON' if target in node['dependencies'] else 'REFERENCES',
                     [node['id']],'DETERMINISTICALLY_DERIVED')
    # Reuse source/notebook/pipeline/native definition analysis and its provenance.
    from lineage_graph import build
    try:
        retained=[{'id':a['id'],'parent':a['parent_id'],'kind':a['kind'],'name':a['name'],
                   'meta':a['metadata'],'hash':a['content_hash']} for a in assets.values()]
        lineage=build(retained,{'records':[]})
        for (source,target,kind),evidence in lineage.edges.items():
            relation={'data':'DERIVED_FROM','binding':'USES','presentation':'PRESENTED_IN',
                      'filter':'FILTERS','context':'FILTER_CONTEXT','produces':'WRITES',
                      'orchestration':'EXECUTES'}.get(kind,kind.upper())
            if kind=='data':
                for proof in evidence:
                    part=assets.get(proof.get('asset'),{})
                    notebook=assets.get(part.get('parent_id'),{})
                    if notebook.get('kind')=='Notebook':edge(notebook['id'],source,'READS',[proof],'DETERMINISTICALLY_DERIVED')
            if kind in ('data','binding'):source,target=target,source
            edge(source,target,relation,evidence,'DETERMINISTICALLY_DERIVED')
        gaps.extend(lineage.gaps)
    except (KeyError,ValueError,TypeError) as exc:
        gaps.append({'reason':'LINEAGE_ANALYSIS_PARTIAL','error_type':type(exc).__name__})
    return {'edges':edges,'gaps':gaps}


class Discovery:
    def __init__(self, store, config):
        self.store,self.config=store,config
        self.policy_hash=digest(config)
        with store.connect() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS enterprise_scans(
              id TEXT PRIMARY KEY,environment TEXT NOT NULL,request_key TEXT NOT NULL,
              policy_hash TEXT NOT NULL,status TEXT NOT NULL,started TEXT NOT NULL,
              ended TEXT,body TEXT,hash TEXT,UNIQUE(environment,request_key));
            CREATE UNIQUE INDEX IF NOT EXISTS enterprise_active_scan
              ON enterprise_scans(environment) WHERE status='RUNNING';
            CREATE TABLE IF NOT EXISTS discovery_models(
              model_id TEXT PRIMARY KEY REFERENCES models(id),environment TEXT NOT NULL,
              policy_hash TEXT NOT NULL,denied INTEGER NOT NULL DEFAULT 0);
            ''')

    def history(self):
        with self.store.connect() as db:
            return [dict(r) for r in db.execute('SELECT id,status,started,ended,policy_hash FROM enterprise_scans WHERE environment=? ORDER BY started DESC',(self.store.environment,))]

    def read(self, identity):
        with self.store.connect() as db:
            row=db.execute('SELECT * FROM enterprise_scans WHERE id=? AND environment=?',(identity,self.store.environment)).fetchone()
            if row is None:raise KeyError('Scan not found')
            body=json.loads(row['body']) if row['body'] else None
            if body is not None and digest(body)!=row['hash']:raise ValueError('Discovery integrity differs')
            return dict(row)|{'body':body}

    def run(self, collect, request_key):
        if not isinstance(request_key,str) or not 1<=len(request_key)<=100:raise ValueError('Invalid scan key')
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            prior=db.execute('SELECT id,policy_hash FROM enterprise_scans WHERE environment=? AND request_key=?',
                             (self.store.environment,request_key)).fetchone()
            if prior:
                if prior['policy_hash']!=self.policy_hash:raise Conflict('Scan key policy differs')
                return self.read(prior['id'])
            if db.execute("SELECT 1 FROM enterprise_scans WHERE environment=? AND status='RUNNING'",(self.store.environment,)).fetchone():
                raise Conflict('Discovery already running; reconcile interrupted collector')
            identity=str(uuid4())
            db.execute('INSERT INTO enterprise_scans VALUES(?,?,?,?,?,?,NULL,NULL,NULL)',
                       (identity,self.store.environment,request_key,self.policy_hash,'RUNNING',utc()))
        try:
            batch=collect()
            if batch['profile_hash']!=self.policy_hash:raise Conflict('Collector profile differs')
            result=self.publish(identity,batch)
        except Exception as exc:
            result={'error_type':type(exc).__name__,'reason':'Scan failed; prior context retained'}
            with self.store.connect() as db:
                db.execute("UPDATE enterprise_scans SET status='FAILED',ended=?,body=?,hash=? WHERE id=?",
                           (utc(),encoded(result),digest(result),identity))
            raise
        return self.read(identity)

    def publish(self, identity, batch):
        # Preserve raw immutable inventory for existing source tools and readers.
        inventory=Inventory(self.store.inventory)
        try:
            for a in batch['assets']:
                inventory.asset(a['id'],a['kind'],a['name'],a['source'],a['metadata'],a['parent_id'])
            for o in batch['observations']:
                inventory.observe(o['asset_id'],o['capability'],o['status'],o['source'],o['detail'])
            for scope,c in batch['coverage'].items():
                inventory.observe(scope,'discovery_coverage','AVAILABLE' if c['status']=='COMPLETE' else 'UNAVAILABLE','discovery',c)
            inventory.finish();scan=inventory.scan
        finally:inventory.db.close()
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            old=db.execute("SELECT body,hash FROM enterprise_scans WHERE environment=? AND status IN ('COMPLETE','PARTIAL') ORDER BY started DESC LIMIT 1",(self.store.environment,)).fetchone()
            previous=json.loads(old['body']) if old else {}
            if old and digest(previous)!=old['hash']:raise ValueError('Prior discovery integrity differs')
            before={a['id']:a for a in previous.get('assets',[])}
            current={a['id']:dict(a,availability='CURRENT',last_seen_scan=scan) for a in batch['assets']}
            changes=[]
            for aid,a in current.items():
                kind='ADDED' if aid not in before else 'CHANGED' if stable(a)!=stable(before[aid]) else None
                if kind:changes.append({'asset_id':aid,'state':kind})
            for aid,a in before.items():
                if aid in current:continue
                allowed_root='fabric://'+self.config['fabric']['workspace_id']
                allowed_sql='sql://'+self.config['sql']['server']+'/'+self.config['sql']['database']
                ancestor=a
                while ancestor.get('parent_id') in before and ancestor['kind'] not in ('SqlObject','SqlSchema'):
                    ancestor=before[ancestor['parent_id']]
                outside_schema=(ancestor['kind']=='SqlObject' and ancestor['metadata'].get('schema_name')!=self.config['sql']['visibility_schema']) or (ancestor['kind']=='SqlSchema' and ancestor['name']!=self.config['sql']['visibility_schema'])
                if outside_schema or not (aid==allowed_root or aid.startswith(allowed_root+'/') or aid==allowed_sql or aid.startswith(allowed_sql+'/')):
                    changes.append({'asset_id':aid,'state':'REMOVED','reason':'OUTSIDE_CURRENT_POLICY'})
                    continue
                coverage=batch['coverage'].get(a['coverage_scope'],{})
                state='REMOVED' if coverage.get('status')=='COMPLETE' else 'UNKNOWN_DUE_TO_PARTIAL_SCAN'
                # A fully absent item also removes its old descendants when workspace listing is complete.
                root='fabric://'+self.config['fabric']['workspace_id']
                item='/'.join(aid.split('/')[:4]) if aid.startswith(root+'/') else None
                if item and item not in current and batch['coverage'].get(root+'/items',{}).get('status')=='COMPLETE':state='REMOVED'
                changes.append({'asset_id':aid,'state':state})
                if state!='REMOVED':current[aid]=dict(a,availability='UNKNOWN_DUE_TO_PARTIAL_SCAN')
            bindings=dict(batch['report_bindings']);binding_gaps=[]
            for a in current.values():
                if a['kind']=='DefinitionPart' and a['name']=='definition.pbir' and a['availability']=='CURRENT':
                    ref=json.loads(a['metadata']['content']).get('datasetReference',{})
                    ids=re.findall(r'(?:^|;)\s*semanticmodelid\s*=\s*([^;]+)',ref.get('byConnection',{}).get('connectionString',''),re.I)
                    if len(ids)==1 and 'byPath' not in ref:
                        try:mid='fabric://'+self.config['fabric']['workspace_id']+'/'+str(UUID(ids[0].strip()))
                        except ValueError:continue
                        if a['parent_id'] in bindings and bindings[a['parent_id']]!=mid:
                            bindings.pop(a['parent_id'])
                            binding_gaps.append({'asset_id':a['parent_id'],'reason':'CONFLICTING_EXPLICIT_MODEL_BINDINGS'})
                            continue
                        bindings[a['parent_id']]=mid
            bindings={r:m for r,m in bindings.items() if r in current and m in current}
            context_graph=graph(current,bindings)
            context_graph['gaps'].extend(binding_gaps)
            result={**batch,'assets':list(current.values()),'changes':changes,'graph':context_graph,
                    'inventory_scan_id':scan,'report_bindings':bindings,'created':utc()}
            self.project(db,result)
            state='COMPLETE' if all(c['status']=='COMPLETE' for c in batch['coverage'].values()) else 'PARTIAL'
            db.execute('UPDATE enterprise_scans SET status=?,ended=?,body=?,hash=? WHERE id=?',
                       (state,utc(),encoded(result),digest(result),identity))
        return result

    def project(self, db, result):
        assets={a['id']:a for a in result['assets']};root='fabric://'+self.config['fabric']['workspace_id']
        active=set()
        for a in assets.values():
            if a['kind']!='SemanticModel' or a['parent_id']!=root:continue
            native=str(UUID(a['metadata']['id']));workspace=self.config['fabric']['workspace_id']
            row=db.execute('SELECT * FROM models WHERE environment=? AND workspace=? AND native_id=?',
                           (self.store.environment,workspace,native)).fetchone()
            if row and not db.execute('SELECT 1 FROM discovery_models WHERE model_id=?',(row['id'],)).fetchone():
                continue # Explicit manual registration is an override; no silent takeover.
            mid=row['id'] if row else str(uuid4());active.add(mid)
            if row is None:
                db.execute('INSERT INTO models VALUES(?,?,?,?,?,?,1,0,NULL,?)',
                           (mid,self.store.environment,workspace,native,a['name'],'[]','{}'))
                db.execute('INSERT INTO discovery_models VALUES(?,?,?,0)',(mid,self.store.environment,self.policy_hash))
                row=db.execute('SELECT * FROM models WHERE id=?',(mid,)).fetchone()
            denied=db.execute('SELECT denied FROM discovery_models WHERE model_id=?',(mid,)).fetchone()[0]
            children=descendants(assets,a['id'])
            ready=(a['availability']=='CURRENT' and result['coverage'].get(a['id']+'/definition',{}).get('status')=='COMPLETE')
            measures=[{'id':x['id'],'name':x['name'],'definition':x['metadata'],'hash':x['content_hash'],'provenance':'DISCOVERED'} for x in children if x['kind']=='Measure']
            reports=[]
            for rid,model in result['report_bindings'].items():
                if model!=a['id'] or assets[rid]['availability']!='CURRENT':continue
                parts=descendants(assets,rid)
                reports.append({'report':assets[rid],'model_id':a['id'],
                    'binding_status':'RESOLVED_EXPLICIT_ID','report_definitions':[x for x in parts if x['kind']=='DefinitionPart'],
                    'gaps':[] if result['coverage'].get(rid+'/definition',{}).get('status')=='COMPLETE' else ['REPORT_DEFINITION_UNAVAILABLE']})
            semantic=analyze(children)
            hashes={x['id']:stable(x) for x in children}
            for report in reports:
                for x in descendants(assets,report['report']['id']):hashes[x['id']]=stable(x)
            old=self.store._context(db,mid,row['context_id']) if row['context_id'] else None
            oldhash=old['source_hashes'] if old else {}
            changes={'added':sorted(hashes.keys()-oldhash.keys()),'removed':sorted(oldhash.keys()-hashes.keys()),
                     'changed':sorted(k for k in hashes.keys()&oldhash.keys() if hashes[k]!=oldhash[k])}
            context={'schema_version':2,'id':str(uuid4()),'model_id':mid,'scan_id':result['inventory_scan_id'],
                     'scan_ended':result['created'],'model_assets':children,'measures':measures,'reports':reports,
                     'source_hashes':hashes,'changes':changes,'semantic_graph':semantic,
                     'affected_measures':affected(sum(changes.values(),[]),semantic,old.get('semantic_graph') if old else None),
                     'discovery':{'policy_hash':self.policy_hash,'definition_available':ready},
                     'capabilities':{'MODEL_QUERYABLE':'UNKNOWN','MEASURE_DEFINITION_AVAILABLE':'SUPPORTED' if ready else 'UNKNOWN'},
                     'limitation':'Automatically discovered metadata; query permissions and effective report context are checked separately.'}
            enabled=bool(ready and measures and not denied)
            db.execute('INSERT INTO model_contexts VALUES(?,?,?,?,?,?)',(context['id'],mid,context['scan_id'],encoded(context),digest(context),utc()))
            db.execute('UPDATE models SET name=?,reports=?,revision=revision+1,context_id=?,enabled=? WHERE id=?',
                       (a['name'],encoded([r['report']['metadata']['id'] for r in reports]),context['id'],int(enabled),mid))
            db.execute('UPDATE discovery_models SET policy_hash=? WHERE model_id=?',(self.policy_hash,mid))
            self.store.event(db,mid,row['revision']+1,'DISCOVERED_CONTEXT','discovery',{'context_id':context['id'],'enabled':enabled,'changes':changes})
        for row in db.execute('SELECT model_id FROM discovery_models WHERE environment=?',(self.store.environment,)).fetchall():
            if row['model_id'] not in active:db.execute('UPDATE models SET enabled=0,revision=revision+1 WHERE id=? AND enabled=1',(row['model_id'],))
