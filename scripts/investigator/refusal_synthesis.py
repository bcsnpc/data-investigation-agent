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
        outputs[key] = {'explanation': {'text': text, 'evidence_ids': [receipt['id']]},
                        'recommended_action': 'Resolve the stated blocker before a new investigation.'}
    return outputs
