"""Static-first proposals. A model may propose unresolved code, never verify it."""
import copy
from .lineage_binding import validate,PROPOSED_BINDING_SCHEMA,MAX_COLUMNS
from .code_static import Unsupported
from .transformation_ast import Reader
from .transformation_sql import extract_statement

def scan_inventory(relation):
    kind=relation['kind']
    if kind=='SCAN':return [{'table':relation['table'],'columns':relation['columns']}]
    if kind=='JOIN':return scan_inventory(relation['left'])+scan_inventory(relation['right'])
    return scan_inventory(relation['input'])

def static(unit,*,schemas,boundary,item,target_table):
    cells=unit['cells'];languages={c['language'].casefold() for c in cells}
    if languages<={'python','pyspark'}:
        # Preserve physical file line addresses while rebuilding only code cells.
        # Notebook JSON uses a cell-local location instead of fabricated file lines.
        if unit['path'].endswith('.ipynb'):
            chunks=[];spans=[];offset=1
            for cell in cells:
                source=cell['source'];source=source if source.endswith('\n') else source+'\n'
                size=len(source.splitlines());spans.append((offset,offset+size-1,cell))
                chunks.append(source);offset+=size
            text=''.join(chunks)
        else:
            lines=[]
            for cell in cells:
                if cell['line_start']<len(lines)+1:raise Unsupported('Overlapping code cell locations')
                lines+=['\n']*(cell['line_start']-len(lines)-1)
                source=cell['source'];lines.append(source if source.endswith('\n') else source+'\n')
                # Number of physical lines, not number of list chunks.
                lines=''.join(lines).splitlines(keepends=True)
            text=''.join(lines)
        reader=Reader(text,schemas);writes=reader.writes;locations=reader.write_locations
    elif languages<={'sql','sparksql','tsql'}:
        writes={};locations={}
        for cell in cells:
            found=extract_statement(cell['source'],schemas)
            if set(writes)&set(found):raise Unsupported('Multiple cell writers for one target')
            writes.update(found)
            locations.update({target:(cell['line_start'],cell['line_end']) for target in found})
    else:raise Unsupported('Code language requires model proposal')
    proposals=[];seeded=[];other_writes=[]
    for target,frame in writes.items():
        if frame.plan is None:seeded.append(target);continue
        if target!=target_table:
            other_writes.append({'table':target,'columns':list(frame.columns),'sources':scan_inventory(frame.plan)});continue
        start,end=locations[target]
        if unit['path'].endswith('.ipynb'):
            span=next((s for s in spans if s[0]<=start<=s[1]),None)
            if span is None or end>span[1]:raise Unsupported('Write crosses retained notebook cell boundary')
            cell=span[2];start=start-span[0]+1;end=end-span[0]+1
        else:cell=next((c for c in cells if c['line_start']<=start<=c['line_end']),None)
        if cell is None:raise Unsupported('Write lacks a retained cell location')
        for name in frame.columns:
            proposals.append(validate({'boundary':copy.deepcopy(boundary),'sources':scan_inventory(frame.plan),
                'target':{'table':target,'column':name},'expression':{'relation':frame.plan,'column':name},
                'location':{'item':item,'path':unit['path'],'cell':cell['id'],'line_start':start,'line_end':end,
                            'content_hash':unit['content_hash']},'extractor':'STATIC'}))
    return {'proposals':proposals,'seeded_without_read':seeded,'other_writes':other_writes,'extractor':'STATIC','reason':None}

def propose(unit,*,schemas,boundary,item,target_table,layers,model=None):
    try:return static(unit,schemas=schemas,boundary=boundary,item=item,target_table=target_table)
    except (Unsupported,SyntaxError,TypeError,KeyError,IndexError) as exc:
        reason=str(exc)
    if model is None:return {'proposals':[],'seeded_without_read':[],'extractor':None,'reason':'Static extraction unavailable; model proposer not supplied: '+reason}
    # Embedded literal row data is not an oracle for the fallback. A refusal is
    # safer than exposing fixture values as if they were code-only evidence.
    if any('createDataFrame' in c['source'] for c in unit['cells']):
        return {'proposals':[],'seeded_without_read':[],'extractor':None,
                'reason':'Static extraction unavailable; model fallback withheld because code includes literal row initialization: '+reason}
    payload={'code':copy.deepcopy(unit),'layers':copy.deepcopy(layers)}
    # The model gets the consumer's MODEL branch, never permission to claim
    # STATIC provenance. Engine-known identities are fixed in that same schema.
    schema=copy.deepcopy(PROPOSED_BINDING_SCHEMA['anyOf'][1])
    schema['$defs']=copy.deepcopy(PROPOSED_BINDING_SCHEMA['$defs'])
    for name,value in boundary.items():schema['properties']['boundary']['properties'][name]={'enum':[value]}
    schema['properties']['target']['properties']['table']={'enum':[target_table]}
    for name,value in {'item':item,'path':unit['path'],'content_hash':unit['content_hash']}.items():
        schema['properties']['location']['properties'][name]={'enum':[value]}
    candidates=model(payload,schema)
    if not isinstance(candidates,list) or len(candidates)>MAX_COLUMNS:raise ValueError('Model proposed-binding count exceeds bound')
    result=[]
    for candidate in candidates:
        candidate=validate(candidate)
        if candidate['extractor']!='MODEL':raise ValueError('Model must declare MODEL extractor')
        if candidate['boundary']!=boundary or candidate['location']['item']!=item or candidate['location']['path']!=unit['path'] or candidate['location']['content_hash']!=unit['content_hash']:
            raise ValueError('Model proposal differs from code/boundary identity')
        if candidate['target']['table']!=target_table:raise ValueError('Model proposal target is outside declared boundary')
        location=candidate['location']
        cell=next((c for c in unit['cells'] if c['id']==location['cell']),None)
        if cell is None or not cell['line_start']<=location['line_start']<=location['line_end']<=cell['line_end']:
            raise ValueError('Model proposal location is outside retained code cell')
        for source in candidate['sources']:
            if source['table'] not in schemas or not set(source['columns'])<=set(schemas[source['table']]):
                raise ValueError('Model proposal source columns are not declared')
        result.append(candidate)
    return {'proposals':result,'seeded_without_read':[],'extractor':'MODEL','reason':reason}
