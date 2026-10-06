"""Closed translation proposals and bounded evidence verification.

Expressions are untrusted compiler inputs, never executable statements here.
Adapters own native parsing, key normalization and query-bound receipts. A
verified sample is neither global equivalence nor snapshot alignment.
"""
import copy
import hashlib
import json
from datetime import datetime
from decimal import Decimal, localcontext, ROUND_HALF_EVEN
from pathlib import Path
from typing import Protocol
from jsonschema import Draft202012Validator
from .code_sources import obj
from .lineage_binding import seal, VerificationHold
from .reported_figure import PRECISION_SCHEMA
from .usage_governance import UsageHold

TEXT = {'type': 'string', 'minLength': 1, 'maxLength': 500}
HASH = {'type': 'string', 'pattern': '^[0-9a-f]{64}$'}
OBJECT = obj({'id': TEXT, 'kind': {'enum': ['TABLE', 'COLUMN', 'MEASURE']}})
KEY_BINDING = obj({'context': TEXT, 'scope_hash': HASH,
    'provenance': {'enum': ['DECLARED_BY_CONFIGURATION', 'DECLARED_BY_DEFINITION']},
    'evidence_id': TEXT,
    'normalization': {'type': 'object', 'minProperties': 1},
    'columns': {'type': 'array', 'minItems': 1, 'maxItems': 32,
                'items': obj({'native': TEXT, 'proposed': TEXT})},
    'definition_hashes': obj({'native': HASH, 'proposed': HASH})})
SCHEMA = obj({
    'kind': {'enum': ['FILTER', 'MEASURE']}, 'definition_hash': HASH,
    'target_engine': TEXT,
    'expression': {'type': 'string', 'minLength': 1, 'maxLength': 8000},
    'objects': {'type': 'array', 'minItems': 1, 'maxItems': 64, 'uniqueItems': True, 'items': OBJECT},
    'grouping': {'type': 'array', 'maxItems': 64, 'uniqueItems': True, 'items': TEXT},
    'evaluation_timestamp': {'type': ['string', 'null'], 'maxLength': 64}})


class TranslationProposer(Protocol):
    def propose(self, request: dict, schema: dict) -> dict: ...


def timestamp(value):
    if not isinstance(value, str): raise ValueError('Evaluation timestamp is missing')
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None: raise ValueError('Evaluation timestamp needs an explicit timezone')
    return parsed


def validate(proposal, request):
    Draft202012Validator(SCHEMA).validate(proposal)
    if not isinstance(request.get('scope'), dict):
        raise ValueError('Translation requires explicit declared scope; absence is not empty scope')
    for key in ('kind', 'definition_hash', 'target_engine', 'grouping'):
        if proposal[key] != request[key]: raise ValueError('Translation differs from requested ' + key)
    if proposal['definition_hash'] != seal(request['definition']):
        raise ValueError('Definition hash differs from original definition')
    if proposal['grouping'] != sorted(proposal['grouping']): raise ValueError('Grouping must be canonical')
    catalog = request['metadata']['objects']
    ids = [o['id'] for o in proposal['objects']]
    if len(ids) != len(set(ids)): raise ValueError('Duplicate translation object')
    if any(catalog.get(o['id']) != o['kind'] for o in proposal['objects']):
        raise ValueError('Translation touches an object absent from metadata')
    expected = request['evaluation_timestamp'] if request['relative'] else None
    if proposal['evaluation_timestamp'] != expected: raise ValueError('Relative evaluation timestamp differs')
    if expected is not None: timestamp(expected)
    return copy.deepcopy(proposal)


def propose(request, proposer, model_call):
    """Caller meters/records every provider call; the response cannot self-verify."""
    return validate(model_call(request, lambda: proposer.propose(copy.deepcopy(request), copy.deepcopy(SCHEMA))), request)


def key_fingerprint(keys, normalization):
    """Binary hash of a complete, adapter-normalized key set, not a sample.

    The adapter must supply the explicit normalization declaration and translate
    verified cross-boundary keys to the same namespace. Typed JSON encodings
    preserve null/zero/text distinctions and length framing prevents collisions.
    """
    if not isinstance(normalization, dict) or not normalization:
        raise ValueError('Explicit key normalization is required')
    if not isinstance(keys, list) or len(keys) > 100000:
        raise ValueError('Complete selected key set exceeds bound')
    encodings = []
    for key in keys:
        if not isinstance(key, list) or not key: raise ValueError('Key needs a nonempty typed tuple')
        if any(type(v) not in (str, int, bool, type(None)) for v in key):
            raise ValueError('Adapter must encode nonintegral keys explicitly')
        encodings.append(json.dumps(key, ensure_ascii=False, separators=(',', ':')).encode('utf8'))
    if len(set(encodings)) != len(encodings): raise ValueError('Selected keys are not unique')
    digest = hashlib.sha256()
    for encoded in sorted(encodings): digest.update(len(encoded).to_bytes(8, 'big') + encoded)
    return {'count': len(encodings), 'binary_hash': digest.hexdigest(), 'normalization': copy.deepcopy(normalization)}


