"""Check form names inside their selected native containment before asking."""
from copy import deepcopy
import re
import unicodedata


def check(request,catalog,*,probe=None):
    value=deepcopy(request);checks=[];queries=[]
    if not isinstance(value,dict):return value,checks,queries
    for field,kind in (('report','REPORT'),('page','PAGE'),('visual','VISUAL')):
        supplied=value.get(field)
        if not isinstance(supplied,str) or supplied in catalog.nodes:continue
        within=None
        if field=='page' and catalog.nodes.get(value.get('report'),{}).get('kind')=='REPORT':
            within={p['id'] for p in catalog.pages(value['report'])}
        if field=='visual':
            if catalog.nodes.get(value.get('report'),{}).get('kind')!='REPORT':continue
            pages=catalog.pages(value['report'])
            if value.get('page'):
                pages=[p for p in pages if p['id']==value['page']]
            within={v['id'] for p in pages for v in catalog.visuals(value['report'],p['id'])}
        normalize=lambda text:re.sub(r'[^\w]+','',unicodedata.normalize('NFKC',text).casefold())
        rows=[r for r in catalog.ranked(supplied,kind,within=within) if r['confidence'] in ('NAMED','NORMALIZED')
              and normalize(r.get('matched_name')or catalog.nodes[r['id']]['label'])==normalize(supplied)]
        checks.append({'field':field,'supplied':supplied,'basis':'NATIVE_NAME_AND_SELECTED_CONTAINMENT',
                       'candidates':[{'id':r['id'],'name':catalog.nodes[r['id']]['label']} for r in rows]})
        if len(rows)==1:
            value[field]=rows[0]['id']
        elif field=='visual' and 2<=len(rows)<=3 and probe and value.get('reported_figure'):
            from .investigation_read_tools import compare_figure
            observations=[]
            for row in rows:
                observation=probe(row['id'],deepcopy(value),queries)
                observations.append({'candidate':row['id'],**deepcopy(observation)})
            checks[-1]['native_value_checks']=observations
            successful=[r for r in observations if r.get('status')=='SUCCEEDED' and r.get('query_id') and 'value'in r]
            matches=[r for r in successful if compare_figure(value['reported_figure'],r['value'])['matches']]
            if len(successful)==len(rows) and len(matches)==1:value[field]=matches[0]['candidate']
    return value,checks,queries
