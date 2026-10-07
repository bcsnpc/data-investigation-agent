"""Carry a verified KEY profile into translation, without relabelling receipts.

Column identities are explicit catalog declarations. Original BINDING_SAMPLE
addresses remain original; the certificate records its derived key universes.
"""
import copy
from decimal import Decimal
from jsonschema import Draft202012Validator


def certify(declaration, verification, columns):
    from .translation_proposer import KEY_BINDING
    from .lineage_binding import revalidate_verification
    Draft202012Validator(KEY_BINDING).validate(declaration)
    checked=revalidate_verification(verification)
    if (checked['status']!='VERIFIED' or checked['address']['profile']!='KEY'
            or checked['proposal'].get('binding_kind')!='KEY'):
        raise ValueError('NO_KEY_BINDING: profile is not a verified KEY binding')
    if checked['context']!=declaration['context'] or checked['key_normalization']!=declaration['normalization']:
        raise ValueError('KEY context or normalization differs')
    if len(declaration['columns'])!=1 or set(columns)!={'native','proposed'}:
        raise ValueError('Per-column KEY certificate requires one explicit correspondence')
    proposal=checked['proposal']
    native=columns['native'];proposed=columns['proposed']
    for side in ('native','proposed'):
        if set(columns[side])!={'id','table','column'} or columns[side]['id']!=declaration['columns'][0][side]:
            raise ValueError('KEY catalog identity differs from correspondence')
    if {'table':native['table'],'column':native['column']}!=proposal['target']:
        raise ValueError('KEY target differs from its catalog declaration')
    if not any(s['table']==proposed['table'] and proposed['column'] in s['columns'] for s in proposal['sources']):
        raise ValueError('KEY source is absent from its catalog declaration')
    # Computed columns and ambiguous ownership cannot establish correspondence.
    relation=proposal['expression']['relation'];column=proposal['expression']['column']
    def origin(node, name):
        kind=node['kind']
        if kind=='SCAN':return (node['table'],name) if name in node['columns'] else None
        if kind in ('PROJECT','AGGREGATE'):
            match=next((c for c in node['columns'] if c['name']==name),None)
            if match is None or match['expression']['kind']!='COLUMN':return None
            return origin(node['input'],match['expression']['name'])
        if kind=='JOIN':
            left=origin(node['left'],name);right=origin(node['right'],name)
            if left and right and name not in node['keys']:return None
            return left or right
        return origin(node['input'],name)
    if origin(relation,column)!=(proposed['table'],proposed['column']):
        raise ValueError('KEY source column lacks one declared identity-preserving origin')
    observations=[]
    for original in checked['observations']:
        keys=[]
        for row in original['evidence']['values']:
            value=row['key_value'];cell=value if isinstance(value,dict) else None
            value=cell['value'] if cell else value
            if cell and cell['type']=='decimal':value=int(Decimal(value))
            if isinstance(value,str):
                if declaration['normalization']['case_fold']:value=value.casefold()
                if declaration['normalization']['trim']:value=value.rstrip(' ')
            keys.append([value])
        observations.append({'keys':keys,'evidence':copy.deepcopy(original['evidence'])})
    return {'version':'per-binding-key-v1','kind':'KEY','declaration':copy.deepcopy(declaration),
        'binding_verification':checked,'column_catalog':copy.deepcopy(columns),
        'observations':observations,'status':'VERIFIED','snapshot_status':checked['snapshot_status']}
