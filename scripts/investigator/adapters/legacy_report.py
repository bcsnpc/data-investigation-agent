"""Bounded PBIR-Legacy structure; never manufacture enhanced PBIR documents."""
import json
from urllib.parse import quote

def object_json(value):
    if isinstance(value,str):value=json.loads(value)
    if not isinstance(value,dict):raise ValueError('PBIR_LEGACY_CONFIG_OBJECT_REQUIRED')
    return value

def children(document):
    if not isinstance(document,dict)or not isinstance(document.get('sections'),list)or not 1<=len(document['sections'])<=100:
        raise ValueError('PBIR_LEGACY_PAGE_BOUND')
    seen=set();count=0
    for i,page in enumerate(document['sections']):
        name=page.get('name')if isinstance(page,dict)else None
        if not isinstance(name,str)or not 1<=len(name)<=256 or name in seen:raise ValueError('PBIR_LEGACY_PAGE_IDENTITY')
        seen.add(name);visuals=page.get('visualContainers',[])
        if not isinstance(visuals,list):raise ValueError('PBIR_LEGACY_VISUAL_SHAPE')
        yield '/page/'+quote(name,safe=''),'ReportPage',page.get('displayName',name),page,None,'/sections/'+str(i)
        ids=set()
        for j,visual in enumerate(visuals):
            count+=1
            if count>5000 or not isinstance(visual,dict):raise ValueError('PBIR_LEGACY_VISUAL_BOUND')
            cfg=object_json(visual.get('config'));vid=cfg.get('name')
            if not isinstance(vid,str)or not 1<=len(vid)<=256 or vid in ids:raise ValueError('PBIR_LEGACY_VISUAL_IDENTITY')
            ids.add(vid)
            path='/sections/'+str(i)+'/visualContainers/'+str(j)
            yield '/page/'+quote(name,safe='')+'/visual/'+quote(vid,safe=''),'ReportVisual',vid,visual,'/page/'+quote(name,safe=''),path

def expand(store,item,raw,source):
    document=json.loads(raw)
    values=list(children(document))  # Validate the whole layout before publication.
    for suffix,kind,name,metadata,parent,_ in values:
        store.asset(item+suffix,kind,name,source,metadata,item+(parent or ''))

def location(document,asset_id,item,metadata):
    for suffix,_,_,native,_,pointer in children(document):
        if item+suffix==asset_id:
            if native!=metadata:raise ValueError('PBIR_LEGACY_CHILD_CONTENT_DIFFERS')
            return pointer
    return None
