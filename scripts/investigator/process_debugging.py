"""Platform-neutral deterministic vertical process debugger.

Adapters expose discovered paths and governed probes. The engine chooses no
layer, query, or next hop: it follows the returned path in order and stops on
the first evidence-bound outcome. Values are compared only when an adapter says
both quantities are comparable under the same declared scope.
"""
from dataclasses import dataclass,replace
from typing import Protocol
from .process_outcomes import ACTIONS,EVIDENCE_ROLES

VERSION='process-debugging-v2'
REQUIRED_CAPABILITIES=frozenset(('resolve_measure_path','evaluate_scoped_quantity'))
OPTIONAL_CAPABILITIES=frozenset(('presentation_freshness','presentation_context',
    'transformation_definition','job_history','ingestion','independent_lower_surface','failure_detail'))


@dataclass(frozen=True)
class Probe:
    status: str                 # OBSERVED, NOT_COMPARABLE, UNAVAILABLE
    layer: str
    evidence: dict | None = None
    value: object = None
    reason: str | None = None
    query: str | None = None
    execution_surface: dict | None = None
    surface_report: dict | None = None   # the surface's own answer, never the client's belief
    surface_reportable: tuple = ()        # declared fields this surface is able to report
    failure: dict | None = None           # why the probe is UNAVAILABLE, as specifically as known


# An execution surface is established by the surface's own answer. The adapter
# declares what it intended to reach; the surface reports who connected and to
# what. How a surface answers is the adapter's concern; the engine only compares.
SURFACE_REPORT_REQUIRED=('identity',)


def attest_surface(declared, report, reportable=()):
    """Compare a declared execution surface with the surface's self-report.

    Every field the surface is able to report must be reported; a field it
    cannot report stays unattested and is carried into every claim's limits.
    """
    required=sorted(set(SURFACE_REPORT_REQUIRED)|set(reportable or ()))
    if not isinstance(declared,dict) or not isinstance(declared.get('identity'),str) or not declared['identity']:
        return {'status':'IDENTITY_NOT_DECLARED','reason':'SURFACE_IDENTITY_NOT_DECLARED','required_fields':required,
                'contradictions':[],'attested_fields':[],'unattested_fields':[]}
    if (not isinstance(report,dict) or not report
            or any(not isinstance(k,str) or not isinstance(v,str) or not v for k,v in report.items())
            or any(k not in report for k in required)):
        return {'status':'MISSING','reason':'SURFACE_SELF_REPORT_MISSING','required_fields':required,
                'contradictions':[],'attested_fields':[],'unattested_fields':sorted(declared)}
    contradictions=[{'field':k,'declared':declared.get(k),'reported':v} for k,v in sorted(report.items())
                    if not isinstance(declared.get(k),str) or declared[k].casefold()!=v.casefold()]
    return {'status':'CONTRADICTED' if contradictions else 'MATCHED',
            'reason':'SURFACE_SELF_REPORT_CONTRADICTS_DECLARED' if contradictions else None,'required_fields':required,
            'contradictions':contradictions,'attested_fields':sorted(set(report)&set(declared)),
            'unattested_fields':sorted(set(declared)-set(report))}


def attest(probe):
    """A probe that claims a surface is observed only if the surface agrees."""
    if probe.evidence is None or probe.status=='UNAVAILABLE':return probe
    result=attest_surface(probe.execution_surface,probe.surface_report,probe.surface_reportable)
    evidence=dict(probe.evidence,surface_report=probe.surface_report,surface_attestation=result)
    if result['status']=='MATCHED':
        return Probe(probe.status,probe.layer,evidence,probe.value,probe.reason,probe.query,
                     probe.execution_surface,probe.surface_report,probe.surface_reportable)
    # Deliberate: a failed attestation outranks every other status. A probe that
    # was NOT_COMPARABLE and also untrusted is reported as untrusted, and its
    # prior status is kept in the evidence so the distinction is not lost.
    evidence['status_before_attestation']=probe.status
    return Probe('UNAVAILABLE',probe.layer,evidence,None,result['reason'],probe.query,
                 probe.execution_surface,probe.surface_report,probe.surface_reportable)


def unattested_surface_fields(observations):
    """Every field of a compared surface that its surface did not report."""
    result=[]
    for o in observations:
        if o.get('tool')!='process' or o.get('comparison_status')!='CROSS_SURFACE_VERIFIED':continue
        for side in ('upper','lower'):
            attestation=o.get(side+'_surface_attestation') or {}
            for field in attestation.get('unattested_fields',[]):
                entry={'layer':o.get(side+'_layer'),'field':field,'evidence_id':o.get(side+'_evidence_id')}
                if entry not in result:result.append(entry)
    return result


