"""Model-facing projection only. Full pinned case evidence remains resolvable."""
from copy import deepcopy
from .estate_graph_contract import digest
from .retained_definition_evidence import references


def project(context):
    result=deepcopy(context)
    refs={r['asset_id']:{'evidence_id':'case-evidence:'+digest(r),**r} for r in references(context)}
    definitions=[]
    for item in context.get('retained_native_definitions',[]):
        ref=refs.get(item.get('id'))
        if ref:
            definitions.append({**ref,'kind':item['kind'],
                'fetch':'get_evidence returns the complete original native definition; no estate read.'})
        else:
            definitions.append(deepcopy(item))
    result['retained_native_definitions']=definitions
    # Bodies embedded again in path metadata must not defeat on-demand lookup.
    path=result.get('path',{})
    for node in path.get('nodes',[]) if isinstance(path,dict) else []:
        props=node.get('properties',{})
        asset=props.get('asset_id') or props.get('definition_source_id')
        ref=refs.get(asset) or refs.get(node.get('provenance',{}).get('source_id'))
        if not ref:continue
        for key in ('content','definition','definitions'):
            if props.get(key):props[key]={'fetch_evidence_id':ref['evidence_id']}
    result['definition_lookup']='Full original definitions stay pinned in the case. Fetch get_evidence(id) before making a claim that needs their contents.'
    return result
