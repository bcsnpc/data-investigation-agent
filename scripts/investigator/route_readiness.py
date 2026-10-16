"""Current scoring admission for individual evidence-backed routes.

Original onboarding receipts keep their original identity. An unrelated engine
revision carries readiness only after current-component offline verification;
it never relabels historical receipts or enlarges their admitted scope.
"""
import copy
import re
from pathlib import Path
from .estate_readiness import (PINS, assess_named_scope, load_ref)

VERSION = 'route-readiness-v1'
COMPONENTS = ('discovery', 'adapter', 'binding_verifier')
# These are behaviour versions, not source/engine hashes. Behaviour changes to
# the installed onboarding components require an explicit version bump here.
COMPONENT_VERSIONS = dict.fromkeys(COMPONENTS, '1.0.0')


def component_versions():
    return dict(COMPONENT_VERSIONS)


def current_engine_hash():
    from .runtime import fingerprint
    return fingerprint()


def _versions(value):
    if (not isinstance(value, dict) or set(value) != set(COMPONENTS) or
            any(not isinstance(v, str) or not re.fullmatch(r'\d+\.\d+\.\d+', v) for v in value.values())):
        raise ValueError('ONBOARDING_COMPONENT_VERSIONS_REQUIRED')
    return value


def _tape(ref, base):
    value = load_ref(ref, base)
    from .process_tape import Tape
    path = Path(ref['path'])
    if not path.is_absolute():
        path = Path(base) / path
    tape = Tape(path)
    # Tape validates the seal and every event; load_ref additionally pins bytes.
    return value, tape.bootstrap, {'path': str(path.resolve()), 'sha256': ref['sha256']}


def _inputs(certificate, base):
    if certificate.get('version') != VERSION:
        raise ValueError('ROUTE_CERTIFICATE_VERSION_UNSUPPORTED')
    original = certificate['original']
    manifest = load_ref(original['manifest_ref'], base)
    index = load_ref(original['index_ref'], base)
    scope_ref = original['scope_ref']
    scope = load_ref(scope_ref, base)
    pins = index['pins']
    if scope['pins'] != pins:
        raise ValueError('ORIGINAL_ROUTE_PINS_DIFFER')
    report = assess_named_scope(manifest, pins, index, scope_ref, base=base)
    return manifest, index, scope, pins, report


def _publication_tapes(index, base):
    publication = load_ref(index['stages']['publication'], base)
    executions = publication.get('publication', {}).get('executions', [])
    if not executions:
        raise ValueError('ROUTE_VERIFICATION_CAPTURE_INVENTORY_MISSING')
    dedicated = {}; native = {}
    for execution in executions:
        _, bootstrap, ref = _tape(execution['capture_ref'], base)
        target = dedicated if bootstrap['entry_point'] == 'code_verifier' else native
        if bootstrap['entry_point'] not in ('code_verifier', 'workspace'):
            raise ValueError('ROUTE_VERIFICATION_CAPTURE_KIND_UNSUPPORTED')
        if ref['sha256'] in dedicated or ref['sha256'] in native:
            raise ValueError('ROUTE_VERIFICATION_CAPTURE_DUPLICATED')
        target[ref['sha256']] = (ref, bootstrap)
    if not dedicated:
        raise ValueError('CURRENT_COMPONENT_VERIFICATION_TAPE_REQUIRED')
    return dedicated, native


def _conserve(refs, expected, base):
    found = []
    for ref in refs:
        _, _, checked = _tape(ref, base)
        found.append(checked['sha256'])
    if len(found) != len(set(found)) or set(found) != set(expected):
        raise ValueError('ROUTE_VERIFICATION_TAPE_CONSERVATION_FAILED')


def _replay_receipt(value, ref, bootstrap, current_engine):
    if (not isinstance(value, dict) or value.get('matched') is not True or
            value.get('status') != 'COMPLETED'):
        raise ValueError('ROUTE_VERIFICATION_REPLAY_MISMATCH')
    if (value.get('capture_sha256') != ref['sha256'] or
            value.get('recorded_engine_hash') != bootstrap['engine_hash'] or
            value.get('verification_engine_hash') != current_engine):
        raise ValueError('ROUTE_VERIFICATION_REPLAY_IDENTITY_DIFFERS')
    # Absence is not a zero counter. Refuse booleans (False == 0 in Python).
    for field in ('network_requests', 'model_calls', 'estate_reads'):
        if type(value.get(field)) is not int or value[field] != 0:
            raise ValueError('ROUTE_VERIFICATION_REPLAY_NOT_OFFLINE')
    if not re.fullmatch('[0-9a-f]{64}', str(value.get('result_sha256', ''))):
        raise ValueError('ROUTE_VERIFICATION_REPLAY_RESULT_HASH_REQUIRED')
    return copy.deepcopy(value)


