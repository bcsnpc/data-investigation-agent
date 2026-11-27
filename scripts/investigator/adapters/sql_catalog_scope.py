"""Native catalog scope selection; never infer schema membership by name."""
from copy import deepcopy


def project(snapshot,requested_schema=None):
    result=deepcopy(snapshot)
    # Older installations retain their explicit schema boundary. A connection-
    # only scan enumerates the objects its identity can actually see.
    whole=requested_schema in(None,'*')
    if not whole:
        result['objects']=[o for o in result['objects']if o['schema_name']==requested_schema]
    ids={o['object_id']for o in result['objects']}
    for key in ('columns','keys','definitions'):
        result[key]=[r for r in result.get(key,[])if r['object_id']in ids]
    for key in ('foreign_keys','checks'):
        result[key]=[r for r in result.get(key,[])if r['parent_object_id']in ids]
    result['visibility_schema']='*'if whole else requested_schema
    schemas=sorted({o['schema_name']for o in result['objects']})
    if not whole and requested_schema not in schemas:schemas.append(requested_schema)
    return result,schemas
