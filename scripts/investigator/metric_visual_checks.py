"""Read candidate visuals before choosing a metric's checked representative."""
import copy,json,itertools
from types import SimpleNamespace
from .onboarding import digest,encoded,Conflict


def record(store,body,plan,checks):
    claim=body['claim'];binding=claim['selected_binding']
    if binding.get('kind')=='MULTIPLE':raise Conflict('METRIC_MULTI_BRANCH_WALK_UNAVAILABLE')
    candidates=plan['candidates']
    required={c['target_id']for c in candidates}
    if not required or set(checks['coverage']['checked_visual_ids'])!=required:
        raise Conflict('METRIC_CANDIDATE_COVERAGE_INCOMPLETE')
    if any(c['outcome']!='OBSERVED_AGREEMENT'for c in checks['comparisons']):
        raise Conflict('METRIC_CONTEXT_NOT_COMPARABLE')
    if len({c['comparison_scope_hash']for c in candidates})!=1:
        raise Conflict('METRIC_CONTEXT_NOT_COMPARABLE')
    chosen=min(candidates,key=lambda c:c['target_id'])
    if chosen['declaration']['restrictions']!=[]:
        raise Conflict('METRIC_FILTERED_LOWER_COMPARISON_UNSUPPORTED')
    value={'version':'metric-checked-representative-v1','claim_id':body['id'],
        'revision':body['revision'],'claim_hash':digest(claim),'confirmation_hash':digest(body['confirmation']),
        'catalog_hash':body['catalog_hash'],'measure_id':binding['measure_id'],
        'target_id':chosen['target_id'],'model_id':chosen['model_id'],
        'candidate_ids':sorted(required),'selection_basis':'CHECKED_SAME_CONTEXT_AGREEMENT'if len(required)>1 else'CHECKED_UNIQUE_METRIC_VISUAL',
        'plan':copy.deepcopy(plan),'checks':copy.deepcopy(checks)}
    with store.connect()as db:
        db.execute('CREATE TABLE IF NOT EXISTS claim_metric_selections(claim_id TEXT PRIMARY KEY,body TEXT,hash TEXT)')
        db.execute('INSERT INTO claim_metric_selections VALUES(?,?,?)',(body['id'],encoded(value),digest(value)))
    return dict(value,hash=digest(value))


def load(store,body,catalog,config):
    with store.connect()as db:
        exists=db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='claim_metric_selections'").fetchone()
        row=db.execute('SELECT body,hash FROM claim_metric_selections WHERE claim_id=?',(body['id'],)).fetchone()if exists else None
    if not row:raise Conflict('Metric representative lacks checked selection evidence')
    value=json.loads(row[0])
    if digest(value)!=row[1]or value['claim_hash']!=digest(body['claim'])or value['confirmation_hash']!=digest(body['confirmation'])or value['catalog_hash']!=digest(catalog):
        raise Conflict('Metric representative evidence changed')
    from .claim_candidate_checks import verified_probe
    workspace=SimpleNamespace(store=store,agent=SimpleNamespace(config=config))
    from .page_investigations import PageInvestigations,equal
    service=PageInvestigations(workspace);service._catalog=lambda:copy.deepcopy(catalog)
    current_plan=service.prepare(body,'PAGE_CONSISTENCY')
    if current_plan!=value['plan']:raise Conflict('Metric representative plan differs from current confirmed scope')
    byid={e['id']:e for e in value['checks']['evidence']}
    candidates=value['plan']['candidates']
    ids=set();observed=[]
    for candidate in candidates:
        matches=[p for p in byid.values()if p.get('cell_address',{}).get('target_id')==candidate['target_id']]
        if len(matches)!=1:raise Conflict('Metric representative lacks one original candidate receipt')
        checked=verified_probe(workspace,candidate,matches[0]);ids.add(candidate['target_id'])
        observed.append((candidate,checked))
    if sorted(ids)!=value['candidate_ids']or value['target_id']!=min(ids):
        raise Conflict('Metric representative candidate conservation differs')
    expected=[]
    for(left,a),(right,b)in itertools.combinations(observed,2):
        if left['measure_id']!=right['measure_id']:outcome='NOT_COMPARABLE';reason='DIFFERENT_METRIC_BINDING'
        elif left['comparison_scope_hash']!=right['comparison_scope_hash']:outcome='NOT_COMPARABLE';reason='DIFFERENT_DECLARED_RESTRICTIONS'
        else:outcome='OBSERVED_AGREEMENT'if equal(a['value'],b['value'])else'OBSERVED_DIFFERENCE';reason=None
        expected.append({'left_visual_id':left['target_id'],'right_visual_id':right['target_id'],
            'left_label':left['label'],'right_label':right['label'],'measure_name':left['measure_name'],
            'outcome':outcome,'reason':reason,'left_value':a['value'],'right_value':b['value'],
            'evidence_ids':[a['id'],b['id']],'snapshot_status':'SNAPSHOT_UNVERIFIED','cause_established':False})
    if value['checks']['comparisons']!=expected:
        raise Conflict('Metric representative comparison differs from original verified quantities')
    if len({c['comparison_scope_hash']for c in candidates})!=1 or any(c['outcome']!='OBSERVED_AGREEMENT'for c in expected):
        raise Conflict('Metric representative has no same-context agreement')
    return dict(value,hash=row[1])


class MetricVisualChecks:
    def __init__(self,workspace):self.workspace=workspace
    def prepare(self,body):
        from .page_investigations import PageInvestigations
        return PageInvestigations(self.workspace).prepare(body,'PAGE_CONSISTENCY')
    def run(self,body,adapter):
        from .page_investigations import PageInvestigations
        service=PageInvestigations(self.workspace);plan=self.prepare(body)
        checks=service.consistency(body,adapter)
        checks['kind']='METRIC_VISUAL_CONSISTENCY'
        if checks['status']=='PARTIAL':
            # An unavailable native read is a safety/read failure, never an agent-eligible capability gap.
            failed=any(r.get('disposition')=='UNAVAILABLE' for r in checks.get('coverage',{}).get('dispositions',[]))
            checks['reason']='METRIC_CANDIDATE_READ_UNAVAILABLE' if failed else 'METRIC_CANDIDATE_COVERAGE_INCOMPLETE'
        elif checks.get('outcome')=='OBSERVED_DIFFERENCE':
            checks['first_finding']='The metric differs between its addressed visuals under equivalent declared context.'
        elif checks.get('outcome')=='NOT_COMPARABLE'and len(plan.get('candidates',[]))!=1:
            checks['reason']='METRIC_CONTEXT_NOT_COMPARABLE'
        if checks['status']=='OBSERVED'and checks.get('outcome')=='OBSERVED_AGREEMENT'or (
            checks['status']=='NOT_COMPARABLE'and len(plan.get('candidates',[]))==1
            and len(checks.get('coverage',{}).get('checked_visual_ids',[]))==1):
            try:checks['metric_selection']=record(self.workspace.store,body,plan,checks)
            except Conflict as exc:checks['reason']=str(exc)
        return checks
