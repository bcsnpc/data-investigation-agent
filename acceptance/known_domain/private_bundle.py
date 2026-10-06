"""Verify ciphertext before decrypting immutable, private replay evidence."""
import argparse
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import tarfile

MAGIC = b'DIA1'
PUBLIC_MAGIC = b'DIA2'


def recipient_key(key):
    """Domain-separated recipient key; the existing Actions secret never leaves CI."""
    if len(key) != 32:
        raise ValueError('PRIVATE_BUNDLE_KEY_LENGTH')
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from nacl.public import PrivateKey
    return PrivateKey(HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
        info=b'dia/private-replay/sealed-box-recipient/v2').derive(key))


def recipient_public_key(key):
    return bytes(recipient_key(key).public_key)


def seal_for_recipient(plain, public_key):
    """Standard libsodium sealed box; local publication needs only a public key."""
    from nacl.public import PublicKey, SealedBox
    return PUBLIC_MAGIC + SealedBox(PublicKey(public_key)).encrypt(PUBLIC_MAGIC + plain)


def hydrate(ciphertext, expected_hash, key, output, *, expected_members=61, inventory=None):
    raw = Path(ciphertext).read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_hash:
        raise ValueError('PRIVATE_BUNDLE_HASH_MISMATCH_BEFORE_DECRYPTION')
    if len(raw) < 32 or raw[:4] not in (MAGIC, PUBLIC_MAGIC):
        raise ValueError('PRIVATE_BUNDLE_FORMAT')
    if raw.startswith(PUBLIC_MAGIC):
        from nacl.public import SealedBox
        inner = SealedBox(recipient_key(key)).decrypt(raw[4:])
        if not inner.startswith(PUBLIC_MAGIC):
            raise ValueError('PRIVATE_BUNDLE_AUTHENTICATED_FORMAT')
        plain = inner[4:]
    else:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        plain = AESGCM(key).decrypt(raw[4:16], raw[16:], MAGIC)
    output = Path(output).resolve()
    if output.exists():
        raise ValueError('PRIVATE_BUNDLE_OUTPUT_ALREADY_EXISTS')
    with tarfile.open(fileobj=io.BytesIO(plain), mode='r:gz') as archive:
        members = archive.getmembers()
        if len(members) != expected_members or sum(m.size for m in members) > 3_000_000_000:
            raise ValueError('PRIVATE_BUNDLE_SIZE_OR_INVENTORY')
        if len({m.name for m in members}) != len(members):
            raise ValueError('PRIVATE_BUNDLE_DUPLICATE_MEMBER')
        for member in members:
            if (not member.isfile() or Path(member.name).is_absolute()
                    or not (output/member.name).resolve().is_relative_to(output)):
                raise ValueError('PRIVATE_BUNDLE_UNSAFE_MEMBER')
        if inventory is not None:
            actual = {m.name: hashlib.sha256(archive.extractfile(m).read()).hexdigest()
                      for m in members}
            if actual != inventory:
                raise ValueError('PRIVATE_BUNDLE_MEMBER_HASH_DIFFERS')
        output.mkdir()
        archive.extractall(output, members=members, filter='data')


def tape_path(run, fixture_root):
    """Relocate separately; sealed source files and their hashes stay unchanged."""
    root = Path(fixture_root).resolve()
    mapping_file = root/'replay-paths.json'
    if mapping_file.exists():
        mapping = json.loads(mapping_file.read_text(encoding='utf8'))
        relative = mapping.get(run['tape_path'])
        if not isinstance(relative, str):
            raise ValueError('PRIVATE_TAPE_PATH_NOT_DECLARED')
        path = (root/relative).resolve()
        if not path.is_relative_to(root) or Path(relative).is_absolute():
            raise ValueError('PRIVATE_TAPE_PATH_LEAVES_BUNDLE')
        return path
    path = Path(run['tape_path'])
    return path if path.is_absolute() else root/path


def estate_manifest(tape, fixture_root):
    """Locate the immutable installation input by its already sealed digest."""
    estate=tape.bootstrap['config'].get('_estate',{})
    enabled=any(row['may_infer_from_code'] for row in estate.get('lineage',{}).get('code_locations',[]))
    if not enabled:return None
    digest=estate.get('manifest_hash')
    import re
    if not isinstance(digest,str) or not re.fullmatch('[0-9a-f]{64}',digest):
        raise ValueError('SEALED_ESTATE_MANIFEST_HASH_INVALID')
    path=Path(fixture_root)/'estate-manifests'/(digest+'.json')
    if not path.is_file():raise ValueError('MISSING_SEALED_ESTATE_MANIFEST')
    return path


def main():
    p = argparse.ArgumentParser()
    p.add_argument('ciphertext', type=Path, nargs='?')
    p.add_argument('output', type=Path, nargs='?')
    p.add_argument('--manifest', type=Path, default=Path(__file__).parent/'private-bundle.json')
    p.add_argument('--public-key', action='store_true')
    a = p.parse_args()
    key = base64.b64decode(os.environ.pop('KNOWN_DOMAIN_REPLAY_KEY'), validate=True)
    if a.public_key:
        print('REPLAY_RECIPIENT_PUBLIC_KEY='+base64.b64encode(recipient_public_key(key)).decode('ascii'))
        return
    if a.ciphertext is None or a.output is None:
        p.error('ciphertext and output required')
    manifest = json.loads(a.manifest.read_text())
    hydrate(a.ciphertext, manifest['ciphertext_sha256'], key, a.output,
            expected_members=manifest.get('member_count',61), inventory=manifest.get('inventory'))


if __name__ == '__main__':
    main()
