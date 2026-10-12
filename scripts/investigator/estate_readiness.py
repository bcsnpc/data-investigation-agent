"""Prospective scoring admission from retained onboarding evidence, never warnings.

This control is offline. It neither authorizes reads nor changes execution.
Historical tape grading does not call it. An evidence index locates original,
hash-pinned receipts; it cannot supply a completion verdict of its own.
"""
import hashlib
import json
from pathlib import Path

VERSION = 'estate-readiness-v1'
STAGES = ('discovery', 'discovery_approval', 'transformations', 'bindings',
          'reader_verification', 'publication')
PINS = ('manifest_hash', 'context_identity', 'context_hash', 'config_hash', 'engine_hash')


def sha(value):
    return hashlib.sha256(value).hexdigest()


def load_ref(ref, base):
    if not isinstance(ref, dict) or set(ref) != {'path', 'sha256'}:
        raise ValueError('ORIGINAL_RECEIPT_REFERENCE_REQUIRED')
    path = Path(ref['path'])
    if not path.is_absolute():
        path = Path(base) / path
    raw = path.read_bytes()
    if sha(raw) != ref['sha256']:
        raise ValueError('ORIGINAL_RECEIPT_HASH_DIFFERS')
    return json.loads(raw)


def boundary(row):
    return row['from_layer'], row['to_layer']


def exactly(rows, expected, name):
    if len(rows) != len(set(rows)) or set(rows) != set(expected):
        raise ValueError(name + '_CONSERVATION_FAILED')


def require_pins(receipt, pins):
    if receipt.get('pins') != pins:
        raise ValueError('ONBOARDING_PINS_DIFFER')


def discovery(receipt, manifest, pins, *, scope_assets=None):
    require_pins(receipt, pins)
    scan = receipt['scan']
    if not scan.get('coverage'):
        raise ValueError('DISCOVERY_NOT_COMPLETE')
    if scope_assets is None:
        if scan.get('status') != 'COMPLETE':
            raise ValueError('DISCOVERY_NOT_COMPLETE')
        if any(c.get('status') != 'COMPLETE' for c in scan['coverage'].values()):
            raise ValueError('DISCOVERY_PARTIAL')
    assets = scan['assets']
    if isinstance(assets, dict):
        assets = list(assets.values())
    ids = {a['id'] for a in assets}
    required = {l['asset_id'] for l in manifest['layers']} | {r['asset_id'] for r in manifest['resources']}
    if not required <= ids:
        raise ValueError('DISCOVERY_DECLARED_ASSET_MISSING')
    if scope_assets is not None:
        by_id = {a['id']: a for a in assets}
        if not set(scope_assets) <= ids:
            raise ValueError('DISCOVERY_SCOPE_ASSET_MISSING')
        for asset in scope_assets:
            original = by_id[asset]
            coverage = scan['coverage'].get(original.get('coverage_scope'), {})
            if (original.get('availability') != 'CURRENT' or
                    coverage.get('status') != 'COMPLETE' or not original.get('content_hash')):
                raise ValueError('DISCOVERY_SCOPE_COVERAGE_INCOMPLETE:' + asset)


def approval(receipt, manifest, pins):
    require_pins(receipt, pins)
    original = receipt['approval']
    aliases = {'manifest_hash': 'manifest_sha256', 'context_identity': 'context_id',
               'context_hash': 'context_hash', 'config_hash': 'config_hash', 'engine_hash': 'engine_hash'}
    from .onboarding import digest
    manifest_ref = next((s for s in receipt['sources'] if s.get('field') == 'manifest'), {})
    if receipt.get('manifest') != manifest or digest(manifest) != pins['manifest_hash'] or original.get('manifest_sha256') != manifest_ref.get('sha256'):
        raise ValueError('DISCOVERY_APPROVAL_MANIFEST_DIFFERS')
    if any(original.get(aliases[k]) != pins[k] for k in PINS if k != 'manifest_hash'):
        raise ValueError('DISCOVERY_APPROVAL_PINS_DIFFER')
    if not original.get('authority'):
        raise ValueError('DISCOVERY_APPROVAL_AUTHORITY_MISSING')


