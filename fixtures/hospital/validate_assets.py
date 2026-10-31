"""Offline structural checks; deliberately not a native rendering claim."""
import json
from pathlib import Path


def validate(root):
    root=Path(root)
    models={}
    for path in(root/'models').glob('*.SemanticModel/model.bim'):
        model=json.loads(path.read_text())
        models[path.parent.resolve()]={t['name']:{'columns':{c['name']for c in t['columns']},'measures':{m['name']for m in t.get('measures',[])}}for t in model['model']['tables']}
    count=0;bookmarks=0;drills=0
    for report in(root/'reports').glob('*.Report'):
        definition=json.loads((report/'definition.pbir').read_text())
        relative=definition['datasetReference'].get('byPath',{}).get('path')
        if not relative:raise ValueError('Offline bundle validation requires an explicit local model path')
        model_path=(report/relative).resolve()
        if model_path not in models:raise ValueError(('Missing bound model',report,model_path))
        tables=models[model_path]
        def walk(value):
            if isinstance(value,dict):
                for kind in('Column','Measure'):
                    if kind in value and isinstance(value[kind],dict):
                        item=value[kind];entity=item.get('Expression',{}).get('SourceRef',{}).get('Entity')
                        if entity:
                            column=item['Property'];field_type='columns'if kind=='Column'else'measures'
                            if entity not in tables or column not in tables[entity][field_type]:raise ValueError(('Unbound report field',report.name,kind,entity,column))
                for child in value.values():walk(child)
            elif isinstance(value,list):
                for child in value:walk(child)
        for path in(report/'definition').rglob('*.json'):
            value=json.loads(path.read_text());walk(value)
            if path.name=='visual.json':count+=1
            if path.name.endswith('.bookmark.json'):
                bookmarks+=1
                if not value['explorationState'].get('filters'):raise ValueError('Bookmark must carry actual filter state')
            if path.name=='page.json'and value.get('pageBinding',{}).get('type')=='Drillthrough':drills+=1
    if len(models)!=3 or bookmarks<2 or drills<1:raise ValueError(('Missing required assets',len(models),bookmarks,drills))
    return {'models':len(models),'visual_containers':count,'filtered_bookmarks':bookmarks,'drillthrough_pages':drills,'all_fields_bound':True,'native_rendering_verified':False}
