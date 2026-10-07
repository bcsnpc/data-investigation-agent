"""Observe procedure stages without choosing a route or collecting new evidence."""
from functools import wraps

METHODS = {
    'resolve_path':'context', 'declared_context':'reproduce', 'declared_cells':'reproduce',
    'evaluate_declared_context':'reproduce', 'observe_selection_value':'reproduce',
    'evaluate':'walk', 'direct_source_comparison':'walk', 'presentation_context':'walk',
    'presentation_freshness':'walk', 'transformation_definition':'walk',
    'failure_detail':'walk', 'refresh_timing':'walk', 'snapshot_identity':'walk',
    'job_history':'source', 'ingestion':'source', 'source_delivery':'source', 'record_presence':'source',
}
LABELS = {'intake':'Interpreting the ticket', 'context':'Resolving declared context',
          'reproduce':'Checking declared report context', 'walk':'Comparing the declared path',
          'source':'Checking source and load evidence', 'compose':'Composing the explanations'}


class Adapter:
    """Delegate unchanged arguments/results; persist START before entering a call.

    Application evaluation is source work only where the estate declares that
    role. Native method names select stage attribution, never investigation logic.
    """
    def __init__(self, adapter, record):
        object.__setattr__(self, '_adapter', adapter)
        object.__setattr__(self, '_record', record)

    def __setattr__(self, key, value): setattr(self._adapter, key, value)

    def __getattr__(self, key):
        value = getattr(self._adapter, key)
        if key not in METHODS or not callable(value): return value
        @wraps(value)
        def invoke(*args, **kwargs):
            stage = METHODS[key]
            if key == 'evaluate' and args and isinstance(args[0], dict):
                layer = args[0].get('id')
                estate = getattr(self._adapter, 'config', {}).get('_estate', {})
                if any(l.get('asset_id') == layer and l.get('role') == 'APPLICATION' for l in estate.get('layers', [])):
                    stage = 'source'
            self._record('PROCESS_STAGE_STARTED', {'stage':stage, 'operation':key})
            error = None
            try: return value(*args, **kwargs)
            except BaseException as exc:
                error = type(exc).__name__
                raise
            finally:
                self._record('PROCESS_STAGE_FINISHED', {'stage':stage, 'operation':key, 'error_type':error})
        return invoke


def label(event):
    detail = event.get('detail') or {}
    if event['kind'] not in ('PROCESS_STAGE_STARTED','PROCESS_STAGE_FINISHED'): return None
    stage = detail.get('stage')
    if stage not in LABELS: raise ValueError('Unrecognized recorded process stage')
    suffix = ' started' if event['kind'].endswith('STARTED') else ' failed' if detail.get('error_type') else ' finished'
    return LABELS[stage] + suffix
