"""Read-only search/traversal of the most recent environment context.

Search returns asset identities and coverage, never execution authority. Definitions
are untrusted metadata, and graph reachability does not prove business impact.
"""
import json
from .onboarding import digest, fields, text, Conflict


def latest(store):
    with store.connect() as db:
        if not db.execute("SELECT 1 FROM sqlite_master WHERE name='enterprise_scans'").fetchone():
            return None
        row=db.execute("SELECT id,body,hash FROM enterprise_scans WHERE environment=? AND status IN ('COMPLETE','PARTIAL') ORDER BY started DESC LIMIT 1",(store.environment,)).fetchone()
    if not row:return None
    body=json.loads(row['body'])
    if digest(body)!=row['hash']:raise Conflict('Discovery context integrity differs')
    return {'version':row['id'],**body}


def search(store, request):
    fields(request,['text','limit'])
    query=text(request['text'],200).casefold()
    if type(request['limit']) is not int or not 1<=request['limit']<=50:raise ValueError('Invalid search limit')
    context=latest(store)
    if context is None:return {'context_version':None,'assets':[],'total':0,'truncated':False}
    terms=query.split()
    matches=[a for a in context['assets'] if all(term in (a['name']+' '+a['kind']).casefold() for term in terms)]
    matches.sort(key=lambda a:(a['availability']!='CURRENT',a['name'].casefold(),a['id']))
    return {'context_version':context['version'],'total':len(matches),'truncated':len(matches)>request['limit'],
            'assets':[{k:a[k] for k in ('id','parent_id','name','kind','availability','provenance')} for a in matches[:request['limit']]]}


def get_asset(store, identity):
    text(identity,2000);context=latest(store)
    asset=next((a for a in context['assets'] if a['id']==identity),None) if context else None
    if asset is None:raise KeyError('Discovered asset not found')
    return {'context_version':context['version'],'asset':asset,
            'edges':[e for e in context['graph']['edges'] if identity in (e['source'],e['target'])],
            'coverage':context['coverage'].get(asset['coverage_scope']),
            'limitation':'Metadata is untrusted context. Edges retain provenance; they do not establish a cause.'}