def inventory(receipt, manifest, pins):
    require_pins(receipt, pins)
    # The retained extractor receipt must enumerate what was discovered, even
    # for a direct source with an explicitly empty declaration inventory.
    declarations = receipt['discovered_declarations']
    entries = receipt['inventory']
    exactly([d['id'] for d in declarations], [e['id'] for e in entries], 'DECLARATION')
    discovered = {d['id']: d for d in declarations}
    allowed = {'READ', 'DIRECT', 'UNSUPPORTED'}
    for entry in entries:
        if entry.get('disposition') not in allowed:
            raise ValueError('DECLARATION_DISPOSITION_REQUIRED')
        if entry['disposition'] == 'UNSUPPORTED':
            raise ValueError('TRANSFORMATION_UNSUPPORTED:' + discovered[entry['id']]['form'])
        if entry.get('declaration_hash') != discovered[entry['id']]['content_hash']:
            raise ValueError('DECLARATION_CONTENT_DIFFERS')
        if entry['disposition'] == 'DIRECT':
            if discovered[entry['id']].get('operation') != 'DIRECT_REFERENCE':
                raise ValueError('DIRECT_SOURCE_NOT_ESTABLISHED')
        elif not entry.get('retained_content_hash') or not entry.get('reader'):
            raise ValueError('TRANSFORMATION_READ_EVIDENCE_MISSING')
    # Explicit completeness belongs to the extractor's receipt. A warnings
    # array, accepted limit, or a producer's READY/VERIFIED label never suffices.
    if receipt.get('extraction_status') != 'COMPLETE':
        raise ValueError('TRANSFORMATION_INVENTORY_INCOMPLETE')
    expected = [boundary(b) for b in manifest['lineage']['bindings']]
    exactly([boundary(b) for b in receipt['boundary_inventory']], expected, 'BOUNDARY')
    for item in receipt['boundary_inventory']:
        if not item.get('declarations') or not set(item['declarations']) <= set(discovered):
            raise ValueError('BOUNDARY_DECLARATION_EVIDENCE_MISSING')


def proposals(receipt, manifest, pins):
    require_pins(receipt, pins)
    from .lineage_binding import validate
    rows = [validate(p) for p in receipt['proposals']]
    expected = [boundary(b) for b in manifest['lineage']['bindings']]
    # Several quantity/key bindings at one boundary are legitimate; coverage
    # is over boundaries, while conservation/uniqueness is over full proposals.
    from .lineage_binding import seal
    exactly([seal(p) for p in rows], [seal(p) for p in rows], 'PROPOSAL_IDENTITY')
    if {boundary(p['boundary']) for p in rows} != set(expected):
        raise ValueError('PROPOSED_BINDING_CONSERVATION_FAILED')
    if not expected:
        raise ValueError('NO_EXECUTABLE_BINDING_INVENTORY')


def verification(receipt, manifest, pins):
    require_pins(receipt, pins)
    from .lineage_binding import revalidate_verification
    rows = receipt['verifications']
    from .lineage_binding import seal
    exactly([seal(v['proposal']) for v in rows], [seal(v['proposal']) for v in rows], 'VERIFICATION_IDENTITY')
    if {boundary(v['proposal']['boundary']) for v in rows} != {
            boundary(b) for b in manifest['lineage']['bindings']}:
        raise ValueError('VERIFIED_BINDING_CONSERVATION_FAILED')
    for original in rows:
        checked = revalidate_verification(original)
        if checked.get('status') != 'VERIFIED':
            raise ValueError('BINDING_NOT_VERIFIED')
        if original['context'] not in receipt['model_contexts'].values():
            raise ValueError('VERIFICATION_CONTEXT_DIFFERS')
        for observation in original['observations']:
            # Revalidation owns quantity/attestation gates. The readiness gate
            # additionally requires native retained reader receipts, not a
            # model's assertion that a simulated read was live.
            evidence = observation.get('evidence', {})
            if observation.get('status') != 'COMPLETED' or not evidence.get('id') or evidence.get('surface_report_binding') != 'VALUE_QUERY':
                raise ValueError('LIVE_READER_RECEIPT_MISSING')


