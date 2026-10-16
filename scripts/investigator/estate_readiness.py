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
    allowed = {'READ', 'DIRECT', 'BOUNDARY', 'UNSUPPORTED'}
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
        elif entry['disposition']=='BOUNDARY':
            original=discovered[entry['id']]
            ceiling=next((b for b in manifest.get('scope_boundaries',[]) if b['asset_id']==original.get('owner')),None)
            if (original.get('operation')!='DECLARED_BOUNDARY' or ceiling is None or
                    ceiling['kind']!='REACHABILITY_CEILING' or not ceiling['unchecked_limits'] or
                    ceiling['unchecked_limits']!=original.get('unchecked_limits')):
                raise ValueError('TRANSFORMATION_COMPARISON_CEILING_UNESTABLISHED')
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


def declared_routes(receipt, manifest):
    routes=receipt.get('declared_routes', [])
    if not routes:
        return []
    from .adapters.readiness_registry import declared_route_validator
    check=declared_route_validator(manifest)
    checked=[check(route,manifest=manifest,scan=receipt['scan']) for route in routes]
    exactly([r['route_identity'] for r in checked],[r['route_identity'] for r in checked],'DECLARED_ROUTE_IDENTITY')
    return checked


def proposals(receipt, manifest, pins, *, runtime_manifest=None):
    require_pins(receipt, pins)
    from .lineage_binding import validate
    rows = [validate(p) for p in receipt['proposals']]
    expected = [boundary(b) for b in manifest['lineage']['bindings']]
    # Several quantity/key bindings at one boundary are legitimate; coverage
    # is over boundaries, while conservation/uniqueness is over full proposals.
    from .lineage_binding import seal
    exactly([seal(p) for p in rows], [seal(p) for p in rows], 'PROPOSAL_IDENTITY')
    direct=declared_routes(receipt,runtime_manifest or manifest)
    if {boundary(p['boundary']) for p in rows}|{boundary(r['boundary']) for r in direct} != set(expected):
        raise ValueError('PROPOSED_BINDING_CONSERVATION_FAILED')
    if not expected:
        raise ValueError('NO_EXECUTABLE_BINDING_INVENTORY')


def verification(receipt, manifest, pins, *, runtime_manifest=None):
    require_pins(receipt, pins)
    from .lineage_binding import revalidate_verification
    rows = receipt['verifications']
    from .lineage_binding import seal
    exactly([seal(v['proposal']) for v in rows], [seal(v['proposal']) for v in rows], 'VERIFICATION_IDENTITY')
    direct=declared_routes(receipt,runtime_manifest or manifest)
    if {boundary(v['proposal']['boundary']) for v in rows}|{boundary(r['boundary']) for r in direct} != {
            boundary(b) for b in manifest['lineage']['bindings']}:
        raise ValueError('VERIFIED_BINDING_CONSERVATION_FAILED')
    for original in rows:
        checked = revalidate_verification(original)
        if checked.get('status') != 'VERIFIED':
            raise ValueError('BINDING_NOT_VERIFIED')
        if original['context'] not in receipt['model_contexts'].values():
            recompile_retained_proposal(original['proposal'],receipt.get('compatible_code_units',[]))
        for observation in original['observations']:
            # Revalidation owns quantity/attestation gates. The readiness gate
            # additionally requires native retained reader receipts, not a
            # model's assertion that a simulated read was live.
            evidence = observation.get('evidence', {})
            if observation.get('status') != 'COMPLETED' or not evidence.get('id') or evidence.get('surface_report_binding') != 'VALUE_QUERY':
                raise ValueError('LIVE_READER_RECEIPT_MISSING')


def recompile_retained_proposal(proposal, units):
    """Old context proof is reusable only for an identical current code plan.

    The old context and observation are never rewritten as current. This is a
    component compatibility check, not a new value or snapshot observation.
    """
    from .transformation_reader import static
    from .lineage_binding import seal
    location=proposal['location']
    matched=[]
    for entry in units:
        raw=Path(entry['source_path']).read_bytes()
        unit=entry['unit']
        if sha(raw)!=unit['content_hash'] or unit['content_hash']!=location['content_hash']:
            continue
        # Whole-file cells must actually be the retained file, not a producer's
        # replacement program with a borrowed content-hash label.
        text=raw.decode('utf8').replace('\r\n','\n').replace('\r','\n')
        if (len(unit['cells'])!=1 or unit['cells'][0]['source']!=text or
                unit['cells'][0]['line_start']!=1 or
                unit['cells'][0]['line_end']!=len(text.splitlines())):
            continue
        found=static(unit,schemas=entry['schemas'],boundary=proposal['boundary'],
            item=location['item'],target_table=proposal['target']['table'])['proposals']
        for candidate in found:
            # Capture-relative paths and whole-file cell labels are recorder
            # provenance. The exact file hash, source span, item and entire
            # compiled plan still have to match; no original witness changes.
            location = dict(candidate['location'])
            for label in ('path', 'cell'):
                location[label] = proposal['location'][label]
            comparable = dict(candidate, location=location)
            if seal(comparable) == seal(proposal):
                matched.append(candidate)
    if len(matched)!=1:
        raise ValueError('VERIFICATION_CONTEXT_COMPONENT_COMPATIBILITY_UNESTABLISHED')


