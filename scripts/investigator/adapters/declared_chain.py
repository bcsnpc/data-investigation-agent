"""Scoped, definition-backed additive quantity paths for the Microsoft adapter."""
from ..privacy_identities import text_digest
import hashlib
import copy
from .notebook_quantities import DeclaredQuantities

TYPES={'long':'bigint','bigint':'bigint','int':'int','string':'nvarchar','double':'float','boolean':'bit'}

def extend(context, layers):
    if len(layers)<2:return layers,[],None
    assets=[a for a in context.get('assets',[]) if a.get('availability')=='CURRENT']
    by_id={a['id']:a for a in assets};writers={};errors=[]
    parts=[a for a in assets if a.get('kind')=='DefinitionPart' and a.get('metadata',{}).get('path')=='notebook-content.py']
    if len(parts)>32:return layers,[],{'upper_layer':layers[-1]['id'],'lower_layer':'unresolved upstream','reason':'Definition analysis budget exceeded'}
    for part in parts:
        code=part['metadata'].get('content','')
        try:analysis=DeclaredQuantities(code)
        except (ValueError,TypeError,KeyError,IndexError,RecursionError):
            errors.append(part['id']);continue
        for path,frame in analysis.writes.items():writers.setdefault(path,[]).append((part,frame,text_digest(code)))
    planned=list(layers);seen={l['id'] for l in planned};notes=[]
    column=next((c.get('sourceColumn') for c in planned[-1].get('declared_columns',[])
                 if c.get('name')==planned[-1].get('semantic_column')),None)
    gap=None
    # Metadata expansion is bounded independently from the execution ceiling.
    for _ in range(32):
        upper=planned[-1];asset=by_id.get(upper['id']);path=(asset or {}).get('metadata',{}).get('location')
        matches=writers.get(path,[])
        from .copy_quantity import resolve as copy_mapping
        copy_proof,copy_reason=copy_mapping(context,upper['id'],column)
        if matches and copy_proof:
            gap={'upper_layer':upper['id'],'lower_layer':'unresolved upstream','reason':'Ambiguous declared notebook and Copy Job producers'};break
        if not matches and copy_proof:
            source=copy_proof['source'];meta=source['metadata']
            contract={'kind':'UNCHANGED_ADDITIVE_COLUMN','column':copy_proof['source_column'],
                'definition_asset_id':copy_proof['definition_asset_id'],'definition_hash':copy_proof['definition_hash'],
                'operations':[{'operation':'COPY','grain':'Full-table overwrite with explicit one-to-one column mappings; no declared source predicate.'}],
                'scope':'whole entity, no filters or grouping',
                'limitation':'The declared copy mapping is not a source capture cut or proof of synchronized snapshots.'}
            planned.append({'id':source['id'],'kind':'application_quantity','measure':upper['measure'],
                'semantic_column':copy_proof['source_column'],'source_column':copy_proof['source_column'],
                'definition_asset_id':copy_proof['definition_asset_id'],'transformation_asset_id':copy_proof['producer_id'],
                'binding':{'status':'RESOLVED','provenance':'DECLARED_BY_DEFINITION',
                    'asset':{k:source[k] for k in ('id','name','parent_id','kind')},
                    'declared_connection_asset_id':copy_proof['connection_asset_id']},
                'compiled':{'server':copy_proof['server'],'database':copy_proof['database'],
                    'source_column':copy_proof['source_column'],'schema':meta['schema_name'],'table':meta['name']},
                'quantity_contract':contract,'copy_mapping_proof':copy_proof})
            notes.append({'upper_layer':upper['id'],'lower_layer':source['id'],**contract})
            gap=None;break
        if len(matches)!=1:
            gap={'upper_layer':upper['id'],'lower_layer':'unresolved upstream','reason':
                 'Ambiguous declared writers' if matches else 'No supported declared producer; '+copy_reason+'; unsupported definitions: '+str(len(errors))};break
        part,frame,definition_hash=matches[0]
        if column not in frame.origins:
            gap={'upper_layer':upper['id'],'lower_layer':'unresolved upstream','reason':
                 'No declared upstream read for this quantity (literal initialization or derived/unsupported column)'};break
        source_path,source_column=frame.origins[column]
        targets=[a for a in assets if a.get('kind')=='LakehouseTable' and a.get('metadata',{}).get('location')==source_path]
        if len(targets)!=1:
            gap={'upper_layer':upper['id'],'lower_layer':source_path,'reason':'Declared input is absent or ambiguous in the approved catalog'};break
        target=targets[0]
        if target['id'] in seen:
            gap={'upper_layer':upper['id'],'lower_layer':target['id'],'reason':'Declared dependency cycle'};break
        source_matches=writers.get(source_path,[])
        source_copy,_=copy_mapping(context,target['id'],source_column)
        if len(source_matches)>1 or (source_matches and source_copy):
            gap={'upper_layer':upper['id'],'lower_layer':target['id'],'reason':'Ambiguous physical schema declarations for input'};break
        if not source_matches and not source_copy:
            gap={'upper_layer':upper['id'],'lower_layer':target['id'],'reason':'No unique physical schema declaration for input'};break
        source_columns=(source_matches[0][1].columns if source_matches else
            {k:v['data_type'] for k,v in source_copy['destination_columns'].items()})
        if source_columns.get(source_column) not in ('long','bigint','int','smallint','tinyint'):
            gap={'upper_layer':upper['id'],'lower_layer':target['id'],'reason':'Only unchanged integral additive quantities are supported'};break
        name=target['name'];schema,table=name.split('.',1) if '.' in name else ('dbo',name)
        contract={'kind':'UNCHANGED_ADDITIVE_COLUMN','column':source_column,
            'definition_asset_id':part['id'],'definition_hash':definition_hash,
            'operations':frame.operations,'scope':'whole entity, no filters or grouping',
            'limitation':'Row multiplicity and whole-row deduplication may change the total; agreement does not establish intended grain, key uniqueness or a common snapshot.'}
        vocabulary=copy.deepcopy(frame.vocabulary.get(column,{}))
        # Names can also be business concepts. Reject identifier form, never
        # equality with catalog names (even within this quantity's scope).
        from ..business_vocabulary import safe_term
        if any(not safe_term(v['text']) for v in vocabulary.values()):vocabulary={}
        for v in vocabulary.values():
            v.update(definition_asset_id=part['id'],definition_hash=definition_hash)
        planned.append({'id':target['id'],'kind':'declared_quantity','source_column':source_column,
            'definition_asset_id':part['id'],'transformation_asset_id':part['parent_id'],
            'measure':upper['measure'],'semantic_column':source_column,'semantic_table':name,
            'binding':{'status':'RESOLVED','asset':{k:target[k] for k in ('id','name','parent_id','kind')},
                       'provenance':'DECLARED_BY_DEFINITION'},
            'compiled':{'source_column':source_column,
                'schema':schema,'table':table,'catalog':[{'id':target['id'],'provenance':'DECLARED_BY_DEFINITION',
                    'metadata':{'schema_name':schema,'name':table,'type_desc':'USER_TABLE','columns':[
                        {'name':c,'data_type':TYPES.get(t,t if t in ('smallint','tinyint') else 'sql_variant')} for c,t in source_columns.items()]}}]},
            'quantity_contract':contract,'business_vocabulary':vocabulary})
        notes.append({'upper_layer':upper['id'],'lower_layer':target['id'],**contract})
        seen.add(target['id']);column=source_column
    else:gap={'upper_layer':planned[-1]['id'],'lower_layer':'unresolved upstream','reason':'Metadata path-depth bound reached'}
    return planned,notes,gap
