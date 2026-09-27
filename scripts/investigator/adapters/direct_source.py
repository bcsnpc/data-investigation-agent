"""Positive, deliberately narrow proof of an unchanged declared-source quantity."""
import hashlib
import re


def connection_proof(document, expression, source, partition, definition):
    # Full expression, not a search for a connection hidden inside M transforms.
    pattern=r'\s*let\s+([A-Za-z][A-Za-z0-9_]*)\s*=\s*Sql\.Database\(\s*"([^"\r\n]+)"\s*,\s*"([^"\r\n]+)"\s*\)\s+in\s+\1\s*'
    match=re.fullmatch(pattern,expression or '')
    if (not match or set(source)!={'type','schemaName','entityName','expressionSource'}
        or source['type']!='entity' or partition.get('mode') not in ('directLake','import')
        or document.get('roles') or any('calculationGroup' in t for t in document.get('tables',[]))):
        return None
    return {'definition_asset_id':definition['id'],
            'definition_hash':hashlib.sha256(definition['metadata']['content'].encode('utf-8')).hexdigest(),
            'server':match[2],'endpoint':match[3],'storage_mode':partition['mode']}


def quantity_proof(metadata, layer, config):
    binding=layer['binding'];connection=binding.get('unchanged_connection')
    if not connection or binding.get('provenance')!='DECLARED_BY_DEFINITION':return None
    if connection['server'].casefold()!=config.get('fabric',{}).get('sql_reader',{}).get('server','').casefold():return None
    tables=[a for a in metadata.get('assets',[]) if a.get('kind')=='SemanticTable' and a.get('name')==layer['semantic_table']]
    if (len(tables)!=1 or tables[0]['id']!=metadata['measure']['parent_id']
        or connection.get('semantic_table_id')!=tables[0]['id']):return None
    columns=[a for a in metadata.get('assets',[]) if a.get('kind')=='SemanticColumn'
             and a.get('name')==layer['semantic_column'] and a.get('parent_id')==tables[0]['id']]
    if len(columns)!=1:return None
    column=columns[0].get('metadata',{})
    if (column.get('dataType')!='int64' or not column.get('sourceColumn')
        or column.get('expression') or column.get('type') not in (None,'data')):return None
    return {'version':1,'basis':'UNCHANGED_DECLARED_SOURCE','presentation_layer':tables[0]['id'],
            'source_layer':layer['id'],'measure_id':metadata['measure']['id'],
            'source_column':column['sourceColumn'],'aggregate':'SUM','scope':'WHOLE_ENTITY',
            'intervening_operations':[], 'provenance':'DECLARED_BY_DEFINITION',**connection}
