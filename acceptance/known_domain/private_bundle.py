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


def hydrate(ciphertext, expected_hash, key, output):
    raw = Path(ciphertext).read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_hash:
        raise ValueError('PRIVATE_BUNDLE_HASH_MISMATCH_BEFORE_DECRYPTION')
    if not raw.startswith(MAGIC) or len(raw) < 32:
        raise ValueError('PRIVATE_BUNDLE_FORMAT')
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    plain = AESGCM(key).decrypt(raw[4:16], raw[16:], MAGIC)
    output = Path(output).resolve()
    if output.exists():
        raise ValueError('PRIVATE_BUNDLE_OUTPUT_ALREADY_EXISTS')
    with tarfile.open(fileobj=io.BytesIO(plain), mode='r:gz') as archive:
        members = archive.getmembers()
        if len(members) != 61 or sum(m.size for m in members) > 3_000_000_000:
            raise ValueError('PRIVATE_BUNDLE_SIZE_OR_INVENTORY')
        if len({m.name for m in members}) != len(members):
            raise ValueError('PRIVATE_BUNDLE_DUPLICATE_MEMBER')
        for member in members:
            if (not member.isfile() or Path(member.name).is_absolute()
                    or not (output/member.name).resolve().is_relative_to(output)):
                raise ValueError('PRIVATE_BUNDLE_UNSAFE_MEMBER')
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
    p.add_argument('ciphertext', type=Path)
    p.add_argument('output', type=Path)
    a = p.parse_args()
    manifest = json.loads((Path(__file__).parent/'private-bundle.json').read_text())
    key = base64.b64decode(os.environ.pop('KNOWN_DOMAIN_REPLAY_KEY'), validate=True)
    hydrate(a.ciphertext, manifest['ciphertext_sha256'], key, a.output)


if __name__ == '__main__':
    main()
