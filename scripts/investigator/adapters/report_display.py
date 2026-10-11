"""UI titles retain their own provenance, separate from search aliases."""
from .report_cells import catalog


def install(workspace):
    def display(model_id):
        return {v['target_id']:v['display_names'] for v in catalog(workspace.store.get(model_id),include_display_names=True)}
    workspace.visual_display_names=display
