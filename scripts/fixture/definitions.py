"""Bind retained fixture templates to returned IDs; not investigation reasoning."""
import base64,copy,json,re
from uuid import UUID
SLOT=re.compile(r'\$\{([A-Z_0-9]+)\}')

def bind(value, slots, replacements=None):
    replacements=replacements or {}
    def visit(node):
        if isinstance(node,dict):return {k:visit(v) for k,v in node.items()}
        if isinstance(node,list):return [visit(v) for v in node]
        if not isinstance(node,str):return copy.deepcopy(node)
        def substitute(match):
            key=match.group(1)
            if key not in slots:raise ValueError('Unbound fixture slot '+key)
            result=slots[key]
            if not isinstance(result,str) or not result or any(c in result for c in ('"','\\','\n','\r')):
                raise ValueError('Unsafe fixture slot '+key)
            return result
        result=SLOT.sub(substitute,node)
        for before,after in replacements.items():result=result.replace(before,after)
        return result
    result=visit(value)
    if SLOT.search(json.dumps(result)):raise ValueError('Unbound fixture slot in result')
    return result

def definition(template,slots,replacements=None):
    parts=[]
    for part in template['parts']:
        text=bind(part['content'],slots,replacements)
        if part['path'].endswith(('.json','.bim','.pbism','.pbir','.platform')):json.loads(text)
        parts.append({'path':part['path'],'payloadType':'InlineBase64','payload':base64.b64encode(text.encode()).decode()})
    return {'parts':parts}


def model_slots(lakehouse,logical_id,slot):
    """The retained Sql.Database template names the SQL endpoint, not its lakehouse."""
    if slot not in ('ITEM_2','ITEM_3'):raise ValueError('Unknown model database slot')
    endpoint=lakehouse['properties']['sqlEndpointProperties']
    if endpoint['provisioningStatus']!='Success':raise ValueError('Model source endpoint is not provisioned')
    database=str(UUID(endpoint['id']));item=str(UUID(lakehouse['id']))
    if database==item:raise ValueError('Model source endpoint was confused with the lakehouse')
    return {'ITEM_1':str(UUID(logical_id)),slot:database,'WAREHOUSE_ENDPOINT':endpoint['connectionString']}
