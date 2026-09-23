"""Unambiguous local contract repairs; never rewrite executable queries or evidence."""
from . import proposal_limits as limits
import copy


def repair(proposal):
    value = copy.deepcopy(proposal)
    events = []
    if not isinstance(value, dict):
        return value, events

    def bound(container, key, limit, path):
        text = container.get(key)
        if isinstance(text, str) and len(text) > limit:
            container[key] = text[:limit-1]+'…'
            events.append({'repair_kind': 'text_bound', 'field': path,
                           'original_characters': len(text), 'retained_characters': limit,
                           'omitted_characters': len(text)-(limit-1)})

    bound(value, 'question', limits.QUESTION, 'question')
    hypotheses = value.get('hypotheses')
    if isinstance(hypotheses, list):
        unique = []
        for index, hypothesis in enumerate(hypotheses):
            # Conflicting same-ID updates remain invalid. Do not choose which
            # claim or status is true, merge evidence, or invent replacement IDs.
            if isinstance(hypothesis, dict) and any(hypothesis == old for old in unique):
                events.append({'repair_kind': 'hypothesis_id', 'field': 'hypotheses', 'removed_updates': 1})
                continue
            unique.append(hypothesis)
        value['hypotheses'] = unique
        for index, hypothesis in enumerate(unique):
            if isinstance(hypothesis, dict):
                bound(hypothesis, 'claim', limits.HYPOTHESIS_CLAIM, f'hypotheses[{index}].claim')
    assessment = value.get('assessment')
    if isinstance(assessment, dict):
        bound(assessment, 'claim', limits.ASSESSMENT_CLAIM, 'assessment.claim')
        for key in ('alternatives', 'limits'):
            if isinstance(assessment.get(key), list):
                for index, text in enumerate(assessment[key]):
                    holder = {'text': text}
                    bound(holder, 'text', limits.ASSESSMENT_DETAIL, f'assessment.{key}[{index}]')
                    assessment[key][index] = holder['text']
        support = assessment.get('support')
        if isinstance(support, dict):
            for key in ('mechanism', 'intent_basis', 'remaining_test'):
                bound(support, key, limits.ASSESSMENT_DETAIL, 'assessment.support.'+key)
    return value, events


def candidate_with_schema(store, config, state, proposal, observe):
    """Fetch catalog prerequisites once, then recompile under unchanged policy."""
    from .dynamic_reasoning import candidate, MissingSourceContext, lookup
    try:
        return candidate(store, config, state, proposal)
    except MissingSourceContext as exc:
        targets = exc.recovery_assets
        if len(targets) > 16:
            raise ValueError('Schema repair asset limit exceeded') from exc
        for target in targets:
            item = lookup(store, {'operation': 'asset', 'value': target['id']})
            state['observations'].append(item)
            observe(item)
        # Missing, partial, stale or unauthorized metadata still fails admission.
        return candidate(store, config, state, proposal)
