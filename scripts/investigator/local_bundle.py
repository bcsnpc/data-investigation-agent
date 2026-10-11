"""Immutable exported fixture quantities, with explicit local execution identity.

Only typed additive quantities are evaluated. No query text, native engine
claims, authentication, seeded-data recreation, or network fallback exists.
"""
import hashlib
import json
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from decimal import Decimal, localcontext
from .onboarding import Conflict, digest

VERSION = 'local-fixture-export-v1'

class UnsupportedLocalQuantity(Conflict): pass

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()

def quote(value):
    return '"' + value.replace('"', '""') + '"'

class LocalBundle:
    def __init__(self, path, manifest_sha256):
        self.path = Path(path).resolve(); self.manifest_file = self.path / 'manifest.json'
        if sha(self.manifest_file) != manifest_sha256: raise Conflict('LOCAL_MANIFEST_HASH_MISMATCH')
        self.manifest_sha256 = manifest_sha256
        self.manifest = json.loads(self.manifest_file.read_text(encoding='utf-8'))
        if self.manifest.get('version') != VERSION or self.manifest.get('engine') != 'SQLITE_LOCAL_COPY' or self.manifest.get('status') != 'COMPLETE':
            raise Conflict('LOCAL_EXPORT_CONTRACT_UNSUPPORTED')
        if self.manifest.get('tape_class') != 'EXACT':
            raise UnsupportedLocalQuantity('Projected value computation needs a tested projection-aware local contract')
        database = self.manifest['database']
        if database['file'] != 'data.sqlite': raise Conflict('LOCAL_DATABASE_PATH_UNSUPPORTED')
        self.database = self.path / database['file']; self.database_sha256 = database['sha256']
        rows = self.manifest['assets']
        self.assets = {a['asset_id']: a for a in rows}
        if len(self.assets) != len(rows): raise Conflict('LOCAL_DUPLICATE_ASSET')
        self.definitions = []
        for definition in self.manifest.get('definitions', []):
            file = self.path / definition['file']
            if file.resolve().parent != self.path or not re.fullmatch(r'definition-[0-9]{4}\.txt', file.name):
                raise Conflict('LOCAL_DEFINITION_PATH_UNSUPPORTED')
            self.definitions.append((file, definition['sha256']))
        self._verify()
        with self.connect() as db:
            for asset in rows:
                if not re.fullmatch(r't[0-9]{4}', asset['table']): raise Conflict('LOCAL_TABLE_BINDING_INVALID')
                schema = db.execute('PRAGMA table_info(' + quote(asset['table']) + ')').fetchall()
                types = {'INTEGER': 'INTEGER', 'BOOLEAN': 'INTEGER', 'REAL': 'REAL', 'TEXT': 'TEXT',
                         'DECIMAL': 'TEXT', 'DATE': 'TEXT', 'DATETIME': 'TEXT', 'BINARY': 'BLOB'}
                if ([r[1] for r in schema] != [c['name'] for c in asset['columns']]
                    or [r[2].upper() for r in schema] != [types.get(c['logical_type']) for c in asset['columns']]):
                    raise Conflict('LOCAL_EXPORTED_COLUMNS_DIFFER')
                if db.execute('SELECT COUNT(*) FROM ' + quote(asset['table'])).fetchone()[0] != asset['rows']:
                    raise Conflict('LOCAL_EXPORTED_ROW_COUNT_DIFFERS')
        self._verify()

    def _verify(self):
        if sha(self.manifest_file) != self.manifest_sha256 or sha(self.database) != self.database_sha256:
            raise Conflict('LOCAL_EXPORT_CHANGED')
        if any(sha(file) != expected for file, expected in self.definitions):
            raise Conflict('LOCAL_DEFINITION_HASH_MISMATCH')
        for suffix in ('-wal', '-journal'):
            sibling = Path(str(self.database) + suffix)
            if sibling.exists() and sibling.stat().st_size:
                raise Conflict('LOCAL_EXPORT_IS_NOT_IMMUTABLE_SINGLE_FILE')

    @contextmanager
    def connect(self):
        self._verify()
        db = sqlite3.connect(self.database.as_uri() + '?mode=ro&immutable=1', uri=True)
        db.execute('PRAGMA query_only=ON')
        try:
            yield db
        finally:
            db.close()

    def quantity(self, asset_id, column, restrictions=()):
        self._verify()
        asset = self.assets.get(asset_id)
        if asset is None: raise UnsupportedLocalQuantity('Asset not present in local export: ' + asset_id)
        byname = {c['name']: c for c in asset['columns']}
        if column not in byname: raise UnsupportedLocalQuantity('No exact exported quantity column: ' + column)
        if byname[column]['logical_type'] not in ('INTEGER', 'DECIMAL'):
            raise UnsupportedLocalQuantity('Only exact INTEGER or DECIMAL additive SUM is supported locally')
        for r in restrictions:
            if set(r) != {'column', 'operator', 'values'} or r['column'] not in byname or r['operator'] != 'IN':
                raise UnsupportedLocalQuantity('Unsupported or unbound local restriction')
            if byname[r['column']]['logical_type'] not in ('INTEGER', 'BOOLEAN', 'DATE', 'DATETIME'):
                raise UnsupportedLocalQuantity('Native string/collation semantics are not established locally')
            if not isinstance(r['values'], list): raise UnsupportedLocalQuantity('Restriction values must be explicit')
            expected = {'INTEGER': int, 'BOOLEAN': bool, 'DATE': str, 'DATETIME': str}[byname[r['column']]['logical_type']]
            if any(type(v) is not expected for v in r['values']):
                raise UnsupportedLocalQuantity('Restriction value type differs from exported column')
        with self.connect() as db:
            columns = [column, *dict.fromkeys(r['column'] for r in restrictions if r['column'] != column)]
            rows = db.execute('SELECT ' + ','.join(quote(c) for c in columns) + ' FROM ' + quote(asset['table'])).fetchall()
        total = None
        with localcontext() as ctx:
            ctx.prec = 256
            for row in rows:
                mapped = dict(zip(columns, row))
                if any(mapped[r['column']] not in r['values'] for r in restrictions): continue
                value = mapped[column]
                if value is None: continue
                if byname[column]['logical_type'] == 'INTEGER' and type(value) is not int:
                    raise Conflict('LOCAL_INTEGER_VALUE_TYPE_DIFFERS')
                if byname[column]['logical_type'] == 'DECIMAL' and not isinstance(value, str):
                    raise Conflict('LOCAL_DECIMAL_VALUE_TYPE_DIFFERS')
                number = Decimal(value)
                if not number.is_finite(): raise Conflict('LOCAL_NONFINITE_QUANTITY')
                if len(number.as_tuple().digits) > 100 or abs(number.as_tuple().exponent) > 100:
                    raise UnsupportedLocalQuantity('Local decimal exceeds exact arithmetic bound')
                total = number if total is None else total + number
        self._verify()
        return {'value': None if total is None else format(total, 'f'),
            'plan': {'asset_id': asset_id, 'column': column, 'restrictions': list(restrictions)},
            'bundle_manifest_sha256': self.manifest_sha256, 'database_sha256': self.database_sha256,
            'native_export_receipt': asset['receipt'], 'snapshot_alignment': 'SNAPSHOT_UNVERIFIED',
            'execution_mode': 'LOCAL_EXPORTED'}
