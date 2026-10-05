"""Transport policy from exact compiled asset identities, never query text."""
DEFAULT_WORKER_TIMEOUT=90


def policy(config,request,*,default_timeout=DEFAULT_WORKER_TIMEOUT):
    ids=set(request.get('asset_ids',[]))
    layers=[l for l in config.get('_estate',{}).get('layers',[]) if l['asset_id'] in ids]
    return {'serverless':any(l.get('serverless',False) for l in layers),
            'worker_timeout_seconds':max([l.get('worker_timeout_seconds',default_timeout) for l in layers] or [default_timeout])}
