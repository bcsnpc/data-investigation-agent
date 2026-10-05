"""Exact full-table Copy Job mappings; a data edge alone is not equivalence."""
import json


def approval_sample(context,target_id,column,*,boundary,context_id,cell,precision):
    """Compile only a served, exact full-entity declaration for sampled approval."""
    from ..lineage_binding import validate
    proof,reason=resolve(context,target_id,column)
    if proof is None:raise ValueError('Declared approval mapping unavailable: '+reason)
    current={a['id']:a for a in context['assets'] if a.get('availability')=='CURRENT'}
    target=current[target_id];part=current[proof['definition_asset_id']]
    source_column=proof['source_column'];table=proof['source']['id']
    relation={'kind':'SCAN','table':table,'columns':[source_column]}
    if source_column!=column:
        relation={'kind':'PROJECT','input':relation,'columns':[
            {'name':column,'expression':{'kind':'COLUMN','name':source_column}}]}
    proposal=validate({'boundary':boundary,'sources':[{'table':table,'columns':[source_column]}],
        'target':{'table':target['id'],'column':column},
        'expression':{'relation':relation,'column':column},
        'location':{'item':part['parent_id'],'path':part['metadata']['path'],'cell':'declaration',
                    'line_start':1,'line_end':max(1,len(part['metadata']['content'].splitlines())),
                    'content_hash':proof['definition_hash']},'extractor':'STATIC'})
    return {'proposal':proposal,'context':context_id,'cell':cell,'precision':precision}


def resolve(context, target_id, column):
    current={a['id']:a for a in context.get('assets',[]) if a.get('availability')=='CURRENT'}
    edges=[e for e in context.get('graph',{}).get('edges',[]) if e.get('relation')=='DERIVED_FROM'
           and e.get('source')==target_id and current.get(e.get('target'),{}).get('kind')=='SqlObject']
    if len(edges)!=1:return None,'No unique declared application mapping for input'
    edge=edges[0];source=current[edge['target']]
    proofs=[]
    for evidence in edge.get('evidence',[]):
        part=current.get(evidence.get('asset'),{})
        if part.get('kind')!='DefinitionPart' or part.get('metadata',{}).get('path')!='copyjob-content.json':continue
        try:
            doc=json.loads(part['metadata']['content']);prop=doc['properties']
            if set(doc)!={'properties','activities'} or set(prop)-{'jobMode','source','destination','policy'}:continue
            if set(prop['source'])!={'type','connectionSettings'}:continue
            settings=prop['source']['connectionSettings']
            if set(settings)!={'type','typeProperties','externalReferences'} or settings['type']!='AzureSqlDatabase':continue
            if set(settings['typeProperties'])!={'database'} or set(settings['externalReferences'])!={'connection'}:continue
            activity_id=evidence['detail']['activity']
            activities=[a for a in doc['activities'] if a['id']==activity_id]
            if len(activities)!=1:continue
            p=activities[0]['properties']
            # Unknown source predicates, query text, append/incremental delivery,
            # expressions, truncation and duplicate mappings cannot prove this
            # narrow unchanged-column quantity contract.
            if prop.get('jobMode')!='Batch' or prop['source'].get('type')!='AzureSqlTable':continue
            if prop['destination'].get('type')!='LakehouseTable':continue
            if set(p)-{'source','destination','enableStaging','translator','typeConversionSettings'}:continue
            if set(p['source'])!={'datasetSettings','partitionSettings'}:continue
            if set(p['source']['datasetSettings'])!={'schema','table'}:continue
            if p['source']['partitionSettings']!={'partitionOption':'None'}:continue
            dest=p['destination']
            if dest.get('writeBehavior')!='Overwrite' or dest.get('partitionOption')!='None':continue
            if set(dest)-{'partitionOption','writeBehavior','datasetSettings','applyVOrder','enableTimestampNtz','enableChangeDataFeed'}:continue
            if set(dest['datasetSettings'])!={'schema','table'}:continue
            if p.get('enableStaging') is not False:continue
            if p.get('typeConversionSettings')!={'typeConversion':{'allowDataTruncation':False,'treatBooleanAsNumber':False}}:continue
            translator=p['translator']
            if set(translator)!={'type','mappings'} or translator['type']!='TabularTranslator':continue
            mappings=translator['mappings']
            if not mappings or any(set(m)!={'source','destination'} or set(m['source'])!={'name'}
                or set(m['destination'])!={'name'} for m in mappings):continue
            if len({m['source']['name'] for m in mappings})!=len(mappings):continue
            if len({m['destination']['name'] for m in mappings})!=len(mappings):continue
            source_meta=source['metadata'];ds=p['source']['datasetSettings']
            if (source_meta['schema_name'],source_meta['name'],source_meta['type_desc'])!=(ds['schema'],ds['table'],'USER_TABLE'):continue
            connection_id=prop['source']['connectionSettings']['externalReferences']['connection']
            connections=[a for a in current.values() if a['kind']=='SourceConnection' and a['metadata'].get('id')==connection_id]
            if len(connections)!=1:continue
            connection=connections[0];details=connection['metadata']['connectionDetails']
            if details['type']!='SQL' or 'sql://'+details['path'].replace(';','/',1)!=source['parent_id']:continue
            destination=prop['destination']['connectionSettings']['typeProperties']
            target=current[target_id]
            if destination.get('rootFolder')!='Tables':continue
            if target['parent_id']!='fabric://'+destination['workspaceId']+'/'+destination['artifactId']:continue
            if target['name']!=dest['datasetSettings']['schema']+'.'+dest['datasetSettings']['table']:continue
            source_columns={c['name']:c for c in source_meta['columns']}
            if any(m['source']['name'] not in source_columns or
                'computed_definition' not in source_columns[m['source']['name']] or
                source_columns[m['source']['name']]['computed_definition'] is not None for m in mappings):continue
            columns={m['destination']['name']:source_columns[m['source']['name']] for m in mappings}
            selected=[m for m in mappings if m['destination']['name']==column]
            if len(selected)!=1 or columns[column]['data_type'] not in ('int','bigint','smallint','tinyint'):continue
            proofs.append({'source':source,'source_column':selected[0]['source']['name'],
                'destination_columns':columns,'definition_asset_id':part['id'],
                'definition_hash':part['content_hash'],'producer_id':part['parent_id'],
                'connection_asset_id':connection['id'],'connection_hash':connection['content_hash'],
                'mapping':p,'server':details['path'].split(';')[0],'database':details['path'].split(';')[1]})
        except (KeyError,TypeError,ValueError):continue
    if len(proofs)!=1:return None,'Copy mapping cannot establish an unchanged whole-entity integral quantity'
    return proofs[0],None
