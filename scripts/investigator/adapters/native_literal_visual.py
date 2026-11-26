"""Identify complete, unbound static text separately from numeric data visuals.

Only the exact admitted native asset is considered. Missing or dynamic content
is never evidence of a non-data visual; explicit targets remain the caller's choice.
"""
from ..estate_graph_contract import digest


def nonmatching_literal(asset, figure):
    meta=asset.get('metadata',{})
    if (asset.get('kind')!='ReportVisual' or not isinstance(meta,dict)
            or not isinstance(meta.get('visual'),dict)
            or meta['visual'].get('visualType')!='textbox'):
        return None
    literals=[]
    def static(value):
        if isinstance(value,list):return all(static(item) for item in value)
        if not isinstance(value,dict):return True
        if any(key.casefold() in ('query','queryref','datafields','datatransforms') for key in value):return False
        if 'expr' in value:
            expr=value['expr']
            if not isinstance(expr,dict) or set(expr)!={'Literal'}:return False
            literal=expr['Literal']
            if not isinstance(literal,dict) or set(literal)!={'Value'} or not isinstance(literal['Value'],str):return False
            literals.append(literal['Value'])
        return all(static(item) for item in value.values())
    if not static(meta):return None
    try:
        groups=meta['visual']['objects']['general']
        paragraphs=[p for group in groups for p in group['properties']['paragraphs']]
        if not paragraphs:return None
        text=[]
        for paragraph in paragraphs:
            runs=paragraph['textRuns']
            if not runs or any(not isinstance(run.get('value'),str) for run in runs):return None
            text.append(''.join(run['value'] for run in runs))
        # Dates and numbers in an annotation do not make it a measured visual.
        # A static literal has no data binding; it belongs in the exclusions
        # proof, not in the set requiring native quantity reads.
    except (KeyError,TypeError,ValueError):
        return None
    return {'basis':'EXACT_NATIVE_STATIC_LITERAL','asset_id':asset['id'],
            'metadata_sha256':digest(meta),
            'reason':'Complete static text visual has no native data binding; it is not a measured number candidate.'}