def binding_identity(proposal):
    """Physical plan identity; recorder path/cell labels are provenance, not plan."""
    return sha(json.dumps({k:proposal[k]for k in ('boundary','sources','target','expression')}
        |{'binding_kind':proposal.get('binding_kind'),'code_hash':proposal['location']['content_hash']},
        sort_keys=True,separators=(',',':')).encode())


def required_code_binding_identities(receipt,manifest,scope_inventory):
    from .transformation_reader import static
    from .adapters.readiness_registry import required_native_bindings
    scan=receipt['scan'];assets=scan['assets'];by_id={a['id']:a for a in assets}
    layer_parent={by_id[l['asset_id']].get('parent_id'):l['id']for l in manifest['layers']}
    entries={e['id']:e for e in scope_inventory['declarations']}
    result=required_native_bindings(receipt,manifest,scope_inventory)
    for declaration in scope_inventory['discovered_declarations']:
        if declaration['form']!='STATIC_WRITER':continue
        entry=entries[declaration['id']]
        if entry['disposition']=='BOUNDARY':continue
        owner=by_id[declaration['owner']];target=owner['metadata']['location']
        lower={layer_parent[by_id[a].get('parent_id')]for a in entry['dependencies']}
        if len(lower)!=1:raise ValueError('SCOPED_CODE_WRITER_BOUNDARY_UNESTABLISHED')
        boundary_row={'from_layer':lower.pop(),'to_layer':layer_parent[owner.get('parent_id')]}
        units=[u for u in receipt['compatible_code_units']if u['unit']['content_hash']==declaration['code_hash']]
        if len(units)!=1:raise ValueError('SCOPED_CODE_UNIT_UNESTABLISHED')
        unit=units[0];raw=Path(unit['source_path']).read_bytes();text=raw.decode('utf8').replace('\r\n','\n').replace('\r','\n')
        if sha(raw)!=unit['unit']['content_hash'] or len(unit['unit']['cells'])!=1 or unit['unit']['cells'][0]['source']!=text:
            raise ValueError('SCOPED_CODE_UNIT_CONTENT_DIFFERS')
        found=static(unit['unit'],schemas=unit['schemas'],boundary=boundary_row,
            item='readiness',target_table=target)['proposals']
        if not found:raise ValueError('SCOPED_CODE_WRITER_PROPOSALS_MISSING')
        result.extend(binding_identity(p)for p in found)
    return result


def publication(receipt, manifest, pins, *, runtime_manifest=None):
    require_pins(receipt, pins)
    if receipt.get('publication',{}).get('kind') == 'RETAINED_EXECUTION':
        return retained_execution_publication(receipt,runtime_manifest or manifest)
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


