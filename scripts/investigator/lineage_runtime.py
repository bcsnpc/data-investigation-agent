"""Qualify adapter candidate paths using current sampled lineage evidence.

An adapter's static path is a candidate, not permission to bypass verification.
The quantities in the walk remain its original input/output quantities: the
verifier's transformed source expression is never substituted into the walk.
"""
import copy
from .transformation_service import select
from .lineage_binding import revalidate_verification,seal


def qualify(path, *, estate, declared, inferred, current_hashes, addresses,
            context, cell, precision):
    result=copy.deepcopy(path)
    layers=result['layers']
    by_asset={l['asset_id']:l['id'] for l in estate['layers']}
    locations={ (b['from_layer'],b['to_layer']):b for b in estate['lineage'].get('code_locations',[]) }
    evidence=[]
    for i,(upper,lower) in enumerate(zip(layers,layers[1:])):
        edge=(by_asset.get(lower['id']),by_asset.get(upper['id']))
        location=locations.get(edge)
        if not location or not location['may_infer_from_code']:continue
        reason=None
        if not estate['lineage']['inference']['enabled']:
            reason='Code inference is not authorised for this declared boundary.'
        upper_address=addresses.get(upper['id']);lower_address=addresses.get(lower['id'])
        column=upper.get('source_column')
        if not column:
            matches=[c.get('sourceColumn') for c in upper.get('declared_columns',[])
                     if c.get('name')==upper.get('semantic_column')]
            column=matches[0] if len(matches)==1 else None
        if not reason and (not upper_address or not lower_address or not column):
            reason='The candidate boundary lacks exact object locations or a declared quantity column.'
        selection=None
        if not reason:
            selection=select(declared=declared,inferred=inferred,current_hashes=current_hashes,
                boundary={'from_layer':edge[0],'to_layer':edge[1]},target_column=column,
                context=context,cell=cell,precision=precision)
            if selection['status']!='RESOLVED':reason=selection['reason'] if 'reason' in selection else 'The sampled code binding is ambiguous.'
        if not reason:
            verification=revalidate_verification(selection['verification'])
            proposal=verification['proposal']
            loc=proposal['location']
            permitted=[x for x in location['locations'] if x['path']==loc['path']]
            if not permitted:reason='Verified code location is outside the configured boundary.'
            elif proposal['target']['table']!=upper_address or not any(
                    s['table']==lower_address and lower.get('source_column') in s['columns']
                    for s in proposal['sources']):
                reason='Verified expression does not bind the candidate input and output objects and quantity.'
        evidence.append({'upper_layer':upper['id'],'lower_layer':lower['id'],
            'selection':copy.deepcopy(selection),'reason':reason})
        if reason:
            excluded=(selection or {}).get('excluded',[])
            refusal=({'lineage_refusal':{'proposal_count':len(excluded),
                'inventoried_proposal_count':selection.get('inventoried_proposal_count',len(excluded)),
                'statuses':sorted({r['status'] for r in excluded}),
                'reason_categories':sorted({r['reason_category'] for r in excluded})}} if excluded else {})
            result.update(layers=layers[:i+1],stopped_by='NO_LINEAGE',
                missing_comparable_quantity=reason,unresolved_boundary={
                    'upper_layer':upper['id'],'lower_layer':lower['id'],'reason':reason,**refusal})
            break
        # Carry the proof rather than a bare producer-owned VERIFIED label.
        lower['binding']={**lower.get('binding',{}),'provenance':selection['provenance'],
            'lineage_verification':verification,'code_location':copy.deepcopy(permitted[0])}
    result.setdefault('evidence',{})['lineage_qualification']=evidence
    return result
