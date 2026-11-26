import sys,json,hashlib,base64,re,datetime,copy,collections
from urllib.parse import quote
from pathlib import Path
sys.path.insert(0,'scripts')
from metadata_inventory import expand_definition
from investigator.adapters.estate_graph_static import extract,walk
from investigator import estate_graph_contract as c
from investigator.process_tape import bytes_of
root=Path('.local/healthnet-test');out=root/'backfill';assets={a['id']:a for a in json.loads((root/'assets.json').read_bytes())['assets']};native=json.loads(Path('config/estates/healthnet-native.json').read_bytes());now=datetime.datetime.now(datetime.timezone.utc).isoformat();models={};raw_models={};raw_bims={};checks=[];gaps=[];bindings=[]
class Store:
 def asset(self,identity,kind,name,source,metadata,parent=None):
  assets[identity]=dict(id=identity,kind=kind,name=name,parent_id=parent,metadata=metadata,availability='CURRENT',provenance=source,observed_at=now,content_hash=c.digest(metadata));return identity
store=Store()
for db,cn in [('clinical','clinical'),('billing','billing'),('raw','raw'),('dw','warehouse')]:
 rows=json.loads((out/(db+'-sql-columns.json')).read_bytes())['rows'];rows=rows.get('rows',[])if isinstance(rows,dict)else rows;groups=collections.defaultdict(list)
 for r in rows:groups[(r['schema_name'],r['table_name'],int(r['object_id']))].append(r)
 con=native['sql_connections'][cn];parent='sql://'+con['server']+'/'+con['database']
 assert parent in assets
 for (schema,table,oid),cols in groups.items():
  identity=parent+'/object/'+str(oid);meta=dict(name=table,schema_name=schema,type_desc='USER_TABLE',temporal_type=cols[0]['temporal_type'],columns=[dict(name=r['column_name'],column_id=r['column_id'],data_type=r['data_type'])for r in cols],schema_basis='RETAINED_EXACT_NATIVE_CATALOG')
  store.asset(identity,'SqlObject',schema+'.'+table,'HEALTHNET_FRESH_NATIVE_SQL_METADATA',meta,parent)
  for col in cols:store.asset(identity+'/column/'+quote(col['column_name'],safe=''),'SqlColumn',col['column_name'],'HEALTHNET_FRESH_NATIVE_SQL_METADATA',dict(name=col['column_name'],column_id=col['column_id'],data_type=col['data_type']),identity)
 checks.append(dict(scope=con['database'],tables=len(groups),columns=len(rows),native_metadata_sha256=hashlib.sha256((out/(db+'-sql-columns.json')).read_bytes()).hexdigest()))
