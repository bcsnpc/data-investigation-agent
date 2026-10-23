"""A native checked transformation is reusable evidence, not an outcome alias."""
import copy
from .assessment_support import validate
from .estate_graph_contract import canonical


def design_witness(assessment,observations):
    """Trusted adapter helper. Terminal validation rechecks this proof again."""
    validate(assessment,observations)
    if assessment.get('classification')!='TRANSFORMATION_LOGIC':raise ValueError('CHECKED_NATIVE_TRANSFORMATION_REQUIRED')
    return {'checked':True,'business_correctness_claim':False,
            'mechanism':assessment['support']['mechanism'],
            'native_assessment':copy.deepcopy(assessment),'native_observations':copy.deepcopy(observations)}


def validate_design(witness,reads,comparisons):
    from .evidence_verdicts import quantity
    assessment=witness.get('native_assessment');observations=witness.get('native_observations')
    if not isinstance(assessment,dict)or not isinstance(observations,dict):raise ValueError('NATIVE_DESIGN_EVIDENCE_REQUIRED')
    rebuilt=design_witness(assessment,observations)
    if witness.get('mechanism')!=rebuilt['mechanism'] or witness.get('business_correctness_claim')is not False:raise ValueError('NATIVE_DESIGN_MECHANISM_CHANGED')
    process=assessment['support']['process']
    definitions=process['evidence_by_role']['transformation_definition']
    if not definitions:raise ValueError('NATIVE_DEFINITION_EVIDENCE_REQUIRED')
    native_comparisons=[observations[identity] for identity in process['evidence_by_role']['comparison']]
    for comparison in comparisons:
        a=reads.get(comparison.get('left'));b=reads.get(comparison.get('right'))
        if not a or not b or canonical(a['context'])!=canonical(b['context']) or quantity(a)==quantity(b):continue
        for native in native_comparisons:
            if native.get('values_equal')is not False:continue
            if (native.get('upper_evidence_id'),native.get('lower_evidence_id'))!=(a['receipt_id'],b['receipt_id']):continue
            matched=True
            for result in (a,b):
                original=observations.get(result['receipt_id'],{})
                if (original.get('status')!='COMPLETED' or not isinstance(original.get('declared_context'),dict)
                        or canonical(original['declared_context'])!=canonical(result['context'])
                        or original.get('query')!=result.get('query')
                        or original.get('execution_surface')!=result.get('execution_surface')):matched=False
            if matched:return rebuilt['mechanism']
    raise ValueError('NATIVE_DESIGN_COMPARISON_RECEIPTS_OR_CONTEXT_DIFFER')

def validate_access(witness,reads,comparisons):
    from .evidence_verdicts import quantity
    if witness.get('impersonated') is not False:raise ValueError('ACCESS_IMPERSONATION_FORBIDDEN')
    for comparison in comparisons:
        a=reads.get(comparison.get('left'));b=reads.get(comparison.get('right'))
        if not a or not b:continue
        if (not a.get('authenticated_identity') or a.get('authenticated_identity')==b.get('authenticated_identity')
                or a.get('identity_verified')is not True or b.get('identity_verified')is not True):continue
        if (not a.get('query') or a.get('query')!=b.get('query') or canonical(a['context'])!=canonical(b['context'])
                or not a.get('expression_hash') or a.get('expression_hash')!=b.get('expression_hash') or quantity(a)==quantity(b)):continue
        surfaces=[r.get('execution_surface') for r in (a,b)]
        if not all(isinstance(v,dict) for v in surfaces):continue
        routes=[{k:v for k,v in surface.items() if k!='identity'} for surface in surfaces]
        if routes[0]!=routes[1]:continue
        return 'Two separately authorized identities returned different values for the same query, expression and declared context on the same data surface. No user was impersonated.'
    raise ValueError('ACCESS_REQUIRES_ORIGINAL_PAIRED_AUTHORIZED_READS')


def validate_history(witness,reads,comparisons,entries,now):
    from .evidence_verdicts import quantity
    from .estate_graph_contract import timestamp
    from .live_gateway import validate_sql,_object
    history=witness.get('native_history')
    if (not isinstance(history,dict) or not history.get('receipt_id') or history.get('read_only_verified')is not True
            or history.get('route_admitted')is not True):raise ValueError('ORIGINAL_HISTORY_READ_REQUIRED')
    source=history.get('subject')
    declared_sources={node['id'] for entry in entries if entry['kind']=='PATH' for node in entry['value'].get('nodes',[])
        if node.get('properties',{}).get('system_of_record')is True and node.get('confidence','DECLARED') not in ('INFERRED','UNKNOWN')}
    if source not in declared_sources:raise ValueError('HISTORY_REQUIRES_DECLARED_SYSTEM_OF_RECORD')
    validate_sql(history['query'],{_object(v) for v in history['read_only_objects']})
    changes=history.get('changes')
    if not isinstance(changes,list) or not 1<=len(changes)<=100:raise ValueError('SOURCE_ROW_HISTORY_REQUIRED')
    for comparison in comparisons:
        a=reads.get(comparison.get('left'));b=reads.get(comparison.get('right'))
        if not a or not b or b['subject']!=source or history.get('key')!=b['key']:continue
        if canonical(a['context'])!=canonical(b['context']) or canonical(history.get('context'))!=canonical(b['context']):continue
        if history.get('execution_surface')!=b.get('execution_surface'):continue
        if quantity(a)!=quantity({'state':'VALUE','value':history.get('before_quantity')}) or quantity(b)!=quantity({'state':'VALUE','value':history.get('after_quantity')}):continue
        if any(change.get('key')==b['key'] and change.get('before')!=change.get('after') and change.get('effective_at') and change.get('changed_at') and timestamp(change['effective_at'])<timestamp(change['changed_at'])<=now for change in changes):
            return 'A retained read of the declared system of record establishes a back-dated row correction; its checked before/after quantities match this observed split.'
    raise ValueError('HISTORY_CHANGE_NOT_CONNECTED_TO_OBSERVED_QUANTITY')
