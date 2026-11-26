"""Prove that a retained literal text visual cannot display a stated number.

Only the exact admitted native asset is considered. Missing or dynamic content
is never evidence of a non-data visual; a matching literal remains a candidate.
"""
from decimal import Decimal, InvalidOperation
import re
from ..estate_graph_contract import digest


def nonmatching_literal(asset, figure):
    if not figure or figure.get('state')!='NUMBER' or figure.get('precision')!='EXACT':
        return None
    meta=asset.get('metadata',{})
    if asset.get('kind')!='ReportVisual' or meta.get('visual',{}).get('visualType')!='textbox':
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
        content=' '.join([*text,*literals])
        # Spelled quantities or unknown magnitude conventions remain ambiguous.
        if re.search(r'\b(zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|hundred|thousand|million|billion)\b',content,re.I):return None
        number=Decimal(figure['value'])
        for match in re.finditer(r'[-+]?\d[\d,]*(?:\.\d+)?\s*[kmb]?',content,re.I):
            token=match.group().replace(',','').strip().lower()
            scale={'k':1000,'m':1000000,'b':1000000000}.get(token[-1],1)
            value=Decimal(token[:-1].strip() if scale!=1 else token)*scale
            if value==number:return None
    except (KeyError,TypeError,ValueError,InvalidOperation):
        return None
    return {'basis':'EXACT_NATIVE_LITERAL_NONMATCH','asset_id':asset['id'],
            'metadata_sha256':digest(meta),
            'reason':'Literal-only text visual contains no matching stated numeric value.'}
