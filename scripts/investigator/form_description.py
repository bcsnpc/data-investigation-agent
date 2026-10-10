"""Selected form facts are description anchors, not fabricated text quotes."""
import re, copy
from jsonschema import Draft202012Validator
from . import form_intake
from .onboarding import digest


def anchor(request,models,extraction,candidate_binding=None):
    Draft202012Validator(form_intake.SCHEMA).validate(request)
    original_hash=digest(request)
    authority='FORM_SELECTION'
    if request['target_id'] is None and candidate_binding is not None:
        from .form_candidates import matching
        matched=matching(request,models,candidate_binding)
        if matched['status']!='BOUND':return None
        request=copy.deepcopy(request)
        request.update(target_id=matched['scope']['target_id'],cell_mode=matched['scope']['cell_mode'])
        # A named member of an equivalent matching set preserves that actual
        # referent; a representative is needed only when text names none.
        from .intake_extraction import active
        named=set()
        for hint in extraction['visuals']:
            if not active(hint,extraction):continue
            word=re.sub(r'\s+(?:card|matrix|chart)$','',hint['quote']['quote'],flags=re.I).strip() if hint['form'] in ('CARD','MATRIX','CHART') else hint['quote']['quote']
            for m in models:
                for v in m.get('visuals',[]):
                    if v['target_id'] in matched['equivalent_target_ids'] and any(' '.join(word.casefold().split())==' '.join(n.casefold().split()) for n in v.get('names',[])):named.add(v['target_id'])
        if len(named)==1:request['target_id']=next(iter(named))
        authority='CANDIDATE_VALUE_RECEIPTS'
    pairs=[(m,v) for m in models for v in m.get('visuals',[]) if v['target_id']==request['target_id']
           and v['report_id']==request['report_id'] and v.get('page_id')==request['page_id']]
    if len(pairs)!=1:return None
    model,visual=pairs[0]
    # An explicitly different named object remains description evidence.
    from .intake_extraction import active
    def normal(s):return ' '.join(s.casefold().split())
    for hint in extraction['visuals']:
        if not active(hint,extraction):continue
        form=hint.get('form','TITLE');word=hint['quote']['quote']
        if form in ('CARD','MATRIX','CHART') and visual.get('form')!=form:return None
        if form=='TOTAL' and request['cell_mode']!='TOTAL':return None
        if form=='UNGROUPED' and request['cell_mode'] not in (None,'UNGROUPED'):return None
        if form in ('CARD','MATRIX','CHART'):
            word=re.sub(r'\s+(?:card|matrix|chart)$','',word,flags=re.I).strip()
        hits=[v for v in model.get('visuals',[]) if any(normal(word)==normal(n) for n in v.get('names',[]))]
        if hits and visual['target_id'] not in {v['target_id'] for v in hits}:return None
    for hint in extraction['reports']:
        if not active(hint,extraction):continue
        hits=[r for m in models for r in m.get('reports',[]) if normal(hint['quote']['quote'])==normal(r['name'])]
        if hits and request['report_id'] not in {r['id'] for r in hits}:return None
    for hint in extraction['pages']:
        if not active(hint,extraction):continue
        hits={v['page_id'] for v in model.get('visuals',[]) if any(normal(hint['quote']['quote'])==normal(n) for n in v.get('page_names',[]))}
        if hits and request['page_id'] not in hits:return None
    return {'target_id':visual['target_id'],'report_id':visual['report_id'],'page_id':visual['page_id'],
            'mode':request['cell_mode'] or ('UNGROUPED' if not visual['grouping_columns'] else None),
            'figure_source':None,'request_hash':original_hash,'model_id':model['id'],'authority':authority}


def evidence(request,models,text,candidate_binding=None):
    selection={'request_hash':digest(request),'catalog_hash':digest(models),'document_hash':digest(text)}
    if candidate_binding is not None:selection['candidate_binding_hash']=digest(candidate_binding)
    return {'resolution_kind':'FORM_DESCRIPTION_VALUE_MATCH' if candidate_binding is not None else 'FORM_DESCRIPTION_SELECTION',
            'report_id':request['report_id'],'source':None,'selection':selection}


def validate_input(payload):
    from .form_scope import document
    request=payload['_form_description_input']
    doc=document(request,payload.get('_form_configuration'))
    part=next(p for p in doc['parts'] if p['pointer']=='/description')
    if payload['text']!=doc['text'][:part['end']]:
        raise ValueError('Form description authority belongs to different text')


def identifiers(extraction,ticket):
    from .intake_rules import RuleViolation
    for item in extraction['identifiers']:
        span=item['quote']
        for match in re.finditer(r'\b(?:invoked|activated|applied)\b(?:(?!\b(?:and|then|but)\b)[^;.!?\n])*',ticket,re.I):
            if re.search(r'\bbookmark\b',match.group(),re.I) and match.start()<=span['start'] and span['end']<=match.end():
                raise RuleViolation('PAGE_STATE_IS_NOT_IDENTIFIER',
                    'The quoted label belongs to an invoked bookmark, not a record identifier or number. Retain page-state context; do not put its label into identifiers.')


def transposed_measure(quote,candidates,visual,audit):
    """One adjacent letter swap within this picked visual's closed names.

    This is not target search or numeric matching. Two possible names refuse;
    a resolved ordinary name never reaches this fallback.
    """
    from .intake_name_resolution import tokens
    words=tokens(quote);hits=[]
    def one_swap(left,right):
        if len(left)!=len(right) or left==right:return False
        diff=[i for i,(a,b) in enumerate(zip(left,right)) if a!=b]
        return len(diff)==2 and diff[1]==diff[0]+1 and left[diff[0]]==right[diff[1]] and left[diff[1]]==right[diff[0]]
    for c in candidates:
        if c['id'] not in visual['measure_ids']:continue
        for name in (c['name'],*c.get('aliases',[])):
            declared=tokens(name)
            if len(words)==len(declared) and sum(a!=b for a,b in zip(words,declared))==1 and all(a==b or one_swap(a,b) for a,b in zip(words,declared)):
                hits.append((c,name));break
    if len(hits)!=1:return None
    candidate,name=hits[0]
    audit.append({'resolution':'FORM_PICKED_VISUAL_CLOSED_MEASURE_TRANSPOSITION',
        'quote':quote,'declared_name':name,'measure_id':candidate['id'],'target_id':visual['target_id']})
    return candidate
