"""Sampled declared-lineage approval, separate from the client manifest.

Approval executes the same verifier as inference. The record is scoped to the
whole manifest and retained sample; declared edges without evidence never pass.
"""
import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from .lineage_binding import verify, require_declared_approval, seal, validate, revalidate_verification, VerificationHold

VERSION='sampled-lineage-approval-v1'


def approve(manifest, *, samples, compiler, execute, ledger, destination, now=None):
    """Verify every declared edge, retaining failures before refusing approval.

    samples is an adapter-produced list of executable code declarations and
    existing cell addresses, not figures or an approval verdict from a model.
    The compiler independently checks objects, connections and the selected cell.
    """
    destination=Path(destination)
    if destination.exists():raise FileExistsError('Lineage approval already exists: '+str(destination))
    expected={(b['from_layer'],b['to_layer']) for b in manifest['lineage']['bindings']}
    planned=[]
    for sample in samples:
        if set(sample)!={'proposal','context','cell','precision'}:
            raise ValueError('Declared approval sample: expected proposal, context, cell and precision only')
        p=validate(sample['proposal'])
        edge=(p['boundary']['from_layer'],p['boundary']['to_layer'])
        if edge not in expected:
            raise ValueError('Approval sample is not a configured declared binding: '+str(edge))
        planned.append((edge,copy.deepcopy(sample)))
    covered={edge for edge,_ in planned}
    if covered!=expected:
        raise ValueError('Declared approval has no executable sample for: '+str(sorted(expected-covered)))
    results=[]
    for _,sample in planned:
        try:
            result=verify(sample['proposal'],context=sample['context'],cell=sample['cell'],
                precision=sample['precision'],compiler=compiler,execute=execute)
        except VerificationHold as exc:
            ledger.append(exc.verification)
            raise
        ledger.append(result)
        results.append(result)
    require_declared_approval(results)
    record={'version':VERSION,'manifest_hash':seal(manifest),
        'approved_at':now or datetime.now(timezone.utc).isoformat(),
        'declared_verifications':results,
        'limitation':'Approval verifies only the recorded quantity, context, cell and precision; it does not certify global equivalence or aligned snapshots.'}
    wrapped={'approval':record,'sha256':seal(record)}
    destination=Path(destination)
    destination.parent.mkdir(parents=True,exist_ok=True)
    # One immutable approval per destination. New approvals require a new file.
    with destination.open('x',encoding='utf8') as stream:
        json.dump(wrapped,stream,sort_keys=True,indent=2)
    return wrapped


def read_approval(path,manifest):
    wrapped=json.loads(Path(path).read_text(encoding='utf8'))
    if set(wrapped)!={'approval','sha256'} or seal(wrapped['approval'])!=wrapped['sha256']:
        raise ValueError('Lineage approval integrity differs')
    record=wrapped['approval']
    if set(record)!={'version','manifest_hash','approved_at','declared_verifications','limitation'} or record['version']!=VERSION:
        raise ValueError('Unknown lineage approval contract')
    if record['manifest_hash']!=seal(manifest):
        raise ValueError('Lineage approval belongs to a different manifest')
    expected={(b['from_layer'],b['to_layer']) for b in manifest['lineage']['bindings']}
    covered=set()
    for result in record['declared_verifications']:
        require_declared_approval([result])
        check=revalidate_verification(result)
        require_declared_approval([check])
        p=check['proposal'];covered.add((p['boundary']['from_layer'],p['boundary']['to_layer']))
    if covered!=expected:raise ValueError('Declared approval does not cover exactly the configured bindings')
    return copy.deepcopy(record)
