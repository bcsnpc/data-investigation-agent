"""Optional constant-per-connection context, never an execution authorization."""
from urllib.parse import urlsplit
from .onboarding import encoded


def attach(payload, config, ceiling):
    """Run AFTER normal projection. Never evict evidence to make room for labels."""
    uri=urlsplit(payload.get('starting_measure_id',''))
    workspace=config.get('fabric',{}).get('workspace_id')
    parts=uri.path.strip('/').split('/')
    if uri.scheme!='fabric' or uri.netloc!=workspace or not parts[0]:return payload
    sql=config.get('sql',{})
    if not all(sql.get(k) for k in ('server','database','visibility_schema')):return payload
    registry={
        's':{'system':'AZURE_SQL','connection':'sql://'+sql['server']+'/'+sql['database'],
             'schemas':[sql['visibility_schema']]},
        'f':{'system':'FABRIC_METADATA','connection':'fabric://'+workspace,
             'schema':'UNKNOWN','sql_endpoint':'NOT_ESTABLISHED'},
        'p':{'system':'POWER_BI','connection':'fabric://'+workspace+'/'+parts[0],
             'schema':'N/A','sql_endpoint':'NOT_ESTABLISHED'},
        'a':{'system':'UNKNOWN'}}
    proposed={**payload,'connections':registry}
    return proposed if len(encoded(proposed))<=ceiling else payload


def prefix(identity, registry):
    # Scoped identity boundaries, not similar names or arbitrary URI prefixes.
    for key in ('s','p','f'):
        root=registry.get(key,{}).get('connection')
        if root and (identity==root or identity.startswith(root+'/')):return key
    return 'a'
