"""Metadata-only family-group split; outcomes and previous responses are never inputs."""
import hashlib,itertools,json
from collections import Counter

SEED='round-ten-f-before-tuning-v1'
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def split(original,rebuilt):
 rows=[{'id':estate+':'+r['id'],'family':r.get('family'),'class':('family' if r.get('family') else r['id'].split('-',1)[0]),'record_hash':digest(r)} for estate,g in [('original',original),('rebuilt',rebuilt)] for r in g['cases']]
 counts=Counter(r['family'] for r in rows if r['family'])
 choices=[c for c in itertools.combinations(sorted(counts),4) if sum(counts[f] for f in c)==22]
 held_families=min(choices,key=lambda c:digest([SEED,list(c)]))
 held={r['id'] for r in rows if r['family'] in held_families}
 for cls,n in [('question',1),('refusal',3),('visual',2)]:
  eligible=sorted([r for r in rows if r['class']==cls],key=lambda r:digest([SEED,r['id']]))
  held.update(r['id'] for r in eligible[:n])
 return {'version':1,'seed':SEED,'reason':'Whole family groups including both estates; four held-out families plus stratified question/refusal/visual classes; no prior score or response used.',
  'dev':[r for r in rows if r['id'] not in held],'held_out':[r for r in rows if r['id'] in held]}
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('original');p.add_argument('rebuilt');p.add_argument('output');a=p.parse_args()
 value=split(json.loads(open(a.original,encoding='utf8').read()),json.loads(open(a.rebuilt,encoding='utf8').read()))
 target=__import__('pathlib').Path(a.output)
 if target.exists():raise RuntimeError('Split already sealed')
 target.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8')
 target.with_suffix('.sha256').write_text(hashlib.sha256(target.read_bytes()).hexdigest()+'\n')
 print('SEALED',len(value['dev']),len(value['held_out']),target.with_suffix('.sha256').read_text().strip())
