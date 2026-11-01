"""Lossless JSON DAG and exact string slices for bounded independent grading."""
import json,collections,difflib

def sample_native_history(value, limit=3):
 """Label bounded grader samples; immutable captures retain the full history."""
 from copy import deepcopy
 from hashlib import sha256
 if type(limit)is not int or limit<1:raise ValueError('HISTORY_SAMPLE_BOUND')
 result=deepcopy(value)
 def visit(node):
  if isinstance(node,dict):
   for key,child in list(node.items()):
    if key in ('recent_runs','runs','audit_runs')and isinstance(child,list)and len(child)>limit:
     node[key+'_sample']=child[:limit]
     node[key+'_omitted_from_grader']=len(child)-limit
     node[key+'_original_sha256']=sha256(json.dumps(child,sort_keys=True,separators=(',',':')).encode()).hexdigest()
     del node[key]
    else:visit(child)
  elif isinstance(node,list):
   for child in node:visit(child)
 visit(result)
 return result
def encode(value,*,minimum_string=180,minimum_slice=100,string_references=False):
 if type(minimum_string)is not int or type(minimum_slice)is not int or minimum_string<40 or minimum_slice<20:raise ValueError('LOSSLESS_POOL_MINIMUMS')
 if type(string_references)is not bool:raise ValueError('LOSSLESS_POOL_REFERENCE_MODE')
 if string_references and 'pool_reference_prefix'in value.get('delivered',{}):raise ValueError('POOL_REFERENCE_METADATA_COLLISION')
 raw=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)
 counts=collections.Counter();atoms=set()
 def count(v):
  if isinstance(v,str):atoms.add(v)
  if isinstance(v,(dict,list,str))and len(raw(v))>20:counts[raw(v)]+=1
  if isinstance(v,dict):
   for x in v.values():count(x)
  elif isinstance(v,list):
   for x in v:count(x)
 count(value);pool=[];known={};strings=[];prefix='@'
 if string_references:
  while any(s.startswith(prefix)and s[len(prefix):].isascii()and s[len(prefix):].isdecimal()for s in atoms):prefix+='@'
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
   return prefix+str(known[key])if string_references else {'p':known[key]}
  return contents(v)
 def contents(v):
  if isinstance(v,dict):return {k:node(x)for k,x in v.items()}
  if isinstance(v,list):return [node(x)for x in v]
  return v
 result={k:node(v,root=True)for k,v in value.items()}
 result['delivered']['verbatim_pool']=pool
 result['delivered']['pool_encoding']='p indexes verbatim_pool; join concatenates literals and slice [pool-index,start,end] of prior strings (end exclusive).'
 if string_references:
  result['delivered']['pool_reference_prefix']=prefix
  result['delivered']['pool_encoding']='v2: strings prefix+decimal index reference verbatim_pool; join concatenates literals and slice [index,start,end) of prior strings.'
 assert decode(result)==value
 return result

def decode(result):
 pool=result['delivered']['verbatim_pool'];cache={}
 prefix=result['delivered'].get('pool_reference_prefix')if result['delivered'].get('pool_encoding','').startswith('v2:')else None
 def unpool(i):
  if i not in cache:
   x=pool[i]
   cache[i]=''.join(unpool(p['slice'][0])[p['slice'][1]:p['slice'][2]]if isinstance(p,dict)else p for p in x['join'])if isinstance(x,dict)and set(x)=={'join'}else restore(x)
  return cache[i]
 def restore(v):
  if prefix is not None and isinstance(v,str)and v.startswith(prefix)and v[len(prefix):].isascii()and v[len(prefix):].isdecimal():return unpool(int(v[len(prefix):]))
  if prefix is None and isinstance(v,dict)and set(v)=={'p'}:return unpool(v['p'])
  if isinstance(v,dict):return {k:restore(x)for k,x in v.items()}
  if isinstance(v,list):return [restore(x)for x in v]
  return v
 metadata={'verbatim_pool','pool_encoding'}|({'pool_reference_prefix'}if prefix is not None else set())
 check={**result,'delivered':{k:v for k,v in result['delivered'].items()if k not in metadata}}
 return restore(check)


def fit_task(value,*,maximum_characters=24000):
 """Additional lossless transport for an UNSENT oversized grading task only."""
 if type(maximum_characters)is not int or not 1<=maximum_characters<=24000:raise ValueError('GRADER_INPUT_BOUND')
 size=lambda v:len(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False))
 if size(value)<=maximum_characters:return value
 candidates=[encode(value,minimum_string=a,minimum_slice=b,string_references=True)for a,b in ((180,100),(80,40),(40,20))]
 chosen=min(candidates,key=size)
 if size(chosen)>maximum_characters:raise ValueError('EXACT_GRADER_PACKET_DOES_NOT_FIT')
 assert decode(chosen)==value
 return chosen
