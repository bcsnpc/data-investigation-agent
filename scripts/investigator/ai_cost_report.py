"""Actual normalized provider usage, grouped by AI step and model."""
from collections import defaultdict


def summarize(events):
    groups = defaultdict(list)
    for event in events:
        if event.get('event') == 'AI_NORMALIZED_USAGE':
            groups[(event['step'], event['provider'], event['model'])].append(event)
    rows = []
    for (step, provider, model), calls in sorted(groups.items()):
        total = sum(c['normalized_usage']['input_tokens'] for c in calls)
        cached = sum(c['normalized_usage']['cached_input_tokens'] for c in calls)
        cost = sum(c['cost_microdollars'] for c in calls)
        rows.append({'step':step, 'provider':provider, 'model':model, 'calls':len(calls),
            'actual_microdollars':cost, 'mean_microdollars_per_call':cost / len(calls),
            'input_tokens':total, 'cached_input_tokens':cached,
            'cache_read_ratio':cached / total if total else 0,
            'calls_detail':[{'actual_microdollars':c['cost_microdollars'],
                            'usage':c['normalized_usage']} for c in calls]})
    return rows