def assess_route(certificate, current_pins, *, replay_verifications, output, base='.'):
    """Recompute original proofs and automatically replay a changed engine.

    ``replay_verifications`` is an installed internal execution port, not a
    client-supplied verdict or cached READY label. It must execute current
    components against the sealed verification tape and deny external calls.
    """
    route = certificate.get('route', {}) if isinstance(certificate, dict) else {}
    result = {'version': VERSION, 'route': copy.deepcopy(route), 'status': 'BLOCKED',
              'scoring': 'NOT_SCORED', 'reason': "this metric isn't onboarded yet",
              'estate_reads': 0, 'model_calls': 0, 'network_requests': 0}
    step = 'onboarding_evidence'
    try:
        if (not isinstance(certificate, dict) or set(current_pins) != set(PINS) or
                any(not isinstance(v, str) or not v for v in current_pins.values())):
            raise ValueError('CURRENT_ROUTE_IDENTITY_REQUIRED')
        if current_pins['engine_hash'] != current_engine_hash():
            raise ValueError('CURRENT_ROUTE_ENGINE_IDENTITY_DIFFERS')
        manifest, index, scope, pins, original = _inputs(certificate, base)
        result['original_readiness'] = original
        if original['status'] != 'READY':
            blocked = next((r for r in original.get('stages', []) if r['status'] != 'VERIFIED'), None)
            step = blocked['stage'] if blocked else step
            raise ValueError(blocked['reason'] if blocked else original.get('detail', 'ORIGINAL_ROUTE_NOT_READY'))
        if any(current_pins[k] != pins[k] for k in PINS if k != 'engine_hash'):
            raise ValueError('CURRENT_ONBOARDING_EVIDENCE_IDENTITY_DIFFERS')
        constraints = original['scope']['constraints']
        if (set(route) != {'id', 'label', 'measure_id'} or
                any(not isinstance(v, str) or not v for v in route.values()) or
                route['measure_id'] not in constraints['measure_ids']):
            raise ValueError('ROUTE_IDENTITY_NOT_IN_VERIFIED_SCOPE')
        step = 'component_versions'
        baseline = certificate['component_baseline']
        if (set(baseline) != {'versions', 'engine_hash', 'authority'} or
                baseline['engine_hash'] != pins['engine_hash'] or
                baseline['authority'] != 'COMPONENT_BASELINE_ADOPTION'):
            raise ValueError('ORIGINAL_COMPONENT_BASELINE_REQUIRED')
        if _versions(baseline['versions']) != _versions(component_versions()):
            raise ValueError('ONBOARDING_COMPONENT_CHANGED_REVERIFICATION_REQUIRED')
        step = 'verification_inventory'
        dedicated, native = _publication_tapes(index, base)
        _conserve(certificate['verification_tapes'], dedicated, base)
        _conserve(certificate['native_witness_tapes'], native, base)
        result['verification_coverage'] = {
            'dedicated_verification_tapes': len(dedicated),
            'retained_native_witness_tapes': len(native),
            'native_witness_validation': 'Current six-stage consumer revalidation; not full current workspace replay'}
        replays = []
        if current_pins['engine_hash'] != pins['engine_hash']:
            step = 'offline_revalidation'
            if not callable(replay_verifications):
                raise ValueError('AUTOMATIC_ROUTE_REPLAY_REQUIRED')
            for identity, (ref, bootstrap) in sorted(dedicated.items()):
                observed = replay_verifications(ref, bootstrap['engine_hash'], current_pins['engine_hash'],
                    output=Path(output) / identity)
                replays.append(_replay_receipt(observed, ref, bootstrap, current_pins['engine_hash']))
        result.update(status='READY', scoring='ADMITTED', reason=None, first_missing_step=None,
                      component_versions=component_versions(), current_pins=dict(current_pins),
                      original_pins=dict(pins), scope=copy.deepcopy(original['scope']),
                      revalidation={'required': current_pins['engine_hash'] != pins['engine_hash'],
                                    'replays': replays})
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
        result.update(first_missing_step=step, detail=str(exc))
    return result


