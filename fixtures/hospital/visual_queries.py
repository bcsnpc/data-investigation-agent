"""Owner baseline queries compiled only from hospital report definitions."""
import json
from pathlib import Path


def identifier(value):return "'"+value.replace("'","''")+"'"
def column(table,name):return identifier(table)+'['+name.replace(']',']]')+']'
def measure(name):return '['+name.replace(']',']]')+']'


def report_queries(folder):
    folder=Path(folder)
    contexts=[('default',[])]
    for path in sorted((folder/'definition/bookmarks').glob('*.bookmark.json')):
        b=json.loads(path.read_text());filters=[]
        for f in b['explorationState']['filters']['byName'].values():
            ref=f['expression']['Column'];values=f['filter']['Where'][0]['Condition']['In']['Values']
            literal=values[0][0]['Literal']['Value']
            if not(literal.startswith("'")and literal.endswith("'")):raise ValueError('Only authored categorical bookmark literals')
            value=literal[1:-1].replace("''", "'")
            filters.append('TREATAS({'+json.dumps(value)+'},'+column(ref['Expression']['SourceRef']['Entity'],ref['Property'])+')')
        contexts.append((b['displayName'],filters))
    result=[]
    for path in sorted((folder/'definition/pages').glob('*/visuals/*/visual.json')):
        v=json.loads(path.read_text());visual=v['visual'];query=visual.get('query',{}).get('queryState',{})
        title=visual.get('visualContainerObjects',{}).get('title',[{}])[0].get('properties',{}).get('text',{}).get('expr',{}).get('Literal',{}).get('Value',v['name'])
        groups=[];values=[]
        for role in query.values():
            for p in role.get('projections',[]):
                field=p['field'];kind=next(iter(field));ref=field[kind]
                if kind=='Column':
                    c=column(ref['Expression']['SourceRef']['Entity'],ref['Property'])
                    if c not in groups:groups.append(c)
                elif kind=='Measure':values.extend([json.dumps(p['displayName']),measure(ref['Property'])])
                else:raise ValueError('Unsupported baseline field '+kind)
        for context,filters in contexts:
            record={'visual_id':v['name'],'page_id':path.parents[2].name,'title':title.strip("'"),'type':visual['visualType'],'context':context}
            if not query:record['query']=None;record['reason']='Static text, no data query'
            else:
                table='SUMMARIZECOLUMNS('+','.join(groups+filters+values)+')'
                order=''.join(','+g+',ASC' for g in groups)
                record['query']='EVALUATE VAR T = '+table+' RETURN ADDCOLUMNS(TOPN(100,T'+order+'),"__baseline_total_rows",COUNTROWS(T))'
                record['window_limit']=100
            result.append(record)
    return result
