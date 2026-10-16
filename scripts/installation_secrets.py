"""Owner-selected existing secret mechanism for an isolated local worktree.

The override changes location only; identity/scope checks remain in each reader.
No file or folder is created, and no fallback to a different account occurs.
"""
import os
from pathlib import Path


def root(default):
    value=os.environ.get('INVESTIGATOR_EXISTING_SECRET_ROOT')
    if value is None:return Path(default)
    selected=Path(value)
    if not selected.is_absolute() or not (selected/'.local').is_dir():
        raise ValueError('EXISTING_SECRET_ROOT_REQUIRED')
    return selected.resolve()