def _evidence(observation, context, address):
    from .process_debugging import attest_surface
    evidence = observation.get('evidence')
    if not isinstance(evidence, dict) or not evidence.get('id'):
        raise ValueError('Original probe receipt is missing')
    if evidence.get('context_id') != context or evidence.get('read_address') != address:
        raise ValueError('Original probe context or address differs')
    from .read_address import validate as validate_address
    validate_address(address)
    attestation = evidence.get('surface_attestation') or {}
    if not isinstance(attestation, dict): raise ValueError('Malformed original surface attestation')
    fields = attestation.get('required_fields')
    if not isinstance(fields, list) or any(not isinstance(f, str) for f in fields):
        raise ValueError('Malformed attestation required-field inventory')
    check = attest_surface(evidence.get('execution_surface'), evidence.get('surface_report'), attestation.get('required_fields', ()))
    if check != attestation or check['consistency'] != 'MATCHED' or check.get('missing_required_fields'):
        raise ValueError('Original probe surface attestation failed')
    if evidence.get('surface_report_binding') != 'VALUE_QUERY' or evidence.get('surface_report_receipt_id') != evidence['id']:
        raise ValueError('Surface self-report is not query-bound')
    payload = {k: observation[k] for k in ('quantity', 'keys', 'complete', 'normalization') if k in observation}
    if evidence.get('translation_result') != payload:
        raise ValueError('Translation result differs from original probe receipt')
    return evidence


def _quantity(value, precision):
    if value == {'state': 'BLANK'}: return ('BLANK',)
    if not isinstance(value, dict) or set(value) != {'state', 'value'} or value['state'] != 'NUMBER':
        raise ValueError('Quantity is neither a number nor BLANK')
    if not isinstance(value['value'], str) or len(value['value']) > 128:
        raise ValueError('Quantity requires bounded decimal text')
    with localcontext() as ctx:
        ctx.prec = 256
        number = Decimal(value['value'])
        if not number.is_finite(): raise ValueError('Nonfinite quantity')
        if precision['state'] == 'STATED_PLACE':
            number = number.quantize(Decimal(1).scaleb(precision['place']), rounding=ROUND_HALF_EVEN)
    return ('NUMBER', number)


def verify_key_binding(declaration, observations):
    """Recompute a bounded complete-key witness; never promote quantity proofs.

    Ordered columns are declared correspondence, not a guessed join. Both
    original value-query receipts must carry the entire normalized key universe
    at that scope. This proves correspondence for the recorded universe only;
    no snapshot or global semantic-equivalence claim follows.
    """
    Draft202012Validator(KEY_BINDING).validate(declaration)
    columns = declaration['columns']
    if any(len({c[side] for c in columns}) != len(columns) for side in ('native', 'proposed')):
        raise ValueError('Key binding repeats a column')
    if len(observations) != 2: raise ValueError('Key binding requires two original observations')
    address = {'kind': 'KEY_BINDING', 'declaration_hash': seal(declaration)}
    fingerprints = []
    for observation in observations:
        if observation.get('status') != 'COMPLETED': raise ValueError('Key-binding probe did not complete')
        _evidence(observation, declaration['context'], address)
        if observation.get('complete') is not True or observation.get('normalization') != declaration['normalization']:
            raise ValueError('Complete key-binding universe was not established')
        if any(len(key) != len(columns) for key in observation['keys']):
            raise ValueError('Key-binding tuple differs from declared column order')
        fingerprints.append(key_fingerprint(observation['keys'], declaration['normalization']))
    from .surface_difference import grade, BOUNDARY_GRADES
    if grade(observations[0]['evidence'], observations[1]['evidence'])['grade'] not in BOUNDARY_GRADES:
        raise ValueError('Key binding lacks an independent attested boundary')
    return {'declaration': copy.deepcopy(declaration), 'observations': copy.deepcopy(observations),
            'status': 'VERIFIED' if fingerprints[0] == fingerprints[1] else 'FALSIFIED',
            'key_sets': fingerprints, 'snapshot_status': 'SNAPSHOT_UNVERIFIED'}


