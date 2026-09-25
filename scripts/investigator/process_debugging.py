"""Platform-neutral deterministic vertical process debugger.

Adapters expose discovered paths and governed probes. The engine chooses no
layer, query, or next hop: it follows the returned path in order and stops on
the first evidence-bound outcome. Values are compared only when an adapter says
both quantities are comparable under the same declared scope.
"""
from dataclasses import dataclass
from typing import Protocol
from .process_outcomes import ACTIONS,EVIDENCE_ROLES

VERSION='process-debugging-v1'
REQUIRED_CAPABILITIES=frozenset(('resolve_measure_path','evaluate_scoped_quantity'))


@dataclass(frozen=True)
class Probe:
    status: str                 # OBSERVED, NOT_COMPARABLE, UNAVAILABLE
    layer: str
    evidence: dict | None = None
    value: object = None
    reason: str | None = None
    query: str | None = None


class ProcessAdapter(Protocol):
    def capabilities(self) -> set[str]: ...
    def resolve_path(self, measure_id: str) -> dict: ...
    def presentation_freshness(self, path: dict, scope: dict) -> dict: ...
    def evaluate(self, layer: dict, measure_id: str, scope: dict) -> Probe: ...
    def presentation_context(self, boundary: dict, scope: dict) -> dict: ...
    def transformation_definition(self, boundary: dict) -> dict: ...
    def job_history(self, boundary: dict) -> dict: ...
    def ingestion(self, path: dict, scope: dict) -> dict: ...


def applicability(adapter: ProcessAdapter):
    """Compute eligibility from advertised adapter capabilities."""
    available=frozenset(adapter.capabilities())
    missing=sorted(REQUIRED_CAPABILITIES-available)
    return {'eligible':not missing,'required':sorted(REQUIRED_CAPABILITIES),
            'available':sorted(available),'missing':missing}


def _observation(item, *roles):
    if not item:return None
    result=dict(item)
    result.setdefault('status','COMPLETED')
    result.setdefault('completeness','COMPLETE_RESPONSE')
    result['process_roles']=sorted(set(result.get('process_roles',[]))|set(roles))
    return result


def _answer(outcome, step, observations, deepest, stopped_by='REACHED', baseline=None,
            roles=None, missing_capability=None, explanation=None):
    evidence_ids=[o['id'] for o in observations if o.get('id')]
    role_refs={role:[] for role in EVIDENCE_ROLES}
    for role in roles or ():
        role_refs[role]=[o['id'] for o in observations if role in o.get('process_roles',[]) and o.get('id')]
    baseline=baseline or {'status':'NOT_ESTABLISHED','layer':None,
                          'reason':'No comparable presentation quantity was available.',
                          'evidence_ids':[]}
    process={'procedure_step':step,'recommended_action':ACTIONS[outcome],
             'visibility_boundary':{'deepest_layer':deepest,'stopped_by':stopped_by,
                                    'evidence_ids':evidence_ids[-2:]},
             'baseline_above':baseline,'evidence_by_role':role_refs,
             'missing_capability':missing_capability}
    return {'classification':outcome,'terminating_step':step,
            'claim':explanation or outcome.replace('_',' ').title(),
            'evidence_ids':evidence_ids,
            'alternatives':['A different declared scope could change the comparison.'],
            'limits':[f'Checked through {deepest}; stopped because {stopped_by.lower().replace("_"," ")}.'],
            'support':{'mechanism':explanation or 'The deterministic process procedure matched this outcome.',
                'mechanism_evidence_ids':evidence_ids[-2:],
                'intent_dependency':'NOT_REQUIRED',
                'intent_basis':'The outcome describes implemented process behavior without deciding whether it is intended.',
                'intent_evidence_ids':[],
                'measure_connection':'ESTABLISHED' if baseline['status']=='ESTABLISHED' else 'NOT_ESTABLISHED_CAPABILITY',
                'measure_connection_basis':'The baseline and boundary observations use the selected measure and declared scope.',
                'measure_connection_evidence_ids':baseline['evidence_ids'],
                'remaining_test':'Confirm intent separately when the implemented behavior is not desired.',
                'process':process},
            '_observations':observations,
            'technical_output':{'queries':[{'evidence_id':o['id'],'query':o['query']}
                               for o in observations if o.get('query')],
                                'visibility_boundary':process['visibility_boundary']}}


