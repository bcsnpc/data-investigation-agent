"""Retained discussion and attachments, never automatic scope changes."""
import copy
from datetime import datetime,timezone
from .onboarding import fields,text

def append(workspace,request,*,actor='USER'):
    fields(request,['ticket_id','revision','request_key','text','attachment_id','review_id'])
    text(request['request_key'],100);text(request['text'],2000)
    if actor not in ('USER','AGENT'):raise ValueError('Unknown discussion actor')
    saved=workspace.smart_intake.tickets.get(request['ticket_id'])
    image=workspace.screenshots.image(request['attachment_id']) if request['attachment_id'] else None
    review=workspace.screenshots.saved('workspace_image_reviews',request['review_id']) if request['review_id'] else None
    if review and (not image or review['attachment']['id']!=image['id']):raise ValueError('Review does not belong to attached screenshot')
    from .onboarding import digest,Conflict
    key=request['request_key'];prior=saved['ticket'].get('comment_keys',{}).get(key)
    if prior:
        if prior!=digest(request):raise Conflict('Comment key reused with different content')
        return saved
    def retain(ticket):
        ticket.setdefault('comments',[]).append({'id':key,'actor':actor,'text':request['text'],
            'created':datetime.now(timezone.utc).isoformat(),'attachment':copy.deepcopy(image),'review':copy.deepcopy(review)})
        ticket.setdefault('comment_keys',{})[key]=digest(request)
        return ticket
    return workspace.smart_intake.tickets.update(request['ticket_id'],request['revision'],retain)

def progress(workspace,identity):
    saved=workspace.smart_intake.tickets.get(identity);ticket=saved['ticket']
    steps=[]
    if ticket.get('session_id'):
        # Read only retained events; a status view never dispatches a probe.
        with workspace.store.connect() as db:
            import json
            for row in db.execute('SELECT kind,detail,created FROM adaptive_events WHERE session_id=? ORDER BY id',(ticket['session_id'],)):
                detail=json.loads(row['detail']);kind=row['kind']
                if kind not in ('PROCESS_STAGE_STARTED','PROCESS_STAGE_FINISHED','PROCESS_STOPPED','PROCESS_FAILED','PROCESS_BUDGET_STOPPED'):continue
                operation=detail.get('operation','');stage=detail.get('stage','')
                label=('Checking the saved report context' if 'reproduc' in operation else
                       'Tracing the definition' if stage=='context' else
                       'Comparing the quantities' if 'probe' in operation or 'compar' in operation else
                       'Checking how the data was loaded' if 'ingestion' in operation or 'job' in operation else
                       'Explaining the difference' if 'judge' in operation else
                       'Checks finished' if kind=='PROCESS_STOPPED' else 'Investigation check')
                steps.append({'label':label,'status':'STARTED' if kind.endswith('STARTED') else 'FAILED' if 'FAILED' in kind else 'FINISHED','at':row['created']})
    return {'ticket_id':identity,'state':ticket['state'],'steps':steps}
