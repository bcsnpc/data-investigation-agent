"""Resolve definition-declared pointers without widening their declared scope.

The caller translates provider syntax into stable scope identities and exact
target labels.  This module never searches outside those roots and never picks
between multiple matches.
"""


def descendants(assets, roots):
    by_parent={}
    for asset in assets:
        by_parent.setdefault(asset.get('parent_id'),[]).append(asset)
    selected=[];seen=set();frontier=list(roots)
    while frontier:
        current=frontier.pop(0)
        if current in seen:continue
        seen.add(current)
        for asset in by_parent.get(current,[]):
            selected.append(asset);frontier.append(asset['id'])
    return selected


def resolve(assets, declaration):
    """Return one exact target, an explicit absence, or every ambiguous match."""
    roots=declaration.get('scope_ids')
    labels=declaration.get('target_labels')
    kinds=declaration.get('target_kinds')
    if not isinstance(roots,list) or not roots or any(not isinstance(x,str) or not x for x in roots):
        raise ValueError('Declared pointer requires stable scope identities')
    if not isinstance(labels,list) or not labels or any(not isinstance(x,str) or not x for x in labels):
        raise ValueError('Declared pointer requires exact target labels')
    if not isinstance(kinds,list) or not kinds or any(not isinstance(x,str) or not x for x in kinds):
        raise ValueError('Declared pointer requires target kinds')
    denied=declaration.get('denied_scope_ids',[])
    if not isinstance(denied,list) or any(not isinstance(x,str) or not x for x in denied):
        raise ValueError('Denied scope identities differ')
    provenance={'provenance':'DECLARED_BY_DEFINITION'}
    for key in ('definition_asset_id','definition_offset','declared_connection_asset_id'):
        if key in declaration:provenance[key]=declaration[key]
    if any(root in denied for root in roots):
        return {'status':'ACCESS_DENIED','scope_ids':roots,
                'denied_scope_ids':sorted(root for root in roots if root in denied),'candidates':[],**provenance}
    by_id={a['id']:a for a in assets}
    # Some inventories represent a connection/container only as the stable parent
    # identity on its children.  That is still an explicit scope; it is not a
    # license to search elsewhere.
    parent_ids={a.get('parent_id') for a in assets if a.get('parent_id')}
    missing=[root for root in roots if root not in by_id and root not in parent_ids]
    if missing:
        return {'status':'SCOPE_NOT_DISCOVERED','scope_ids':roots,'missing_scope_ids':missing,
                'candidates':[],**provenance}
    allowed_labels={x.casefold() for x in labels};allowed_kinds=set(kinds)
    matches=[a for a in descendants(assets,roots)
             if a.get('availability')=='CURRENT' and a.get('kind') in allowed_kinds
             and a.get('name','').casefold() in allowed_labels]
    matches.sort(key=lambda a:a['id'])
    candidates=[{k:a[k] for k in ('id','parent_id','kind','name') if k in a} for a in matches]
    if len(candidates)==1:
        return {'status':'RESOLVED','scope_ids':roots,'asset':candidates[0],
                'candidates':candidates,**provenance}
    return {'status':'AMBIGUOUS' if candidates else 'NO_MATCH_IN_SCOPE','scope_ids':roots,
            'candidates':candidates,**provenance}
