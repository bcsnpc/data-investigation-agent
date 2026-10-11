"""Read workers use pipes, never an editor console or an interactive window."""
import os
import subprocess


def options(kwargs, *, platform=None):
    result = dict(kwargs)
    if (os.name if platform is None else platform) == 'nt':
        # Values are Win32 creation flags, also testable on non-Windows CI.
        no_window = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)
        new_console = getattr(subprocess, 'CREATE_NEW_CONSOLE', 0x00000010)
        detached = getattr(subprocess, 'DETACHED_PROCESS', 0x00000008)
        flags = result.get('creationflags', 0)
        # Explicit caller isolation flags are preserved; Windows ignores
        # CREATE_NO_WINDOW when either of these flags is present.
        if not flags & (new_console | detached):
            result['creationflags'] = flags | no_window
    return result
