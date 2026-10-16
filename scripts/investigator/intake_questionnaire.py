"""One consumer-owned questionnaire for web, chat and API.

Selections identify objects, not quantities observed on somebody else's screen.
The existing form controller interprets descriptions and preserves its scope
and provenance checks. Hidden legacy inputs remain available on their old port.
"""
import copy
from jsonschema import Draft202012Validator
from . import ticket_protocol as p, form_intake

VERSION='intake-questionnaire-v1'
ID=p.ID
OPTIONAL_TEXT={'anyOf':[{'type':'string','maxLength':2000},{'type':'null'}]}
COMPARISON={'oneOf':[
    p.obj({'kind':{'const':'OTHER_REPORT'},'report_id':ID,'page_id':ID}),
    p.obj({'kind':{'const':'OTHER_PAGE'},'page_id':ID}),
    p.obj({'kind':{'const':'APPLICATION'},'source_value':OPTIONAL_TEXT},optional=('source_value',)),
    p.obj({'kind':{'const':'NOTHING'}})]}
SCHEMA=p.obj({'version':{'const':VERSION},'request_key':{**ID,'maxLength':100},'subject':{'enum':['REPORT','MEASURE_TEXT']},'report_id':form_intake.NULL_ID,'page_id':form_intake.NULL_ID,
    'visual_id':{'anyOf':[ID,{'type':'null'}]},'comparing':COMPARISON,
    'description':{'type':'string','maxLength':2000},
    'screenshot_review_id':{'anyOf':[ID,{'type':'null'}]}},optional=('screenshot_review_id','subject'))
SCHEMA['allOf']=[{'if':{'required':['subject'],'properties':{'subject':{'const':'MEASURE_TEXT'}}},
    'then':{'properties':{**{k:{'type':'null'} for k in ('report_id','page_id','visual_id')},
        'description':{'type':'string','minLength':1,'maxLength':2000},
        'comparing':{'properties':{'kind':{'enum':['APPLICATION','NOTHING']}}}}},
    'else':{'properties':{'report_id':ID,'page_id':ID}}}]
DEFINITION={'version':VERSION,'schema':SCHEMA,'fields':[
    {'name':'report_id','label':'Report','kind':'select','optional':False,'list':'questionnaire/catalog'},
    {'name':'page_id','label':'Page / tab','kind':'select','optional':False,'list':'questionnaire/pages','depends_on':'report_id'},
    {'name':'visual_id','label':'Visual','kind':'select','optional':True,'list':'questionnaire/visuals','depends_on':'page_id'},
    {'name':'comparing','label':'Comparing with','kind':'comparison','optional':False,'choices':[
        {'value':'OTHER_REPORT','label':'Another report','reveals':['report_id','page_id']},
        {'value':'OTHER_PAGE','label':'Another page in the same report','reveals':['page_id']},
        {'value':'APPLICATION','label':'The source system / application','reveals':['source_value','screenshot']},
        {'value':'NOTHING','label':'Nothing specific — it looks wrong','reveals':[]}]},
    {'name':'description','label':'Description','kind':'text','optional':True,'maxLength':2000},
    {'name':'screenshot_review_id','label':'Screenshot','kind':'screenshot','optional':True}],
    'subject_choice':{'name':'subject','label':'Question about','default':'REPORT','choices':[
        {'value':'REPORT','label':'A report visual'}, {'value':'MEASURE_TEXT','label':'A measure, without a report visual'}]},
    'hidden_legacy_fields':['page-picture picker','value_seen','cell_mode','cell_keys','extra comparison choices'],
    'visual_list_source':'RETAINED_APPROVED_DEFINITION',
    'quantity_rule':'A picked visual identifies the measure and declared scope. Its current query value is not a user-reported figure. Figures come from exact description spans or reviewed screenshot evidence.'}

def validate(request,models):
    Draft202012Validator(SCHEMA).validate(request)
    if request.get('subject')=='MEASURE_TEXT':return copy.deepcopy(request)
    reports=[r for m in models for r in m.get('reports',[]) if r['id']==request['report_id']]
    if len(reports)!=1:raise ValueError('Selected report is absent or ambiguously bound')
    visuals=[v for m in models for v in m.get('visuals',[]) if v['report_id']==request['report_id']]
    if request['page_id'] not in {v['page_id'] for v in visuals}:raise ValueError('Selected page has no approved executable definition')
    if request['visual_id'] is not None and len([v for v in visuals if v['page_id']==request['page_id'] and v['target_id']==request['visual_id']])!=1:
        raise ValueError('Selected visual is outside the selected report/page')
    comparison=request['comparing'];kind=comparison['kind']
    if kind=='OTHER_REPORT':
        target_report=comparison['report_id']
        if target_report==request['report_id']:raise ValueError('Another report must be a different report')
        if len([r for m in models for r in m.get('reports',[]) if r['id']==target_report])!=1:raise ValueError('Comparison report is absent or ambiguously bound')
        if not any(v['report_id']==target_report and v['page_id']==comparison['page_id'] for m in models for v in m.get('visuals',[])):
            raise ValueError('Comparison page has no approved executable definition')
    if kind=='OTHER_PAGE' and (comparison['page_id']==request['page_id'] or comparison['page_id'] not in {v['page_id'] for v in visuals}):
        raise ValueError('Another page must be a different approved page in the selected report')
    return copy.deepcopy(request)

def to_form(request,models,*,review=None):
    validate(request,models)
    description=request['description']
    if request.get('screenshot_review_id'):
        if review is None or review['id']!=request['screenshot_review_id'] or review['provenance']!='USER_REVIEWED_SCREENSHOT_TRANSCRIPTION':
            raise ValueError('Screenshot needs a retained user-reviewed transcription')
        description+='\nReviewed screenshot: '+review['text']
        if len(description)>2000:raise ValueError('Description and reviewed screenshot exceed the shared intake bound')
    visuals=[v for m in models for v in m.get('visuals',[]) if v['target_id']==request['visual_id']]
    mode='UNGROUPED' if len(visuals)==1 and not visuals[0]['grouping_columns'] else None
    kind=request['comparing']['kind']
    return {'version':form_intake.VERSION,'request_key':request['request_key'],
        **({'subject':'MEASURE_TEXT'} if request.get('subject')=='MEASURE_TEXT' else {}),
        'report_id':request['report_id'],'page_id':request['page_id'],'target_id':request['visual_id'],
        'cell_mode':mode,'value_seen':None,'comparison':'APPLICATION' if kind=='APPLICATION' else (None if description.strip() else 'LOOKS_WRONG') if kind=='NOTHING' else form_intake.SUBJECT_ROUTE,
        'description':description,'cell_keys':[]}