for name in ['operations','revenue','productivity']:
 d=json.loads((out/(name+'-definition.json')).read_bytes());parts={p['path']:base64.b64decode(p['payload']).decode('utf-8')for p in d['definition']['parts']};raw=parts['model.bim'];m=json.loads(raw)['model'];raw_models[name]=m;raw_bims[name]=raw
 model=next(a for a in assets.values()if a['kind']=='SemanticModel'and a['name']=='HealthNet '+name.capitalize());mid=model['id'];models[name]=mid
 # Replace only native descendants of each refreshed model; reports retain exact native bindings.
 removed={mid};changed=True
 while changed:
  new={a['id']for a in assets.values()if a.get('parent_id')in removed};changed=not new<=removed;removed|=new
 for key in removed-{mid}:assets.pop(key,None)
 expand_definition(store,mid,'SemanticModel',parts,'HEALTHNET_FRESH_NATIVE_DEFINITION')
 deps=json.loads((out/(name+'-CALCULATIONS.json')).read_bytes());rows=[{k.strip('[]'):v for k,v in r.items()}for r in deps['response']['rows']];assert deps['response']['status']=='PASS'and len(rows)<=1000
 result=dict(status='COLLECTED',request=dict(kind='CALCULATIONS',target=dict(workspace=mid.split('/')[-2],model=mid.split('/')[-1])),rows=rows,unknown=None,receipt=dict(status='SUCCEEDED',rows=rows,error=None,receipt_id='healthnet-native-metadata:'+hashlib.sha256((out/(name+'-CALCULATIONS.json')).read_bytes()).hexdigest()))
 store.asset(mid+'/engine-dependencies/CALCULATIONS','EngineDependencyMetadata','CALCULATIONS','HEALTHNET_EXISTING_OWNER_NATIVE_METADATA',dict(result=result,model_name=model['name'],model_definition_hash=hashlib.sha256(raw.encode()).hexdigest()),mid)
 table_columns={t['name']:{v['name']for v in t.get('columns',[])}for t in m['tables']}
 native_columns=[{k.strip('[]'):v for k,v in row.items()}for row in json.loads((out/(name+'-COLUMNS.json')).read_bytes())['response']['rows']]
 for col in native_columns:
  tid=next(a['id']for a in assets.values()if a['kind']=='SemanticTable'and a.get('parent_id')==mid and a['name']==col['Table'])
  cid=tid+'/columns/'+quote(col['Name'],safe='')
  if col['Name']not in table_columns.get(col['Table'],set()):
   store.asset(cid,'SemanticColumn',col['Name'],'HEALTHNET_NATIVE_INFO_VIEW_COLUMNS',dict(native_column=col,dataType=col['DataType'],sourceColumn=col.get('SourceColumn'),type=col.get('Type'),isHidden=col.get('IsHidden')),tid)
  table_columns.setdefault(col['Table'],set()).add(col['Name'])

 refs=[]
 for row in rows:
  if row['REFERENCED_OBJECT_TYPE']=='COLUMN':refs.append(('CALC_DEPENDENCY',row['REFERENCED_TABLE'],row['REFERENCED_OBJECT']))
 for rel in m.get('relationships',[]):
  for side in ['from','to']:refs.append(('RELATIONSHIP',rel.get(side+'Table'),rel.get(side+'Column')))
 for origin,table,col in refs:
  if col not in table_columns.get(table,set()):gaps.append(dict(model=name,kind='MISSING_REFERENCED_COLUMN',origin=origin,table=table,column=col))
 params={}
 for p in m.get('expressions',[]):
  mt=re.fullmatch(r'\s*"((?:[^"]|"")*)"\s+meta\s+\[.*\]\s*',p.get('expression',''),re.S)
  if mt:params[p['name']]=mt.group(1).replace('""','"')
 for index,t in enumerate(m['tables']):
  tid=next(a['id']for a in assets.values()if a['kind']=='SemanticTable'and a.get('parent_id')==mid and a['name']==t['name'])
  for pi,partition in enumerate(t.get('partitions',[])):
   expr=partition.get('source',{}).get('expression','');expr='\n'.join(expr)if isinstance(expr,list)else expr
   match=re.search(r'Sql\.Database\(\s*([\w]+)\s*,\s*([\w]+)\s*\)',expr);nav=re.search(r'\[Schema="([^"]+)",Item="([^"]+)"\]',expr)
   if partition.get('source',{}).get('type')=='entity':
    native_source=partition['source'];expression=next(e['expression']for e in m['expressions']if e['name']==native_source['expressionSource'])
    match=re.search(r'Sql\.Database\(\s*([\w]+)\s*,\s*([\w]+)\s*[,)]',expression)
    nav=re.match(r'(.*)\|(.*)',native_source['schemaName']+'|'+native_source['entityName'])

   if not match or not nav or any(x not in params for x in match.groups()):gaps.append(dict(model=name,table=t['name'],kind='UNRESOLVED_NATIVE_IMPORT_PARTITION'));continue
   server,database=[params[k]for k in match.groups()];warehouse=[a for a in assets.values()if a['kind']=='Warehouse'and a['id'].split('/')[-1]==database]
   if len(warehouse)!=1:raise ValueError('NATIVE_DATABASE_GUID_NOT_UNIQUE')
   connections=[(key,v)for key,v in native['sql_connections'].items()if v['server']==server and v['database']==warehouse[0]['metadata']['displayName']]
   if len(connections)!=1:raise ValueError('EXACT_NATIVE_SQL_CONNECTION_NOT_UNIQUE')
   cn,con=connections[0];parent='sql://'+server+'/'+con['database'];physical=[a for a in assets.values()if a['kind']=='SqlObject'and a.get('parent_id')==parent and a['metadata']['schema_name']==nav[1]and a['metadata']['name']==nav[2]]
   if len(physical)!=1:raise ValueError('EXACT_NATIVE_IMPORT_OBJECT_NOT_UNIQUE '+t['name'])
   obj=physical[0];sqlcols={v['name']for v in obj['metadata']['columns']}
   missing=[v.get('sourceColumn')for v in t.get('columns',[])if v.get('sourceColumn')not in sqlcols]
   if missing:gaps.append(dict(model=name,table=t['name'],kind='MISSING_NATIVE_SOURCE_COLUMN',columns=missing))
   bindings.append(dict(model=name,model_id=mid,table=t['name'],table_asset=tid,partition_index=pi,table_index=index,source_type=partition['source']['type'],connection=cn,server=server,native_database_id=database,sql_database=con['database'],schema=nav[1],source_table=nav[2],source_asset=obj['id'],columns_checked=len(t.get('columns',[])),definition_sha256=hashlib.sha256(raw.encode()).hexdigest()))
 checks.append(dict(model=name,tables=len(m['tables']),columns=sum(len(t.get('columns',[]))for t in m['tables']),dependency_rows=len(rows),referenced_columns_checked=len(refs)))
