"""Small practice report over an existing model, for guided source cases."""
from copy import deepcopy
import json
from .definitions import definition


def application_report(template,*,workspace_name,model_name,model_id,logical_id):
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
    return definition({'parts':selected},{'WORKSPACE_NAME':workspace_name,'MODEL_NAME':model_name,
        'ITEM_4':model_id,'REPORT_LOGICAL_ID':logical_id})
