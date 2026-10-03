"""Deterministic refusal delivery; never a model-authored technical verdict."""
import copy
from . import process_receipts
from .onboarding import digest


def earliest(state):
    for observation in state.get('observations', []):
        name, spec = process_receipts.identify(observation)
        if spec.refusal_stage:
            return observation
    return None


def render(state):
    receipt = earliest(state)
    if receipt is None: return None
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
        outputs[key] = {'explanation': {'text': rendered, 'evidence_ids': [receipt['id']]},
                        'recommended_action': 'Resolve the stated blocker before a new investigation.'}
        if hint:outputs[key]['descriptor_hint']=copy.deepcopy(hint)
    return outputs