# Verify visual native member references against the refreshed model catalog, using exact report binding.
visual_checks=0
for a in assets.values():
 if a['kind']!='ReportVisual':continue
 parent=a['parent_id'];seen=set()
 while parent in assets and parent not in seen:
  seen.add(parent);pa=assets[parent]
  if pa['kind']=='Report':break
  parent=pa.get('parent_id')
 else:continue
 report=assets[parent];model_id=report.get('metadata',{}).get('datasetId')
 for definition in assets.values():
  if definition['kind']=='DefinitionPart'and definition.get('parent_id')==parent and definition['name']=='definition.pbir':
   match=re.search(r'semanticmodelid=([0-9a-f-]{36})',definition['metadata']['content'],re.I)
   if match:model_id=match[1]
 model_key=next((k for k,v in models.items()if v.split('/')[-1]==model_id),None)
 if model_key is None:continue
 m=raw_models[model_key];tables={t['name']:t for t in m['tables']}
 for path,value in walk(a['metadata']):
  if not isinstance(value,dict):continue
  for kind,field in [('Column','columns'),('Measure','measures')]:
   v=value.get(kind)
   if not isinstance(v,dict):continue
   entity=v.get('Expression',{}).get('SourceRef',{}).get('Entity');prop=v.get('Property')
   if entity and prop:
    visual_checks+=1
    if prop not in {r['name']for r in tables.get(entity,{}).get(field,[])}:gaps.append(dict(kind='MISSING_VISUAL_MEMBER',visual=a['id'],table=entity,member=prop,member_kind=kind))
# Native stored SQL bodies and fresh copy definitions are discovery inputs, never expectations.
for p in out.glob('pipeline-*.json'):
 doc=json.loads(p.read_bytes());pid='fabric://'+native['fabric']['workspace_id']+'/'+p.stem.removeprefix('pipeline-')
 if 'definition' in doc:
  expand_definition(store,pid,'DataPipeline',{v['path']:base64.b64decode(v['payload']).decode('utf8')for v in doc['definition']['parts']},'HEALTHNET_FRESH_NATIVE_PIPELINE')
modules=[m for m in json.loads((out/'dw-sql-modules.json').read_bytes())['rows']if m['schema_name']=='dbo'and m['type_desc']=='SQL_STORED_PROCEDURE']
warehouse_root='sql://'+native['sql_connections']['warehouse']['server']+'/'+native['sql_connections']['warehouse']['database']
for module in modules:
 store.asset(warehouse_root+'/part/'+module['schema_name']+'.'+module['object_name']+'.sql','NativeSqlModuleMetadata',module['object_name']+'.sql','HEALTHNET_FRESH_SYS_SQL_MODULES',dict(path=module['object_name']+'.sql',content=module['definition']),warehouse_root)
blobs=out/'graph-definitions';blobs.mkdir(exist_ok=True)
def sink(raw):
 h=hashlib.sha256(raw).hexdigest();(blobs/h).write_bytes(raw);return dict(sha256=h,bytes=len(raw),uri='https://diaplatformd5dd7d65.blob.core.windows.net/snapshots/files/'+h)
