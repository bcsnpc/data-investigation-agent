"""Offline mapping derivation from exact retained graph/owner declarations."""
import copy
import hashlib
import json
from pathlib import Path

from cloud_value_verifier import Refused, _one, _column
from investigator.model_context import assets as model_assets
from investigator.onboarding import digest


def load_owners(index_path, root):
    index_path=Path(index_path);root=Path(root)
    index=json.loads(index_path.read_bytes());by_id={};receipts=[]
    for row in index['owners']:
        path=root/row['path'];raw=path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=row['sha256']:raise Refused('OWNER_PAYLOAD_HASH_DIFFERS')
        body=json.loads(raw)
        receipts.append({k:row[k] for k in ('owner','observed_at','sha256')})
        for asset in body.get('assets',[]):
            if asset['id'] in by_id and by_id[asset['id']]!=asset:raise Refused('OWNER_ASSET_CONFLICT')
            by_id[asset['id']]=asset
    return list(by_id.values()),receipts


def required_columns(model, program, restrictions):
    catalog={a['id']:a for a in model_assets(model['context'])}
    required={program['column']}|{r['field_id'] for r in restrictions}
    required|={program[k] for k in ('filter_column','fact_key','lookup_key') if k in program}
    main=catalog[program.get('filter_column',program['column'])]['parent_id']
    for identity in list(required):
        table=catalog[identity]['parent_id']
        if table==main or table==program.get('remove_table'):continue
        names=catalog[main]['name'],catalog[table]['name']
        rel=_one([a for a in catalog.values() if a['kind']=='SemanticRelationship'
            and a['metadata'].get('fromTable')==names[0] and a['metadata'].get('toTable')==names[1]
            and a['metadata'].get('isActive',True) is True],'REQUIRED_RELATIONSHIP_AMBIGUOUS')
        required.add(_column(model,names[0],rel['metadata']['fromColumn'])['id'])
        required.add(_column(model,names[1],rel['metadata']['toColumn'])['id'])
    return sorted(required)


def endpoint(container, all_assets, endpoint_receipts):
    asset=_one([a for a in all_assets if a['id']==container], 'MAPPING_CONTAINER_UNRESOLVED')
    if asset['kind']=='Warehouse':
        meta=asset['metadata'];server=meta.get('properties',{}).get('connectionString')
        if not server:raise Refused('WAREHOUSE_CONNECTION_UNDECLARED')
        declared=[]
        for part in all_assets:
            if part['kind']!='DefinitionPart' or part.get('metadata',{}).get('path')!='pipeline-content.json':continue
            for index,activity in enumerate(json.loads(part['metadata']['content']).get('properties',{}).get('activities',[])):
                link=activity.get('linkedService',{}).get('properties',{}).get('typeProperties',{})
                if link.get('artifactId')==meta['id'] and link.get('endpoint')==server:
                    database=activity.get('typeProperties',{}).get('database')
                    if isinstance(database,str):declared.append((database,part['id'],index,digest(part['metadata'])))
        databases={row[0] for row in declared}
        if len(databases)>1:raise Refused('WAREHOUSE_DATABASE_DECLARATION_AMBIGUOUS')
        database=next(iter(databases)) if databases else meta['id']
        return {'surface':'FABRIC_SQL','server':server,'database':database,
            'container_asset_id':container,'provenance':{'asset_id':asset['id'],'content_hash':asset['content_hash'],
                'database_address':'EXPLICIT_SCRIPT_ACTIVITY_DATABASE' if declared else 'EXPLICIT_WAREHOUSE_ITEM_ID',
                'script_declarations':[{'part_id':row[1],'activity_index':row[2],'metadata_hash':row[3]} for row in declared]}}
    matches=[r for r in endpoint_receipts if container=='fabric://'+r['request']['workspace']+'/'+r['request']['lakehouse']]
    row=_one(matches,'LAKEHOUSE_ENDPOINT_BINDING_UNRESOLVED')
    response=row['response'];sql=response.get('properties',{}).get('sqlEndpointProperties',{})
    if response['id']!=row['request']['lakehouse'] or response['workspaceId']!=row['request']['workspace'] or not sql.get('connectionString'):
        raise Refused('LAKEHOUSE_ENDPOINT_RECEIPT_DISAGREES')
    return {'surface':'FABRIC_SQL','server':sql['connectionString'],'database':response['displayName'],
        'container_asset_id':container,'sql_endpoint_id':sql['id'],
        'provenance':{'request':copy.deepcopy(row['request']),'receipt_hash':digest(row)}}


