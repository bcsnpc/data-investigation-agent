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


def validate_inputs(journal, tape):
    """Admit hash-pinned local metadata before replaying any operation.

    These bytes are inputs to the original reader, not bounded responses. A
    missing sidecar must not first surface as a later cleanup CLOCK mismatch.
    The sealed tape and its config are never rewritten or supplemented here.
    """
    from pathlib import Path
    import hashlib
    pin = tape.bootstrap.get('config', {}).get('fabric', {}).get('retained_endpoints')
    if pin is None:return
    from investigator.adapters.retained_endpoints import validate
    validate(pin)
    path = Path(pin['receipt_path'])
    if not path.is_file():
        raise journal.TapeError('REPLAY_RETAINED_ENDPOINT_INPUT_MISSING:' + str(path))
    with path.open('rb') as stream:
        actual = hashlib.file_digest(stream, 'sha256').hexdigest()
    if actual != pin['receipt_sha256']:
        raise journal.TapeError('REPLAY_RETAINED_ENDPOINT_INPUT_HASH_DIFFERS:' + str(path))


@contextmanager
def first_tape_error(journal, diagnostics):
    """Observe the original event or direct-value mismatch without changing it."""
    import base64
    import traceback
    original_event, original_take = journal.Tape.event, journal.Tape.take
    event_depth = 0
    def record(self, kind, index, expected, error, body=None):
        if diagnostics:return
        detail = {'error_type': type(error).__name__, 'reason': str(error),
                  'requested_kind': kind, 'index_before': index, 'index_after': self.index,
                  'recorded_kind': expected['kind'] if expected else None,
                  'traceback': traceback.format_exc()}
        if kind == 'WORKER_START':
            detail['actual_body_base64'] = base64.b64encode(body or b'').decode()
            detail['recorded_body_base64'] = expected.get('body') if expected else None
        diagnostics.append(detail)
    def event(self, kind, body=None):
        nonlocal event_depth
        index = self.index
        expected = self.events[index] if index < len(self.events) else None
        event_depth += 1
        try:return original_event(self, kind, body)
        except journal.TapeError as error:
            record(self, kind, index, expected, error, body)
            raise
        finally:event_depth -= 1
    def take(self, kind):
        index = self.index
        expected = self.events[index] if index < len(self.events) else None
        try:return original_take(self, kind)
        except journal.TapeError as error:
            if not event_depth:record(self, kind, index, expected, error)
            raise
    with patch.object(journal.Tape, 'event', event), patch.object(journal.Tape, 'take', take):
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
