"""Lossless JSON DAG and exact string slices for bounded independent grading."""
import json,collections,difflib
def encode(value,*,minimum_string=180,minimum_slice=100):
 if type(minimum_string)is not int or type(minimum_slice)is not int or minimum_string<40 or minimum_slice<20:raise ValueError('LOSSLESS_POOL_MINIMUMS')
 raw=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)
 counts=collections.Counter()
 def count(v):
  if isinstance(v,(dict,list,str))and len(raw(v))>20:counts[raw(v)]+=1
  if isinstance(v,dict):
   for x in v.values():count(x)
  elif isinstance(v,list):
   for x in v:count(x)
 count(value);pool=[];known={};strings=[]
 def node(v,root=False):
  key=raw(v)
  if not root and (isinstance(v,str)and len(v)>minimum_string or isinstance(v,(dict,list,str))and counts[key]>1 and len(key)>20):
   if key not in known:
    index=len(pool);known[key]=index;pool.append(None)
    if isinstance(v,str):
     best=v
     for prior,text in strings:
      parts=[];position=0
      for m in difflib.SequenceMatcher(None,text,v,autojunk=False).get_matching_blocks():
       if m.size<minimum_slice:continue
       if m.b>position:parts.append(v[position:m.b])
       parts.append({'slice':[prior,m.a,m.a+m.size]});position=m.b+m.size
      if not parts:continue
      if position<len(v):parts.append(v[position:])
      candidate={'join':parts}
      if len(raw(candidate))<len(raw(best)):best=candidate
     strings.append((index,v));pool[index]=best
    else:pool[index]=contents(v)
   return {'p':known[key]}
  return contents(v)
 def contents(v):
  if isinstance(v,dict):return {k:node(x)for k,x in v.items()}
  if isinstance(v,list):return [node(x)for x in v]
  return v
 result={k:node(v,root=True)for k,v in value.items()}
 result['delivered']['verbatim_pool']=pool
 result['delivered']['pool_encoding']='p indexes verbatim_pool; join concatenates literals and slice [pool-index,start,end] of prior strings (end exclusive).'
 assert decode(result)==value
 return result

def decode(result):
 pool=result['delivered']['verbatim_pool'];cache={}
 def unpool(i):
  if i not in cache:
   x=pool[i]
   cache[i]=''.join(unpool(p['slice'][0])[p['slice'][1]:p['slice'][2]]if isinstance(p,dict)else p for p in x['join'])if isinstance(x,dict)and set(x)=={'join'}else restore(x)
  return cache[i]
 def restore(v):
  if isinstance(v,dict)and set(v)=={'p'}:return unpool(v['p'])
  if isinstance(v,dict):return {k:restore(x)for k,x in v.items()}
  if isinstance(v,list):return [restore(x)for x in v]
  return v
 check={**result,'delivered':{k:v for k,v in result['delivered'].items()if k not in ('verbatim_pool','pool_encoding')}}
 return restore(check)
