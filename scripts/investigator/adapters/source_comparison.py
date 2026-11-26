"""Bind application comparisons to admitted native SQL source objects."""
from ..primary_verification import query_references


def require_source_read(args, case):
    # Native addresses distinguish application SQL from Fabric SQL endpoints.
    # A missing optional SOR declaration does not erase an admitted source route.
    layers = case['context'].get('layers', {})
    source = {key: {o['id'] for o in layer.get('objects', [])
                    if o.get('id', '').startswith('sql://')}
              for key, layer in layers.items()}
    source = {key: ids for key, ids in source.items() if ids}
    declaration = case['context'].get('system_of_record', {})
    if declaration.get('layer') in layers and declaration.get('asset_id'):
        source.setdefault(declaration['layer'], set()).add(declaration['asset_id'])
    requested = (case['intake'].get('compared_with') or {}).get('source')
    if requested:
        # When intake names an exact source object, another source won't do.
        node = next((n for n in case['context'].get('path', {}).get('nodes', [])
                     if n['id'] == requested), {})
        asset = node.get('properties', {}).get('asset_id')
        if asset is None and requested.startswith('sql://'):
            asset=requested
        if asset is None and declaration.get('declared') is True:
            asset=declaration.get('asset_id')
        # Older admitted contexts omit the source node but bind a single
        # application route. Reuse that native route, never a name match.
        if asset is None and len(source)==1:
            pass  # Single admitted database route, possibly multiple tables.
        elif asset is None:
            source={}
        else:
            source = {key: {identity for identity in ids
                            if identity == asset or identity.startswith(asset.rstrip('/') + '/object/')}
                      for key, ids in source.items()}
        source = {key: ids for key, ids in source.items() if ids}
    references = query_references(case, args['evidence_ids'])
    reads = [q for q in case['queries'] if q['id'] in references
             and q.get('purpose') in ('compare', 'recreate', 'record', 'history', 'lookup')
             and set(q.get('asset_ids', [])) & source.get(q['layer'], set())
             and not __import__('re').search(r'\b(?:sys\.|INFORMATION_SCHEMA\.|DESCRIBE\b|SHOW\b)', q.get('text', ''), __import__('re').I)]
    if args.get('verdict_class') == 'UNRESOLVED' and args.get('undecided'):
        return  # An honest missing-source handoff is not a source conclusion.
    if not any(q.get('status') == 'SUCCEEDED' and not q.get('truncated') and not q.get('result', {}).get('truncated') for q in reads):
        raise ValueError('SOURCE_COMPARISON_REQUIRES_CITED_SOURCE_READ: compare the requested application/source using its admitted native data route before concluding; metadata or warehouse reads alone do not establish the source value. If unavailable, retain checked findings and the precise missing source fact in an UNRESOLVED handoff.')
