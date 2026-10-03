"""Deterministic refusal delivery; never a model-authored technical verdict."""
import copy
from . import process_receipts
from .onboarding import digest


def earliest(state):
    # An internal crash must remain visible even after an earlier side-check
    # refusal; it cannot be delivered as that capability's unavailability.
    for observation in state.get('observations', []):
        if observation.get('check_kind')=='BUDGET_STOP':return observation
    for observation in state.get('observations', []):
        if observation.get('check_kind')=='PROCESS_FAILED':return observation
    for observation in state.get('observations', []):
        name, spec = process_receipts.identify(observation)
        if spec.refusal_stage:
            return observation
    return None


def render(state,payload=None):
    receipt = earliest(state)
    if receipt is None: return None
    process_receipts.validate_for_synthesis(receipt)
    item = process_receipts.summary(receipt)
    question = state.get('text') or state.get('envelope', {}).get('symptom')
    if not isinstance(question, str) or not question.strip():
        raise ValueError('Refusal output requires the original question')
    reason = item['text']; stage = item['stage']
    text = ('You asked: ' + question + '\nAnswer to your question: Not answered.\n\n'
            'The investigation stopped during ' + stage + '.\n'
            'Reason: ' + reason + '\n'
            'No explanation of the reported difference was established.\n'
            'Recommended action: Resolve the stated blocker before a new investigation.')
    outputs = {'version': 1, 'provenance': 'DETERMINISTIC_REFUSAL_RENDERING',
               'source_hash': digest(state), 'refusal': copy.deepcopy(item)}
    for key in ('business_output', 'technical_output'):
        from .selection_descriptor import note,render as render_descriptor
        request=state.get('envelope',{}).get('selection_request') or (state.get('proposal') or {}).get('selection_request')
        hint=note(request.get('descriptor')) if request else None
        qualification=render_descriptor(hint,business=key=='business_output') if hint else ''
        rendered=text
        if key=='business_output':
            from .narrative_form import validate
            category=receipt.get('refusal_category')
            plain={'AMBIGUOUS':'More than one possible target remains; the investigation cannot choose between them.',
                   'UNAVAILABLE':'The target check was unavailable, so the requested selection could not be established.',
                   'VALUE_ABSENT':'The stated value was not found in the checked selection.',
                   'UNSUPPORTED':'A declared selection cannot be handled faithfully with the available capability.'}
            business_reason=plain.get(category)
            if business_reason is None:
                try:business_reason=validate(' '.join(reason.split()),business=True)
                except ValueError:business_reason='The required check could not be established. Its detailed blocker is retained in the technical explanation.'
            try:business_question=validate(' '.join(question.split()),business=True)
            except ValueError:business_question='You asked about the reported figure and its selections.'
            rendered=text.replace(question,business_question).replace(reason,business_reason)
            rendered=validate(rendered+('\n'+qualification if qualification else ''),business=True)
        else:rendered+=('\n'+qualification if qualification else '')
        # A refused walk does not erase completed, separately validated cells.
        cells=[]
        from .declared_reproduction import validate as validate_cell_finding
        originals={o['id']:o for o in state.get('observations',[]) if o.get('id')}
        invalid_cells=[]
        for observation in originals.values():
            if observation.get('check_kind')!='DECLARED_CONTEXT_REPRODUCTION':continue
            try:validate_cell_finding(observation,originals)
            except (ValueError,KeyError):invalid_cells.append(observation['id'])
            else:cells.append(observation)
        if invalid_cells:
            rendered+='\nCompleted cell facts could not be validated.'
            if key=='technical_output':rendered+=' Receipts: '+', '.join(invalid_cells)+'.'
        if cells:
            from .declared_reproduction import render as render_cell
            from .reproduction_composition import body,select,action,from_payload,technical_cells,hedges
            display={r['id']:r for r in from_payload(payload or {})}
            cells=[display.get(c['id'],c) for c in cells]
            from .question_account import build,render as render_account
            checked=copy.deepcopy(state)
            checked['observations']=[o for o in state['observations'] if o.get('check_kind')!='DECLARED_CONTEXT_REPRODUCTION' or o['id'] in {c['id'] for c in cells}]
            prefix=render_account(build(checked))
            if key=='business_output':
                from .narrative_form import validate
                rendered=validate(prefix+'\n\n'+body(cells),True)
                if receipt.get('check_kind')=='BUDGET_STOP':rendered+='\nReason: '+reason
            else:
                rendered=prefix+'\n\nWhat else was checked: the vertical walk stopped during '+stage+'.\nReason: '+reason+'.'
                rendered+='\n\nCompleted within-layer cells:\n'+'\n'.join(technical_cells(cells))
                limits=hedges(cells,select(cells))
                rendered+='\nLimits:\n'+'\n'.join('- '+limit for limit in limits)
                rendered+='\nRecommended action: '+action(select(cells))['text']
        outputs[key] = {'explanation': {'text': rendered, 'evidence_ids': [receipt['id']]},
                        'recommended_action': 'Resolve the stated blocker before a new investigation.'}
        if cells:outputs[key]['recommended_action']=action(select(cells))
        if hint:outputs[key]['descriptor_hint']=copy.deepcopy(hint)
        if receipt.get('check_kind')=='PROCESS_FAILED':
            if key=='technical_output':
                failure=receipt['failure']
                outputs[key]['explanation']['text']+='\nDiagnostic: '+failure['error_type']+' at '+failure['module']+':'+str(failure['line'])+'.'
        if receipt.get('check_kind')=='BUDGET_STOP':
            if key=='technical_output':
                outputs[key]['explanation']['text']+='\nAdmission: '+receipt['admission_reason']+'. Sub-budgets: '+', '.join(
                    name+' '+str(receipt['phase_counts'][name])+'/'+str(receipt['phase_limits'][name]) for name in ('WALK','REPRODUCTION'))+'.'
                retained=[o for o in state.get('observations',[]) if o['id']!=receipt['id']]
                outputs[key]['explanation']['text']+='\nCompleted evidence before the stop:\n'+'\n'.join(
                    '- '+str(o.get('tool'))+' '+str(o.get('check_kind') or o.get('status'))+'; receipt '+o['id']+
                    ('; quantity '+str(o['quantity']) if 'quantity' in o else '')+'.' for o in retained)
                outputs[key]['explanation']['text']+='\nChecks not run: '+', '.join(
                    p['operation']+' on '+str(p.get('layer') or p.get('target')) for p in receipt['not_run_probes'])+'.'
    return outputs
