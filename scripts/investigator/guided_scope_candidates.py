"""Native candidate addresses; a model shortlist never excludes another fit."""
from copy import deepcopy
import re


def inventory(text,mapped,catalog):
    proposal=mapped.get('prefilled')or{}
    figure=proposal.get('reported_figure')or{}
    if proposal.get('table')or figure.get('state')!='NUMBER'or figure.get('precision')!='EXACT':return {}
    question_fields={f.get('field')for f in mapped.get('question',{}).get('fields',[])}
    visual_words=bool(re.search(r'\b(?:card|visual|chart|matrix)\b',text,re.I))
    if not (question_fields&{'page','visual'} or visual_words):return {}
    reports=catalog.report_matches(text)
    if not reports and proposal.get('report')in catalog.nodes:
        reports=[{'id':proposal['report']}]
    named=(proposal.get('details')or{}).get('measure')or proposal.get('measure')
    metrics={r['id']for r in catalog.measure_matches(text)}
    if named in catalog.nodes:metrics&={named}
    elif named:metrics={i for i in metrics if catalog.nodes[i]['label'].casefold()==str(named).casefold()}
    if not metrics:return {}
    page_rows=[];visual_rows=[]
    for report in reports:
        pages=catalog.named_pages(text,report['id'])or catalog.pages(report['id'])
        if 'page'in question_fields:
            page_rows.extend(pages)
        for page in pages:
            visual_rows.extend(v for v in catalog.visuals(report['id'],page['id'])
                               if any(m['id']in metrics for m in v.get('measures',[])))
    # A full native title is stronger than a shorter title embedded in it.
    explicit=[v for v in visual_rows if v['name'] and re.search(r'(?<!\w)'+re.escape(v['name'])+r'(?!\w)',text,re.I)]
    if explicit:
        width=max(len(v['name'])for v in explicit);visual_rows=[v for v in explicit if len(v['name'])==width]
    rows=page_rows if 'page'in question_fields and not explicit else visual_rows
    return {r['id']:deepcopy(catalog.nodes[r['id']])for r in rows}


def address(proposal,catalog,target):
    """Fallback neutral address; executable ports add the unique native cell."""
    node=catalog.nodes[target];kind=node['kind']
    reports=catalog.reports_for(target)
    if kind=='REPORT':reports=[{'id':target}]
    if len(reports)!=1:raise ValueError('CANDIDATE_REPORT_PARENT_NOT_UNIQUE')
    report=reports[0]['id'];result={k:deepcopy(v)for k,v in proposal.items()if k not in ('report','page','visual','table','measure')}
    result['report']=report
    if kind=='PAGE':result['page']=target
    if kind=='VISUAL':
        pages=[p for p in catalog.pages(report)if any(v['id']==target for v in catalog.visuals(report,p['id']))]
        if len(pages)!=1:raise ValueError('CANDIDATE_PAGE_PARENT_NOT_UNIQUE')
        result.update(page=pages[0]['id'],visual=target)
    return result


def label(catalog,target):
    node=catalog.nodes[target];parts=[node['label']]
    if re.fullmatch(r'[a-fA-F0-9-]{12,}',parts[0]):parts[0]='Visual (catalog title unavailable)'
    if node['kind']=='VISUAL':
        parents=[p for r in catalog.reports_for(target)for p in catalog.pages(r['id'])
                 if any(v['id']==target for v in catalog.visuals(r['id'],p['id']))]
        if len(parents)==1:parts.append('on '+parents[0]['name'])
    reports=catalog.reports_for(target)
    if node['kind']in ('PAGE','VISUAL')and len(reports)==1:parts.append('in '+reports[0]['name'])
    return ' '.join(parts)