def retained_execution_publication(receipt,manifest):
    """Declared routes need retained execution, not a fictitious profile append.

    Every reused witness must occur in original capture bytes associated with
    a retained successful offline replay. This does not replace observations,
    publish a runtime inferred binding, or claim fresh data currency.
    """
    import base64
    values=[]
    def visit(value):
        if isinstance(value,dict):
            values.append(value)
            for key,item in value.items():
                visit(item)
                if key=='body' and isinstance(item,str):
                    try:visit(json.loads(base64.b64decode(item)))
                    except (ValueError,TypeError,UnicodeDecodeError):pass
        elif isinstance(value,list):
            for item in value:visit(item)
    executions=receipt['publication']['executions']
    if not executions:raise ValueError('PUBLICATION_EXECUTION_RECEIPTS_REQUIRED')
    for execution in executions:
        capture=load_ref(execution['capture_ref'],'.')
        from .process_tape import Tape
        Tape(execution['capture_ref']['path'])
        run=load_ref(execution['run_ref'],'.')
        replay=load_ref(execution['replay_ref'],'.')
        if Path(run['tape_path']).resolve()!=Path(execution['capture_ref']['path']).resolve():
            raise ValueError('PUBLICATION_REPLAY_CAPTURE_DIFFERS')
        if replay.get('matched') is not True or replay.get('status')!='COMPLETED' or replay.get('network_requests')!=0:
            raise ValueError('PROFILE_OFFLINE_REPLAY_NOT_MATCHED')
        bootstraps=[json.loads(base64.b64decode(e['body'])) for e in capture['events'] if e['kind']=='BOOTSTRAP']
        if len(bootstraps)!=1 or not bootstraps[0].get('engine_hash') or replay.get('recorded_engine_hash')!=bootstraps[0]['engine_hash']:
            raise ValueError('PUBLICATION_REPLAY_ENGINE_DIFFERS')
        final=json.loads(base64.b64decode(capture['events'][-1]['body']))
        captured_hash=replay.get('capture_sha256')
        if captured_hash is not None:
            if captured_hash!=execution['capture_ref']['sha256']:
                raise ValueError('PUBLICATION_REPLAY_CAPTURE_HASH_DIFFERS')
        elif (not isinstance(final.get('result'),dict)or not final['result'].get('id') or
              replay.get('session')!=final['result'] or replay.get('outputs')!=final.get('outputs')):
            # Historical receipts predate an input-hash field. Exact native
            # FINAL/session/outputs (including unique read IDs) associate them;
            # this is expressly narrower than a recorded full-capture hash.
            raise ValueError('PUBLICATION_LEGACY_FINAL_ASSOCIATION_UNESTABLISHED')
        visit(capture['events'])
    for witness in receipt['verifications']:
        if not any(witness==value for value in values):
            raise ValueError('PUBLISHED_WITNESS_NOT_IN_REPLAYED_CAPTURE')
    direct=declared_routes(receipt,manifest)
    for route in receipt.get('declared_routes',[]):
        for observation in route['selected_observations']:
            if not any(observation==value for value in values):
                raise ValueError('PUBLISHED_DECLARED_READ_NOT_IN_REPLAYED_CAPTURE')
    if not receipt['verifications'] and not direct:
        raise ValueError('NO_EXECUTED_READINESS_ROUTES')


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


def assess(manifest, pins, index=None, *, base='.', _approved_manifest=None, _scope_assets=None, _scope_inventory=None):
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
            elif stage in ('bindings','reader_verification','publication') and _approved_manifest is not None:
                CHECKS[stage](receipt,manifest,pins,runtime_manifest=_approved_manifest)
            else:
                CHECKS[stage](receipt, manifest, pins)
            retained[stage] = receipt
            rows.append({'stage': stage, 'status': 'VERIFIED'})
        except (ValueError, KeyError, TypeError, OSError) as exc:
            rows.append({'stage': stage, 'status': 'BLOCKED', 'reason': str(exc)})
    if 'bindings' in retained and 'reader_verification' in retained:
        from .lineage_binding import seal
        planned = {seal(p) for p in retained['bindings']['proposals']}|{
            r['route_identity'] for r in declared_routes(retained['bindings'],_approved_manifest or manifest)}
        checked = {seal(v['proposal']) for v in retained['reader_verification']['verifications']}|{
            r['route_identity'] for r in declared_routes(retained['reader_verification'],_approved_manifest or manifest)}
        if planned != checked:
            rows[STAGES.index('reader_verification')] = {
                'stage': 'reader_verification', 'status': 'BLOCKED',
                'reason': 'PROPOSED_VERIFIED_IDENTITY_CONSERVATION_FAILED'}
    if _scope_inventory is not None and 'transformations' in retained and 'bindings' in retained:
        try:
            required=required_code_binding_identities(retained['transformations'],manifest,_scope_inventory)
            exactly([binding_identity(p)for p in retained['bindings']['proposals']],required,'SCOPED_CODE_BINDING')
        except (ValueError,KeyError,TypeError,OSError)as exc:
            rows[STAGES.index('bindings')]={'stage':'bindings','status':'BLOCKED','reason':str(exc)}
    ready = all(r['status'] == 'VERIFIED' for r in rows)
    admitted_constraints=[]
    if ready:
        for route in declared_routes(retained.get('reader_verification',{}),_approved_manifest or manifest):
            admitted_constraints.append(route['constraints'])
    return {'version': VERSION, 'pins': dict(pins), 'status': 'READY' if ready else 'BLOCKED',
            'scoring': 'ADMITTED' if ready else 'NOT_SCORED',
            'reason': None if ready else 'estate-not-fully-onboarded', 'stages': rows,
            'admitted_constraints':admitted_constraints,
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
        if item.get('disposition') not in ('RESOLVED', 'DIRECT', 'BOUNDARY'):
            raise ValueError('SCOPE_DECLARATION_UNSUPPORTED:' + original['form'])
        if item['disposition'] == 'DIRECT':
            if original.get('operation') != 'DIRECT_REFERENCE' or item.get('dependencies'):
                raise ValueError('SCOPE_DIRECT_SOURCE_NOT_ESTABLISHED')
        elif item['disposition'] == 'BOUNDARY':
            # A declared reachability ceiling is not a claim of direct source
            # identity. Its inputs remain expressly unchecked.
            if (original.get('operation') != 'DECLARED_BOUNDARY' or
                    item.get('dependencies') or
                    not isinstance(original.get('unchecked_limits'), list) or
                    not original['unchecked_limits'] or
                    any(not isinstance(v, str) or not v.strip()
                        for v in original['unchecked_limits']) or
                    item.get('unchecked_limits') != original['unchecked_limits']):
                raise ValueError('SCOPE_BOUNDARY_NOT_ESTABLISHED')
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
        declared_boundaries = {b['asset_id']: b for b in manifest.get('scope_boundaries', [])}
        for item in receipt['dependency_inventory']['declarations']:
            if item['disposition'] != 'BOUNDARY':
                continue
            original = next(d for d in receipt['dependency_inventory']['discovered_declarations']
                            if d['id'] == item['id'])
            owner = next(n['asset_id'] for n in receipt['dependency_inventory']['nodes']
                         if item['id'] in n['declarations'])
            boundary = declared_boundaries.get(owner)
            if (boundary is None or boundary.get('unchecked_limits') != original['unchecked_limits'] or
                    boundary.get('kind') != 'REACHABILITY_CEILING'):
                raise ValueError('SCOPE_BOUNDARY_NOT_DECLARED_IN_MANIFEST')
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
                        _approved_manifest=manifest, _scope_assets=assets,
                        _scope_inventory=receipt['dependency_inventory'])
        constraints=scope.get('constraints')
        if constraints is not None:
            validate_scope_constraints(constraints)
            if report['status']=='READY' and constraints not in report.get('admitted_constraints',[]):
                raise ValueError('SCOPE_QUANTITY_CONSTRAINTS_NOT_ESTABLISHED_BY_DECLARED_ROUTE')
        report.update(scope={'name': scope['name'], 'roots': list(scope['roots']),
                             'assets': sorted(assets), 'layers': sorted(layer_ids),
                             'constraints': scope.get('constraints'),
                             'limits': scope.get('limits', [])},
                      estate_status='NOT_ESTABLISHED_BY_SCOPED_ASSESSMENT')
        return report
    except (ValueError, KeyError, TypeError, OSError) as exc:
        return {'version': VERSION, 'status': 'BLOCKED', 'scoring': 'NOT_SCORED',
                'reason': 'estate-not-fully-onboarded', 'detail': str(exc),
                'estate_status': 'NOT_ESTABLISHED_BY_SCOPED_ASSESSMENT',
                'estate_reads': 0, 'model_calls': 0}