def surface_limit(entry):
    return 'Unattested surface field '+entry['field']+' on '+str(entry['layer'])+': the surface did not report it.'


def refine_failure(adapter, available, layer, probe):
    """Prefer the most specific failure the surface can give.

    A surface may report a failure only generically through the interface that
    was read. When the adapter marks a failure GENERIC and declares
    `failure_detail`, the engine asks it for a more specific failure from
    another interface to the same surface. Refinement never changes the status:
    an UNAVAILABLE probe stays UNAVAILABLE. It only replaces a generic reason
    with the most specific one obtained, and keeps both.
    """
    failure=probe.failure
    if probe.status!='UNAVAILABLE' or not isinstance(failure,dict) or failure.get('specificity')!='GENERIC':
        return probe
    if 'failure_detail' not in available:
        return replace(probe,failure=dict(failure,refinement='NOT_DECLARED'))
    try:
        detail=adapter.failure_detail(layer,probe)
    except Exception as exc:
        return replace(probe,failure=dict(failure,refinement='FAILED',refinement_error_type=type(exc).__name__))
    if not isinstance(detail,dict) or detail.get('specificity')!='SPECIFIC' or not detail.get('codes'):
        return replace(probe,failure=dict(failure,refinement='NO_SPECIFIC_FAILURE',
                                          refinement_detail=detail if isinstance(detail,dict) else None))
    specific=', '.join(str(c) for c in detail['codes'])
    reason=(probe.reason or 'The surface reported a generic failure.')+' Most specific failure via '+str(
        detail.get('interface') or 'another interface')+': '+specific+'.'
    return replace(probe,reason=reason,failure=dict(failure,refinement='OBTAINED',most_specific=detail))


def _failure_entry(probe):
    failure=probe.failure or {}
    specific=failure.get('most_specific') or {}
    return {'layer':probe.layer,'reason':probe.reason,'interface':failure.get('interface'),
            'generic_codes':failure.get('codes',[]),'refinement':failure.get('refinement'),
            'specific_interface':specific.get('interface'),'specific_codes':specific.get('codes',[])}


def _surface_key(surface):
    if not isinstance(surface,dict):return None
    required=('engine','connection','object')
    if any(not isinstance(surface.get(key),str) or not surface[key] for key in required):return None
    return tuple(surface[key] for key in required)


class ProcessAdapter(Protocol):
    def capabilities(self) -> set[str]: ...
    def resolve_declared_source(self, declaration: dict) -> dict: ...
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
            roles=None, missing_capability=None, explanation=None, skipped_steps=(),capabilities=(),failures=()):
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
             'missing_capability':missing_capability,'skipped_steps':list(skipped_steps),
             'capabilities_declared':sorted(set(capabilities))}
    comparisons=[o for o in observations if o.get('tool')=='process'
                 and o.get('comparison_status')=='CROSS_SURFACE_VERIFIED']
    within_layer=[o for o in observations if o.get('tool')=='process'
                  and o.get('comparison_status')=='WITHIN_LAYER_CHECK']
    not_comparable=[{'upper_layer':o.get('upper_layer'),'lower_layer':o.get('lower_layer'),
                     'reason':o.get('reason')} for o in observations
                    if o.get('comparison_status') in ('NOT_COMPARABLE','WITHIN_LAYER_CHECK')]
    unattested=unattested_surface_fields(observations)
    return {'classification':outcome,'terminating_step':step,
            'claim':explanation or outcome.replace('_',' ').title(),
            'evidence_ids':evidence_ids,
            'alternatives':['A different declared scope could change the comparison.'],
            'limits':[f'Checked through {deepest}; stopped because {stopped_by.lower().replace("_"," ")}.']
                     +[surface_limit(u) for u in unattested],
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
            'business_output':{'conclusion':explanation or outcome.replace('_',' ').title(),
                               'failures':list(failures),
                               'unattested_surface_fields':unattested,
                               'skipped_steps':list(skipped_steps)},
            'technical_output':{'failures':list(failures),
                                'queries':[{'evidence_id':o['id'],'query':o['query']}
                               for o in observations if o.get('query')],
                                'visibility_boundary':process['visibility_boundary'],
                                'unattested_surface_fields':unattested,
                                'skipped_steps':list(skipped_steps),
                                'capabilities_declared':sorted(set(capabilities)),
                                'boundary_summary':{'resolved_boundaries':len(comparisons),
                                    'comparisons_executed':len(comparisons),
                                    'within_layer_checks':len(within_layer),
                                    'not_comparable':not_comparable}}}


