"""Scored names are referent evidence, never lineage or quantity equivalence."""
import json
import re
from pathlib import Path


def policy():
    value = json.loads((Path(__file__).resolve().parents[2] / 'acceptance/model_steps/intake-resolution-policy.json').read_text(encoding='utf8'))
    if (value['version'] != 'intake-name-scoring-v1' or not value['reason']
            or not 0 < value['threshold'] <= 1
            or not 0 < value['margin'] <= 1):
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
    query = set(tokens(quote))
    ranked = {}
    for candidate in candidates:
        best = (0.0, 'no_token_overlap', candidate['name'])
        for name, alias in [(candidate['name'], False), *[(n, True) for n in candidate.get('aliases', [])]]:
            words = set(tokens(name))
            if query and query == words:
                score, basis = (settings['alias_score'], 'declared_alias') if alias else (settings['exact_score'], 'normalized_exact')
            elif query and words and (query <= words or words <= query):
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
    close = [r for r in eligible if eligible[0]['score']-r['score'] <= settings['margin']]
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


def closed_value(quote, values):
    """A spelling repair needs an enumerated metadata domain, not a data read."""
    settings = policy()
    if not isinstance(values, list) or len(values) > settings['closed_value_maximum']:
        raise ValueError('A short closed value list is required for spelling repair')
    exact = [v for v in values if tokens(str(v)) == tokens(quote)]
    if len(exact) == 1:return exact[0]
    def distance(a, b):
        previous = list(range(len(b)+1))
        for i, x in enumerate(a, 1):
            current = [i]
            for j, y in enumerate(b, 1):current.append(min(current[-1]+1,previous[j]+1,previous[j-1]+(x!=y)))
            previous = current
        return previous[-1]
    close = [v for v in values if distance(quote.casefold(), str(v).casefold()) <= settings['closed_value_edit_distance']]
    if len(close) != 1:raise ValueError('Closed selection value is ambiguous or unresolved')
    return close[0]