def publication(receipt, manifest, pins):
    require_pins(receipt, pins)
    replay = receipt['replay']
    published = receipt['publication']
    if replay.get('status') != 'COMPLETED' or replay.get('matched') is not True:
        raise ValueError('PROFILE_OFFLINE_REPLAY_NOT_MATCHED')
    if published.get('status') != 'PROFILE_APPEND_ACCEPTED':
        raise ValueError('VERIFIED_PROFILE_UNPUBLISHED')
    native = published.get('verification_pins', {})
    if any(native.get(k) != pins[k] for k in ('manifest_hash', 'context_identity', 'config_hash', 'engine_hash')):
        raise ValueError('PUBLISHED_PROFILE_PINS_DIFFER')
    if replay.get('capture_sha256') != published.get('capture_sha256'):
        raise ValueError('PUBLICATION_REPLAY_CAPTURE_DIFFERS')
    # The exact original replay bytes, rather than a reserialised summary,
    # are checked by the source-binding step below.
    source = next((s for s in receipt['sources'] if s.get('field') == 'replay'), None)
    if source is None or published.get('replay_receipt_sha256') != source['sha256']:
        raise ValueError('PUBLICATION_REPLAY_RECEIPT_DIFFERS')


CHECKS = dict(zip(STAGES, (discovery, approval, inventory, proposals, verification, publication)))


def bind_sources(receipt, base):
    """Every checked fact must equal its original receipt, not producer prose.

    A JSON pointer names a value in a hash-pinned authoritative artifact.
    The bridge may rename a field; it may not invent, edit or omit its data.
    """
    fields = set(receipt) - {'pins', 'sources'}
    sources = receipt.get('sources', [])
    exactly([s.get('field') for s in sources], fields, 'AUTHORITATIVE_FIELD')
    for source in sources:
        if set(source) != {'path', 'sha256', 'field', 'pointer'}:
            raise ValueError('AUTHORITATIVE_FIELD_REFERENCE_REQUIRED')
        value = load_ref({k: source[k] for k in ('path', 'sha256')}, base)
        pointer = source['pointer']
        if not isinstance(pointer, str) or pointer and not pointer.startswith('/'):
            raise ValueError('AUTHORITATIVE_JSON_POINTER_INVALID')
        for token in pointer.split('/')[1:] if pointer else []:
            token = token.replace('~1', '/').replace('~0', '~')
            value = value[int(token)] if isinstance(value, list) else value[token]
        if value != receipt[source['field']]:
            raise ValueError('AUTHORITATIVE_FIELD_DIFFERS:' + source['field'])


def assess(manifest, pins, index=None, *, base='.', _approved_manifest=None, _scope_assets=None):
    """An incomplete estate remains runnable for diagnostics, but not scoreable."""
    if set(pins) != set(PINS) or any(not isinstance(v, str) or not v for v in pins.values()):
        raise ValueError('READINESS_CURRENT_PINS_REQUIRED')
    rows = []
    retained = {}
    valid_index = isinstance(index, dict) and index.get('version') == VERSION and index.get('pins') == pins
    for stage in STAGES:
        try:
            if not valid_index:
                raise ValueError('ONBOARDING_EVIDENCE_INDEX_MISSING_OR_STALE')
            receipt = load_ref(index['stages'][stage], base)
            bind_sources(receipt, base)
            if stage == 'discovery' and _scope_assets is not None:
                discovery(receipt, manifest, pins, scope_assets=_scope_assets)
            elif stage == 'discovery_approval' and _approved_manifest is not None:
                approval(receipt, _approved_manifest, pins)
            else:
                CHECKS[stage](receipt, manifest, pins)
            retained[stage] = receipt
            rows.append({'stage': stage, 'status': 'VERIFIED'})
        except (ValueError, KeyError, TypeError, OSError) as exc:
            rows.append({'stage': stage, 'status': 'BLOCKED', 'reason': str(exc)})
    if 'bindings' in retained and 'reader_verification' in retained:
        from .lineage_binding import seal
        planned = {seal(p) for p in retained['bindings']['proposals']}
        checked = {seal(v['proposal']) for v in retained['reader_verification']['verifications']}
        if planned != checked:
            rows[STAGES.index('reader_verification')] = {
                'stage': 'reader_verification', 'status': 'BLOCKED',
                'reason': 'PROPOSED_VERIFIED_IDENTITY_CONSERVATION_FAILED'}
    ready = all(r['status'] == 'VERIFIED' for r in rows)
    return {'version': VERSION, 'pins': dict(pins), 'status': 'READY' if ready else 'BLOCKED',
            'scoring': 'ADMITTED' if ready else 'NOT_SCORED',
            'reason': None if ready else 'estate-not-fully-onboarded', 'stages': rows,
            'estate_reads': 0, 'model_calls': 0}


