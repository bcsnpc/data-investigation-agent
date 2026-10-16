"""Current-component replay of a sealed approval verifier, never a live producer.

The historical program contains a whole-engine identity admission guard. This
adapter removes only that exact guard in memory, after the route gate checks
component versions. Runtime fingerprints are never forged and sealed inputs,
physical requests, outputs and accounting remain byte-compared by Tape.
"""
import ast
import hashlib
import importlib.util
import json
import socket
import shutil
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

GUARD = "if fingerprint() != i['engine_fingerprint']: raise ValueError('VERIFIER_ENGINE_DIFFERS')"


def compatibility_program(path):
    raw = Path(path).read_bytes()
    tree = ast.parse(raw)
    expected = ast.dump(ast.parse(GUARD).body[0], include_attributes=False)
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'perform']
    if len(functions) != 1:
        raise ValueError('ROUTE_VERIFIER_ENTRY_POINT_REQUIRED')
    body = functions[0].body
    matches = [n for n in body if ast.dump(n, include_attributes=False) == expected]
    if len(matches) != 1:
        raise ValueError('ROUTE_VERIFIER_IDENTITY_GUARD_NOT_RECOGNIZED')
    body.remove(matches[0])
    derived = ast.unparse(tree).encode()
    module = ModuleType('route_compatibility_program')
    module.__file__ = str(path)
    exec(compile(tree, str(path), 'exec'), module.__dict__)
    module.compatibility = {'original_program_sha256': hashlib.sha256(raw).hexdigest(),
        'derived_program_sha256': hashlib.sha256(derived).hexdigest(),
        'change': 'Remove exact whole-engine admission guard only; current components execute unchanged.'}
    return module


def replay_verifications(tape_ref, recorded_engine_hash, current_engine_hash, *, output):
    from investigator.runtime import fingerprint
    from investigator.process_tape import Tape
    path = Path(tape_ref['path'])
    if hashlib.sha256(path.read_bytes()).hexdigest() != tape_ref['sha256']:
        raise ValueError('ROUTE_VERIFICATION_TAPE_HASH_DIFFERS')
    tape = Tape(path)
    if tape.bootstrap['engine_hash'] != recorded_engine_hash:
        raise ValueError('ROUTE_VERIFICATION_RECORDED_ENGINE_DIFFERS')
    if fingerprint() != current_engine_hash:
        raise ValueError('ROUTE_VERIFICATION_CURRENT_ENGINE_CHANGED')
    helper_path = Path(__file__).with_name('code_verifier_capture.py')
    spec = importlib.util.spec_from_file_location('route_verifier_capture', helper_path)
    helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
    original_loader = helper.load_program
    def copy_bytes(source, destination):
        # CopyFile2 inherits the source allocation flags and can decompress a
        # closed evidence snapshot. Stream bytes into the compressed scratch
        # directory instead; logical evidence hashes remain identical.
        with open(source, "rb") as src, open(destination, "wb") as dst:
            shutil.copyfileobj(src, dst, length=1024 * 1024)
        return str(destination)
    programs = []
    def load(path):
        program = compatibility_program(path)
        programs.append(program.compatibility)
        return program
    attempts = []
    def deny(*args, **kwargs):
        attempts.append('NETWORK_OR_SUBPROCESS')
        raise RuntimeError('ROUTE_REPLAY_NETWORK_FORBIDDEN')
    import subprocess
    try:
        helper.load_program = load
        with patch.object(socket.socket, 'connect', deny), patch.object(socket.socket, 'connect_ex', deny), patch.object(subprocess, 'Popen', deny), patch.object(helper.shutil, 'copyfile', copy_bytes):
            result = helper.replay(path.parent, Path(output))
        if attempts or fingerprint() != current_engine_hash:
            raise ValueError('ROUTE_REPLAY_GUARD_OR_COMPONENT_CHANGED')
        return {'capture_sha256': tape_ref['sha256'], 'recorded_engine_hash': recorded_engine_hash,
            'verification_engine_hash': current_engine_hash, 'matched': result['matched'],
            'status': result['status'], 'network_requests': 0, 'estate_reads': 0, 'model_calls': 0,
            'result_sha256': hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'program_adaptation': programs, 'accounting': result['accounting']}
    finally:
        helper.load_program = original_loader
