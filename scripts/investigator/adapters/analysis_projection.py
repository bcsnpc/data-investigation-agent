"""Analysis-only native representation projection; original query records stay exact."""
from copy import deepcopy
import re

NUMERIC=re.compile(r'^(?:u?int(?:8|16|32|64)|float(?:16|32|64)|double|single|decimal(?:128|256)?(?:\(\d+,\s*\d+\))?)$',re.I)
def project(record,layer,fields):
 if record.get('status')!='SUCCEEDED':return record,{}
 rows=record.get('result',{}).get('rows',[])
 if len(rows)>250 or any(not isinstance(r,dict)for r in rows):raise ValueError('ANALYSIS_ROW_BOUND_OR_SHAPE')
 headers={k for row in rows for k in row};bindings={}
 objects=[o for o in (layer.get('objects')or[])if isinstance(o,dict)]
 byid={o['id']:o for o in objects if o.get('id')};assets=set(record.get('asset_ids',[]))
 def metadata(obj):
  value=obj.get('metadata');return value if isinstance(value,dict)else{}
 for field in dict.fromkeys(fields):
  candidates={field}if field in headers else set()
  if layer.get('dialect')=='DAX':
   alias='['+field+']'
   if alias in headers:candidates.add(alias)
   for obj in objects:
    parent=byid.get(obj.get('parent_id'),{})
    if obj.get('kind')=='SemanticColumn'and (obj.get('name')or metadata(obj).get('name'))==field and (obj.get('id')in assets or obj.get('parent_id')in assets):
     name=parent.get('name')or metadata(parent).get('name')
     if name and name+'['+field+']'in headers:candidates.add(name+'['+field+']')
    if obj.get('kind')=='SemanticTable'and obj.get('id')in assets:
     cols=metadata(obj).get('columns')or[]
     if any(isinstance(c,dict)and c.get('name')==field for c in cols):
      name=obj.get('name')or metadata(obj).get('name')
      if name and name+'['+field+']'in headers:candidates.add(name+'['+field+']')
  if len(candidates)>1:raise ValueError('ANALYSIS_AMBIGUOUS_OUTPUT_COLUMN:'+field)
  if candidates:bindings[field]=next(iter(candidates))
 if len(set(bindings.values()))!=len(bindings):raise ValueError('ANALYSIS_AMBIGUOUS_OUTPUT_BINDING')
 view=deepcopy(record);types={};native_types=record.get('result',{}).get('column_types')
 if not isinstance(native_types,dict):native_types={}
 for field,header in bindings.items():
  typ=native_types.get(header)
  if isinstance(typ,str)and typ.casefold()not in('unknown','variant','object','any','null'):
   types[field]=('integer'if re.fullmatch(r'u?int(?:8|16|32|64)',typ,re.I)else'number')if NUMERIC.fullmatch(typ)else'boolean'if typ.casefold()in('bool','boolean')else'literal'
 for row in view['result']['rows']:
  original=deepcopy(row)
  for field,header in bindings.items():
   if header in original and field!=header:row.pop(header,None);row[field]=original[header]
 view['analysis_scalar_types']=types
 return view,bindings
