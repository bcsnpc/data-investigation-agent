"""Plan only: preserve existing Blob lifecycle rules and scope screenshot expiry."""
import argparse
import copy
import hashlib
import json
from pathlib import Path


def plan(current, estates):
    if not isinstance(current,dict)or set(current)!={'rules'}or not isinstance(current['rules'],list):
        raise ValueError('LIFECYCLE_POLICY_SHAPE')
    if not isinstance(estates,dict)or not estates:raise ValueError('SCREENSHOT_ESTATES_REQUIRED')
    result=copy.deepcopy(current);replacements={}
    for estate,days in estates.items():
        if not isinstance(estate,str)or not 1<=len(estate)<=100 or type(days)is not int or not 1<=days<=36500:
            raise ValueError('SCREENSHOT_RETENTION_DECLARATION')
        key=hashlib.sha256(estate.encode()).hexdigest();name='dia-screenshot-'+key
        prefix='screenshots/images/'+key+'/'
        replacements[name]={'enabled':True,'name':name,'type':'Lifecycle','definition':{
            'filters':{'blobTypes':['blockBlob'],'prefixMatch':[prefix]},
            'actions':{'baseBlob':{'delete':{'daysAfterCreationGreaterThan':days}}}}}
    seen=set()
    for rule in result['rules']:
        if not isinstance(rule,dict)or not isinstance(rule.get('name'),str)or rule['name']in seen:
            raise ValueError('LIFECYCLE_RULE_IDENTITY')
        seen.add(rule['name'])
        if rule['name']in replacements:
            expected=replacements[rule['name']]['definition']['filters']
            if rule.get('type')!='Lifecycle'or rule.get('definition',{}).get('filters')!=expected:
                raise ValueError('LIFECYCLE_RULE_NAME_COLLISION')
        elif rule.get('enabled')is True and rule.get('definition',{}).get('actions',{}).get('baseBlob',{}).get('delete'):
            prefixes=rule.get('definition',{}).get('filters',{}).get('prefixMatch')or['']
            for new in replacements.values():
                desired=new['definition']['filters']['prefixMatch'][0]
                if any(desired.startswith(p)or p.startswith(desired)for p in prefixes):
                    raise ValueError('EXISTING_DELETE_POLICY_OVERLAPS_SCREENSHOT_RETENTION')
    result['rules']=[replacements.pop(r['name'],r)for r in result['rules']]
    result['rules'].extend(replacements[k]for k in sorted(replacements))
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--current-policy',type=Path,required=True)
    p.add_argument('--estates',type=Path,required=True,help='JSON object mapping exact environment names to retention days')
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();result=plan(json.loads(a.current_policy.read_bytes()),json.loads(a.estates.read_bytes()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x',encoding='utf8')as f:json.dump(result,f,indent=2)
    print(json.dumps({'status':'PLAN_ONLY','rules':len(result['rules']),'output':str(a.output)}))


if __name__=='__main__':main()
