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


@contextmanager
def first_tape_error(journal, diagnostics):
    """Retain the original mismatch even if engine recovery masks it later.

    Only the separate private replay diagnostics receive these bytes. This is
    observation, not normalization: the original exception is always re-raised.
    """
    import base64
    import traceback
    original = journal.Tape.event
    def event(self, kind, body=None):
        index = self.index
        expected = self.events[index] if index < len(self.events) else None
        try:
            return original(self, kind, body)
        except journal.TapeError as error:
            if not diagnostics:
                detail = {'error_type': type(error).__name__, 'reason': str(error),
                          'requested_kind': kind, 'index_before': index, 'index_after': self.index,
                          'recorded_kind': expected['kind'] if expected else None,
                          'traceback': traceback.format_exc()}
                if kind == 'WORKER_START':
                    detail['actual_body_base64'] = base64.b64encode(body or b'').decode()
                    detail['recorded_body_base64'] = expected.get('body') if expected else None
                diagnostics.append(detail)
            raise
    with patch.object(journal.Tape, 'event', event):
        yield


class _ReplayConfigRoot:
    """Sealed absolute config paths retain their original platform semantics."""
    def __init__(self, root):
        self.root = root

    def __truediv__(self, value):
        class Absolute:
            def __init__(self,normalized):self.normalized=normalized
            def resolve(self):return self.normalized
            def __str__(self):return self.normalized
        windows = PureWindowsPath(value)
        if windows.is_absolute():
            import ntpath
            return Absolute(ntpath.normpath(str(value)))
        if windows.drive:
            raise ValueError('REPLAY_WINDOWS_DRIVE_RELATIVE_PATH_UNSUPPORTED')
        if PurePosixPath(value).is_absolute():
            import posixpath
            return Absolute(posixpath.normpath(str(value)))
        return self.root / value


@contextmanager
def configuration_paths(journal):
    """Correct historical config path interpretation, only during replay.

    The original validator still checks every field. Its repository root gets
    Windows lexical absolute-path semantics only for the duration of that call.
    Relative and native absolute paths retain the original host resolution.
    No tape/expected byte is read to decide or modify a configuration value.
    """
    import metadata_config
    root = metadata_config.ROOT
    original = getattr(metadata_config,'validate_config',None)
    if original is None:
        # Older pinned engines validate inline in load_config. Other historical
        # modules may already hold aliases to that function, so replacing the
        # loader would miss them. Preserve the exact function and its checks;
        # adapt only its module-global path root while an active tape replays.
        if not callable(getattr(metadata_config,'load_config',None)):
            raise ValueError('REPLAY_CONFIGURATION_ENTRY_POINT_UNSUPPORTED')
        class HistoricalRoot:
            def __truediv__(self,value):
                active=journal.ACTIVE.get()
                return (_ReplayConfigRoot(root) if active is not None and active.replaying else root)/value
            def __getattr__(self,name):return getattr(root,name)
        with patch.object(metadata_config,'ROOT',HistoricalRoot()):yield
        return
    def validate(config):
        active = journal.ACTIVE.get()
        if active is None or not active.replaying:
            return original(config)
        with patch.object(metadata_config, 'ROOT', _ReplayConfigRoot(root)):
            return original(config)
    with patch.object(metadata_config, 'validate_config', validate):
        yield
