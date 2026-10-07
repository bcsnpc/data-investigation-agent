"""Capture-time privacy projection; keys and unprojected values stay in memory.

Column identities are exact adapter-resolved identities, never basenames. This
codec does not make an unlabelled payload safe: producers must supply structured
column/value evidence before a value may occur in prose or a query.
"""
import base64
import hashlib
import hmac
import json
import re
from .provider_tape_contract import parse

EXACT = 'EXACT'
PROJECTED = 'PRIVACY_PROJECTED'
VERSION = 'estate-privacy-projection-v1'
TOKEN = re.compile(r'privacy_v1_[0-9a-f]{64}\Z')


class ProjectionError(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf8')


def declaration(value):
    if not isinstance(value, dict):
        raise ProjectionError('PRIVACY_DECLARATION_FIELDS')
    if value == {'tape_class': EXACT}:
        return dict(value)
    if (set(value) != {'tape_class', 'version', 'estate_id', 'key_reference', 'columns'}
            or value['tape_class'] != PROJECTED or value['version'] != VERSION
            or any(not isinstance(value[k], str) or not value[k].strip()
                   for k in ('estate_id', 'key_reference'))
            or not isinstance(value['columns'], list) or not value['columns']
            or any(not isinstance(c, str) or not c.strip() for c in value['columns'])
            or value['columns'] != sorted(set(value['columns']))):
        raise ProjectionError('PRIVACY_DECLARATION_FIELDS')
    return json.loads(canonical(value))


class Projection:
    def __init__(self, policy, secret_store):
        self.policy = declaration(policy)
        if self.policy['tape_class'] != PROJECTED:
            raise ProjectionError('PRIVACY_PROJECTOR_REQUIRES_PROJECTED_ESTATE')
        # The resolver returns bytes in memory. Neither its result nor a hash
        # of an unkeyed sensitive value is part of the capture contract.
        self._key = secret_store(self.policy['key_reference'])
        if not isinstance(self._key, bytes) or len(self._key) < 32:
            raise ProjectionError('PRIVACY_KEY_REQUIRES_256_BITS')
        self.policy_hash = hashlib.sha256(canonical(self.policy)).hexdigest()
        self.key_binding = hmac.new(self._key, canonical({
            'purpose': 'privacy-key-binding', 'estate': self.policy['estate_id'],
            'policy': self.policy_hash}), hashlib.sha256).hexdigest()
        self._values = {}
        self._issued = set()
        self._identity_values = {}
        self._spans = {}
        self._projected_spans = {}

    def descriptor(self):
        return {'tape_class': PROJECTED, 'comparison': 'EXACT_AFTER_PROJECTION',
                'policy': self.policy, 'policy_hash': self.policy_hash,
                'key_binding': self.key_binding}

    def require_descriptor(self, value):
        if value != self.descriptor():
            raise ProjectionError('PRIVACY_POLICY_OR_KEY_CHANGED_RE_RECORD_REQUIRED')

    def sign(self, value):
        return hmac.new(self._key, canonical({'purpose':'privacy-tape-seal',
            'estate':self.policy['estate_id'],'value':value}),hashlib.sha256).hexdigest()

    def key_set(self, columns, keys, normalization):
        """Hash projected, typed key tuples, never a raw sensitive key digest.

        This is a producer boundary: exact resolved identities accompany every
        tuple. A precomputed raw digest cannot be repaired by replacing prose.
        The shared verifier still owns uniqueness and normalization validation.
        """
        if (not isinstance(columns,list) or not columns
                or any(not isinstance(c,str) or not c for c in columns)
                or len(columns)!=len(set(columns))):
            raise ProjectionError('PRIVACY_UNRESOLVED_COLUMN_IDENTITY')
        if not isinstance(keys,list):
            raise ProjectionError('PRIVACY_ROW_SHAPE')
        projected=[]
        for key in keys:
            if not isinstance(key,list) or len(key)!=len(columns):
                raise ProjectionError('PRIVACY_ROW_WIDTH')
            projected.append([self.bind(column,value) for column,value in zip(columns,key)])
        from .translation_proposer import key_fingerprint
        return {'columns':list(columns),'keys':projected,
                **key_fingerprint(projected,normalization)}

    def register_span(self,ticket,source):
        identity=canonical(source)
        if identity not in self._spans:self._spans[identity]=[]
        if ticket not in self._spans[identity]:self._spans[identity].append(ticket)

    def prepare_spans(self):
        for identity,tickets in self._spans.items():
            source=parse(identity);candidates=[]
            for ticket in tickets:
                quote=self._text(source['quote'])
                start=len(self._text(ticket[:source['start']]))
                end=start+len(quote)
                if self._text(ticket)[start:end]!=quote:
                    raise ProjectionError('PRIVACY_SPAN_CROSSES_PROJECTED_VALUE')
                candidates.append({'start':start,'end':end,'quote':quote})
            if any(value!=candidates[0] for value in candidates):
                raise ProjectionError('PRIVACY_SPAN_SOURCE_AMBIGUITY')
            self._projected_spans[identity]=candidates[0]

    def trust_sealed_tokens(self, value):
        """Called only after the keyed tape seal and key binding are checked."""
        text=canonical(value).decode('utf8')
        self._issued.update(re.findall(r'privacy_v1_[0-9a-f]{64}',text))

    def bind(self, column, value):
        if column not in self.policy['columns']:
            return value
        if value is None:
            return None  # BLANK stays distinct from zero and a missing result.
        if not isinstance(value, str):
            # Replacing a sensitive numeral in prose can also replace a count
            # or amount. Until typed numeric provenance is available, refuse.
            raise ProjectionError('PRIVACY_SENSITIVE_TYPE_UNSUPPORTED')
        if TOKEN.fullmatch(value):
            if value in self._issued:
                return value
            raise ProjectionError('PRIVACY_TOKEN_REQUIRES_VERIFIED_PROVENANCE')
        payload = canonical({'purpose': VERSION, 'estate': self.policy['estate_id'],
                             'type': 'string', 'value': value})
        token = 'privacy_v1_' + hmac.new(self._key, payload, hashlib.sha256).hexdigest()
        self._values[value] = token
        self._issued.add(token)
        return token

    def _decode(self, text):
        if isinstance(text,bytes):
            try:text=text.decode('utf8')
            except UnicodeError:return None
        try:
            value = parse(text)
        except (ValueError, TypeError):
            if isinstance(text,str) and re.match(r'^\[[A-Za-z_][A-Za-z0-9_ ]*\](?:$|[+*/<>=-])',text):
                return None  # A declared DAX member, not serialized JSON.
            if isinstance(text,str) and text.strip().startswith(('{','[')):
                raise ProjectionError('PRIVACY_AMBIGUOUS_NESTED_JSON') from None
            return None
        return value if isinstance(value, (dict, list)) else None

    def _encoded_json(self, text):
        try:
            raw=base64.b64decode(text,validate=True)
            if base64.b64encode(raw).decode('ascii')!=text:
                return None
            return self._decode(raw)
        except ProjectionError:
            raise
        except (ValueError,TypeError,UnicodeError):
            return None

    def discover(self, value):
        """Learn resolved sensitive values before projecting the whole packet."""
        if isinstance(value, dict):
            # Exact column/value receipts and exact-key object rows.
            if set(('column_id', 'value')) <= value.keys():
                self.bind(value['column_id'], value['value'])
            if 'column_id' in value and isinstance(value.get('values'),list):
                for cell in value['values']:self.bind(value['column_id'],cell)
            for key, child in value.items():
                if key in self.policy['columns']:
                    if isinstance(child,dict) and child.get('column_id')==key:
                        pass  # A resolved column declaration, not a row cell.
                    elif isinstance(child, list):
                        for item in child:
                            self.bind(key, item)
                    else:
                        self.bind(key, child)
                self.discover(child)
            # Tabular wire rows: identities must already be resolved by adapter.
            if isinstance(value.get('columns'), list) and isinstance(value.get('rows'), list):
                columns = value['columns']
                if any(not isinstance(c,str) or not c for c in columns) or len(columns)!=len(set(columns)):
                    raise ProjectionError('PRIVACY_UNRESOLVED_COLUMN_IDENTITY')
                for row in value['rows']:
                    if isinstance(row, list):
                        if len(row) != len(columns):
                            raise ProjectionError('PRIVACY_ROW_WIDTH')
                        for column, cell in zip(columns, row):
                            if isinstance(column, str):
                                self.bind(column, cell)
                    elif isinstance(row,dict) and set(row)==set(columns):
                        for column,cell in row.items():self.bind(column,cell)
                    else:
                        raise ProjectionError('PRIVACY_ROW_SHAPE')
        elif isinstance(value, list):
            for child in value:
                self.discover(child)
        elif isinstance(value, str):
            parsed = self._decode(value)
            if parsed is None:
                parsed=self._encoded_json(value)
            if parsed is not None:
                self.discover(parsed)

    def _text(self, value):
        if value in self._issued:
            return value
        if value and value in self._values:
            return self._values[value]
        parsed = self._decode(value)
        if parsed is not None:
            return canonical(self._project(parsed)).decode('utf8')
        parsed=self._encoded_json(value)
        if parsed is not None:
            return base64.b64encode(canonical(self._project(parsed))).decode('ascii')
        # Longer values first: replacement cannot expose a contained name.
        pattern = '|'.join(re.escape(v) for v in sorted(self._values, key=lambda s: (-len(s), s)) if v)
        if pattern:
            # A short sensitive string must not mutate a previously projected
            # token in a prose paragraph on a second projection.
            combined=r'privacy_v1_[0-9a-f]{64}|'+pattern
            return re.sub(combined, lambda m: m.group() if m.group() in self._issued
                          else self._values[m.group()], value)
        return value

    def _project(self, value):
        if isinstance(value, str):
            return self._text(value)
        if isinstance(value, list):
            return [self._project(v) for v in value]
        if isinstance(value, dict):
            if set(value)=={'start','end','quote'}:
                identity=canonical(value)
                if identity in self._projected_spans:return dict(self._projected_spans[identity])
                if self._text(value['quote'])!=value['quote']:
                    raise ProjectionError('PRIVACY_SPAN_REQUIRES_SOURCE_BINDING')
            # Structural names are not column values. Rewriting them would
            # change the schema being replayed (a person can be named "value"
            # or "quantity"). Refuse an unrepresentable collision rather
            # than silently rename a consumer-owned field.
            for key in value:
                if self._text(key) != key and key not in self._identity_values:
                    raise ProjectionError('PRIVACY_VALUE_COLLIDES_WITH_STRUCTURAL_KEY')
            result={self._identity_values.get(k,k):self._project(v) for k,v in value.items()}
            if len(result)!=len(value):
                raise ProjectionError('PRIVACY_PROJECTED_KEY_COLLISION')
            for column in self.policy['columns']:
                if column in value:
                    cell=value[column]
                    if not (isinstance(cell,dict) and cell.get('column_id')==column):
                        result[self._text(column)]=([self.bind(column,x) for x in cell]
                            if isinstance(cell,list) else self.bind(column,cell))
            if value.get('column_id') in self.policy['columns'] and 'value' in value:
                result['value']=self.bind(value['column_id'],value['value'])
            if isinstance(value.get('columns'),list) and isinstance(value.get('rows'),list):
                for index,row in enumerate(value['rows']):
                    if isinstance(row,list):
                        result['rows'][index]=[self.bind(column,cell)
                            if isinstance(column,str) and column in self.policy['columns']
                            else self._project(cell)
                            for column,cell in zip(value['columns'],row)]
            return result
        return value

    def project(self, value):
        self.discover(value)
        return self._project(value)

    def body(self, data, *, base64_body=False):
        """JSON-only capture boundary. Opaque bytes refuse, never pass through."""
        try:
            value = parse(data)
            if base64_body:
                if not isinstance(value, dict) or not isinstance(value.get('body'), str):
                    raise ProjectionError('PRIVACY_BODY_WRAPPER')
                inner = base64.b64decode(value['body'], validate=True)
                value = {**value, 'body': parse(inner)}
            projected = self.project(value)
            if base64_body:
                projected['body'] = base64.b64encode(canonical(projected['body'])).decode('ascii')
            return canonical(projected)
        except (ValueError, TypeError, UnicodeError) as exc:
            if isinstance(exc, ProjectionError):
                raise
            raise ProjectionError('PRIVACY_OPAQUE_BODY_REFUSED') from None
