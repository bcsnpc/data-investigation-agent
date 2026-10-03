"""Conservative provider schema preflight for the configured strict route.

Azure's documented subset excludes type-specific bounds/patterns; the local
consumer still validates them. The observed strict grammar also rejects quoted
enum literals. This check performs no HTTP call and does not claim live support.
"""
from jsonschema import Draft202012Validator

KEYS=frozenset(('type','properties','required','additionalProperties','items','enum','anyOf','description'))
TYPES=frozenset(('string','number','integer','boolean','object','array','null'))


def validate(schema):
    Draft202012Validator.check_schema(schema)
    if schema.get('type')!='object' or 'anyOf' in schema:
        raise ValueError('Provider schema root must be an object')
    count=[0]
    def walk(node,path,depth):
        if not isinstance(node,dict):raise ValueError('Provider schema node is not an object: '+path)
        unknown=set(node)-KEYS
        if unknown:raise ValueError('Provider schema unsupported keywords at '+path+': '+', '.join(sorted(unknown)))
        kinds=node.get('type',[]);kinds=[kinds] if isinstance(kinds,str) else kinds
        if any(k not in TYPES for k in kinds):raise ValueError('Provider schema unsupported type at '+path)
        if 'object' in kinds:
            props=node.get('properties',{});count[0]+=len(props)
            if depth>5 or count[0]>100:raise ValueError('Provider schema exceeds object size/depth at '+path)
            if node.get('additionalProperties') is not False or set(node.get('required',[]))!=set(props):
                raise ValueError('Provider schema must require every field and forbid extras at '+path)
            for key,value in props.items():walk(value,path+'.'+key,depth+1)
        if 'array' in kinds:walk(node['items'],path+'[]',depth+1)
        for branch in node.get('anyOf',[]):walk(branch,path+'.anyOf',depth)
        for literal in node.get('enum',[]):
            if isinstance(literal,str) and any(c in literal for c in ('"','\n','\r')):
                raise ValueError('Provider schema enum literal cannot contain a quote or line break at '+path)
    walk(schema,'root',1)
    return schema
