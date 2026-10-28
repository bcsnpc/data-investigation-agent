"""Database/validator feedback remains evidence of a failed query, never absence."""
from copy import deepcopy

def classify(message,*,validation=False):
    text=message.casefold()
    if any(s in text for s in ('unknown or ambiguous dax member','invalid column','invalid object','object unavailable','cannot be resolved','column could not')):return 'wrong column or table'
    if any(s in text for s in ('convert','conversion','cast','operand type','type mismatch')):return 'type or CONVERT/CAST'
    if any(s in text for s in ('system_time','temporal','date filter')):return 'date filter'
    if any(s in text for s in ('group by','aggregate','aggregation')):return 'grain/aggregation'
    if validation:return 'validator rejection'
    if any(s in text for s in ('syntax','parse error','incorrect syntax','currentschema')):return 'dialect'
    return 'endpoint error'

def schema_slice(layer,asset_ids=None):
    selected=set(asset_ids or[])
    return [{'id':o['id'],**{k:deepcopy(o['metadata'][k])for k in ('name','schema_name','type_desc','columns')if k in o.get('metadata',{})}}
        for o in layer['objects']if not selected or o['id'] in selected]
