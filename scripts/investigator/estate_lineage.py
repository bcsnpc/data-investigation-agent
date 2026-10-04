"""Use declared installation bindings without inventing quantity equivalence."""
import copy


def apply(path, estate):
    result=copy.deepcopy(path)
    resources={l['id']:l['asset_id'] for l in estate['layers']}
    declarations=[{'upper_layer':resources[b['to_layer']],
        'lower_layer':resources[b['from_layer']],'provenance':b['provenance']}
        for b in estate['lineage']['bindings']]
    result['estate_lineage_declarations']=declarations
    layers=result['layers']
    for i,(upper,lower) in enumerate(zip(layers,layers[1:])):
        selected=[b for b in declarations if b['upper_layer']==upper['id']]
        if selected and (len(selected)!=1 or selected[0]['lower_layer']!=lower['id']):
            reason='The discovered quantity path conflicts with the configured lineage declaration; no fallback binding was selected.'
            result.update(layers=layers[:i+1],stopped_by='NO_LINEAGE',unresolved_boundary={
                'upper_layer':upper['id'],'lower_layer':lower['id'],'reason':reason})
            return result
    if result.get('unresolved_boundary') and layers:
        selected=[b for b in declarations if b['upper_layer']==layers[-1]['id']]
        if selected:
            result['unresolved_boundary']={'upper_layer':layers[-1]['id'],
                'lower_layer':selected[0]['lower_layer'] if len(selected)==1 else 'ambiguous configured upstream',
                'reason':'Configured lineage is declared, but no unique faithful quantity contract could be compiled from the retained definitions; configuration is not a comparison proof.'}
    return result