def _binding_for(request):
    proof = request['metadata'].get('key_binding')
    if not isinstance(proof, dict): raise ValueError('Cross-boundary selected keys need a verified binding')
    recomputed = verify_key_binding(proof['declaration'], proof['observations'])
    if recomputed != proof or proof['status'] != 'VERIFIED':
        raise ValueError('Key binding does not verify against original observations')
    declaration = proof['declaration']
    catalog = request['metadata']['objects']
    if any(catalog.get(column[side]) != 'COLUMN'
           for column in declaration['columns'] for side in ('native', 'proposed')):
        raise ValueError('Key-binding column is absent from discovered metadata')
    if (declaration['context'] != request['context'] or declaration['scope_hash'] != seal(request['scope'])
            or declaration['normalization'] != request['metadata']['normalization']
            or declaration['definition_hashes'] != request['metadata'].get('key_definition_hashes')):
        raise ValueError('Key binding is stale or outside the translation scope')
    return proof


def verify(proposal, request, *, cells, compiler, execute, budget, cross_boundary=False, extension=False, native_observation=None):
    """Compile all plans before reading, then compare original attested answers.

    execute is an isolated adapter route; budget is the verification-class meter
    (physical admission remains outside it). No investigation cap is changed.
    """
    proposal = validate(proposal, request)
    if native_observation is not None and (not extension or len(cells) != 1):
        raise ValueError('Existing native observation is only for one-cell extension')
    if extension and native_observation is None:
        raise ValueError('One-probe extension requires the original native cell observation')
    context = request['context']
    if not isinstance(context, str) or not context: raise ValueError('Retained context required')
    if proposal['kind'] == 'MEASURE':
        if len(cells) < (1 if extension else 3) or len(cells) > 32:
            raise ValueError('Measure verification needs three bounded cells, or one explicit extension')
        if len({seal(c) for c in cells}) != len(cells): raise ValueError('Sample cells repeat')
        from .report_cell import validate as validate_cell
        for cell in cells: validate_cell(cell, cell.get('measure_id'))
        if any(c not in request['available_cells'] for c in cells): raise ValueError('Cell absent from retained addresses')
        if not cross_boundary: raise ValueError('Measure verification requires an independent boundary')
        Draft202012Validator(PRECISION_SCHEMA).validate(request['precision'])
    elif cells != [None] or extension:
        raise ValueError('Filter verification uses one complete selected key set')
    receipt = {'version': 1, 'proposal': proposal, 'request': copy.deepcopy(request), 'cells': copy.deepcopy(cells),
               'cross_boundary': cross_boundary, 'extension': extension,
               'native_observation': copy.deepcopy(native_observation), 'observations': [],
               'status': 'UNVERIFIED', 'reason': None, 'snapshot_status': 'SNAPSHOT_UNVERIFIED',
               'limits': ['Matching served snapshots were not established; timing is not excluded.',
                          'Verification covers only the recorded scope and sampled cells; not global equivalence or business intent.']}
    if proposal['kind'] == 'FILTER' and cross_boundary:
        try: _binding_for(request)
        except (ValueError, KeyError, TypeError) as exc:
            receipt['reason'] = 'Key-binding verification unavailable: ' + str(exc)
            return receipt
    plans = []
    try:
        for cell in cells:
            address = {'kind': 'TRANSLATION', 'proposal_hash': seal(proposal), 'cell': cell,
                       'evaluation_timestamp': proposal['evaluation_timestamp']}
            for side in ('NATIVE', 'PROPOSED'):
                plan = None if side == 'NATIVE' and native_observation is not None else compiler(proposal, side, request, address)
                plans.append((side, address, plan))
    except (ValueError, NotImplementedError) as exc:
        receipt['reason'] = 'Cannot compile faithfully: ' + str(exc); return receipt
    for side, address, plan in plans:
        try:
            reused = side == 'NATIVE' and native_observation is not None
            observation = copy.deepcopy(native_observation) if reused else budget.read('TARGET' if side == 'NATIVE' else 'SOURCE', lambda: execute(side, plan))
            receipt['observations'].append(copy.deepcopy(observation))
            if not isinstance(observation, dict) or observation.get('status') != 'COMPLETED':
                raise ValueError('Probe did not complete: ' + str(observation.get('reason') if isinstance(observation, dict) else 'Malformed observation'))
            _evidence(observation, context, {'kind': 'CELL', 'cell': address['cell']} if reused else address)
        except UsageHold as exc:
            receipt['reason'] = 'Verification budget/deadline stopped: ' + str(exc)
            raise VerificationHold(receipt) from exc
        except (ValueError, OSError, ArithmeticError) as exc:
            receipt['reason'] = 'Verification unavailable: ' + str(exc); return receipt
        if side != 'PROPOSED': continue
        left, right = receipt['observations'][-2:]
        try:
            if cross_boundary:
                from .surface_difference import grade, BOUNDARY_GRADES
                if grade(left['evidence'], right['evidence'])['grade'] not in BOUNDARY_GRADES:
                    raise ValueError('No independent attested boundary')
            else:
                triples = [tuple(o['evidence']['execution_surface'].get(k) for k in ('engine', 'connection', 'object')) for o in (left, right)]
                if triples[0] != triples[1] or any(v is None for v in triples[0]):
                    raise ValueError('Same-engine filter comparison requires the same resolved surface')
            if proposal['kind'] == 'FILTER':
                norm = request['metadata']['normalization']
                fingerprints = []
                for o in (left, right):
                    if o.get('complete') is not True or o.get('normalization') != norm:
                        raise ValueError('Complete normalized key set was not established')
                    fingerprints.append(key_fingerprint(o['keys'], norm))
                if cross_boundary:
                    proof = _binding_for(request)
                    for index, o in enumerate((left, right)):
                        if o['evidence']['execution_surface'] != proof['observations'][index]['evidence']['execution_surface']:
                            raise ValueError('Selected keys differ from the verified key-binding surface')
                        universe = {seal(key) for key in proof['observations'][index]['keys']}
                        if any(seal(key) not in universe for key in o['keys']):
                            raise ValueError('Selected key is outside the verified key-binding universe')
                receipt.setdefault('key_sets', []).append(fingerprints)
                equal = fingerprints[0] == fingerprints[1]
            else:
                equal = _quantity(left.get('quantity'), request['precision']) == _quantity(right.get('quantity'), request['precision'])
        except (ValueError, KeyError, ArithmeticError, NotImplementedError) as exc:
            receipt['reason'] = 'Verification unavailable: ' + str(exc); return receipt
        if not equal:
            receipt.update(status='FALSIFIED', reason='Native and proposed observations differ.'); return receipt
    receipt.update(status='VERIFIED', reason='All recorded comparisons agree at the declared scope and precision.')
    return receipt


