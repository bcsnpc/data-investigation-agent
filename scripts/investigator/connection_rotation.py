"""Explicit owner-only connection credential rotation; never an investigator tool.

The core sees credential references and metadata, never credential values.
The adapter owns application, secret-store and connection operations.
"""
import json
from pathlib import Path


class RotationIncomplete(RuntimeError):
    pass


def rotate(adapter, checkpoint, save):
    """Resume a bounded rotation. Old credential survives every partial failure.

    Checkpoints contain metadata only. The adapter must persist a new credential
    in the existing secret store before returning its opaque reference.
    """
    state = json.loads(json.dumps(checkpoint))
    state.setdefault('version', 1)
    if state['version'] != 1:
        raise ValueError('ROTATION_CHECKPOINT_VERSION')
    if state.get('status') == 'COMPLETE':
        return state
    targets = adapter.targets()
    if not targets or len(set(targets)) != len(targets):
        raise ValueError('ROTATION_TARGET_INVENTORY')
    if state.get('targets', targets) != targets:
        raise ValueError('ROTATION_TARGETS_CHANGED')
    state['targets'] = targets
    if 'before' not in state:
        state['before'] = adapter.observe()
        state['status'] = 'PREFLIGHT_RECORDED'
        save(state)
    if 'new_credential' not in state:
        state['new_credential'] = adapter.create_and_store(days=30)
        state['status'] = 'NEW_CREDENTIAL_STORED'
        save(state)
    state.setdefault('updated', [])
    state.setdefault('verified', {})
    for target in targets:
        if target not in state['updated']:
            adapter.update(target, state['new_credential'])
            state['updated'].append(target)
            state['status'] = 'CONNECTION_UPDATED'
            save(state)
        # A prior successful read cannot certify a later changed connection.
        proof = adapter.verify(target)
        if not isinstance(proof, dict) or proof.get('status') != 'PASS' or not proof.get('evidence_id'):
            state['verified'][target] = proof
            state['status'] = 'VERIFICATION_FAILED_OLD_CREDENTIAL_RETAINED'
            save(state)
            raise RotationIncomplete('CONNECTION_READ_NOT_VERIFIED:' + target)
        state['verified'][target] = proof
        save(state)
    after = adapter.observe()
    adapter.assert_unchanged_scope(state['before'], after)
    state['after_before_removal'] = after
    state['status'] = 'BOTH_VERIFIED'
    save(state)
    adapter.remove_old()
    state['after'] = adapter.observe()
    state['status'] = 'COMPLETE'
    save(state)
    return state


def main(args):
    from .adapters.connection_rotation import execute
    result = execute(Path(args.config), apply=args.apply)
    print(json.dumps(result, sort_keys=True))
    return 0 if result.get('status') in ('PLAN', 'COMPLETE') else 1
