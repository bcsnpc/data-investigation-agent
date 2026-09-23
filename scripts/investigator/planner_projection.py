"""Deterministic context fitting; omitted context is not a removed catalog asset."""
import copy
from .onboarding import encoded


def omitted_values(original, projected):
    """Count excluded fields/items, including nested asset/schema metadata."""
    if isinstance(original, dict) and isinstance(projected, dict):
        return sum(1 if key not in projected else omitted_values(value, projected[key])
                   for key, value in original.items())
    if isinstance(original, list) and isinstance(projected, list):
        if original and all(isinstance(item, dict) and 'id' in item for item in original + projected):
            by_id = {item['id']: item for item in projected}
            return sum(1 if item['id'] not in by_id else omitted_values(item, by_id[item['id']])
                       for item in original)
        return max(0, len(original)-len(projected)) + sum(
            omitted_values(left, right) for left, right in zip(original, projected))
    return int(original != projected)


def content_projection(metadata, original, retained):
    metadata.update(planner_content_truncated=retained < original,
                    retained_end_offset=metadata.get('offset', 0) + retained,
                    planner_content_projection={
                        'status': 'RETAINED' if retained == original else 'OMITTED' if retained == 0 else 'TRUNCATED',
                        'retrieved_characters': original, 'retained_characters': retained,
                        'omitted_characters': original - retained,
                        'reason': 'PLANNER_CONTEXT_LIMIT', 'catalog_removal': False})


def fit(payload, ceiling):
    """Fit the projected input, preserving scope, receipts, schema and tool authority.

    Directory tails and older action descriptions precede source excerpts. If the
    protected minimum cannot fit, return an explicit over-limit view for the
    existing runtime admission check to hold without dispatch.
    """
    before = len(encoded(payload))
    if before <= ceiling:
        return payload
    result = copy.deepcopy(payload)
    audit = {'input_characters_before': before, 'ceiling': ceiling,
             'status': 'TRUNCATED', 'catalog_removal': False, 'omissions': {}}
    result['planner_projection'] = audit

    def oversized():
        return len(encoded(result)) > ceiling

    for field in ('context_entry_points', 'action_history', 'context'):
        entries = result.get(field, [])
        while entries and oversized():
            indexes = [i for i, entry in enumerate(entries)
                       if field != 'context' or entry.get('id') != result.get('starting_measure_id')]
            if not indexes:
                break
            index = indexes[0] if field == 'action_history' else indexes[-1]
            entries.pop(index)
            audit['omissions'][field] = audit['omissions'].get(field, 0) + 1
            if field == 'context':
                result['context_truncated'] = True
            if field == 'context_entry_points':
                result['context_directory_truncated'] = True
    for observation in result.get('observations', []):
        metadata = observation.get('metadata', {})
        content = metadata.get('content')
        if observation.get('tool') != 'context' or not isinstance(content, str):
            continue
        original = metadata.get('planner_content_projection', {}).get('retrieved_characters', len(content))
        while content and oversized():
            # Chunked halving is stable, bounded and does not need a model decision.
            content = content[:len(content)//2]
            metadata['content'] = content
            content_projection(metadata, original, len(content))
            observation['planner_sample_truncated'] = True
            audit['omissions']['content_characters'] = sum(
                o.get('metadata', {}).get('planner_content_projection', {}).get('omitted_characters', 0)
                for o in result.get('observations', []))
    if oversized():
        audit['status'] = 'PROTECTED_CONTEXT_EXCEEDS_LIMIT'
    return result
