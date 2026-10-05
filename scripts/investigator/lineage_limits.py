"""Engine-owned reasons for refusing sampled code lineage, never model caveats."""
def category(row, status=None):
    if status == 'STALE':return 'STALE_CODE'
    if row.get('status') == 'FALSIFIED':return 'SAMPLED_VALUES_DIFFER'
    reason=row.get('reason') or ''
    if reason.startswith('Cannot compile faithfully:'):return 'FAITHFUL_COMPILATION_UNAVAILABLE'
    if any(o.get('status')=='FAILED' for o in row.get('observations',[])):return 'READ_FAILED'
    if 'read did not complete' in reason or 'read failed' in reason:return 'READ_FAILED'
    if 'context, cell address or precision' in reason:return 'SAMPLE_MISMATCH'
    if 'surface' in reason:return 'SURFACE_EVIDENCE_UNAVAILABLE'
    return 'VERIFICATION_NOT_ESTABLISHED'


def technical(boundary):
    facts=boundary.get('lineage_refusal')
    if not facts:return None
    statuses=', '.join(facts['statuses']);categories=', '.join(facts['reason_categories'])
    return (f"Unchecked {boundary['upper_layer']} -> {boundary['lower_layer']}: "
            f"{facts['inventoried_proposal_count']} proposal(s) inventoried; "
            f"{facts['proposal_count']} selected-quantity proposal(s), {statuses}; "
            f"verifier reason categories: {categories}. The boundary was treated as unbound.")


def business(payload):
    from .layer_roles import name
    sentences=[]
    for row in payload.get('deterministic_process_finding',{}).get('unverified_boundaries',[]):
        if row.get('lineage_refusal'):
            sentences.append('The connection between the '+name(payload,row['lower_layer'])+
                ' and the '+name(payload,row['upper_layer'])+
                ' could not be verified from the processing code, so that part of the process was not checked.')
    return ' '.join(dict.fromkeys(sentences))


def validate_outputs(assessment, outputs):
    """Additional inferred-column invariant; historical declared tapes unaffected."""
    rows=assessment.get('technical_output',{}).get('unverified_boundaries',[])
    required=[technical(r) for r in rows if r.get('lineage_refusal')]
    if not required:return []
    technical_text=outputs.get('technical_output',{}).get('explanation',{}).get('text','')
    business_text=outputs.get('business_output',{}).get('explanation',{}).get('text','')
    errors=[]
    for row in rows:
        facts=row.get('lineage_refusal')
        if not facts:continue
        for token in (str(facts['proposal_count'])+' selected-quantity proposal(s)',
                      str(facts['inventoried_proposal_count'])+' proposal(s) inventoried',
                      *facts['statuses'], *facts['reason_categories'], 'treated as unbound'):
            if token not in technical_text:errors.append('technical_output:UNBOUND_LINEAGE_REASON_MISSING')
    if 'could not be verified from the processing code' not in business_text:
        errors.append('business_output:UNBOUND_LINEAGE_LIMIT_MISSING')
    return sorted(set(errors))
