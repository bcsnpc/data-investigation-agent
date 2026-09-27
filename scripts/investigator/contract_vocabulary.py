"""Expose every schema enum from the exact validator schema, without a second list."""
import json


def enumerations(schema):
    found={}
    def walk(node,path):
        if isinstance(node,dict):
            if 'enum' in node:found[path]=node['enum']
            for key,value in node.items():
                if key!='enum':walk(value,path+'/'+key)
        elif isinstance(node,list):
            for index,value in enumerate(node):walk(value,path+'/'+str(index))
    walk(schema,'$')
    return found


def instructions(base,schema):
    return base+'\nExact allowed vocabularies, generated from this response schema. For each listed field choose only a listed value; never paraphrase an enum. Other prose fields are not enum fields:\n'+json.dumps(enumerations(schema),ensure_ascii=False,sort_keys=True)
