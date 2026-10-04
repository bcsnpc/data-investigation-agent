"""Provider view only. Originals are validated and rendered locally, never sent.

Elision is a display decision, not a deletion from the evidence store or a
change to eligibility. The complete local view still renders both outputs.
"""
import copy
from .onboarding import encoded


def build(payload, state, bound):
    from .output_contract import business_text
    from .path_narrative import facts
    outcome = (state.get('assessment') or {}).get('classification')
    result = {'version': 2, 'question': payload['question'],
              'scope': copy.deepcopy(payload['scope']), 'evidence': [],
              'candidates': [], 'boundaries': facts(payload), 'mechanism_evidence': [],
              'elided': [], 'rendered_business': business_text(outcome, payload) if outcome else None}
    if outcome: result['outcome'] = outcome
    from .reproduction_composition import from_payload,select
    lead=select(from_payload(payload))
    if lead:result['answering_cell_receipt_id']=lead['id']
    for entry in payload['evidence']:
        # Citation identity only. No raw receipt, query, self-report, inventory,
        # declaration or model-interpreted copy of a validation field.
        result['evidence'].append({'id': entry['id']})
        row = entry.get('result', {})
        # A display copy, never a reconstructed validation observation. Keep
        # the complete retained definition and judgment together, including
        # provenance and limits; future evidence fields cannot silently vanish.
        if set(entry.get('process_roles', [])) & {'transformation_definition', 'presentation_definition'}:
            result['mechanism_evidence'].append(copy.deepcopy(entry))
        if row.get('check_kind') == 'DECLARED_CONTEXT_REPRODUCTION':
            cell = row.get('cell') or {}
            declarations = row.get('declarations', [])
            result['candidates'].append({
                'receipt_id': entry['id'],
                'definition_receipt_id': row['definition_evidence_id'],
                'read_receipt_ids': [row['upper_evidence_id'], row['lower_evidence_id']],
                'cell_mode': cell.get('mode'), 'cell_id': cell.get('id'),
                'restrictions': copy.deepcopy(row['composed_restrictions']),
                'undeclared_context_value': row['undeclared_context_value'],
                'declared_context_value': row['reproduced_value'],
                'reported_figure': {k: v for k, v in row['reported_figure'].items() if k != 'source'},
                'result': row['label'] or row['unavailability'],
                'grade': row['comparison_status'],
                'attestation': {side: {k: row[side + '_surface_attestation'].get(k)
                    for k in ('status', 'coverage', 'attested_fields', 'missing_required_fields')}
                    for side in ('upper', 'lower')},
                'resolution_kinds': {'report': state['envelope'].get('report_binding', {}).get('resolution_kind'),
                    'selection': row.get('selection_resolution', {}).get('resolution_kind')},
                'qualifications_and_open_set': list(row['limitations']),
                'declaration_counts': {kind: sum(d['disposition'] == kind for d in declarations)
                    for kind in ('ACTIVE', 'CONDITIONAL', 'UNSUPPORTED')}})
    finding = payload.get('deterministic_process_finding')
    if finding:
        result['finding'] = {k: copy.deepcopy(finding[k]) for k in
            ('classification', 'recommended_action', 'conclusion_blocker', 'mandatory_limits')}
    # Drop whole display units with named omissions, never truncate evidence
    # prose or alter the local view. A degraded spine uses local deterministic
    # composition, so provider failure cannot hide validated facts.
    for key in ('mechanism_evidence', 'candidates', 'boundaries', 'evidence'):
        while len(encoded(result)) > bound and result[key]:
            item = result[key].pop()
            identity = item.get('receipt_id') or item.get('comparison_id') or item.get('id')
            result['elided'].append({'section': key, 'id': identity})
        if len(encoded(result)) <= bound: break
    if len(encoded(result)) > bound:
        # IDs and long ticket text can themselves exceed a small provider bound.
        # The store/local rendering still contains them in full.
        counts = {key: sum(e['section'] == key for e in result['elided'])
                  for key in ('mechanism_evidence', 'candidates', 'boundaries', 'evidence')}
        result = {'version': 2, 'evidence': [], 'elided': [
            {'section': 'provider view', 'reason': 'Input bound; use complete local rendering.',
             'omitted_sections': ['question', 'scope', 'finding', 'business wording'], 'counts': counts}]}
    return result


def degraded_outputs(payload, state, spine):
    """No new conclusion: render the original supported assessment locally."""
    from .synthesis_narrative import Response, assemble
    from .output_contract import business_text
    source = state['assessment']
    refs = [payload['evidence'][0]['id']] if payload['evidence'] else []
    technical={'text': 'The recorded checks evaluate the declared calculation.', 'evidence_ids': refs}
    from .path_narrative import divergent_boundaries
    boundaries=divergent_boundaries(payload)
    if boundaries:technical['boundary_evidence_id']=boundaries[0]
    response = Response({'business_output': {'text': business_text(source['classification'], payload), 'evidence_ids': refs},
                         'technical_output': technical})
    assessment, outputs = assemble(response, payload, state)
    for key in ('business_output', 'technical_output'):
        note = ('The explanation used the complete saved evidence locally; part of the model view was omitted to stay within its input allowance.'
                if key == 'business_output' else 'Provider view elided: ' + '; '.join(
                    e['section'] + (' receipt ' + e['id'] if e.get('id') else ': ' + e.get('reason', ''))
                    for e in spine['elided']))
        outputs[key]['explanation']['text'] += '\n' + note
    outputs['provenance'] = 'DETERMINISTIC_BOUNDED_SPINE_RENDERING'
    return assessment, outputs
