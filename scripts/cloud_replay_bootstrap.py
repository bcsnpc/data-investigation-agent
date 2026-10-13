"""Fixed, hash-pinned historical replay bootstrap; no arbitrary command input."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HELPERS = ('acceptance/unknown_domain/recorded_engine.py',
           'acceptance/unknown_domain/lineage_replay.py',
           'acceptance/unknown_domain/catalog_replay.py',
           'scripts/investigator/budget_tape_contract.py',
           'scripts/investigator/provider_tape_contract.py')


def validate(config):
    from investigator.adapters.cloud_replay_transport import endpoint
    from investigator.adapters.managed_identity import validate as identity
    fields = {'version', 'input_url', 'input_sha256', 'result_url', 'identity', 'channel',
              'max_download_bytes', 'max_expanded_bytes', 'shard', 'shards'}
    if not isinstance(config, dict) or set(config) != fields or config['version'] != 1:
        raise ValueError('REPLAY_BOOTSTRAP_CONFIG')
    endpoint(config['input_url']); endpoint(config['result_url']); identity(config['identity'])
    if not config['input_url'].endswith('.tar.gz') or not config['result_url'].endswith('.json'):
        raise ValueError('REPLAY_ARTIFACT_TYPE')
    if not re.fullmatch('[0-9a-f]{64}', config['input_sha256']):
        raise ValueError('REPLAY_INPUT_HASH_REQUIRED')
    if not re.fullmatch('[A-Za-z0-9_-]{1,80}', config['channel']):
        raise ValueError('REPLAY_CHANNEL_REQUIRED')
    for field in ('max_download_bytes', 'max_expanded_bytes'):
        if type(config[field]) is not int or not 0 < config[field] <= 20 * 1024**3:
            raise ValueError('REPLAY_SIZE_BOUND')
    from cloud_offline_worker import partition
    partition([], config['shard'], config['shards'])
    return config


def download(stream, destination, digest, maximum):
    actual = hashlib.sha256(); count = 0
    with Path(destination).open('xb') as output:
        while block := stream.read(1024 * 1024):
            count += len(block)
            if count > maximum:
                raise ValueError('REPLAY_DOWNLOAD_OVERSIZE')
            output.write(block); actual.update(block)
    if actual.hexdigest() != digest:
        raise ValueError('REPLAY_DOWNLOAD_HASH_MISMATCH')
    return count


def extract(archive, destination, maximum):
    """Never use extractall: only bounded ordinary files at declared roots."""
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    total = 0; seen = set()
    with tarfile.open(archive, 'r|gz') as bundle:
        for member in bundle:
            name = member.name
            parts = PurePosixPath(name).parts
            if (not parts or name.startswith('/') or '\\' in name or ':' in name
                    or any(part in ('.', '..', '.git') for part in parts)
                    or name in seen or len(seen) >= 100000):
                raise ValueError('REPLAY_UNSAFE_ARCHIVE_PATH')
            allowed = name in ('engine.bundle', 'replay-manifest.json') or parts[0] == 'evidence'
            if not allowed or not (member.isfile() or member.isdir()):
                raise ValueError('REPLAY_UNSAFE_ARCHIVE_MEMBER')
            seen.add(name)
            target = destination.joinpath(*parts)
            if not target.resolve().is_relative_to(destination):
                raise ValueError('REPLAY_ARCHIVE_ESCAPE')
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True); continue
            total += member.size
            if member.size < 0 or total > maximum:
                raise ValueError('REPLAY_EXPANDED_OVERSIZE')
            target.parent.mkdir(parents=True, exist_ok=True)
            source = bundle.extractfile(member)
            with target.open('xb') as output:
                shutil.copyfileobj(source, output, 1024 * 1024)
    if not (destination / 'engine.bundle').is_file() or not (destination / 'replay-manifest.json').is_file():
        raise ValueError('REPLAY_PACKAGE_INCOMPLETE')
    return total


def prepare_repo(package, repo, env):
    from cloud_offline_worker import sealed_file
    manifest = json.loads((package / 'replay-manifest.json').read_bytes())
    if set(manifest) != {'version', 'entries'} or manifest['version'] != 1 or not 1 <= len(manifest['entries']) <= 10000:
        raise ValueError('REPLAY_MANIFEST')
    revisions = set()
    for entry in manifest['entries']:
        revision = entry.get('engine_revision', '')
        if not re.fullmatch('[0-9a-f]{40}', revision):
            raise ValueError('REPLAY_REVISION')
        sealed_file(package / 'evidence', entry['tape_path'], entry['tape_sha256'])
        revisions.add(revision)
    repo.mkdir()
    subprocess.run(['git', 'init', '--quiet', str(repo)], check=True, env=env, capture_output=True)
    # A Git bundle carries objects and refs but not the sender's shallow file.
    # Each approved immutable revision is the boundary; no parent is required
    # for git archive or byte replay and no parent may be fetched from a network.
    (repo / '.git/shallow').write_text('\n'.join(sorted(revisions)) + '\n', encoding='ascii')
    for revision in sorted(revisions):
        subprocess.run(['git', '-c', 'protocol.file.allow=always', 'fetch', '--no-tags', '--update-shallow',
                        str(package / 'engine.bundle'), revision], cwd=repo, env=env,
                       check=True, capture_output=True, timeout=120)
    for relative in HELPERS:
        target = repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)


def execute(config, *, transport=None):
    config = validate(config)
    if transport is None:
        from investigator.adapters.cloud_replay_transport import Transport
        transport = Transport(config['identity'], config['channel'])
    with tempfile.TemporaryDirectory(prefix='dia-cloud-replay-') as folder:
        root = Path(folder); archive = root / 'input.tar.gz'; package = root / 'package'
        with transport.request(config['input_url']) as stream:
            received = download(stream, archive, config['input_sha256'], config['max_download_bytes'])
        expanded = extract(archive, package, config['max_expanded_bytes'])
        # No ambient Azure credentials, live estate paths, Python hooks or Git configuration
        # propagate into the replay subprocess. Authentication remains in this parent only.
        env = {key: os.environ[key] for key in ('PATH', 'SYSTEMROOT', 'TEMP', 'TMP') if key in os.environ}
        env.update({'DIA_LIVE_ACCESS_DISABLED': '1', 'GIT_CONFIG_NOSYSTEM': '1',
                    'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_TERMINAL_PROMPT': '0'})
        repo = root / 'repo'; prepare_repo(package, repo, env)
        output = root / 'results'
        command = [sys.executable, str(ROOT / 'scripts/cloud_offline_worker.py'), '--mode', 'replay',
                   '--repo', str(repo), '--manifest', str(package / 'replay-manifest.json'),
                   '--evidence', str(package / 'evidence'), '--output', str(output),
                   '--shard', str(config['shard']), '--shards', str(config['shards'])]
        done = subprocess.run(command, env=env, cwd=root, capture_output=True, timeout=7500)
        answer = json.loads((output / f"shard-{config['shard']}.json").read_bytes())
        # Deliberately no ticket IDs, provider bodies, output prose, URLs or exception messages.
        result = {key: answer[key] for key in ('mode', 'shard', 'shards', 'count', 'matched',
                                             'network_requests', 'physical_requests')}
        result.update({'input_sha256': config['input_sha256'], 'download_bytes': received,
                       'expanded_bytes': expanded, 'worker_exit': done.returncode,
                       'claim': 'Exact historical engine replay; not acceptance grading.'})
        encoded = json.dumps(result, sort_keys=True).encode()
        with transport.request(config['result_url'], encoded):
            pass
        print(encoded.decode())
        return 0 if done.returncode == 0 and result['matched'] == result['count'] else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    try:
        return execute(json.loads(args.config.read_bytes()))
    except Exception as exc:
        print(json.dumps({'mode': 'SEALED_REPLAY_BOOTSTRAP_FAILED', 'error_type': type(exc).__name__}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