sources=[a['id']for a in assets.values()if a['kind']=='SqlDatabase'and a['name']in('hn_clinical','hn_billing')];snapshot=extract('healthnet',list(assets.values()),sink,observed_at=now,source_asset_ids=sources);by_asset={n['properties'].get('asset_id'):n['id']for n in snapshot['nodes']if n['properties'].get('asset_id')}
for b in bindings:
 raw=raw_bims[b['model']].encode();ref=sink(raw);proof=dict(source='STATIC_DEFINITION',source_id=models[b['model']]+'/part/model.bim',definition_hash=ref['sha256'],observed_at=c.timestamp(now),span=dict(kind='JSON_POINTER',path='/model/tables/'+str(b['table_index'])+'/partitions/'+str(b['partition_index'])+'/source'))
 source,target=by_asset[b['table_asset']],by_asset[b['source_asset']];edge=c.edge(c.identity('healthnet','retained-catalog','COMPUTED_FROM',['NATIVE_IMPORT_PARTITION',source,target]),'retained-catalog','COMPUTED_FROM',source,target,proof,properties=dict(binding='NATIVE_IMPORT_PARTITION',named_connection=b['connection'],native_database_id=b['native_database_id'],server=b['server'],database=b['sql_database'],schema=b['schema'],table=b['source_table'],definition=ref));snapshot['edges'].append(edge)
 table=raw_models[b['model']]['tables'][b['table_index']]
 for col in table.get('columns',[]):
  if not col.get('sourceColumn'):continue
  semantic=b['table_asset']+'/columns/'+quote(col['name'],safe='');physical=b['source_asset']+'/column/'+quote(col['sourceColumn'],safe='')
  assert semantic in by_asset and physical in by_asset
  cp={**proof,'span':dict(kind='JSON_POINTER',path='/model/tables/'+str(b['table_index'])+'/columns/'+str(table['columns'].index(col))+'/sourceColumn')}
  snapshot['edges'].append(c.edge(c.identity('healthnet','retained-catalog','COMPUTED_FROM',['NATIVE_IMPORT_COLUMN',semantic,physical]),'retained-catalog','COMPUTED_FROM',by_asset[semantic],by_asset[physical],cp,properties=dict(binding='NATIVE_SOURCE_COLUMN',named_connection=b['connection'],definition=ref)))
# Backfill exact literal producer/copy bindings from native metadata. No execution proof is asserted.
import sqlglot
from sqlglot import exp
lineage_gaps=[];native_producers=0;native_copies=0
sql_roots={v['database']:'sql://'+v['server']+'/'+v['database']for v in native['sql_connections'].values()}
def sql_asset(db,schema,table):
 candidates=[a for a in assets.values()if a['kind']=='SqlObject'and a.get('parent_id')==sql_roots.get(db)and a['metadata']['schema_name']==schema and a['metadata']['name']==table]
 return candidates[0]['id']if len(candidates)==1 else None
def link_literal(source,target,proof,props):
 snapshot['edges'].append(c.edge(c.identity('healthnet','retained-catalog','COMPUTED_FROM',[source,target,proof['definition_hash'],props]),'retained-catalog','COMPUTED_FROM',source,target,proof,properties=props))
for module in modules:
 text=module['definition'];reference=sink(text.encode());pid=warehouse_root+'/part/'+module['schema_name']+'.'+module['object_name']+'.sql';proof=dict(source='STATIC_DEFINITION',source_id=pid,definition_hash=reference['sha256'],observed_at=c.timestamp(now),span=dict(kind='TEXT',start=0,end=len(text)))
 try:trees=sqlglot.parse(text,read='tsql')
 except sqlglot.errors.ParseError:lineage_gaps.append(dict(kind='UNPARSED_NATIVE_SQL_MODULE',module=module['object_name']));continue
 for tree in trees:
  for insert in tree.find_all(exp.Insert):
   target=insert.this.this if isinstance(insert.this,exp.Schema)else insert.this
   if not isinstance(target,exp.Table):continue
   target_id=sql_asset(target.catalog or 'hn_dw',target.db or 'dbo',target.name)
   if not target_id:lineage_gaps.append(dict(kind='NATIVE_INSERT_TARGET_NOT_DISCOVERED',module=module['object_name'],target=target.sql()));continue
   procnode=c.identity('healthnet','retained-catalog','PROCEDURE',[pid])
   if not any(n['id']==procnode for n in snapshot['nodes']):snapshot['nodes'].append(c.node(procnode,'retained-catalog','PROCEDURE',module['schema_name']+'.'+module['object_name'],proof,properties=dict(asset_id=pid,expression=text,definition=reference,execution_established=False)))
   link_literal(by_asset[target_id],procnode,proof,dict(binding='NATIVE_SQL_INSERT_TARGET',definition=reference));native_producers+=1
   cte_names={cte.alias_or_name for cte in insert.find_all(exp.CTE)}
   for source in insert.expression.find_all(exp.Table)if insert.expression is not None else []:
    if not source.db and not source.catalog and source.name in cte_names:continue
    source_id=sql_asset(source.catalog or 'hn_dw',source.db or 'dbo',source.name)
    if not source_id:lineage_gaps.append(dict(kind='NATIVE_SQL_INPUT_NOT_DISCOVERED',module=module['object_name'],source=source.sql()));continue
    if source_id!=target_id:link_literal(procnode,by_asset[source_id],proof,dict(binding='NATIVE_SQL_FROM_OBJECT',definition=reference))