def directlake(model, graph, all_assets, fields, endpoint_receipts):
    nodes={n['id']:n for n in graph['nodes']};native={a['id']:a for a in all_assets}
    columns={};objects={};provenance=[];containers=set()
    for identity in fields:
        source=_one([n for n in nodes.values() if n.get('properties',{}).get('asset_id')==identity],'SEMANTIC_GRAPH_COLUMN_UNRESOLVED')
        edge=_one([e for e in graph['edges'] if e['source']==source['id'] and e['kind']=='COMPUTED_FROM'
            and e.get('properties',{}).get('binding_kind')=='DIRECTLAKE_ENTITY'],'DIRECTLAKE_COLUMN_BINDING_UNRESOLVED')
        target=native[nodes[edge['target']]['properties']['asset_id']]
        table=native[target['parent_id']];properties=edge['properties'];containers.add(table['parent_id'])
        if properties['container_asset_id']!=table['parent_id']:raise Refused('DIRECTLAKE_CONTAINER_DISAGREES')
        table_id=table['id'];name=target['metadata'].get('name',target['name'])
        if properties['source_column']!=name:raise Refused('DIRECTLAKE_SOURCE_COLUMN_DISAGREES')
        objects.setdefault(table_id,{'schema':properties['schema'],'table':properties['entity'],
            'columns':[a['metadata'].get('name',a['name']) for a in all_assets if a.get('parent_id')==table_id and a['kind'] in ('LakehouseColumn','WarehouseColumn')]})
        columns[identity]={'object_id':table_id,'column':name}
        provenance.append({'semantic_column_id':identity,'edge_id':edge['id'],'provenance':copy.deepcopy(edge['provenance']),
            'physical_definition':copy.deepcopy(properties['physical_definition']),
            'physical_column_definition':copy.deepcopy(properties.get('physical_column_definition'))})
    container=_one(sorted(containers),'VALUE_MAPPING_SPANS_ENDPOINTS')
    return {'layer_id':container,'endpoint':endpoint(container,all_assets,endpoint_receipts),'objects':objects,'columns':columns,
        'relationships':[a['id'] for a in model_assets(model['context']) if a['kind']=='SemanticRelationship'],
        'provenance':provenance,'derivation':'DIRECTLAKE_SOURCE_COLUMN_AND_EXACT_CONTAINER'}


def notebook_upstream(mapping, all_assets, endpoint_receipts):
    from investigator.adapters.notebook_quantities import DeclaredQuantities
    writers={};native={a['id']:a for a in all_assets}
    for part in all_assets:
        if part['kind']!='DefinitionPart' or part.get('metadata',{}).get('path')!='notebook-content.py':continue
        try:analysis=DeclaredQuantities(part['metadata']['content'])
        except (ValueError,TypeError,KeyError,NotImplementedError):continue
        for path,frame in analysis.writes.items():writers.setdefault(path,[]).append((part,frame))
    result={'columns':{},'objects':{},'relationships':copy.deepcopy(mapping['relationships']),'provenance':[],'derivation':'DECLARED_NOTEBOOK_COLUMN_ORIGINS'}
    containers=set()
    for identity,column in mapping['columns'].items():
        target=native[column['object_id']];location=target['metadata'].get('location')
        alternatives=[]
        for part,frame in writers.get(location,[]):
            origin=frame.origins.get(column['column'])
            if origin:alternatives.append((part,origin,frame.operations))
        origins={tuple(row[1]) for row in alternatives}
        if not origins and writers.get(location):raise Refused('LITERAL_OR_DERIVED_INITIALIZATION_NO_UPSTREAM_READ:'+target['id']+':'+column['column'])
        if len(origins)!=1:raise Refused('NOTEBOOK_ORIGIN_UNDECLARED_OR_AMBIGUOUS:'+target['id']+':'+column['column'])
        path,name=next(iter(origins))
        source=_one([a for a in all_assets if a['kind']=='LakehouseTable' and a['metadata'].get('location')==path], 'NOTEBOOK_INPUT_LOCATION_UNRESOLVED')
        physical=_one([a for a in all_assets if a['kind']=='LakehouseColumn' and a.get('parent_id')==source['id'] and a['metadata'].get('name',a['name'])==name], 'NOTEBOOK_INPUT_COLUMN_UNRESOLVED')
        containers.add(source['parent_id']);result['columns'][identity]={'object_id':source['id'],'column':name}
        result['objects'].setdefault(source['id'],{'schema':source['metadata'].get('schema_name','dbo'),'table':source['metadata']['name'],
            'columns':[a['metadata'].get('name',a['name']) for a in all_assets if a.get('parent_id')==source['id'] and a['kind']=='LakehouseColumn']})
        result['provenance'].append({'semantic_column_id':identity,'target_asset_id':target['id'],'source_asset_id':source['id'],
            'source_column_asset_id':physical['id'],'source_column_metadata_hash':digest(physical['metadata']),
            'writers':[{'part_id':part['id'],'metadata_hash':digest(part['metadata']),'code_sha256':hashlib.sha256(part['metadata']['content'].encode()).hexdigest(),
                'operations':copy.deepcopy(operations)} for part,_,operations in alternatives]})
    container=_one(sorted(containers),'UPSTREAM_MAPPING_SPANS_ENDPOINTS');result['layer_id']=container
    result['endpoint']=endpoint(container,all_assets,endpoint_receipts)
    return result


