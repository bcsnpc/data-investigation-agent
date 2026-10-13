"""Portable lexical command descriptors for historical replay, never I/O bypass."""
from contextlib import contextmanager
from pathlib import PurePosixPath, PureWindowsPath
import re
from unittest.mock import patch


def portable_command(command):
    result = [str(item) for item in command]
    for index, value in enumerate(result):
        # A recorded Windows path keeps Windows lexical meaning on Linux.
        # Configuration-file operands remain actual local paths for content read.
        if index and result[index - 1] == '--config':
            continue
        path = PureWindowsPath(value) if re.match(r'^[A-Za-z]:[\\/]|^\\\\', value) else PurePosixPath(value)
        if index == 0 and re.fullmatch(r'python(?:\d(?:\.\d+)?)?(?:\.exe)?', path.name.casefold()):
            result[index] = 'python'
        elif value.endswith(('.py', '.ps1')):
            result[index] = path.name
    return result


@contextmanager
def install(journal):
    from investigator import tape_worker
    original = tape_worker.descriptor
    def descriptor(command):
        active = journal.ACTIVE.get()
        if active is not None and active.replaying:
            command = portable_command(command)
        return original(command)
    with patch.object(tape_worker, 'descriptor', descriptor):
        yield