def score_prospectively(score, *args, readiness, **kwargs):
    """Mandatory admission for new scores; archived replay never uses this API."""
    # A caller cannot supply a READY label. Recompute from the original index
    # and immutable receipts at scoring time; missing inputs refuse the score.
    try:
        report = assess(readiness['manifest'], readiness['pins'], readiness.get('index'),
                        base=readiness.get('base', '.'))
    except (KeyError, TypeError, ValueError):
        report = {'status': 'BLOCKED', 'reason': 'READINESS_EVIDENCE_INPUTS_REQUIRED'}
    if report['status'] != 'READY':
        return {'scoring': 'NOT_SCORED', 'reason': 'estate-not-fully-onboarded',
                'readiness': report, 'passed': None}
    return score(*args, **kwargs)


def scope_closure(dependency_inventory, roots):
    """Close a named scope over a retained adapter dependency inventory.

    This is not a best-effort walk over the discovery graph. Every discovered
    declaration has an explicit disposition, including unresolved references.
    An absent edge cannot certify that an object is a direct source.
    """
    if dependency_inventory.get('status') != 'COMPLETE':
        raise ValueError('SCOPE_DEPENDENCY_INVENTORY_INCOMPLETE')
    discovered = dependency_inventory['discovered_declarations']
    declarations = dependency_inventory['declarations']
    exactly([d['id'] for d in discovered], [d['id'] for d in declarations],
            'SCOPE_DECLARATION')
    source = {d['id']: d for d in discovered}
    nodes = dependency_inventory['nodes']
    exactly([n['asset_id'] for n in nodes], [n['asset_id'] for n in nodes],
            'SCOPE_NODE')
    by_asset = {n['asset_id']: n for n in nodes}
    by_id = {d['id']: d for d in declarations}
    listed = [item for node in nodes for item in node['declarations']]
    exactly(listed, list(by_id), 'SCOPE_NODE_DECLARATION')
    for item in declarations:
        original = source[item['id']]
        if (not isinstance(original.get('content_hash'), str) or
                not original['content_hash'] or not item.get('content_hash')):
            raise ValueError('SCOPE_DECLARATION_CONTENT_HASH_REQUIRED')
        if item.get('content_hash') != original.get('content_hash'):
            raise ValueError('SCOPE_DECLARATION_CONTENT_DIFFERS')
        owner = next(n['asset_id'] for n in nodes if item['id'] in n['declarations'])
        if original.get('owner') is not None and original['owner'] != owner:
            raise ValueError('SCOPE_DECLARATION_OWNER_DIFFERS')
        if item.get('owner') is not None and item['owner'] != owner:
            raise ValueError('SCOPE_DECLARATION_OWNER_DIFFERS')
        if item.get('disposition') not in ('RESOLVED', 'DIRECT'):
            raise ValueError('SCOPE_DECLARATION_UNSUPPORTED:' + original['form'])
        if item['disposition'] == 'DIRECT':
            if original.get('operation') != 'DIRECT_REFERENCE' or item.get('dependencies'):
                raise ValueError('SCOPE_DIRECT_SOURCE_NOT_ESTABLISHED')
        elif not item.get('dependencies'):
            raise ValueError('SCOPE_RESOLVED_DEPENDENCIES_MISSING')
    reached = set()
    pending = list(roots)
    if not pending or len(pending) != len(set(pending)):
        raise ValueError('SCOPE_ROOTS_REQUIRED')
    while pending:
        asset = pending.pop()
        if asset in reached:
            continue
        node = by_asset.get(asset)
        if node is None or not node['declarations']:
            raise ValueError('SCOPE_ASSET_DEPENDENCIES_UNESTABLISHED:' + asset)
        reached.add(asset)
        for declaration in node['declarations']:
            pending.extend(by_id[declaration].get('dependencies', []))
    return reached


