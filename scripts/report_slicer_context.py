"""Native column-slicer requirements and explicit selections; no runtime evaluation."""
import hashlib
import json
from pathlib import Path
import re
from report_definition_evidence import bundle


def validate_selections(selections):
    if not isinstance(selections,dict) or len(selections)>20 or len(json.dumps(selections))>16000:
        raise ValueError('Bounded visual selection map required')
    for identity,selection in selections.items():
        if not isinstance(identity,str) or not identity or len(identity)>1000:raise ValueError('Invalid visual ID')
        if selection=={'mode':'all'}:continue
        if not isinstance(selection,dict) or set(selection)!={'mode','values'} or selection['mode']!='values':raise ValueError('Invalid selection mode')
        values=selection['values']
        if not isinstance(values,list) or not 1<=len(values)<=100 or any(not isinstance(v,str) or not v or len(v)>200 for v in values) or len(set(values))!=len(values):raise ValueError('Invalid categorical values')
    return json.loads(json.dumps(selections))


def assess(evidence,page_path,selections=None):
    unsigned={k:v for k,v in evidence.items() if k!='bundle_hash'}
    if hashlib.sha256(json.dumps(unsigned,sort_keys=True).encode()).hexdigest()!=evidence.get('bundle_hash'):
        raise ValueError('Definition bundle hash differs')
    if not re.fullmatch(r'definition/pages/[A-Za-z0-9_-]+/page.json',page_path):raise ValueError('Native page required')
    selections={} if selections is None else selections
    selections=validate_selections(selections)
    parts=evidence['report_definitions']
    if sum(p['name']==page_path for p in parts)!=1:raise ValueError('Page unavailable or ambiguous')
    assets={a['id']:a for a in evidence['model_assets']}
    columns={(assets[a['parent_id']]['name'],a['name']) for a in assets.values()
             if a['kind']=='SemanticColumn' and a['parent_id'] in assets and assets[a['parent_id']]['kind']=='SemanticTable'}
    prefix=page_path[:-len('page.json')]+'visuals/'
    requirements=[];unsupported=[];known=set()
    for part in parts:
        if not part['name'].startswith(prefix) or not part['name'].endswith('/visual.json'):continue
        visual=json.loads(part['metadata']['content']).get('visual',{})
        if visual.get('visualType')!='slicer':continue
        identity=part['id']
        if identity in known:raise ValueError('Duplicate slicer identity')
        known.add(identity)
        try:
            state=visual['query']['queryState']
            projections=state['Values']['projections']
            if set(state)!={'Values'} or len(projections)!=1:raise ValueError()
            field=projections[0]['field']
            if set(field)!={'Column'}:raise ValueError()
            column=field['Column'];expression=column['Expression'];source=expression['SourceRef']
            if set(column)!={'Expression','Property'} or set(expression)!={'SourceRef'} or set(source)!={'Entity'}:raise ValueError()
            table,name=source['Entity'],column['Property']
            if (table,name) not in columns:raise ValueError()
        except (KeyError,TypeError,ValueError):
            unsupported.append({'visual_id':identity,'reason':'Only one resolved native model column per slicer is supported'});continue
        selection=selections.get(identity)
        if selection is not None:
            if not isinstance(selection,dict):raise ValueError('Invalid slicer selection')
            if selection=={'mode':'all'}:pass
            elif set(selection)=={'mode','values'} and selection['mode']=='values':
                values=selection['values']
                if not isinstance(values,list) or not 1<=len(values)<=100 or any(not isinstance(v,str) or not v or len(v)>200 for v in values) or len(set(values))!=len(values):raise ValueError('Invalid categorical values')
            else:raise ValueError('Only explicit all or categorical string values are supported')
        elif identity in selections:raise ValueError('Null selection is not an explicit all-values choice')
        requirements.append({'visual_id':identity,'table':table,'column':name,
                             'selection':selection,'status':'CONTEXT_SUPPLIED' if selection is not None else 'NEEDS_INPUT',
                             'definition_hash':part['content_hash']})
    if set(selections)-known:raise ValueError('Selection references a slicer outside this page')
    if evidence['binding_status']!='RESOLVED_EXPLICIT_ID' or evidence['gaps']:
        unsupported.append({'reason':'Native report/model evidence incomplete'})
    status='UNSUPPORTED' if unsupported else 'NEEDS_INPUT' if any(r['status']=='NEEDS_INPUT' for r in requirements) else 'CONTEXT_SUPPLIED' if requirements else 'NO_SLICERS_CAPTURED'
    return {'status':status,'scan_id':evidence['scan_id'],'report_id':evidence['report']['id'],
            'page_path':page_path,'bundle_hash':evidence['bundle_hash'],'slicers':requirements,'unsupported':unsupported,
            'provided_selections':selections,'classification':'UNRESOLVED','root_cause_verified':False,
            'runtime_filter_verified':False,'automatic_defect_routing':False,
            'limitation':'Explicit operator context only; no value existence/type conversion, filter application or DAX evaluation. Other filters, custom slicers, bookmarks, relationships and RLS remain unverified. No captured slicers does not mean unfiltered runtime state.'}


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database',type=Path,required=True)
    parser.add_argument('--scan',required=True)
    parser.add_argument('--report',required=True)
    parser.add_argument('--page',required=True)
    parser.add_argument('--selections',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=assess(bundle(args.database,args.scan,args.report),args.page,json.loads(args.selections.read_text()) if args.selections else None)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8') as output:json.dump(result,output,indent=2)
    print(json.dumps({'status':result['status'],'slicers':len(result['slicers']),'unsupported':len(result['unsupported'])}))