for p in out.glob('pipeline-*.json'):
 doc=json.loads(p.read_bytes())
 if 'definition'not in doc:continue
 for part in doc['definition']['parts']:
  try:body=json.loads(base64.b64decode(part['payload']))
  except (ValueError,UnicodeDecodeError):continue
  reference=sink(base64.b64decode(part['payload']));pid='fabric://'+native['fabric']['workspace_id']+'/'+p.stem.removeprefix('pipeline-')
  for index,activity in enumerate(body.get('properties',{}).get('activities',[])):
   if activity.get('type')!='Copy':continue
   props=activity.get('typeProperties',{});src=props.get('source',{}).get('datasetSettings',{});dst=props.get('sink',{}).get('datasetSettings',{});cid=src.get('externalReferences',{}).get('connection');connection_file=out/('connection-'+str(cid)+'.json')
   if not connection_file.exists():continue
   details=json.loads(connection_file.read_bytes()).get('connectionDetails',{});location=dst.get('linkedService',{}).get('properties',{}).get('typeProperties',{});lake_file=out/('lakehouse-'+str(location.get('artifactId'))+'.json')
   if details.get('type')!='SQL'or not lake_file.exists():continue
   server,db=details['path'].split(';');lake=json.loads(lake_file.read_bytes());endpoint=lake['properties']['sqlEndpointProperties'];native_endpoint=[a for a in assets.values()if a['kind']=='SQLEndpoint'and a['id'].split('/')[-1]==endpoint['id']]
   if len(native_endpoint)!=1:lineage_gaps.append(dict(kind='NATIVE_COPY_ENDPOINT_NOT_DISCOVERED',activity=activity['name']));continue
   sch=src['typeProperties']['schema'];table=src['typeProperties']['table'];source_id=sql_asset(db,sch,table);sink_name=dst['typeProperties']['table'];raw_parent='sql://'+endpoint['connectionString']+'/'+native_endpoint[0]['name'];destinations=[a for a in assets.values()if a['kind']=='SqlObject'and a.get('parent_id')==raw_parent and a['metadata']['name']==sink_name]
   if not source_id or len(destinations)!=1 or sql_roots.get(db)!='sql://'+server+'/'+db:lineage_gaps.append(dict(kind='NATIVE_COPY_OBJECT_NOT_DISCOVERED',activity=activity['name']));continue
   target_id=destinations[0]['id'];proof=dict(source='STATIC_DEFINITION',source_id=pid+'/part/'+part['path'],definition_hash=reference['sha256'],observed_at=c.timestamp(now),span=dict(kind='JSON_POINTER',path='/properties/activities/'+str(index)))
   copy_node=c.identity('healthnet','retained-catalog','COPY_ACTIVITY',['NATIVE_EXACT_BACKFILL',pid,index]);snapshot['nodes'].append(c.node(copy_node,'retained-catalog','COPY_ACTIVITY',activity['name'],proof,properties=dict(native_pipeline=pid,native_connection_id=cid,source_asset=source_id,destination_asset=target_id,definition=reference)))
   link_literal(by_asset[target_id],copy_node,proof,dict(binding='NATIVE_COPY_SINK',definition=reference));link_literal(copy_node,by_asset[source_id],proof,dict(binding='NATIVE_COPY_SOURCE',definition=reference));native_copies+=1
snapshot['definition_hash']=c.digest(dict(base=snapshot['definition_hash'],native_import_bindings=bindings));c.snapshot(snapshot)
(out/'assets.json').write_bytes(bytes_of(dict(assets=list(assets.values()))));(out/'graph.json').write_bytes(bytes_of(snapshot));(out/'source-bindings.json').write_bytes(bytes_of(bindings));report=dict(native_insert_producers=native_producers,native_copy_bindings=native_copies,upstream_lineage_gaps=lineage_gaps,status='COMPLETE'if not gaps else'GAPS',checks=checks,visual_references_checked=visual_checks,model_table_bindings=len(bindings),gaps=gaps,assets=len(assets),nodes=len(snapshot['nodes']),edges=len(snapshot['edges']),engine_changes=0,guard_changes=0,native_metadata_only=True,observed_at=now)
(out/'completeness.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
