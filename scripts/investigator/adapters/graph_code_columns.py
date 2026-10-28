"""Attach bounded notebook language dependencies; never execute retained code."""
from ..transformation_ast import Reader
from ..code_static import Unsupported


def dependencies(plan):
    """Value origins only; row-changing operations remain a separate plan step."""
    kind=plan['kind']
    if kind=='SCAN':return {name:{(plan['table'],name)} for name in plan['columns']}
    if kind=='JOIN':
        left,right=dependencies(plan['left']),dependencies(plan['right'])
        if (left.keys()&right.keys())-set(plan['keys']):raise Unsupported('Ambiguous joined columns')
        # Spark using-column joins retain the left key; right keys still affect
        # row multiplicity, explicitly retained in the relational plan below.
        return {**right,**left}
    incoming=dependencies(plan['input'])
    if kind in ('FILTER','DEDUPE'):return incoming
    if kind not in ('PROJECT','AGGREGATE'):raise Unsupported('Unknown relation kind')
    def scalar(value):
        if value['kind']=='COLUMN':return incoming[value['name']]
        if value['kind']=='LITERAL':return set()
        found=set()
        for nested in value.values():
            if isinstance(nested,dict):found|=scalar(nested)
        return found
    return {column['name']:scalar(column['expression']) for column in plan['columns']}


def attach_notebook(graph,parent,content,proof):
    # Exact retained storage locations bind code to objects. A filename or a
    # table's display-name suffix is not enough to join two catalogs.
    locations={}
    for aid,asset in graph.assets.items():
        if asset['kind']!='LakehouseTable':continue
        location=asset.get('metadata',{}).get('location')
        if isinstance(location,str):locations.setdefault(location,[]).append(aid)
    schemas={}
    for location,aids in locations.items():
        if len(aids)!=1:continue
        schemas[location]={asset['name']:asset.get('metadata',{}).get('type_name','unknown')
            for asset in graph.assets.values() if asset['kind']=='LakehouseColumn' and asset.get('parent_id')==aids[0]}
    reader=Reader(content,schemas)
    lines=content.splitlines(keepends=True);offsets=[0]
    for line in lines:offsets.append(offsets[-1]+len(line))
    def table(path):
        found=locations.get(path,[])
        if len(found)!=1:raise Unsupported('Code path has no unique retained storage-location object: '+path)
        return found[0]
    def column(aid,name,at):
        root=graph.by_asset[aid]
        children={edge['target'] for edge in graph.edges.values() if edge['source']==root and edge['kind']=='CONTAINS'}
        found=[node['id'] for node in graph.nodes.values() if node['id'] in children and node['kind'] in ('COLUMN','CALCULATED_COLUMN') and node['label']==name]
        if len(found)>1:raise Unsupported('Ambiguous code column')
        if found:return found[0]
        # This is a declaration in code, not an observed physical column schema.
        node=graph.add('COLUMN',name,['code-column',aid,name],at,
            {'schema_evidence':'CODE_DECLARED_NOT_OBSERVED','table_asset_id':aid},owner=graph.nodes[root]['owner'])
        graph.link('CONTAINS',root,node,at)
        return node
    attached=0
    for path,frame in reader.writes.items():
        if frame.plan is None:continue # literal seeds are never dependencies
        try:
            output=table(path);origins=dependencies(frame.plan)
            inputs={p:table(p) for values in origins.values() for p,_ in values}
        except (Unsupported,KeyError) as error:
            graph.gap(graph.by_asset[parent],str(error),'Collect the exact missing code-bound object/schema; no name-based substitute is allowed.',proof)
            continue
        first,last=reader.write_locations[path]
        at={**proof,'span':{'kind':'TEXT','start':offsets[first-1],'end':offsets[last]}} if proof['span']['kind']=='TEXT' else proof
        step=graph.add('QUERY_STEP','Declared notebook write',[proof['source_id'],'write',path],at,
            {'language':'PYTHON','relation':frame.plan,'execution_established':False})
        graph.link('CONTAINS',graph.by_asset[parent],step,at)
        graph.link('DERIVED_IN_STEP',graph.by_asset[output],step,at)
        for name,values in origins.items():
            target=column(output,name,at)
            graph.link('DERIVED_IN_STEP',target,step,at)
            for source,name_in in sorted(values):
                origin=column(inputs[source],name_in,at)
                graph.link('COMPUTED_FROM',target,origin,at)
                attached+=1
        # Retain row/filter/join influence separately from scalar origins.
        for source in sorted(inputs):graph.link('COMPUTED_FROM',step,graph.by_asset[inputs[source]],at)
    return attached
