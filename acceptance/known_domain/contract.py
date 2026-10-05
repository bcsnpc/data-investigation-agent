"""Structured earned expectations; narrative wording is never an oracle."""
import copy
ANSWER_CATEGORIES=('ANSWERED','PARTLY_ANSWERED','NOT_ANSWERED','REPRODUCED','NOT_REPRODUCED','NO_REPORTED_FIGURE')


def account(state):
    outputs=(state.get('synthesis') or {}).get('outputs',{})
    value=outputs.get('technical_output',{}).get('question_account')
    if value is not None:return value
    from investigator.question_account import build
    return build(state)


def answer_category(state):
    from investigator.reproduction_composition import select
    a=account(state)
    if 'reproduction_answer' in a:
        lead=select(state.get('observations',[]))
        if lead is None:raise ValueError('Reproduction answer lacks its structured finding')
        return lead['label'] or 'NO_REPORTED_FIGURE'
    if a['status'] not in ANSWER_CATEGORIES:raise ValueError('Unknown question answer category')
    return a['status']


def project(state,cell_id=None):
    observations=state.get('observations',[]);envelope=state['envelope']
    resolutions={}
    for field in ('report_binding','definition_target','name_binding'):
        if (envelope.get(field) or {}).get('resolution_kind') is not None:
            resolutions[field]=envelope[field]['resolution_kind']
    for o in observations:
        if o.get('check_kind')=='REPORT_SELECTION_RESOLUTION':
            resolutions['selection']=o.get('resolution_kind') or (o.get('resolution') or {}).get('resolution_kind')
    boundaries=[];reached=[]
    for o in observations:
        if o.get('comparison_status')=='CROSS_SURFACE_VERIFIED':
            boundaries.append({k:o.get(k) for k in ('upper_layer','lower_layer','values_equal')})
            boundaries[-1]['grade']=(o.get('surface_difference') or {}).get('grade')
        if o.get('status')=='COMPLETED' and o.get('surface_report_binding')=='VALUE_QUERY':
            surface=o.get('execution_surface') or {}
            item={k:surface.get(k) for k in ('engine','connection','object')}
            if item not in reached:reached.append(item)
    reproduction=None
    if cell_id:
        found=[o for o in observations if o.get('check_kind')=='DECLARED_CONTEXT_REPRODUCTION' and o.get('cell',{}).get('id')==cell_id]
        if len(found)==1:
            o=found[0];figure=o.get('reported_figure') or {}
            reproduction={'cell_id':cell_id,'label':o.get('label'),'reproduced_value':o.get('reproduced_value'),
                'reported_state':figure.get('state'),'reported_value':figure.get('value')}
    return {'status':state['status'],'outcome':(state.get('assessment') or {}).get('classification'),
        'answer_category':answer_category(state),'resolutions':resolutions,'boundaries':boundaries,
        'layers_reached':reached,'reproduction':reproduction}


def compare(expected,actual):
    return [{'invariant':key,'expected':copy.deepcopy(value),'observed':copy.deepcopy(actual.get(key))}
            for key,value in expected.items() if actual.get(key)!=value]


def answer_matches(category,text):
    """Check the engine header's category, not equality of a whole sentence."""
    import re
    line=next((line.split(':',1)[1].strip() for line in text.splitlines() if line.startswith('Answer to your question: ')),None)
    if line is None:return False
    patterns={'ANSWERED':r'^Answered\b','PARTLY_ANSWERED':r'^Partly answered\b','NOT_ANSWERED':r'^Not answered\b',
        'REPRODUCED':r'^Yes\b','NOT_REPRODUCED':r'^No\b(?! verdict)', 'NO_REPORTED_FIGURE':r'^No verdict\b'}
    return bool(re.match(patterns[category],line))
