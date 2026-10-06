"""Explicit local retention, with a durable deletion audit and conservative dates.

Never operates on a release bundle or external path. Missing dates, unfinished
tapes and unfamiliar sidecars are kept and named. Default is indefinite.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import os
from .estate_manifest import RETENTION
from jsonschema import Draft202012Validator

DEFAULT = {'tape_days': 'indefinite', 'ledger_days': 'indefinite'}


def owned(path, root):
    original = Path(path)
    resolved = original.resolve()
    root = Path(root).resolve()
    if resolved == root or root not in resolved.parents:
        raise ValueError('Retention target must be strictly inside the declared local root')
    if original.is_symlink(): raise ValueError('Retention refuses symbolic-link targets')
    return resolved


def timestamp(row):
    text = next((row.get(k) for k in ('at', 'date_utc', 'date') if row.get(k)), None)
    if not isinstance(text, str): return None
    try:
        value = datetime.fromisoformat(text.replace('Z', '+00:00'))
        return value.timestamp() if value.tzinfo is not None else None
    except ValueError: return None


def plan(policy, *, root, tapes, ledger, now):
    Draft202012Validator(RETENTION).validate(policy)
    if type(now) not in (float, int): raise ValueError('Retention requires an explicit clock')
    tapes = owned(tapes, root); ledger = owned(ledger, root)
    result = {'policy': policy, 'at_epoch': now, 'delete_files': [], 'expired_ledger_rows': [],
              'keep_ledger_lines': [], 'kept': [], 'ledger_path': str(ledger)}
    if policy['tape_days'] != 'indefinite':
        from .process_tape import Tape
        for path in sorted(tapes.glob('*/tape.json')):
            try:
                path = owned(path, root); tape = Tape(path)
                last = tape.events[-1]
                if last['kind'] != 'FINAL': raise ValueError('Unfinished tape')
                if last['at'] >= now - policy['tape_days'] * 86400: continue
                expected = {'tape.json', 'tape.events.jsonl', 'catalog.sqlite', 'inventory.sqlite'}
                actual = {p.name for p in path.parent.iterdir()}
                if actual - expected: raise ValueError('Unfamiliar tape sidecars')
                members = []
                for member in sorted(path.parent.iterdir()):
                    member = owned(member, root)
                    if not member.is_file(): raise ValueError('Tape sidecar is not a file')
                    members.append({'path': str(member), 'sha256': hashlib.sha256(member.read_bytes()).hexdigest()})
                result['delete_files'].extend(members)
            except (ValueError, OSError) as exc:
                result['kept'].append({'path': str(path), 'reason': str(exc)})
    if ledger.exists():
        for index, line in enumerate(ledger.read_bytes().splitlines(keepends=True)):
            try: row = json.loads(line)
            except (ValueError, UnicodeError): row = {}
            at = timestamp(row)
            expired = policy['ledger_days'] != 'indefinite' and at is not None and at < now - policy['ledger_days'] * 86400
            if expired:
                result['expired_ledger_rows'].append({'line': index + 1, 'sha256': hashlib.sha256(line).hexdigest()})
            else: result['keep_ledger_lines'].append(line)
        result['ledger_sha256'] = hashlib.sha256(ledger.read_bytes()).hexdigest()
    return result


def summary(planned):
    return {k:v for k,v in planned.items() if k != 'keep_ledger_lines'}


def apply(planned, *, root, audit):
    """Recheck every byte before recording authorization and deleting any file."""
    audit = owned(audit, root); ledger = owned(planned['ledger_path'], root)
    targets = [(owned(r['path'], root), r['sha256']) for r in planned['delete_files']]
    if audit == ledger or any(p == audit or p == ledger for p, _ in targets):
        raise ValueError('Retention audit, ledger and tapes must be separate')
    for path, digest in targets:
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('Retention target changed after planning')
    if ledger.exists() and hashlib.sha256(ledger.read_bytes()).hexdigest() != planned['ledger_sha256']:
        raise ValueError('Ledger changed after planning')
    audit.parent.mkdir(parents=True, exist_ok=True)
    def record(status, **fields):
        with audit.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps({'at': datetime.now(timezone.utc).isoformat(), 'operation': 'RETENTION',
                                    'status': status, **fields}, sort_keys=True) + '\n')
            stream.flush(); os.fsync(stream.fileno())
    record('PLANNED', plan=summary(planned))
    for path, digest in targets:
        try: path.unlink()
        except OSError as exc:
            record('FAILED', path=str(path), error=str(exc)); raise
        record('DELETED', path=str(path), sha256=digest)
    if planned['expired_ledger_rows']:
        temporary = ledger.with_name(ledger.name + '.retention-pending')
        with temporary.open('xb') as stream:
            stream.write(b''.join(planned['keep_ledger_lines'])); stream.flush(); os.fsync(stream.fileno())
        temporary.replace(ledger)
        record('LEDGER_EXPIRED', rows=planned['expired_ledger_rows'])
    record('COMPLETED', files=len(targets), ledger_rows=len(planned['expired_ledger_rows']))