def vertical(adapter: ProcessAdapter, measure_id: str, scope: dict, fallback=None):
    """Run the vertical procedure over any discovered path length."""
    available=frozenset(adapter.capabilities())
    failures=[]
    def answer(*args,**kwargs):return _answer(*args,capabilities=available,failures=failures,**kwargs)
    def read(layer):
        probe=refine_failure(adapter,available,layer,attest(adapter.evaluate(layer,measure_id,scope)))
        if probe.status=='UNAVAILABLE' and probe.failure:failures.append(_failure_entry(probe))
        return probe
    eligible=applicability(adapter)
    if not eligible['eligible']:
        evidence=_observation({'id':'process-capability-gap','tool':'capability',
            'available':eligible['available']},'established')
        return answer('NO_KNOWN_PATTERN',0,[evidence],'unresolved path','CAPABILITY_UNAVAILABLE',
            roles=('established',),missing_capability='Missing adapter capabilities: '+', '.join(eligible['missing']))
    path=adapter.resolve_path(measure_id)
    skipped=[];gap_reasons=getattr(adapter,'capability_gaps',lambda:{})()
    def skip(step,capability):
        if not any(x['step']==step and x['capability']==capability for x in skipped):
            skipped.append({'step':step,'capability':capability,
                            'reason':gap_reasons.get(capability,'Adapter does not declare this procedure capability.')})
    def unavailable(step,capability,reason):
        if not any(x['step']==step and x['capability']==capability for x in skipped):
            skipped.append({'step':step,'capability':capability,'reason':reason})
    layers=path.get('layers') or []
    if not layers:
        if fallback:return fallback(path,scope)
        evidence=_observation(path.get('evidence') or {'id':'unresolved-path','tool':'context'},'established')
        return answer('NO_KNOWN_PATTERN',0,[evidence],path.get('boundary','unresolved path'),'NO_LINEAGE',
            roles=('established',),missing_capability='A discovered measure path is required.')
    observations=[]
    path_obs=_observation(path.get('evidence'),'path','established')
    if path_obs:observations.append(path_obs)

    # Step 1: freshness may terminate, but an unavailable check does not block
    # the baseline or the remaining reachable path.
    if 'presentation_freshness' in available:freshness=adapter.presentation_freshness(path,scope)
    else:freshness=None;skip(1,'presentation_freshness')
    fresh_obs=_observation(freshness.get('evidence'),'freshness') if freshness else None
    if fresh_obs:observations.append(fresh_obs)
    if freshness and freshness.get('status')=='LATENT':
        comparison=_observation(freshness.get('comparison_evidence'),'comparison','baseline')
        if comparison:observations.append(comparison)
        baseline={'status':'ESTABLISHED','layer':layers[0]['id'],'reason':None,
                  'evidence_ids':[comparison['id']] if comparison else []}
        return answer('REFRESH_LATENCY',1,observations,layers[0]['id'],baseline=baseline,
                       roles=('freshness','comparison'),
                       explanation='The presentation refresh has not caught up with the matching value below.',
                       skipped_steps=skipped)

    # Step 2: establish our presentation baseline, independent of the ticket's
    # stated number. Failure is explicit and later boundary claims retain it.
    top=read(layers[0])
    if top.evidence:
        top_obs=_observation(top.evidence,'baseline','established')
        if top.query:top_obs['query']=top.query
        top_obs['execution_surface']=top.execution_surface
        observations.append(top_obs)
    baseline={'status':'ESTABLISHED','layer':top.layer,'reason':None,
              'evidence_ids':[top.evidence['id']]} if top.status=='OBSERVED' and top.evidence else {
              'status':'NOT_ESTABLISHED','layer':top.layer,'reason':top.reason or 'Presentation quantity was not comparable.',
              'evidence_ids':[]}

    if len(layers)<2:
        reason=path.get('missing_comparable_quantity') or 'No adjacent layer has a faithfully bound quantity for comparison.'
        if baseline['status']!='ESTABLISHED':
            return answer('NO_KNOWN_PATTERN',2,observations,layers[0]['id'],'CAPABILITY_UNAVAILABLE',baseline,
                roles=('established',),missing_capability=baseline['reason'],skipped_steps=skipped)
        return answer('NO_COMPARABLE_PATH',3,observations,layers[0]['id'],'CAPABILITY_UNAVAILABLE',baseline,
            roles=('path',),missing_capability=reason,
            explanation='The presentation baseline was established, but no adjacent comparable quantity could be resolved. '+reason,
            skipped_steps=skipped)

    # Steps 3-5: compare adjacent reachable layers. NOT_COMPARABLE is recorded
    # and skipped; equality is exact on adapter-normalized values.
    upper=top;verified_boundaries=0;last_verified=top.layer;chain_connected=top.status=='OBSERVED';gaps=[]
    for index,lower_layer in enumerate(layers[1:],start=1):
        lower=read(lower_layer)
        if lower.evidence:
            obs=_observation(lower.evidence,'baseline','established')
            if lower.query:obs['query']=lower.query
            obs['execution_surface']=lower.execution_surface
            observations.append(obs)
        upper_surface=_surface_key(upper.execution_surface);lower_surface=_surface_key(lower.execution_surface)
        if (lower.reason=='NO_INDEPENDENT_LOWER_READ' and upper.evidence and lower.evidence
                and upper_surface is not None and upper_surface==lower_surface):
            marker=_observation({'id':f'boundary-{index}-not-comparable','tool':'process',
                'upper_layer':upper.layer,'lower_layer':lower.layer,'comparison_status':'WITHIN_LAYER_CHECK',
                'reason':'NO_INDEPENDENT_LOWER_READ','values_equal':upper.value==lower.value,
                'upper_evidence_id':upper.evidence['id'],'lower_evidence_id':lower.evidence['id'],
                'upper_execution_surface':upper.execution_surface,
                'lower_execution_surface':lower.execution_surface},'definition_check')
            observations.append(marker);gaps.append(marker);upper=lower;chain_connected=False
            continue
        if upper.status!='OBSERVED' or lower.status!='OBSERVED':
            reason=lower.reason or upper.reason or 'No faithful comparable quantity was available.'
            marker=_observation({'id':f'boundary-{index}-not-comparable','tool':'process',
                'upper_layer':upper.layer,'lower_layer':lower.layer,'comparison_status':'NOT_COMPARABLE',
                'reason':reason,'upper_evidence_id':upper.evidence.get('id') if upper.evidence else None,
                'lower_evidence_id':lower.evidence.get('id') if lower.evidence else None,
                'upper_execution_surface':upper.execution_surface,
                'lower_execution_surface':lower.execution_surface})
            observations.append(marker);gaps.append(marker);upper=lower;chain_connected=False
            continue
        if upper_surface is None or lower_surface is None or upper_surface==lower_surface:
            reason='NO_INDEPENDENT_LOWER_READ'
            marker=_observation({'id':f'boundary-{index}-not-comparable','tool':'process',
                'upper_layer':upper.layer,'lower_layer':lower.layer,'comparison_status':'WITHIN_LAYER_CHECK',
                'reason':reason,'values_equal':upper.value==lower.value,
                'upper_evidence_id':upper.evidence.get('id') if upper.evidence else None,
                'lower_evidence_id':lower.evidence.get('id') if lower.evidence else None,
                'upper_execution_surface':upper.execution_surface,
                'lower_execution_surface':lower.execution_surface},'definition_check')
            observations.append(marker);gaps.append(marker);upper=lower;chain_connected=False
            continue
        comparison=_observation({'id':f'boundary-{index}-comparison','tool':'process',
            'upper_layer':upper.layer,'lower_layer':lower.layer,
            'comparison_status':'CROSS_SURFACE_VERIFIED',
            'values_equal':upper.value==lower.value,
            'upper_evidence_id':upper.evidence.get('id') if upper.evidence else None,
            'lower_evidence_id':lower.evidence.get('id') if lower.evidence else None,
            'upper_execution_surface':upper.execution_surface,
            'lower_execution_surface':lower.execution_surface,
            'upper_surface_attestation':(upper.evidence or {}).get('surface_attestation'),
            'lower_surface_attestation':(lower.evidence or {}).get('surface_attestation')},'comparison',
            *(['flow_consistency'] if chain_connected and upper.value==lower.value else []))
        observations.append(comparison)
        if upper.value==lower.value:
            if chain_connected:verified_boundaries+=1;last_verified=lower.layer
            upper=lower;continue
        boundary_baseline={'status':'ESTABLISHED','layer':upper.layer,'reason':None,
                           'evidence_ids':[upper.evidence['id']] if upper.evidence else []}
        boundary={'upper':layers[index-1],'lower':lower_layer,'index':index,
                  'upper_probe':upper,'lower_probe':lower}
        if index==1:
            if 'presentation_context' in available:context=adapter.presentation_context(boundary,scope)
            else:context=None;skip(3,'presentation_context')
            context_obs=_observation(context.get('evidence'),'presentation_definition') if context else None
            if context_obs:observations.append(context_obs)
            if context and context.get('explains') is True:
                return answer('PRESENTATION_LOGIC',3,observations,lower.layer,baseline=boundary_baseline,
                    roles=('presentation_definition','comparison'),
                    explanation=context.get('explanation'),skipped_steps=skipped)
            if context and context.get('status') not in (None,'COMPLETED'):
                unavailable(3,'presentation_context',context.get('reason') or 'Presentation context check was inconclusive.')
        if 'transformation_definition' in available:definition=adapter.transformation_definition(boundary)
        else:definition=None;skip(5,'transformation_definition')
        definition_obs=_observation(definition.get('evidence'),'transformation_definition') if definition else None
        if definition_obs:observations.append(definition_obs)
        if definition and definition.get('explains') is True:
            return answer('TRANSFORMATION_LOGIC',5,observations,lower.layer,baseline=boundary_baseline,
                roles=('transformation_definition','comparison'),explanation=definition.get('explanation'),
                skipped_steps=skipped)
        if definition and definition.get('status') not in (None,'COMPLETED'):
            unavailable(5,'transformation_definition',definition.get('reason') or 'Transformation-definition check was inconclusive.')
        if 'job_history' in available:job=adapter.job_history(boundary)
        else:job=None;skip(5,'job_history')
        job_obs=_observation(job.get('evidence'),'job_history','prior_state') if job else None
        if job_obs:observations.append(job_obs)
        if job and job.get('status')=='LATENT':
            return answer('LOAD_LATENCY',5,observations,lower.layer,baseline=boundary_baseline,
                roles=('job_history','prior_state','comparison'),explanation=job.get('explanation'),
                skipped_steps=skipped)
        if job and job.get('status')=='UNAVAILABLE':
            unavailable(5,'job_history',job.get('reason') or 'Job-history check was unavailable.')
        missing=[x['capability'] for x in skipped if x['step'] in ((3,5) if index==1 else (5,))]
        if missing:
            reason='Divergence observed, but competing explanations were not checked: '+', '.join(missing)+'.'
            return answer('NO_KNOWN_PATTERN',5,observations,lower.layer,'CAPABILITY_NOT_IMPLEMENTED',
                boundary_baseline,roles=('established',),missing_capability=reason,
                explanation=reason,skipped_steps=skipped)
        absence=_observation({'id':f'boundary-{index}-definition-absence','tool':'process'},'definition_absence','mechanism')
        observations.append(absence)
        return answer('DEFECT',5,observations,lower.layer,baseline=boundary_baseline,
            roles=('mechanism','comparison','definition_absence'),
            explanation='The observed boundary change is not accounted for by a retrieved definition.',
            skipped_steps=skipped)

    # Step 6: no comparable boundary diverged. Check capture/delivery evidence;
    # otherwise name the deepest layer actually reached.
    if verified_boundaries==0:
        reason=(gaps[0]['reason'] if gaps else path.get('missing_comparable_quantity')) or 'No successful boundary comparison connected the baseline to a lower layer.'
        return answer('NO_COMPARABLE_PATH',3,observations,layers[0]['id'],'CAPABILITY_UNAVAILABLE',baseline,
            roles=('path',),missing_capability=reason,
            explanation='The presentation baseline was established, but no boundary below it could be compared faithfully. '+reason,
            skipped_steps=skipped)
    if chain_connected and 'ingestion' in available:ingestion=adapter.ingestion(path,scope)
    else:
        ingestion={'status':'UNAVAILABLE'}
        if chain_connected:skip(6,'ingestion')
    ingestion_obs=_observation(ingestion.get('evidence'),'ingestion') if ingestion else None
    if ingestion_obs:observations.append(ingestion_obs)
    if ingestion and ingestion.get('status')=='GAP':
        return answer('INGESTION_GAP',6,observations,upper.layer,baseline=baseline,
            roles=('ingestion','flow_consistency','comparison'),explanation=ingestion.get('explanation'),
            skipped_steps=skipped)
    deepest=last_verified
    stopped='NOT_COMPARABLE' if gaps else path.get('stopped_by','REACHED')
    if scope.get('ticket_shape')=='BUSINESS_QUESTION':
        return answer('BUSINESS_QUESTION',6,observations,deepest,stopped,baseline,
            roles=('flow_consistency','comparison'),
            explanation=f'The reachable process flow is consistent through {deepest}; the remaining question is business interpretation.',
            skipped_steps=skipped)
    return answer('CONSISTENT_TO_BOUNDARY',6,observations,deepest,stopped,baseline,
        roles=('path','flow_consistency','comparison'),
        explanation=f'Every comparable reachable layer agreed through {deepest}.',skipped_steps=skipped)
