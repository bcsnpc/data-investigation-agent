"""Code-owned admission for explicit, graph-named operational questions."""
import copy,re
from .operational_run_selection import from_text

JOBS={'PIPELINE','COPY_ACTIVITY','NOTEBOOK'}
def admit(ticket,catalog):
    if not isinstance(ticket,dict)or not {'text'}<=set(ticket)<={'id','text','target'}or not isinstance(ticket['text'],str)or not 1<=len(ticket['text'])<=16000:
        return {'status':'HELD','reason':'RAW_TICKET_SHAPE','questions':[]}
    text=ticket['text']
    from .intake_rules import technical_ask
    if re.search(r'\b(?:business correctness|business rule decision|(?:decide|determine|check)[^.!?\n]*business rule|should (?:we |it )?(?:count|include|bill))\b',text,re.I)and not technical_ask(text):
        return {'status':'HELD','reason':'BUSINESS_INTENT_REQUIRES_OWNER','questions':[]}
    if re.search(r'\b(?:higher|lower|total|sum|versus|compared|discrepancy)\b|\bwhich[^.!?\n]*filter|\bfilter[^.!?\n]*hid(?:e|es|ing)',text,re.I):
        return {'status':'HELD','reason':'RAW_CALCULATION_ADMISSION_NOT_INSTALLED','questions':[]}
    candidates=catalog['candidates'];matches=[]
    for node in candidates:
        if node['kind']not in JOBS|{'MODEL'}or not node.get('label'):continue
        for found in re.finditer(r'(?<!\w)'+re.escape(node['label'])+r'(?!\w)',text,re.I):matches.append((node,found.start(),found.end()))
    matches=[row for row in matches if not any(other[1]<=row[1]and other[2]>=row[2]and(other[1],other[2])!=(row[1],row[2])for other in matches)]
    unique={m[0]['id']:m[0]for m in matches}
    operational=bool(re.search(r'\b(job|pipeline|run|refresh|notebook|copy)\b',text,re.I)and re.search(r'\b(fail(?:ed)?|succeed(?:ed)?|status|finish(?:ed)?|complete(?:d|tion)?|queued|running|terminat(?:ed|e))\b',text,re.I))
    if not operational:return {'status':'HELD','reason':'RAW_CALCULATION_ADMISSION_NOT_INSTALLED','questions':[]}
    if len(unique)!=1:
        choices=[{'key':n['id'],'label':n['label'],'kind':n['kind']}for n in sorted(unique.values()or candidates,key=lambda n:(n['label'],n['id']))if n['kind']in JOBS|{'MODEL'}]
        labels=[n['label']for n in choices]
        question='Which job or model do you want me to check?'
        if len(set(labels))!=len(labels):question='Please give the workspace name as well as the job or model name.';choices=[]
        return {'status':'CLARIFYING','reason':'OPERATIONAL_TARGET_UNRESOLVED','questions':[{'text':question,'choices':choices}]}
    node=next(iter(unique.values()))
    if node['kind']=='MODEL'and not re.search(r'\brefresh',text,re.I):return {'status':'HELD','reason':'MODEL_OPERATION_KIND_UNRESOLVED','questions':[]}
    request={'kind':'FACT','subject':node['id'],'question':'REFRESH_STATUS'if node['kind']=='MODEL'else'RUN_STATUS','source':{'start':0,'end':len(text),'quote':text}}
    try:selector=from_text(text)
    except ValueError as error:return {'status':'CLARIFYING','reason':str(error),'questions':[{'text':'Which run start time should I check, including the time zone?','choices':[]}]}
    if selector:request['run_selector']=selector
    return {'status':'READY','reason':'GRAPH_NAMED_OPERATIONAL_TARGET','ticket':{**copy.deepcopy(ticket),'request':request},'target':copy.deepcopy(node),'questions':[]}

def response(ticket,admission):
    questions=admission.get('questions',[])
    if questions:
        business=questions[0]['text'];choices=questions[0]['choices']
        if choices:business+=' Choices: '+', '.join(c['label']for c in choices)+'.'
    else:business="I couldn't resolve this request to a supported investigation target. No investigation value was evaluated."
    return {'ticket':copy.deepcopy(ticket),'status':admission['status'],'intake':copy.deepcopy(admission),'investigation_executed':False,'model_calls':0,'physical_requests':0,'outputs':{'business':business,'technical':business+' Admission: '+admission['reason']},'recording':{'mode':'NORMAL','byte_exact_replay':False}}
