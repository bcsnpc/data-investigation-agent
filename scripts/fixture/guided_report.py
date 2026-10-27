"""Small practice report over an existing model, for guided source cases."""
from copy import deepcopy
import json
from .definitions import definition


def application_report(template,*,workspace_name,model_name,model_id,logical_id,record_fields=()):
    selected=[]
    for part in template['parts']:
        path=part['path']
        if '/visuals/' in path and '/25189fcc5fe05539b3b6/' not in path:continue
        document=json.loads(part['content'])
        if path=='.platform':document['metadata']['displayName']='Application Load Support'
        elif path.endswith('/page.json'):
            document['displayName']='Application Movements';document.pop('filterConfig',None)
        elif path.endswith('/visual.json'):
            # This is fixture publication, not an investigative query writer.
            text=json.dumps(document).replace('Activity','Movements').replace('Handled Quantity','Movement Units')
            document=json.loads(text);document.pop('filterConfig',None)
        elif path=='definition/report.json':document.pop('filterConfig',None)
        selected.append({'path':path,'content':json.dumps(document)})
    page=next(p['path'].rsplit('/',1)[0] for p in selected if p['path'].endswith('/page.json'))
    projections=[{'field':{'Column':{'Expression':{'SourceRef':{'Entity':'Movements'}},'Property':field}},
                  'queryRef':'Movements.'+field,'nativeQueryRef':field} for field in
                 record_fields]
    if record_fields:selected.append({'path':page+'/visuals/round23records/visual.json','content':json.dumps({
        '$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.4.0/schema.json',
        'name':'round23records','position':{'x':24,'y':310,'width':1200,'height':420,'z':7,'tabOrder':7},
        'visual':{'visualType':'tableEx','query':{'queryState':{'Values':{'projections':projections}}},
            'visualContainerObjects':{'title':[{'properties':{'show':{'expr':{'Literal':{'Value':'true'}}},
                'text':{'expr':{'Literal':{'Value':"'Movement records'"}}}}}]}}})})
    return definition({'parts':selected},{'WORKSPACE_NAME':workspace_name,'MODEL_NAME':model_name,
        'ITEM_4':model_id,'REPORT_LOGICAL_ID':logical_id})
