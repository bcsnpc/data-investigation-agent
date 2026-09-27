"""Scoped, definition-backed additive quantity paths for the Microsoft adapter."""
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
        for path,frame in analysis.writes.items():writers.setdefault(path,[]).append((part,frame,hashlib.sha256(code.encode()).hexdigest()))
    planned=list(layers);seen={l['id'] for l in planned};notes=[]
    column=next((c.get('sourceColumn') for c in planned[-1].get('declared_columns',[])
                 if c.get('name')==planned[-1].get('semantic_column')),None)
    gap=None
    # Metadata expansion is bounded independently from the execution ceiling.
    for _ in range(32):
        upper=planned[-1];asset=by_id.get(upper['id']);path=(asset or {}).get('metadata',{}).get('location')
        matches=writers.get(path,[])
        if len(matches)!=1:
            gap={'upper_layer':upper['id'],'lower_layer':'unresolved upstream','reason':
                 'Ambiguous declared writers' if matches else 'No supported declared producer; unsupported definitions: '+str(len(errors))};break
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
        if len(source_matches)!=1:
            gap={'upper_layer':upper['id'],'lower_layer':target['id'],'reason':'No unique physical schema declaration for input'};break
        source_frame=source_matches[0][1]
        if source_frame.columns.get(source_column) not in ('long','bigint','int'):
            gap={'upper_layer':upper['id'],'lower_layer':target['id'],'reason':'Only unchanged integral additive quantities are supported'};break
        name=target['name'];schema,table=name.split('.',1) if '.' in name else ('dbo',name)
        contract={'kind':'UNCHANGED_ADDITIVE_COLUMN','column':source_column,
            'definition_asset_id':part['id'],'definition_hash':definition_hash,
            'operations':frame.operations,'scope':'whole entity, no filters or grouping',
            'limitation':'Row multiplicity and whole-row deduplication may change the total; agreement does not establish intended grain, key uniqueness or a common snapshot.'}
        vocabulary=copy.deepcopy(frame.vocabulary.get(column,{}))
        identifiers={c.casefold() for c in frame.columns}
        # Only identifiers in this definition's quantity scope can exclude a
        # label. A homonym elsewhere in the estate cannot rename this subject.
        paths={path,source_path}|{p for op in frame.operations for p in op.get('inputs',[])}
        scoped_assets=[a for a in assets if a.get('metadata',{}).get('location') in paths]
        identifiers.update(a['name'].casefold() for a in scoped_assets if isinstance(a.get('name'),str))
        identifiers.update(piece.casefold() for a in scoped_assets if isinstance(a.get('name'),str)
                           for piece in a['name'].split('.'))
        from ..business_vocabulary import safe_term
        if any(not safe_term(v['text']) or v['text'].casefold() in identifiers for v in vocabulary.values()):vocabulary={}
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
                        {'name':c,'data_type':TYPES.get(t,'sql_variant')} for c,t in source_frame.columns.items()]}}]},
            'quantity_contract':contract,'business_vocabulary':vocabulary})
        notes.append({'upper_layer':upper['id'],'lower_layer':target['id'],**contract})
        seen.add(target['id']);column=source_column
    else:gap={'upper_layer':planned[-1]['id'],'lower_layer':'unresolved upstream','reason':'Metadata path-depth bound reached'}
    return planned,notes,gap
