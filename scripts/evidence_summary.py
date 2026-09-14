"""Render saved observations and gates without generating new factual claims."""


def summarize(item):
    result = item['result']
    rows = []
    source = item['request'].get('observations', {})
    for metric, observations in (source.items() if isinstance(source, dict) else []):
        for index, observation in enumerate(observations):
            rows.append({'metric': metric, 'layer': observation['layer'], 'status': observation['status'],
                         'value': observation.get('data') if observation['status'] == 'AVAILABLE' else None,
                         'currency': observation.get('currency'), 'filters': observation.get('filters'),
                         'reference': '/request/observations/' + metric + '/' + str(index)})
    boundaries = []
    for index, check in enumerate(result.get('checks', [])):
        boundaries.append({'metric': None, 'status': check['status'], 'reference': '/result/checks/' + str(index)})
    for metric, entry in result.get('metrics', {}).items():
        for index, boundary in enumerate(entry.get('boundaries', [])):
            boundaries.append({'metric': metric, 'status': boundary['status'],
                               'reference': '/result/metrics/' + metric + '/boundaries/' + str(index)})
    statuses = sorted({b['status'] for b in boundaries})
    unavailable = sorted({r['layer'] for r in rows if r['status'] != 'AVAILABLE'})
    text = [f"Recorded classification: {item['classification']}."]
    if unavailable:
        text.append('Evidence is unavailable or incomplete for: ' + ', '.join(unavailable) + '.')
    if 'NOT_COMPARABLE' in statuses:
        text.append('Some boundaries are NOT_COMPARABLE; observed values do not establish a comparable snapshot.')
    if 'INSUFFICIENT_EVIDENCE' in statuses:
        text.append('Some boundaries have INSUFFICIENT_EVIDENCE; their evidence gates remain blocked.')
    text.append('The saved result records a verified cause within its stated scope; defect routing is not authorized.' if result.get('root_cause_verified') is True else 'This summary describes saved evidence and does not establish a root cause or authorize defect routing.')
    return {'version': 'evidence-summary-v1', 'investigation_id': item['id'],
            'classification': item['classification'], 'text': ' '.join(text),
            'observations': rows, 'boundaries': boundaries, 'automatic_defect_routing': False,
            'evidence_url': '/api/investigations/' + item['id']}
