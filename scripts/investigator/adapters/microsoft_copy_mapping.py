"""Retained Copy-activity mapping hypotheses, never verification by name alone."""
import copy
import hashlib
import json


def infer_column_mapping(activity, source_columns, destination_columns):
    """Account for every projected output and retain casts as transformations.

    Fabric's omitted translator means automatic name mapping. This inventory is
    an onboarding hypothesis; it cannot itself earn an executable binding.
    """
    from sqlglot import parse, exp
    if activity.get('type') != 'Copy':
        raise ValueError('Expected a Copy activity')
    prop = activity['typeProperties']
    if 'translator' in prop:
        raise ValueError('Explicit translator must use its explicit mapping path')
    source, sink = prop['source'], prop['sink']
    if source.get('type') != 'AzureSqlSource' or sink.get('type') != 'LakehouseTableSink':
        raise ValueError('Unsupported automatic mapping source or destination')
    ds = source['datasetSettings']['typeProperties']
    trees = parse(source['sqlReaderQuery'], read='tsql')
    if len(trees) != 1 or not isinstance(trees[0], exp.Select):
        raise ValueError('Source projection is not one SELECT')
    tree = trees[0]
    if any(tree.args.get(k) for k in ('joins','where','group','having','qualify','distinct','limit','offset','with_')):
        raise ValueError('Source projection changes or bounds the row set')
    origin = tree.args.get('from_')
    if not origin or not isinstance(origin.this, exp.Table):
        raise ValueError('Source relation is not a declared table')
    table = origin.this
    if table.catalog or table.db != ds['schema'] or table.name != ds['table']:
        raise ValueError('Source query differs from declared source object')
    def index(columns):
        rows = list(columns)
        result = {c['name']: c for c in rows}
        if len(result) != len(rows) or len({n.casefold() for n in result}) != len(result):
            raise ValueError('Ambiguous column names')
        return result
    src, dst = index(source_columns), index(destination_columns)
    mappings = []
    for item in tree.expressions:
        expression = item.this if isinstance(item, exp.Alias) else item
        name = item.alias_or_name
        refs = list(expression.find_all(exp.Column))
        if not name or len(refs) != 1 or refs[0].name not in src or name not in dst:
            raise ValueError('Unresolved projected source or destination column')
        if refs[0].table and refs[0].table != table.alias_or_name:
            raise ValueError('Projection references a different relation')
        if not isinstance(expression, (exp.Column, exp.Cast)):
            raise ValueError('Unsupported projected expression')
        if isinstance(expression, exp.Cast) and not isinstance(expression.this, exp.Column):
            raise ValueError('Unsupported cast operand')
        source_meta = src[refs[0].name]
        if source_meta.get('computed_definition') is not None:
            raise ValueError('Computed source column requires its own proof')
        mappings.append({'source': refs[0].name, 'destination': name,
            'source_type': source_meta['data_type'], 'destination_type': dst[name]['data_type'],
            'expression': expression.sql(dialect='tsql'),
            'unchanged_column': isinstance(expression, exp.Column),
            'provenance': 'INFERRED_FROM_CODE', 'verification': 'UNVERIFIED'})
    if len({m['destination'] for m in mappings}) != len(mappings):
        raise ValueError('Duplicate destination projection')
    if set(dst) != {m['destination'] for m in mappings}:
        raise ValueError('Destination columns are not completely accounted for')
    raw = json.dumps(activity, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    return {'activity': activity['name'], 'definition_hash': hashlib.sha256(raw).hexdigest(),
        'mapping_mode': 'AUTOMATIC_BY_COLUMN_NAME', 'provenance': 'INFERRED_FROM_CODE',
        'verification': 'UNVERIFIED', 'mappings': mappings,
        'source_declaration': copy.deepcopy(source['datasetSettings']),
        'destination_declaration': copy.deepcopy(sink['datasetSettings']),
        'row_delivery': sink.get('tableActionOption'),
        'limitations': ['Column-name mapping is inferred, not verified equivalence.',
                        'Casts require independent type and value verification.',
                        'No source capture cut or served snapshot is established.']}


def graph_mapping(graph, part, activity, connections):
    """Retain a native Copy declaration plus inferred maps, never verification."""
    try:
        prop=activity['typeProperties']; source=prop['source']['datasetSettings']
        cid=source['externalReferences']['connection']; connection=connections[cid]
        pair=connection['data']['connectionDetails']['path'].split(';')
        if len(pair)!=2:raise ValueError('Source connection is not a declared server/database pair')
        database='sql://'+pair[0]+'/'+pair[1]
        declared=source['typeProperties']
        src=graph.find('SqlObject',declared['schema']+'.'+declared['table'],database)
        sink=prop['sink']['datasetSettings']; destination=sink['linkedService']['properties']['typeProperties']
        parent='fabric://'+destination['workspaceId']+'/'+destination['artifactId']
        if parent.rsplit('/',1)[0]!=part['parent'].rsplit('/',1)[0]:raise ValueError('Copy destination leaves declared workspace')
        # The platform lists legacy Lakehouse names without dbo; both retained
        # spellings may describe the declared object, but two objects are ambiguous.
        name=sink['typeProperties']['table'];schema=sink['typeProperties'].get('schema','dbo')
        matches=[a['id'] for a in graph.assets.values() if a['kind']=='LakehouseTable' and a['parent']==parent
                 and a['name'] in (name,schema+'.'+name)]
        if not src or len(matches)!=1:raise ValueError('Copy source or destination declaration unresolved or ambiguous')
        target=matches[0]
        inferred=infer_column_mapping(activity,graph.assets[src]['meta']['columns'],graph.assets[target]['meta']['columns'])
        graph.edge(src,target,'data',part['id'],{'activity':activity['name'],'mapping':inferred,'connection_evidence':connection})
        graph.edge(part['parent'],target,'produces',part['id'],{'activity':activity['name'],'mapping_provenance':'INFERRED_FROM_CODE','verification':'UNVERIFIED'})
    except (KeyError,ValueError,TypeError) as exc:
        graph.gap(part['parent'],'Embedded Copy mapping unavailable',{'activity':activity.get('name'),'reason':str(exc)})


def column_proposals(mapping, *, source_asset, destination_asset, part, boundary):
    """Consumer-valid candidates only for unchanged projected columns.

    The cast columns remain named exclusions. No candidate is verified here.
    """
    from ..lineage_binding import validate
    content=part['metadata']['content'];lines=content.splitlines()
    marker=json.dumps(mapping['activity'],ensure_ascii=False)
    hits=[i+1 for i,line in enumerate(lines) if marker in line and '"name"' in line]
    if len(hits)!=1:raise ValueError('Copy activity location is ambiguous in retained definition')
    if mapping['row_delivery']!='OverwriteSchema':raise ValueError('Copy delivery is not a declared whole-target overwrite')
    if mapping['verification']!='UNVERIFIED' or mapping['provenance']!='INFERRED_FROM_CODE':raise ValueError('Mapping evidence status differs')
    proposals=[];excluded=[]
    for entry in mapping['mappings']:
        if not entry['unchanged_column']:
            excluded.append({'column':entry['destination'],'reason':'Native cast remains unsupported by the neutral expression contract','expression':entry['expression']});continue
        source={'table':source_asset['id'],'columns':[entry['source']]}
        relation={'kind':'PROJECT','input':{'kind':'SCAN',**source},'columns':[
            {'name':entry['destination'],'expression':{'kind':'COLUMN','name':entry['source']}}]}
        proposal={'boundary':copy.deepcopy(boundary),'sources':[source],
            'target':{'table':destination_asset['id'],'column':entry['destination']},
            'expression':{'relation':relation,'column':entry['destination']},
            'location':{'item':part['parent_id'],'path':part['metadata']['path'],
                'cell':'activity:'+mapping['activity'],'line_start':hits[0],'line_end':len(lines),
                'content_hash':hashlib.sha256(content.encode()).hexdigest()},'extractor':'STATIC'}
        proposals.append(validate(proposal))
    return {'proposals':proposals,'excluded':excluded,'provenance':'INFERRED_FROM_CODE','verification':'UNVERIFIED'}
