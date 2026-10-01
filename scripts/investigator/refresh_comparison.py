"""Comparison-based freshness; timestamps enrich evidence and never select an outcome."""
LIMIT='Refresh timing is unavailable to the execution reader. The freshness claim rests on the independently observed declared-source difference, not a refresh timestamp or measured delay.'


def valid_proof(proof, upper, lower, measure=None):
    return (isinstance(proof,dict) and proof.get('version')==1
        and proof.get('basis')=='UNCHANGED_DECLARED_SOURCE'
        and proof.get('presentation_layer')==upper and proof.get('source_layer')==lower
        and (measure is None or proof.get('measure_id')==measure)
        and proof.get('provenance')=='DECLARED_BY_DEFINITION'
        and proof.get('scope')=='WHOLE_ENTITY' and proof.get('aggregate')=='SUM'
        and proof.get('intervening_operations')==[]
        and all(isinstance(proof.get(k),str) and proof[k] for k in
                ('definition_asset_id','definition_hash','source_column','measure_id')))


def whole_entity_context():
    """Context of a compiled whole-entity read, not a claim about user state."""
    return {'version':1,'scope':'WHOLE_ENTITY','filters':[],'dimension_ids':[]}


def equivalent_context(comparison, observations=None):
    """This narrow proof admits only explicitly recorded whole-entity contexts.

    Missing evidence is unknown. Equality of two filtered declarations is not a
    supported translation proof. Read references are rechecked at validation.
    """
    expected=whole_entity_context()
    for side in ('upper','lower'):
        context=comparison.get(side+'_declared_context')
        if context!=expected:return False
        if observations is not None:
            read=observations.get(comparison.get(side+'_evidence_id'),{})
            if read.get('status')!='COMPLETED' or read.get('declared_context')!=context:return False
    return True