def vertical(adapter: ProcessAdapter, measure_id: str, scope: dict, fallback=None):
    """Run the vertical procedure over any discovered path length."""
    eligible=applicability(adapter)
    if not eligible['eligible']:
        evidence=_observation({'id':'process-capability-gap','tool':'capability',
            'available':eligible['available']},'established')
        return _answer('NO_KNOWN_PATTERN',0,[evidence],'unresolved path','CAPABILITY_UNAVAILABLE',
            roles=('established',),missing_capability='Missing adapter capabilities: '+', '.join(eligible['missing']))
    path=adapter.resolve_path(measure_id)
    layers=path.get('layers') or []
    if not layers:
        if fallback:return fallback(path,scope)
        evidence=_observation(path.get('evidence') or {'id':'unresolved-path','tool':'context'},'established')
        return _answer('NO_KNOWN_PATTERN',0,[evidence],path.get('boundary','unresolved path'),'NO_LINEAGE',
            roles=('established',),missing_capability='A discovered measure path is required.')
    observations=[]
    path_obs=_observation(path.get('evidence'),'path','established')
    if path_obs:observations.append(path_obs)

    # Step 1: freshness may terminate, but an unavailable check does not block
    # the baseline or the remaining reachable path.
    freshness=adapter.presentation_freshness(path,scope)
    fresh_obs=_observation(freshness.get('evidence'),'freshness') if freshness else None
    if fresh_obs:observations.append(fresh_obs)
    if freshness and freshness.get('status')=='LATENT':
        comparison=_observation(freshness.get('comparison_evidence'),'comparison')
        if comparison:observations.append(comparison)
        baseline={'status':'ESTABLISHED','layer':layers[0]['id'],'reason':None,
                  'evidence_ids':[comparison['id']] if comparison else []}
        return _answer('REFRESH_LATENCY',1,observations,layers[0]['id'],baseline=baseline,
                       roles=('freshness','comparison'),
                       explanation='The presentation refresh has not caught up with the matching value below.')

    # Step 2: establish our presentation baseline, independent of the ticket's
    # stated number. Failure is explicit and later boundary claims retain it.
    top=adapter.evaluate(layers[0],measure_id,scope)
    if top.evidence:
        top_obs=_observation(top.evidence,'baseline','flow_consistency','established')
        if top.query:top_obs['query']=top.query
        observations.append(top_obs)
    baseline={'status':'ESTABLISHED','layer':top.layer,'reason':None,
              'evidence_ids':[top.evidence['id']]} if top.status=='OBSERVED' and top.evidence else {
              'status':'NOT_ESTABLISHED','layer':top.layer,'reason':top.reason or 'Presentation quantity was not comparable.',
              'evidence_ids':[]}

    # Steps 3-5: compare adjacent reachable layers. NOT_COMPARABLE is recorded
    # and skipped; equality is exact on adapter-normalized values.
    upper=top
    for index,lower_layer in enumerate(layers[1:],start=1):
        lower=adapter.evaluate(lower_layer,measure_id,scope)
        if lower.evidence:
            obs=_observation(lower.evidence,'flow_consistency','established')
            if lower.query:obs['query']=lower.query
            observations.append(obs)
        if upper.status!='OBSERVED' or lower.status!='OBSERVED':
            marker=_observation({'id':f'boundary-{index}-not-comparable','tool':'process',
                'reason':lower.reason or upper.reason},'comparison')
            observations.append(marker);upper=lower
            continue
        comparison=_observation({'id':f'boundary-{index}-comparison','tool':'process',
            'upper_layer':upper.layer,'lower_layer':lower.layer,
            'values_equal':upper.value==lower.value},'comparison')
        observations.append(comparison)
        if upper.value==lower.value:
            upper=lower;continue
        boundary={'upper':layers[index-1],'lower':lower_layer,'index':index}
        if index==1:
            context=adapter.presentation_context(boundary,scope)
            context_obs=_observation(context.get('evidence'),'presentation_definition') if context else None
            if context_obs:observations.append(context_obs)
            if context and context.get('explains') is True:
                return _answer('PRESENTATION_LOGIC',3,observations,lower.layer,baseline=baseline,
                    roles=('presentation_definition','comparison'),
                    explanation=context.get('explanation'))
        definition=adapter.transformation_definition(boundary)
        definition_obs=_observation(definition.get('evidence'),'transformation_definition') if definition else None
        if definition_obs:observations.append(definition_obs)
        if definition and definition.get('explains') is True:
            return _answer('TRANSFORMATION_LOGIC',5,observations,lower.layer,baseline=baseline,
                roles=('transformation_definition','comparison'),explanation=definition.get('explanation'))
        job=adapter.job_history(boundary)
        job_obs=_observation(job.get('evidence'),'job_history','prior_state') if job else None
        if job_obs:observations.append(job_obs)
        if job and job.get('status')=='LATENT':
            return _answer('LOAD_LATENCY',5,observations,lower.layer,baseline=baseline,
                roles=('job_history','prior_state','comparison'),explanation=job.get('explanation'))
        absence=_observation({'id':f'boundary-{index}-definition-absence','tool':'process'},'definition_absence','mechanism')
        observations.append(absence)
        return _answer('DEFECT',5,observations,lower.layer,baseline=baseline,
            roles=('mechanism','comparison','definition_absence'),
            explanation='The observed boundary change is not accounted for by a retrieved definition.')

    # Step 6: no comparable boundary diverged. Check capture/delivery evidence;
    # otherwise name the deepest layer actually reached.
    ingestion=adapter.ingestion(path,scope)
    ingestion_obs=_observation(ingestion.get('evidence'),'ingestion') if ingestion else None
    if ingestion_obs:observations.append(ingestion_obs)
    if ingestion and ingestion.get('status')=='GAP':
        return _answer('INGESTION_GAP',6,observations,upper.layer,baseline=baseline,
            roles=('ingestion','flow_consistency'),explanation=ingestion.get('explanation'))
    deepest=upper.layer if upper.status=='OBSERVED' else layers[0]['id']
    stopped=path.get('stopped_by','REACHED')
    if scope.get('ticket_shape')=='BUSINESS_QUESTION':
        return _answer('BUSINESS_QUESTION',6,observations,deepest,stopped,baseline,
            roles=('flow_consistency',),
            explanation=f'The reachable process flow is consistent through {deepest}; the remaining question is business interpretation.')
    return _answer('CONSISTENT_TO_BOUNDARY',6,observations,deepest,stopped,baseline,
        roles=('path','flow_consistency'),
        explanation=f'Every comparable reachable layer agreed through {deepest}.')