def script_projection_upstream(mapping, all_assets):
    """Exact CTAS projection onto explicitly declared same-Warehouse views.

    The input view is labelled definition-declared, not catalog-observed. Its
    own cross-catalog continuation is retained as a gap, not resolved by name.
    """
    from sqlglot import parse_one, exp
    endpoint_pin=mapping['endpoint'];container=endpoint_pin['container_asset_id'];container_id=container.rsplit('/',1)[1]
    statements=[]
    for part in all_assets:
        if part['kind']!='DefinitionPart' or part.get('metadata',{}).get('path')!='pipeline-content.json':continue
        document=json.loads(part['metadata']['content'])
        for activity_index,activity in enumerate(document.get('properties',{}).get('activities',[])):
            link=activity.get('linkedService',{}).get('properties',{}).get('typeProperties',{})
            if link.get('artifactId')!=container_id or link.get('endpoint')!=endpoint_pin['server']:continue
            if activity.get('typeProperties',{}).get('database')!=endpoint_pin['database']:continue
            for index,script in enumerate(activity.get('typeProperties',{}).get('scripts',[])):
                text=script.get('text','')
                try:tree=parse_one(text,read='tsql')
                except Exception:continue
                if not isinstance(tree,exp.Create) or not isinstance(tree.this,exp.Table) or not isinstance(tree.expression,exp.Select):continue
                statements.append((tree,{'part_id':part['id'],'metadata_hash':digest(part['metadata']),
                    'statement_hash':hashlib.sha256(text.encode()).hexdigest(),
                    'pointer':f'/properties/activities/{activity_index}/typeProperties/scripts/{index}/text',
                    'expression':text,'execution_established':False}))
    output={'layer_id':container+'#declared-input-views','endpoint':copy.deepcopy(endpoint_pin),'objects':{},'columns':{},
        'relationships':copy.deepcopy(mapping['relationships']),'provenance':[],
        'derivation':'DECLARED_CTAS_PROJECTION_IN_EXACT_ACTIVITY_CONNECTION',
        'remaining_gap':'Cross-catalog view input requires an exact endpoint/container binding; display names are not a binding.'}
    for identity,column in mapping['columns'].items():
        target=mapping['objects'][column['object_id']];alternatives=[]
        for tree,proof in statements:
            if tree.kind!='TABLE' or tree.this.catalog or tree.this.db!=target['schema'] or tree.this.name!=target['table']:continue
            query=tree.expression
            if query.args.get('joins') or query.args.get('where') or query.args.get('group') or query.args.get('distinct'):continue
            source=query.args.get('from_')
            if not source or not isinstance(source.this,exp.Table) or source.this.catalog:continue
            selected=[p for p in query.expressions if p.alias_or_name==column['column']]
            if len(selected)!=1 or not isinstance(selected[0].unalias(),exp.Column):continue
            field=selected[0].unalias()
            if field.table and field.table!=source.this.alias_or_name:continue
            views=[(v,p) for v,p in statements if v.kind=='VIEW' and not v.this.catalog and v.this.db==source.this.db and v.this.name==source.this.name]
            if not views:continue
            for view,viewproof in views:
                projected=[x for x in view.expression.expressions if x.alias_or_name==field.name and isinstance(x.unalias(),exp.Column)]
                if len(projected)!=1:continue
                alternatives.append((source.this.db,source.this.name,field.name,proof,viewproof,
                    [x.alias_or_name for x in view.expression.expressions]))
        coordinates={(a[0],a[1],a[2]) for a in alternatives}
        if len(coordinates)!=1:raise Refused('SCRIPT_INPUT_PROJECTION_UNRESOLVED_OR_AMBIGUOUS:'+column['object_id']+':'+column['column'])
        schema,table,name=next(iter(coordinates));object_id=container+'/declared-view/'+schema+'.'+table
        output['objects'][object_id]={'schema':schema,'table':table,'columns':sorted(set(c for a in alternatives for c in a[5])),
            'availability':'DECLARED_IN_RETAINED_SCRIPT_NOT_CATALOG_OBSERVED'}
        output['columns'][identity]={'object_id':object_id,'column':name}
        output['provenance'].append({'semantic_column_id':identity,'target_object_id':column['object_id'],
            'alternatives':[{'projection':a[3],'view':a[4]} for a in alternatives]})
    return output
