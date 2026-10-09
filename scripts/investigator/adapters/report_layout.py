"""Retained report geometry for UI preview, never quantity or scope authority."""
import json
import math
from ..onboarding import digest


def pages(model):
    result=[]
    for report in model.get('context',{}).get('reports',[]):
        retained=report.get('report_definitions',[])
        for part in retained:
            path=part['name'].split('/')
            if len(path)!=4 or path[-1]!='page.json':continue
            doc=json.loads(part['metadata']['content'])
            width,height=doc.get('width'),doc.get('height')
            if not all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) and v>0 for v in (width,height)):continue
            page={'id':report['report']['id']+'/page/'+path[2],
                  'report_id':report['report']['id'],'name':doc.get('displayName',path[2]),
                  'context_id':model.get('context_id',model['context'].get('id')),'context_hash':digest(model['context']),
                  'source':'RETAINED_DEFINITION_LAYOUT_NOT_LIVE_VALUES','visuals':[]}
            for visual in retained:
                location=visual['name'].split('/')
                if len(location)!=6 or location[2]!=path[2] or location[-1]!='visual.json':continue
                definition=json.loads(visual['metadata']['content']);position=definition.get('position',{})
                coordinates=[position.get(k) for k in ('x','y','width','height')]
                if not all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) for v in coordinates):continue
                x,y,w,h=coordinates
                if x<0 or y<0 or w<=0 or h<=0 or x+w>width or y+h>height:continue
                title=location[4]
                for row in definition.get('visual',{}).get('visualContainerObjects',{}).get('title',[]):
                    value=row.get('properties',{}).get('text',{}).get('expr',{}).get('Literal',{}).get('Value')
                    if isinstance(value,str) and value.startswith("'") and value.endswith("'"):
                        title=value[1:-1].replace("''", "'")
                page['visuals'].append({'target_id':visual['id'],'name':title,
                    'box':{'x':x/width,'y':y/height,'width':w/width,'height':h/height}})
            result.append(page)
    return result


def preview(workspace, request):
    from ..onboarding import fields
    fields(request,['report_link'])
    models=[];layouts={}
    for row in workspace.store.list(True):
        model=workspace.store.get(row['id'])
        if not model.get('enabled') or not model.get('context'):continue
        layout=pages(model);layouts[model['id']]=layout
        models.append({'id':model['id'],'reports':[r['report'] for r in model['context'].get('reports',[])],
                       'visuals':[{'report_id':p['report_id'],'page_id':p['id']} for p in layout]})
    from .report_link import bind
    reference=bind(request['report_link'],models)
    return {'pages':[p for p in layouts[reference['model_id']] if p['report_id']==reference['report_id']
                     and reference['page_id'] in (None,p['id'])],
            'qualification':'Retained definition layout; no live figures or current selections are shown.'}


def choices(workspace, ticket_id):
    from ..onboarding import digest
    saved=workspace.smart_intake.tickets.get(ticket_id);ticket=saved['ticket']
    targets={}
    for question in ticket['questions']:
        for choice in question['choices']:
            meaning=ticket['choice_values'].get(digest(question)+'/'+choice['id'],{})
            if meaning.get('target_id'):targets[choice['id']]=meaning['target_id']
    matches={}
    for row in workspace.store.list(True):
        model=workspace.store.get(row['id'])
        if not model.get('enabled') or not model.get('context'):continue
        for page in pages(model):
            for visual in page['visuals']:
                for choice,target in targets.items():
                    if visual['target_id']==target:matches.setdefault(choice,[]).append({'page':page,'visual':visual})
    # A preview cannot pick between duplicated retained bindings.
    return {'choices':{k:v[0] for k,v in matches.items() if len(v)==1},
            'qualification':'Retained definition layout; no live figures or current selections are shown.'}