def assess_named_scope(manifest, pins, index, scope_ref, *, base='.'):
    """Score only an exhaustive named dependency closure, never the estate.

    All six proofs remain required for the scoped manifest. Historical reader
    receipts do not acquire current engine compatibility just by being wrapped.
    A compatibility bridge must satisfy the same original source/pin checks.
    """
    try:
        receipt = load_ref(scope_ref, base)
        bind_sources(receipt, base)
        require_pins(receipt, pins)
        scope = receipt['scope']
        if not isinstance(scope.get('name'), str) or not scope['name']:
            raise ValueError('SCOPE_NAME_REQUIRED')
        assets = scope_closure(receipt['dependency_inventory'], scope['roots'])
        exactly(scope['assets'], assets, 'SCOPE_ASSET')
        layers = [l for l in manifest['layers'] if l['asset_id'] in assets]
        if not layers or not set(scope['roots']) <= {l['asset_id'] for l in layers}:
            raise ValueError('SCOPE_ROOT_NOT_DECLARED_LAYER')
        layer_ids = {l['id'] for l in layers}
        resources = [r for r in manifest['resources'] if r['asset_id'] in assets]
        import copy
        scoped = copy.deepcopy(manifest)
        scoped['layers'] = layers
        scoped['resources'] = resources
        # Required boundaries come from the conserved dependency closure, not
        # only a legacy manifest's explicitly hand-declared binding list. Such
        # a list can omit inferred or definition-declared boundaries entirely.
        layer_by_asset = {l['asset_id']: l['id'] for l in layers}
        declarations = {d['id']: d for d in receipt['dependency_inventory']['declarations']}
        boundaries = set()
        for node in receipt['dependency_inventory']['nodes']:
            if node['asset_id'] not in layer_by_asset:
                continue
            for identity in node['declarations']:
                for dependency in declarations[identity].get('dependencies', []):
                    if dependency in layer_by_asset and dependency != node['asset_id']:
                        boundaries.add((layer_by_asset[dependency], layer_by_asset[node['asset_id']]))
        scoped['lineage']['bindings'] = [dict(from_layer=lower, to_layer=upper)
                                       for lower, upper in sorted(boundaries)]
        report = assess(scoped, pins, index, base=base,
                        _approved_manifest=manifest, _scope_assets=assets)
        report.update(scope={'name': scope['name'], 'roots': list(scope['roots']),
                             'assets': sorted(assets), 'layers': sorted(layer_ids)},
                      estate_status='NOT_ESTABLISHED_BY_SCOPED_ASSESSMENT')
        return report
    except (ValueError, KeyError, TypeError, OSError) as exc:
        return {'version': VERSION, 'status': 'BLOCKED', 'scoring': 'NOT_SCORED',
                'reason': 'estate-not-fully-onboarded', 'detail': str(exc),
                'estate_status': 'NOT_ESTABLISHED_BY_SCOPED_ASSESSMENT',
                'estate_reads': 0, 'model_calls': 0}


def score_named_scope(score, *args, readiness, requested_assets, **kwargs):
    """A scoped READY receipt cannot be used for a different ticket scope."""
    try:
        report = assess_named_scope(readiness['manifest'], readiness['pins'],
            readiness.get('index'), readiness['scope_ref'], base=readiness.get('base', '.'))
    except (KeyError, TypeError, ValueError):
        report = {'status': 'BLOCKED', 'detail': 'SCOPED_READINESS_EVIDENCE_INPUTS_REQUIRED'}
    requested = set(requested_assets)
    if (report['status'] != 'READY' or not requested or
            not requested <= set(report.get('scope', {}).get('assets', []))):
        return {'scoring': 'NOT_SCORED', 'reason': 'estate-not-fully-onboarded',
                'scope_reason': 'REQUEST_OUTSIDE_VERIFIED_SCOPE' if report['status'] == 'READY'
                    else report.get('detail', 'SCOPE_PROOFS_NOT_COMPLETE'),
                'readiness': report, 'passed': None}
    return score(*args, **kwargs)