def revalidate(receipt):
    if receipt['status'] not in ('VERIFIED', 'FALSIFIED'):
        raise ValueError('Unverified translation has no observation proof to revalidate')
    observations = iter(copy.deepcopy(receipt['observations']))
    if receipt['native_observation'] is not None: next(observations)
    class OfflineBudget:
        def read(self, kind, execute): return execute()
    check = verify(receipt['proposal'], receipt['request'], cells=receipt['cells'],
                   compiler=lambda *args: None, execute=lambda *args: next(observations), budget=OfflineBudget(),
                   cross_boundary=receipt['cross_boundary'], extension=receipt['extension'],
                   native_observation=receipt['native_observation'])
    if check != receipt: raise ValueError('Translation receipt differs from original observations')
    return check


class Ledger:
    """Append-only translation evidence; immutable context/metadata scope cache."""
    def __init__(self, path): self.path = Path(path)

    def append(self, receipt):
        if receipt['status'] not in ('VERIFIED', 'FALSIFIED', 'UNVERIFIED'):
            raise ValueError('Only verifier verdicts enter translation ledger')
        if receipt['status'] in ('VERIFIED', 'FALSIFIED'): revalidate(receipt)
        row = {'event': 'TRANSLATION_VERIFICATION', 'receipt': receipt, 'sha256': seal(receipt)}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('a', encoding='utf8') as stream: stream.write(json.dumps(row, sort_keys=True) + '\n')

    def view(self, request):
        result = []
        if not self.path.exists(): return result
        for line in self.path.read_text(encoding='utf8').splitlines():
            row = json.loads(line); receipt = row['receipt']
            if row['event'] != 'TRANSLATION_VERIFICATION' or seal(receipt) != row['sha256']:
                raise ValueError('Translation ledger integrity differs')
            if receipt['status'] in ('VERIFIED', 'FALSIFIED'): revalidate(receipt)
            identity = lambda r: {k: v for k, v in r.items() if k != 'available_cells'}
            result.append({**receipt, 'status': receipt['status'] if identity(receipt['request']) == identity(request) else 'STALE'})
        return result

    def reusable(self, request, cell=None):
        for receipt in reversed(self.view(request)):
            if receipt['status'] == 'FALSIFIED': return None
            if receipt['status'] != 'STALE' and cell in receipt['cells']:
                return receipt if receipt['status'] == 'VERIFIED' else None
        return None

    def candidate(self, request):
        """A fresh existing proposal may be reverified at a new cell, not reasked."""
        for receipt in reversed(self.view(request)):
            if receipt['status'] == 'STALE': continue
            return copy.deepcopy(receipt['proposal']) if receipt['status'] == 'VERIFIED' else None
        return None
