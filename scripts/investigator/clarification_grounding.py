"""Only engine-rendered clarification prose may cross the user boundary.

A model selects a missing fact; it cannot author a factual premise or choices.
Catalog identities remain in the receipt, never in the displayed labels.
"""
import re
from .onboarding import Conflict
FIELDS=('REPORT','PAGE','VISUAL','FIGURE','COMPARISON','SELECTION','BUSINESS_INTENT')
QUESTIONS={'REPORT':'Which report are you asking about?', 'PAGE':'Which page are you asking about?',
 'VISUAL':'Which visual are you asking about?', 'FIGURE':'What figure does that visual show?',
 'COMPARISON':'What would you like that figure compared against?',
 'SELECTION':'What selections were active when you saw that figure?',
 'BUSINESS_INTENT':'Which business rule would you like the application owner to explain?'}

def label(names):
    values=[n for n in names if isinstance(n,str) and n.strip() and
        not re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|^[0-9a-f]{16,}|\w+://|^ReportSection[0-9a-f]+$',n,re.I)]
    if not values:raise Conflict('Clarification has no retained user-visible name')
    return ' / '.join(sorted(set(values)))

def render(field,catalog,fixed,report_id=None,page_id=None):
    if field not in FIELDS:raise Conflict('Unknown clarification field')
    if {'REPORT':'report_id','PAGE':'page_id','VISUAL':'target_id','COMPARISON':'comparison'}.get(field) in fixed and fixed.get({'REPORT':'report_id','PAGE':'page_id','VISUAL':'target_id','COMPARISON':'comparison'}[field]) is not None:
        raise Conflict('Clarification asks for an already picked fact')
    report_id=report_id or fixed.get('report_id');page_id=page_id or fixed.get('page_id')
    rows=[]
    if field=='REPORT':rows=[(r['id'],label([r['name']])) for m in catalog['models'] for r in m.get('reports',[])]
    if field in ('PAGE','VISUAL'):
        if report_id is None:raise Conflict('Page or visual clarification needs a declared report')
        pairs=[(m,r) for m in catalog['models'] for r in m.get('reports',[]) if r['id']==report_id]
        if len(pairs)!=1:raise Conflict('Clarification report is absent or ambiguous')
        model,report=pairs[0]
        visuals=[v for v in model.get('visuals',[]) if v['report_id']==report_id]
        if field=='PAGE':
            pages={}
            for v in visuals:pages.setdefault(v.get('page_id'),set()).update(v.get('page_names',[]))
            rows=[(i,label(n)) for i,n in pages.items() if i is not None]
        else:
            if page_id is None:raise Conflict('Visual clarification needs a declared page')
            rows=[(v['target_id'],label(v.get('names',[]))) for v in visuals if v.get('page_id')==page_id]
    if field in ('REPORT','PAGE','VISUAL') and not rows:raise Conflict('Clarification catalog choices unavailable')
    # Duplicate visible names cannot be repaired with an internal ID.
    if len({name for _,name in rows})!=len(rows):raise Conflict('Clarification names are not distinguishable; screenshot needed')
    return {'question':QUESTIONS[field],'choices':[name for _,name in rows],
            'grounding':{'field':field,'report_id':report_id,'page_id':page_id,
                         'choices':[{'identity':i,'name':name} for i,name in rows]}}
