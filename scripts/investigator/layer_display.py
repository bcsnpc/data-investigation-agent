"""Display labels follow discovered parent identities, never name inference."""


def discovered_labels(assets,layers):
    by_id={a['id']:a for a in assets}
    result={}
    for layer in layers:
        asset=by_id.get(layer['id'])
        if not asset:continue
        parent=by_id.get(asset.get('parent_id'))
        result[asset['id']]={'name':asset.get('name') or asset['id'],
                            'container_id':asset.get('parent_id'),
                            'container_name':(parent or {}).get('name'),
                            'provenance':'DISCOVERED_PARENT_ID'}
    return result
