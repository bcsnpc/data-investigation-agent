"""Scored names are referent evidence, never lineage or quantity equivalence."""
import json
import math
import re
from pathlib import Path


def policy():
    value = json.loads((Path(__file__).resolve().parents[2] / 'acceptance/model_steps/intake-resolution-policy.json').read_text(encoding='utf8'))
    expected={'version','reason','threshold','margin','alias_score','exact_score','containment_score',
              'closed_value_maximum','closed_value_edit_distance'}
    numeric=('threshold','margin','alias_score','exact_score','containment_score')
    if (not isinstance(value,dict) or set(value)!=expected
            or value['version'] != 'intake-name-scoring-v1'
            or not isinstance(value['reason'],str) or not value['reason'].strip()
            or any(type(value[k]) not in (int,float) or not math.isfinite(value[k]) for k in numeric)
            or not 0 < value['threshold'] <= 1 or not 0 < value['margin'] <= 1
            or not value['alias_score']>value['exact_score']>=value['containment_score']>0
            or type(value['closed_value_maximum']) is not int or value['closed_value_maximum']<1
            or type(value['closed_value_edit_distance']) is not int or not 0<=value['closed_value_edit_distance']<=1):
        raise ValueError('Invalid intake name-scoring configuration')
    return value


def tokens(value):
    value = re.sub(r'([a-z])([A-Z])', r'\1 \2', value)
    words = re.findall(r'[^\W_]+', value.casefold())
    return tuple(w[:-3]+'y' if w.endswith('ies') and len(w)>4 else
                 w[:-1] if w.endswith('s') and not w.endswith(('ss','us')) and len(w)>3 else w
                 for w in words)


def rank(quote, candidates, id_field, settings=None):
    settings = settings or policy()
    query_tokens=tokens(quote)
    query = set(query_tokens)
    ranked = {}
    for candidate in candidates:
        best = (0.0, 'no_token_overlap', candidate['name'])
        for name, alias in [(candidate['name'], False), *[(n, True) for n in candidate.get('aliases', [])]]:
            name_tokens=tokens(name)
            words = set(name_tokens)
            if query and query_tokens == name_tokens:
                score, basis = (settings['alias_score'], 'declared_alias') if alias else (settings['exact_score'], 'normalized_exact')
            elif query and words and query < words:
                score, basis = settings['containment_score'], 'token_containment'
            else:
                score = 2*len(query & words)/(len(query)+len(words)) if query or words else 0
                basis = 'token_overlap'
            if score > best[0]: best = (score, basis, name)
        row = {'id': candidate[id_field], 'score': round(best[0], 6), 'basis': best[1], 'matched_name': best[2]}
        if row['score'] > ranked.get(row['id'], {'score': -1})['score']:
            ranked[row['id']] = row
    return sorted(ranked.values(), key=lambda r: (-r['score'], r['id']))


def resolve(quote, candidates, id_field, audit=None):
    settings = policy()
    ranked = rank(quote, candidates, id_field, settings)
    eligible = [r for r in ranked if r['score'] >= settings['threshold']]
    # A runner-up just below threshold still defeats the required lead.
    close = [r for r in ranked if eligible and eligible[0]['score']-r['score'] <= settings['margin']]
    state = 'UNRESOLVED' if not eligible else 'AMBIGUOUS' if len(close)>1 else 'RESOLVED'
    evidence = {'quote': quote, 'resolution': state, 'threshold': settings['threshold'],
                'margin': settings['margin'], 'best': ranked[0] if ranked else None,
                'runner_up': ranked[1] if len(ranked)>1 else None}
    if audit is not None: audit.append(evidence)
    if state != 'RESOLVED':
        error = ValueError(('Ambiguous' if state == 'AMBIGUOUS' else 'Unresolved')+' declared name: '+quote)
        error.resolution_evidence = evidence
        error.candidates = close if close else ranked
        raise error
    return next(c for c in candidates if c[id_field] == eligible[0]['id'])


