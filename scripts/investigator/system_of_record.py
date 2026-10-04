"""Operator-declared terminal asset; equality never discovers authority."""


def declaration(value):
    if (not isinstance(value, dict) or set(value) not in ({'asset_id'},{'asset_id','reachable'})
            or ('reachable' in value and type(value['reachable']) is not bool)
            or not isinstance(value['asset_id'], str)
            or not 1 <= len(value['asset_id']) <= 300
            or value['asset_id'] != value['asset_id'].strip()):
        raise ValueError('System of record requires one explicit stable asset_id')
    return dict(value)


def proof(path, comparisons):
    """Complete ordered chain to the declared asset, never merely deepest read."""
    declared = path.get('system_of_record')
    if declared is None or declared.get('reachable') is False:
        return False
    declared = declaration(declared)
    layers = [layer['id'] for layer in path.get('layers', [])]
    if declared['asset_id'] not in layers or layers.index(declared['asset_id']) == 0:
        return False
    end = layers.index(declared['asset_id'])
    if len(set(layers[:end+1])) != end+1 or len(comparisons) != end:
        return False
    if path.get('max_boundaries', len(layers)) < end:
        return False
    for upper, lower in zip(layers[:end], layers[1:end+1]):
        matches = [c for c in comparisons if c.get('upper_layer') == upper and c.get('lower_layer') == lower]
        if len(matches) != 1:
            return False
        c = matches[0]
        from .surface_difference import BOUNDARY_GRADES
        if (c.get('comparison_status') != 'CROSS_SURFACE_VERIFIED'
                or c.get('surface_difference', {}).get('grade') not in BOUNDARY_GRADES
                or c.get('values_equal') is not True
                or c.get('lower_binding_provenance') == 'INFERRED_FROM_CODE'):
            return False
        for side in ('upper', 'lower'):
            a = c.get(side+'_surface_attestation', {})
            if a.get('status') not in ('MATCHED', 'PARTIAL') or a.get('consistency') != 'MATCHED':
                return False
        # Explicit context agreement, including explicit whole-entity scope.
        if not isinstance(c.get('upper_declared_context'), dict) or c['upper_declared_context'] != c.get('lower_declared_context'):
            return False
    return True


def validate(assessment, observations, comparisons):
    process = assessment['support']['process']
    paths = [observations[r] for r in process['evidence_by_role']['path']]
    if len(paths) != 1 or not proof(paths[0].get('resolved_source_path', {}), comparisons):
        raise ValueError('CONSISTENT_TO_SOURCE requires every boundary to the declared system of record to agree')
    for c in comparisons:
        for side in ('upper','lower'):
            original=observations.get(c.get(side+'_evidence_id'),{})
            if original.get('declared_context') != c.get(side+'_declared_context'):
                raise ValueError('Source consistency scope must match the original quantity receipts')
    terminal = paths[0]['resolved_source_path']['system_of_record']['asset_id']
    from .record_presence import proof as presence_proof
    if not presence_proof(paths[0].get('expected_records',[]),paths[0]['resolved_source_path']['layers'],list(observations.values())):
        raise ValueError('Source consistency requires attested expected-record presence at every layer')
    if process['visibility_boundary']['deepest_layer'] != terminal or process['visibility_boundary']['stopped_by'] != 'REACHED':
        raise ValueError('Source consistency must terminate at the declared system of record')
