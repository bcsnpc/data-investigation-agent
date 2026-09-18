"""Independent model metadata with compatibility for retained report-owned contexts."""


def assets(context):
    context = context or {}
    if 'model_assets' in context:
        return context['model_assets']
    reports = context.get('reports') or []
    return reports[0]['model_assets'] if reports else []