def closed_value(quote, values, audit=None):
    """A spelling repair needs an enumerated metadata domain, not a data read."""
    settings = policy()
    if not isinstance(values, list) or len(values) > settings['closed_value_maximum']:
        raise ValueError('A short closed value list is required for spelling repair')
    if any(type(v) not in (str,bool) for v in values):
        raise ValueError('Spelling repair requires declared text or boolean values')
    exact = [v for v in values if tokens(str(v)) == tokens(quote)]
    if len(exact) == 1:
        if audit is not None:audit.append({'quote':quote,'resolution':'RESOLVED','basis':'closed_value_normalized_exact',
            'resolved_value':exact[0],'score':1.0,'edit_distance':0,'maximum_edit_distance':settings['closed_value_edit_distance']})
        return exact[0]
    def distance(a, b):
        previous = list(range(len(b)+1))
        for i, x in enumerate(a, 1):
            current = [i]
            for j, y in enumerate(b, 1):current.append(min(current[-1]+1,previous[j]+1,previous[j-1]+(x!=y)))
            previous = current
        return previous[-1]
    close = [v for v in values if distance(quote.casefold(), str(v).casefold()) <= settings['closed_value_edit_distance']]
    if len(close) != 1:raise ValueError('Closed selection value is ambiguous or unresolved')
    if audit is not None:
        d=distance(quote.casefold(),str(close[0]).casefold())
        audit.append({'quote':quote,'resolution':'RESOLVED','basis':'unique_closed_value_spelling_repair',
            'resolved_value':close[0],'score':1-d/max(len(quote),len(str(close[0]))),'edit_distance':d,
            'maximum_edit_distance':settings['closed_value_edit_distance']})
    return close[0]


def page_candidates(models,extraction,ticket,candidates,report_words,confirmation,reference,form_anchor,audit):
    """Restrict lookup to a user-declared page. Never use quantity evidence."""
    from .intake_extraction import active,declared_pages
    from .intake_span_references import enabled
    if not enabled():return candidates,[]
    anchor=form_anchor or confirmation or reference
    visuals=[]
    if anchor and anchor.get('page_id') is not None:
        visuals=[v for m in models for v in m.get('visuals',[])
                 if v['report_id']==anchor['report_id'] and v.get('page_id')==anchor['page_id']]
    elif report_words:
        reports=[r for m in models for r in m.get('reports',[])]
        ids={resolve(q,reports,'id')['id'] for q in report_words
             if not any(tokens(q)==tokens(m['name']) for m in models)}
        if len(ids)==1:
            pool=[v for m in models for v in m.get('visuals',[]) if v['report_id'] in ids]
            page_ids=set()
            for model in models:
                for hint in declared_pages(extraction,ticket,model):
                    if active(hint,extraction):
                        pages=[{'id':v['page_id'],'name':n} for v in pool for n in v.get('page_names',[])]
                        if pages:page_ids.add(resolve(hint['quote']['quote'],pages,'id',audit)['id'])
            if len(page_ids)==1:visuals=[v for v in pool if v.get('page_id') in page_ids]
    if not visuals:return candidates,[]
    allowed={mid for v in visuals for mid in v['measure_ids']}
    bindings={(m['id'],mid) for m in models for v in m.get('visuals',[]) if v in visuals for mid in v['measure_ids']}
    scoped=[c for c in candidates if tuple(json.loads(c['resolution_id'])) in bindings]
    audit.append({'resolution':'SELECTED_PAGE_CLOSED_MEASURE_LOOKUP','page_ids':sorted({v['page_id'] for v in visuals}),
                  'target_ids':sorted(v['target_id'] for v in visuals),'measure_ids':sorted(allowed)})
    return scoped,visuals

def page_measure(quote,candidates,visuals,audit):
    """A loose word may identify a retained visual/field on the selected page.

    Morphology is spelling evidence within that closed page, not an alias or
    a selected filter. Every matching measure is retained; rivals refuse.
    """
    def stem(word):
        for suffix in ('ing','ion','ed'):
            if word.endswith(suffix) and len(word)-len(suffix)>=5:return word[:-len(suffix)]
        return word
    query={stem(w) for w in tokens(quote)}
    hits={}
    for c in candidates:
        names=[c['name'],*c.get('aliases',[])]
        names.extend(n for v in visuals if c['id'] in v['measure_ids'] for n in v.get('names',[]))
        matched=[n for n in names if query and query<={stem(w) for w in tokens(n)}]
        if matched:hits[c['resolution_id']]=(c,matched)
    if len(hits)>1:
        exc=ValueError('Ambiguous selected-page field or visual name: '+quote)
        exc.resolution_evidence={'resolution':'AMBIGUOUS','quote':quote};exc.candidates=[c for c,_ in hits.values()]
        raise exc
    if not hits:return None
    c,matched=next(iter(hits.values()))
    audit.append({'resolution':'SELECTED_PAGE_VISUAL_FIELD_NAME','quote':quote,'measure_id':c['id'],
                  'declared_names':sorted(set(matched)),'target_ids':sorted(v['target_id'] for v in visuals if c['id'] in v['measure_ids'])})
    return c