def score_named_scope(score, *args, readiness, requested_assets, requested_scope=None, **kwargs):
    """A scoped READY receipt cannot be used for a different ticket scope."""
    try:
        report = assess_named_scope(readiness['manifest'], readiness['pins'],
            readiness.get('index'), readiness['scope_ref'], base=readiness.get('base', '.'))
    except (KeyError, TypeError, ValueError):
        report = {'status': 'BLOCKED', 'detail': 'SCOPED_READINESS_EVIDENCE_INPUTS_REQUIRED'}
    requested = set(requested_assets)
    constraints = report.get('scope', {}).get('constraints')
    try:validate_scope_constraints(constraints);scope_matches=requested_scope==constraints
    except (ValueError,TypeError):scope_matches=False
    if (report['status'] != 'READY' or not requested or not scope_matches or
            not requested <= set(report.get('scope', {}).get('assets', []))):
        return {'scoring': 'NOT_SCORED', 'reason': 'estate-not-fully-onboarded',
                'scope_reason': 'REQUEST_OUTSIDE_VERIFIED_SCOPE' if report['status'] == 'READY'
                    else report.get('detail', 'SCOPE_PROOFS_NOT_COMPLETE'),
                'readiness': report, 'passed': None}
    return score(*args, **kwargs)


def validate_scope_constraints(value):
    if not isinstance(value,dict) or set(value)!={'kind','measure_ids','filters','dimension_ids'}:
        raise ValueError('SCOPE_QUANTITY_CONSTRAINTS_REQUIRED')
    measures=value['measure_ids']
    if (value['kind']!='WHOLE_ENTITY_QUANTITY' or value['filters']!=[] or
            value['dimension_ids']!=[] or not isinstance(measures,list) or not measures or
            any(not isinstance(v,str)or not v for v in measures)or len(measures)!=len(set(measures))):
        raise ValueError('SCOPE_QUANTITY_CONSTRAINTS_UNSUPPORTED')
    return value
