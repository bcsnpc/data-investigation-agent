"""Neutral, receipt-bound grading; coverage is not independence."""
ENGINE_INDEPENDENT='ENGINE_INDEPENDENT'
OBJECT_DISTINCT='OBJECT_DISTINCT'
WITHIN_LAYER='WITHIN_LAYER_CHECK'
UNESTABLISHED='SURFACE_DIFFERENCE_UNESTABLISHED'
BOUNDARY_GRADES=(ENGINE_INDEPENDENT,OBJECT_DISTINCT)


def grade(upper,lower):
    """Each side must be the quantity observation itself, not a metadata receipt.

    Kind strings are opaque namespaces supplied by the adapter. Equality of
    kind is necessary; the engine never interprets platform property names.
    Identity/version never contribute, even if a hostile producer offers them.
    """
    for observation in (upper,lower):
        attestation=observation.get('surface_attestation') or {}
        if (attestation.get('consistency')!='MATCHED' or attestation.get('missing_required_fields')
                or observation.get('surface_report_binding')!='VALUE_QUERY'
                or observation.get('surface_report_receipt_id')!=observation.get('id')):
            return {'grade':UNESTABLISHED,'differing_field':None,'reason':'QUANTITY_BOUND_SELF_REPORT_REQUIRED'}
    reports=[o.get('surface_report') or {} for o in (upper,lower)]
    types=[o.get('surface_report_types') or {} for o in (upper,lower)]
    if any(not isinstance(v,dict) for v in reports+types):
        return {'grade':UNESTABLISHED,'differing_field':None,'reason':'MALFORMED_SELF_REPORT'}
    incomparable=[];comparable=[]
    for field,result in (('engine',ENGINE_INDEPENDENT),('object',OBJECT_DISTINCT)):
        a,b=[r.get(field) for r in reports]
        if not all(isinstance(v,str) and v for v in (a,b)):continue
        kinds=[t.get(field) for t in types]
        if field=='engine' and any(k!='ENGINE_PRODUCT' for k in kinds):
            # A version/instance/session descriptor is not an engine product,
            # even when a hostile producer places it in the engine slot.
            if a.casefold()!=b.casefold():incomparable.append(field)
            continue
        if not all(isinstance(k,str) and k for k in kinds) or kinds[0]!=kinds[1]:
            if a.casefold()!=b.casefold():incomparable.append(field)
            continue
        comparable.append(field)
        if a.casefold()!=b.casefold():
            return {'grade':result,'differing_field':field,'self_report_kind':kinds[0],
                    'upper_value':a,'lower_value':b,'reason':None}
    a,b=[r.get('connection') for r in reports]
    kinds=[t.get('connection') for t in types]
    if (all(isinstance(v,str) and v for v in (a,b)) and a.casefold()!=b.casefold()
            and (not all(isinstance(k,str) and k for k in kinds) or kinds[0]!=kinds[1])):
        incomparable.append('connection')
    return {'grade':UNESTABLISHED if incomparable or not comparable else WITHIN_LAYER,
            'differing_field':None,'reason':'INCOMPARABLE_SELF_REPORT_KINDS' if incomparable else
            'COMPARABLE_SELF_REPORT_REQUIRED' if not comparable else 'NO_INDEPENDENT_LOWER_READ'}


def validate(comparison,observations):
    """Recompute from original value receipts; marker claims cannot supply facts."""
    originals=[]
    for side in ('upper','lower'):
        original=observations.get(comparison.get(side+'_evidence_id'))
        if not isinstance(original,dict):raise ValueError('Boundary comparison requires its original quantity receipts')
        attestation=original.get('surface_attestation') or {}
        if (attestation.get('consistency')!='MATCHED' or attestation.get('missing_required_fields')
                or comparison.get(side+'_surface_attestation')!=attestation
                or comparison.get(side+'_execution_surface')!=original.get('execution_surface')):
            raise ValueError('A boundary comparison requires both surfaces to be attested')
        from .process_debugging import attest_surface
        if attest_surface(original.get('execution_surface'),original.get('surface_report'),
                          attestation.get('required_fields',()))!=attestation:
            raise ValueError('Original quantity surface attestation differs')
        originals.append(original)
    result=grade(*originals)
    if result['grade'] not in BOUNDARY_GRADES:
        raise ValueError('Boundary comparison lacks comparable quantity-bound difference: '+result['reason'])
    if comparison.get('surface_difference')!=result:
        raise ValueError('Boundary comparison surface difference grade differs from its quantity receipts')
    return result


def wording(result,business=False):
    if result['grade']==ENGINE_INDEPENDENT:
        return ('The two checks used different calculation engines.' if business else
                'ENGINE_INDEPENDENT: comparable quantity-bound engine self-reports differ; this is an engine-independent cross-surface comparison.')
    if result['grade']==OBJECT_DISTINCT:
        return ('The checks read different data sources; different calculation engines were not established, so a shared calculation fault could affect both.' if business else
                'OBJECT_DISTINCT: comparable quantity-bound object self-reports differ; this verifies a data-path boundary, not engine-level independence. Shared computation faults are not excluded.')
    return 'No independently attested boundary comparison was established.'
