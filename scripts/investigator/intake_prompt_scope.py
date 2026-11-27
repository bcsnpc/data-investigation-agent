"""Small initial name index; full catalog lookup remains available on demand."""
from copy import deepcopy


def project(catalog,text):
    from .intake_candidates import explicit_names
    explicit=explicit_names(catalog,text)
    reports=([{'id':explicit['report']}]if explicit.get('report')else catalog.report_matches(text))
    selected={r['id']for r in reports[:3]}|set(explicit.values())
    for report in reports[:3]:
        pages=catalog.pages(report['id'])
        if explicit.get('page'):pages=[p for p in pages if p['id']==explicit['page']]
        for page in pages:
            selected.add(page['id'])
            visuals=catalog.visuals(report['id'],page['id'])
            if explicit.get('visual'):visuals=[v for v in visuals if v['id']==explicit['visual']]
            for visual in visuals:
                selected.add(visual['id']);selected.update(m['id']for m in visual.get('measures',[]))
    for kind in ('MEASURE','TABLE','PIPELINE','COPY_ACTIVITY','NOTEBOOK'):
        selected.update(r['id']for r in catalog.ranked(text,kind)[:3]if r['score']>=.86)
    selected.update(r['id']for r in catalog.sources())
    nodes=[{k:deepcopy(n[k])for k in ('id','kind','label','enrichment')if k in n}
           for n in catalog.nodes.values()if n['id']in selected]
    return {'candidate_names':nodes,'containment':[deepcopy(e)for e in catalog.edges if e['source']in selected and e['target']in selected],
        'report_index':catalog.reports(),'candidate_reports_exhaustive':len(reports)<=3,
        'lookup':'Use lookup_intake_catalog for full retained names/containment. Shortlists never prove uniqueness.'}
