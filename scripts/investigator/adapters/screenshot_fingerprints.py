"""Retained native page definitions become neutral visible-text fingerprints."""
import json
from ..onboarding import digest

def catalog(workspace):
    from .report_cells import catalog as cells
    result=[]
    for entry in workspace.store.list(True):
        if not entry.get('enabled') or not entry.get('context'):continue
        model=entry
        members=workspace.model(entry['id'])
        visuals=cells(model,include_display_names=True)
        for report in model['context'].get('reports',[]):
            parts=report.get('report_definitions',[])
            for part in parts:
                path=part['name'].split('/')
                if len(path)!=4 or path[-1]!='page.json':continue
                page=json.loads(part['metadata']['content']);page_id=report['report']['id']+'/page/'+path[2]
                targets=[];anchors=[]
                for visual in visuals:
                    if visual['page_id']!=page_id:continue
                    labels=visual.get('display_names',[])
                    if not labels:
                        labels=[m['name'] for m in members.get('measures',[]) if m['id'] in visual['measure_ids']]
                    anchors.extend(labels)
                    targets.append(dict(visual,labels=labels))
                # Non-measure visuals (slicers/text boxes) contribute visible literal labels,
                # never hidden restrictions or data values.
                page_parts=[p for p in parts if p['name'].startswith('/'.join(path[:3])+'/')]
                def literals(value):
                    if isinstance(value,dict):
                        for key,item in value.items():
                            if key=='text' and isinstance(item,dict):
                                raw=item.get('expr',{}).get('Literal',{}).get('Value')
                                if isinstance(raw,str) and raw.startswith("'") and raw.endswith("'"):anchors.append(raw[1:-1].replace("''","'"))
                            elif key=='displayName' and isinstance(item,str):anchors.append(item)
                            else:literals(item)
                    elif isinstance(value,list):
                        for item in value:literals(item)
                for p in page_parts:
                    if p['name'].endswith('/visual.json'):literals(json.loads(p['metadata']['content']).get('visual',{}).get('visualContainerObjects',{}))
                names={'report':report['report']['name'],'page':page.get('displayName',path[2])}
                body={'model_id':entry['id'],'report_id':report['report']['id'],'page_id':page_id,
                      'label':names['report']+' / '+names['page'],'names':names,'anchors':sorted(set(anchors)),
                      'targets':targets,'definition_hash':digest([{'id':p['id'],'content':p['metadata']['content']} for p in page_parts])}
                body['candidate_id']=digest({'model':entry['id'],'page':page_id,'definition':body['definition_hash']})
                result.append(body)
    return result