def assess_routes(certificates, current_pins, *, replay_verifications, output, whole_estate=None,
                  route_inventory=None, base='.'):
    reports = [assess_route(c, current_pins, replay_verifications=replay_verifications,
                           output=Path(output) / str(i), base=base) for i, c in enumerate(certificates)]
    ids = [r.get('route', {}).get('id') for r in reports]
    if len(ids) != len(set(ids)):
        raise ValueError('ROUTE_IDENTITY_DUPLICATED')
    inventory = route_inventory or []
    inventory_ids = []
    for route in inventory:
        if (not isinstance(route, dict) or set(route) != {'id', 'label', 'measure_id'} or
                any(not isinstance(v, str) or not v for v in route.values())):
            raise ValueError('DECLARED_ROUTE_INVENTORY_REQUIRED')
        inventory_ids.append(route['id'])
        if route['id'] not in ids:
            reports.append({'version': VERSION, 'route': copy.deepcopy(route), 'status': 'BLOCKED',
                'scoring': 'NOT_SCORED', 'reason': "this metric isn't onboarded yet",
                'first_missing_step': 'route_evidence_missing', 'detail': 'ONBOARDING_ROUTE_EVIDENCE_MISSING',
                'estate_reads': 0, 'model_calls': 0})
        elif next(r['route']['measure_id'] for r in reports if r['route']['id'] == route['id']) != route['measure_id']:
            raise ValueError('DECLARED_ROUTE_IDENTITY_DIFFERS')
    if len(inventory_ids) != len(set(inventory_ids)):
        raise ValueError('DECLARED_ROUTE_INVENTORY_DUPLICATED')
    return {'version': VERSION, 'routes': reports,
            'ready_routes': [r['route'] for r in reports if r['status'] == 'READY'],
            'whole_estate': {'informational': True, 'readiness': whole_estate},
            'estate_reads': 0, 'model_calls': 0}


def score_route(score, *args, certificate, current_pins, requested_measure_id, requested_scope,
                requested_assets, replay_verifications, output, base='.', **kwargs):
    """Only the claim's exact onboarded route may authorize a new score."""
    report = assess_route(certificate, current_pins, replay_verifications=replay_verifications,
                          output=output, base=base)
    scope = report.get('scope', {})
    requested = set(requested_assets)
    if (report['status'] != 'READY' or requested_measure_id != report['route'].get('measure_id') or
            requested_scope != scope.get('constraints') or not requested or
            not requested <= set(scope.get('assets', []))):
        return {'scoring': 'NOT_SCORED', 'passed': None,
                'reason': "this metric isn't onboarded yet", 'readiness': report,
                'detail': 'REQUEST_OUTSIDE_VERIFIED_ROUTE' if report['status'] == 'READY' else report.get('detail')}
    return score(*args, **kwargs)


class RouteAdmission:
    """Internal admission shared by one current-engine scoring cohort.

    Construction performs the actual route assessment/replay once. Neither
    construction nor scoring accepts a producer's READY verdict. Every score
    refreshes installation identity and component versions; drift requires a
    fresh admission. The returned report is a copy, not admission authority.
    """
    def __init__(self, certificate, *, current_identity, replay_verifications, output, base='.'):
        from .shared_state import configured_state
        from .process_tape import ACTIVE
        from .onboarding import digest
        tape=ACTIVE.get()
        state=None if tape is not None and tape.replaying else configured_state()
        if state is not None:
            saved=state.get('readiness_certificate',digest(certificate))['body']
            if saved!=certificate:
                raise ValueError('POSTGRES_READINESS_CERTIFICATE_DIFFERS')
            certificate=saved
        from .onboarding import digest
        if not callable(current_identity):
            raise ValueError('CURRENT_ROUTE_IDENTITY_PORT_REQUIRED')
        self._identity = current_identity
        self._certificate = copy.deepcopy(certificate)
        self._certificate_hash = digest(self._certificate)
        self._pins = copy.deepcopy(current_identity())
        self._versions = component_versions()
        self._report = assess_route(self._certificate, self._pins,
            replay_verifications=replay_verifications, output=output, base=base)

    @property
    def assessment(self):
        return copy.deepcopy(self._report)

    def score(self, score, *args, requested_measure_id, requested_scope, requested_assets, **kwargs):
        from .onboarding import digest
        detail = None
        try:
            now = self._identity()
            if now != self._pins or now.get('engine_hash') != current_engine_hash():
                detail = 'CURRENT_ROUTE_IDENTITY_CHANGED'
            elif component_versions() != self._versions:
                detail = 'ONBOARDING_COMPONENT_CHANGED_REVERIFICATION_REQUIRED'
            elif digest(self._certificate) != self._certificate_hash:
                detail = 'ROUTE_CERTIFICATE_CHANGED'
            elif self._report['status'] != 'READY':
                detail = self._report.get('detail', 'ROUTE_NOT_READY')
            else:
                scope = self._report['scope']
                assets = set(requested_assets)
                if (requested_measure_id != self._report['route']['measure_id'] or
                        requested_scope != scope['constraints'] or not assets or
                        not assets <= set(scope['assets'])):
                    detail = 'REQUEST_OUTSIDE_VERIFIED_ROUTE'
        except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
            detail = str(exc)
        if detail is not None:
            return {'scoring': 'NOT_SCORED', 'passed': None,
                    'reason': "this metric isn't onboarded yet", 'detail': detail,
                    'readiness': self.assessment}
        return score(*args, **kwargs)
