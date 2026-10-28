"""Explicit deployment migration of logical AI routes; no Azure role changes."""
from copy import deepcopy
from urllib.parse import urlsplit

COMPONENTS={'investigator':('reasoning',),'smoke':('reasoning',),'screenshot':('reasoning',),'enrichment':('enrichment',),'writer':('reasoning','enrichment'),'grader':('enrichment','reasoning')}


def migrate(policy):
    result=deepcopy(policy);identities=result['identities']
    reasoning=identities.get('reasoning',{})
    if reasoning.get('reasoning_models')!=['claude-opus-5-5']:raise ValueError('PINNED_OPUS_ROUTE_REQUIRED')
    # Historical model alias is used by structured screenshot/intake interfaces.
    identities['model']=deepcopy(reasoning)
    for entry in identities.values():
        entry['http']=[h for h in entry.get('http',[])if not (urlsplit(h['url']).hostname or '').endswith('.openai.azure.com')]
    return result


def audit(policy):
    identities=policy['identities'];rows=[]
    for component,routes in COMPONENTS.items():
      for identity in routes:
        entry=identities.get(identity,{})
        if identity=='reasoning':
            urls={(r['method'],r['url'],r.get('purpose'))for r in entry.get('http',[])}
            valid=entry.get('reasoning_models')==['claude-opus-5-5'] and all(('POST','https://api.anthropic.com/v1/'+path,'reasoning_model')in urls for path in ('messages','messages/count_tokens'))
            contract='Pinned client-side tools; POST messages/count_tokens only, existing Key Vault GET.'
        else:
            valid=entry.get('role')=='enrichment'and entry.get('enrichment_batches')=={'provider':'anthropic','purpose':'ENRICHMENT_ONLY','model':'claude-sonnet-4-6'}
            contract='Exact bounded batch factory; GET only batch IDs admitted by this session and their ended results.'
        rows.append({'component':component,'identity':identity,'admitted':valid,'contract':contract})
    return rows
