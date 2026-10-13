"""Explicit, privacy-reviewed cold archive plans; never deletes local evidence."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile
import zlib

from .artifact_store import ArtifactError, canonical, digest, hash_id

VERSION = 'finished-round-archive-v1'
ENCODINGS = frozenset({'identity','gzip'})
STREAM_BLOCK = 1024 * 1024
ROUNDS = ('five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen')
from .adapters.platform_credentials import CREDENTIAL_PATH_WORDS
SENSITIVE = re.compile(r'(^|[/_.-])(' + CREDENTIAL_PATH_WORDS + r')([/_.-]|$)', re.I)
LIVE = re.compile(r'(model[-_]spend|shared[-_](?:accounting|catalog)|(?:budget|usage|pot|ledger)(?:[-_.]|$))', re.I)
SECRET_BYTES = re.compile(rb'-----BEGIN [A-Z ]*PRIVATE KEY-----|Bearer\s+[A-Za-z0-9._~-]{16,}|'
                          rb'eyJ[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}|'
                          rb'(?:password|api[_-]?key|client[_-]?secret|AccountKey)\s*[=:]\s*["\x27]?[^\s"\x27;,}]{6,}', re.I)


def sha_file(path):
    whole=hashlib.sha256()
    with Path(path).open('rb') as stream:
        while block:=stream.read(1024*1024):whole.update(block)
    return whole.hexdigest()


def bounded_path(workspace, relative):
    workspace=Path(workspace).resolve(strict=True)
    name=Path(relative)
    if name.is_absolute() or '..' in name.parts or any(ord(c)<32 for c in str(name)):
        raise ArtifactError('ARCHIVE_PATH_OUTSIDE_WORKSPACE')
    candidate=workspace/name
    # Reject links/junctions rather than trusting resolve() to follow them.
    cursor=candidate
    while cursor!=workspace:
        info=cursor.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info,'st_file_attributes',0)&0x400:
            raise ArtifactError('ARCHIVE_REPARSE_POINT_REFUSED')
        cursor=cursor.parent
    resolved=candidate.resolve(strict=True)
    if not resolved.is_relative_to(workspace) or not resolved.is_file():
        raise ArtifactError('ARCHIVE_PATH_OUTSIDE_WORKSPACE')
    return resolved


def eligible(relative):
    parts=Path(relative).parts
    if len(parts)<3 or parts[0]!='.local':return False
    folder=parts[1]
    return folder=='process-tapes' or any(folder==f'round-{n}' or folder.startswith(f'round-{n}-') for n in ROUNDS)


def protected_path(relative, protected):
    normalized=Path(relative).as_posix().casefold()
    if any(normalized==Path(p).as_posix().casefold() for p in protected):return True
    if LIVE.search(Path(relative).name):return True
    # Catalogs are eligible only inside sealed tape directories, not shared roots.
    if Path(relative).name.casefold() in ('catalog.sqlite','inventory.sqlite'):
        return 'process-tapes' not in Path(relative).parts and not any(
            p in ('tapes','captures','replays') for p in Path(relative).parts)
    return False


def privacy_reason(path, relative):
    if SENSITIVE.search(Path(relative).as_posix()) or Path(relative).suffix.lower() in ('.pfx','.pem','.key','.clixml'):
        return 'SENSITIVE_PATH'
    if Path(relative).suffix.lower() in ('.zip','.gz','.7z','.tar','.bz2','.xz','.enc'):
        return 'OPAQUE_CONTAINER_REQUIRES_SEPARATE_REVIEW'
    tail=b''
    with Path(path).open('rb') as stream:
        while block:=stream.read(1024*1024):
            combined=tail+block
            if SECRET_BYTES.search(combined):return 'CREDENTIAL_PATTERN'
            tail=combined[-4096:]
    return None


def sealed_snapshot_reason(path):
    if Path(path).name.casefold() not in ('catalog.sqlite','inventory.sqlite'):return None
    try:
        from .process_tape import Tape
        Tape(Path(path).parent/'tape.json')
    except (ValueError, OSError, KeyError, TypeError):
        return 'SNAPSHOT_WITHOUT_VALID_SEALED_TAPE'
    return None


def plan(workspace, relative_files, *, protected, finished_statement, storage_encoding='identity'):
    if storage_encoding not in ENCODINGS:raise ArtifactError('ARCHIVE_STORAGE_ENCODING')
    if not finished_statement or not isinstance(protected,list):
        raise ArtifactError('FINISHED_SCOPE_AND_PROTECTED_PATHS_REQUIRED')
    workspace=Path(workspace).resolve(strict=True)
    entries=[];excluded=[]
    for relative in sorted(set(relative_files)):
        path=bounded_path(workspace,relative)
        reason=('OUTSIDE_FINISHED_ROUNDS' if not eligible(relative) else
                'LIVE_STATE_PROTECTED' if protected_path(relative,protected) else
                sealed_snapshot_reason(path) or privacy_reason(path,relative))
        if reason:
            excluded.append({'path':Path(relative).as_posix(),'reason':reason});continue
        before=path.stat();identity=sha_file(path);after=path.stat()
        if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):
            raise ArtifactError('ARCHIVE_SOURCE_CHANGED_DURING_PLAN')
        entries.append({'path':Path(relative).as_posix(),'sha256':identity,'bytes':after.st_size})
    result={'version':VERSION,'workspace':str(workspace),'created_at':datetime.now(timezone.utc).isoformat(),
            'finished_statement':finished_statement,'protected_paths':sorted(protected),
            'privacy_status':'QUARANTINED_PENDING_REVIEW','entries':entries,'excluded':excluded}
    if storage_encoding!='identity':result['storage_encoding']=storage_encoding
    return result


def load_pinned(path, expected_sha):
    hash_id(expected_sha)
    raw=Path(path).read_bytes()
    if digest(raw)!=expected_sha:raise ArtifactError('ARCHIVE_MANIFEST_SHA_DIFFERS')
    manifest=json.loads(raw)
    if manifest.get('version')!=VERSION or manifest.get('privacy_status')!='QUARANTINED_PENDING_REVIEW':
        raise ArtifactError('ARCHIVE_MANIFEST_SCHEMA')
    if manifest.get('storage_encoding','identity') not in ENCODINGS:raise ArtifactError('ARCHIVE_STORAGE_ENCODING')
    if not isinstance(manifest.get('protected_paths'),list) or not manifest.get('finished_statement'):
        raise ArtifactError('ARCHIVE_PROTECTION_RECORD_REQUIRED')
    seen=set()
    for entry in manifest['entries']:
        if set(entry)!={'path','sha256','bytes'} or entry['path'] in seen:
            raise ArtifactError('ARCHIVE_ENTRY_SCHEMA')
        seen.add(entry['path']);hash_id(entry['sha256'])
        if type(entry['bytes']) is not int or entry['bytes']<0:raise ArtifactError('ARCHIVE_ENTRY_SIZE')
        if not eligible(entry['path']) or protected_path(entry['path'],manifest['protected_paths']):
            raise ArtifactError('ARCHIVE_PROTECTED_PATH')
    return manifest


def privacy_approved(review, manifest_sha):
    if (not isinstance(review,dict) or review.get('status')!='APPROVED' or
        review.get('manifest_sha256')!=manifest_sha or not review.get('reviewer') or not review.get('basis')):
        raise ArtifactError('ARCHIVE_PRIVACY_REVIEW_REQUIRED')


def verify_local(manifest, entry):
    path=bounded_path(manifest['workspace'],entry['path'])
    if protected_path(entry['path'],manifest['protected_paths']) or sealed_snapshot_reason(path) or privacy_reason(path,entry['path']):
        raise ArtifactError('ARCHIVE_PROTECTED_OR_QUARANTINED')
    if path.stat().st_size!=entry['bytes'] or sha_file(path)!=entry['sha256']:
        raise ArtifactError('ARCHIVE_LOCAL_HASH_DIFFERS')
    return path


def encoded_chunks(path, encoding, stats):
    """Bounded streaming gzip, no whole-file buffer or temporary archive."""
    if encoding not in ENCODINGS:raise ArtifactError('ARCHIVE_STORAGE_ENCODING')
    encoder=zlib.compressobj(level=6,wbits=31) if encoding=='gzip' else None
    whole=hashlib.sha256();size=0
    with Path(path).open('rb') as stream:
        while block:=stream.read(STREAM_BLOCK):
            out=encoder.compress(block) if encoder else block
            if out:
                whole.update(out);size+=len(out);yield out
        if encoder:
            out=encoder.flush()
            whole.update(out);size+=len(out);yield out
    stats.update(stored_bytes=size,stored_sha256=whole.hexdigest(),stream_complete=True)


def verify_download(chunks, encoding, entry):
    """Verify original bytes while consuming stored bytes; reject trailing gzip."""
    if encoding not in ENCODINGS:raise ArtifactError('ARCHIVE_STORAGE_ENCODING')
    decoder=zlib.decompressobj(wbits=31) if encoding=='gzip' else None
    original=hashlib.sha256();stored=hashlib.sha256();original_size=stored_size=0
    try:
        for block in chunks:
            stored.update(block);stored_size+=len(block)
            if decoder:
                if decoder.eof and block:raise ArtifactError('ARCHIVE_GZIP_TRAILING_BYTES')
                pending=block
                while pending:
                    plain=decoder.decompress(pending,STREAM_BLOCK)
                    pending=decoder.unconsumed_tail
                    original_size+=len(plain);original.update(plain)
                    if original_size>entry['bytes']:raise ArtifactError('ARCHIVE_REMOTE_SIZE_EXCEEDED')
                    if decoder.unused_data:raise ArtifactError('ARCHIVE_GZIP_TRAILING_BYTES')
            else:
                original_size+=len(block);original.update(block)
                if original_size>entry['bytes']:raise ArtifactError('ARCHIVE_REMOTE_HASH_DIFFERS')
        if decoder and not decoder.eof:raise ArtifactError('ARCHIVE_GZIP_INCOMPLETE')
    except zlib.error:
        raise ArtifactError('ARCHIVE_GZIP_CORRUPT') from None
    if original.hexdigest()!=entry['sha256'] or original_size!=entry['bytes']:
        raise ArtifactError('ARCHIVE_REMOTE_HASH_DIFFERS')
    return {'download_verified_sha256':original.hexdigest(),'original_bytes':original_size,
            'stored_bytes':stored_size,'stored_sha256':stored.hexdigest(),'storage_encoding':encoding}


def publish(manifest, manifest_sha, review, client):
    """Injected archive client: no overwrite; verify while Hot, then Archive."""
    privacy_approved(review,manifest_sha)
    if digest(canonical(manifest))!=manifest_sha:raise ArtifactError('ARCHIVE_MANIFEST_SHA_DIFFERS')
    encoding=manifest.get('storage_encoding','identity')
    if encoding not in ENCODINGS:raise ArtifactError('ARCHIVE_STORAGE_ENCODING')
    # Verify all sources before the first upload. No partially approved set.
    paths=[verify_local(manifest,e) for e in manifest['entries']]
    receipts=[]
    for entry,path in zip(manifest['entries'],paths):
        key='originals/'+entry['sha256']+'/'+digest(entry['path'].encode())
        if encoding=='gzip':key += '.gz'
        uploaded=client.upload_hot(key,path,encoding=encoding) if encoding!='identity' else client.upload_hot(key,path)
        before=client.properties(key)
        if before['tier']!='Hot' or not before.get('etag'):raise ArtifactError('ARCHIVE_HOT_VERIFICATION_REQUIRED')
        verified=verify_download(client.download_chunks(key),encoding,entry)
        if uploaded is not None and (uploaded.get('stream_complete') is not True or any(
                uploaded.get(key)!=verified[key] for key in ('stored_bytes','stored_sha256'))):
            raise ArtifactError('ARCHIVE_UPLOAD_DOWNLOAD_ENCODING_DIFFERS')
        hot=client.properties(key)
        if hot['tier']!='Hot' or hot.get('etag')!=before['etag']:raise ArtifactError('ARCHIVE_OBJECT_CHANGED_DURING_VERIFICATION')
        client.archive(key,hot['etag'])
        final=client.properties(key)
        if final['tier']!='Archive' or not final.get('etag'):raise ArtifactError('ARCHIVE_TIER_NOT_CONFIRMED')
        receipts.append({**entry,'blob':key,'etag':final['etag'],'tier':'Archive',
                         **verified,'verified_at':datetime.now(timezone.utc).isoformat()})
    return {'version':'verified-archive-receipt-v1','manifest_sha256':manifest_sha,
            'privacy_review':review,'objects':receipts,'local_deletion_performed':False,
            'original_bytes':sum(e['bytes'] for e in receipts),'stored_bytes':sum(e['stored_bytes'] for e in receipts)}


def cleanup_script(manifest, manifest_sha, receipt):
    """Owner-run script only. Individual files; all paths/hashes rechecked."""
    if receipt.get('manifest_sha256')!=manifest_sha:raise ArtifactError('ARCHIVE_RECEIPT_MANIFEST_DIFFERS')
    if digest(canonical(manifest))!=manifest_sha:raise ArtifactError('ARCHIVE_MANIFEST_SHA_DIFFERS')
    privacy_approved(receipt.get('privacy_review'),manifest_sha)
    expected={e['path']:e for e in manifest['entries']};verified=[]
    for row in receipt.get('objects',[]):
        entry=expected.get(row.get('path'))
        if (not entry or any(row.get(k)!=entry[k] for k in ('sha256','bytes')) or
            row.get('download_verified_sha256')!=entry['sha256'] or row.get('tier')!='Archive' or not row.get('etag')):
            raise ArtifactError('ARCHIVE_RECEIPT_NOT_VERIFIED')
        if manifest.get('storage_encoding','identity')=='gzip':
            if (row.get('storage_encoding')!='gzip' or row.get('original_bytes')!=entry['bytes'] or
                type(row.get('stored_bytes')) is not int or row['stored_bytes']<0):
                raise ArtifactError('ARCHIVE_COMPRESSED_RECEIPT_NOT_VERIFIED')
            hash_id(row.get('stored_sha256'))
        path=verify_local(manifest,entry)
        verified.append({'path':str(path),'sha256':entry['sha256'],'bytes':entry['bytes']})
    import base64
    encoded=base64.b64encode(canonical({'workspace':manifest['workspace'],'files':verified})).decode()
    return '''# Generated from a SHA-pinned verified archive receipt. No recursive deletion.
$ErrorActionPreference = 'Stop'
$plan = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String(''' + "'"+encoded+"'" + ''')) | ConvertFrom-Json
$root = [IO.Path]::GetFullPath($plan.workspace).TrimEnd('\\') + '\\'
$log = Join-Path $plan.workspace '.local/archive-cleanup-removals.jsonl'
$freed = [long]0
foreach ($entry in $plan.files) {
    $resolved = (Resolve-Path -LiteralPath $entry.path -ErrorAction Stop).Path
    if (-not $resolved.StartsWith($root, [StringComparison]::OrdinalIgnoreCase)) { throw 'Path left workspace' }
    $cursor = Get-Item -LiteralPath $resolved -Force
    while ($cursor.FullName.TrimEnd('\\') -ne $root.TrimEnd('\\')) {
        if (($cursor.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Reparse point refused' }
        $cursor = if ($cursor.PSIsContainer) { $cursor.Parent } else { $cursor.Directory }
        if ($null -eq $cursor) { throw 'Workspace ancestor missing' }
    }
    $item = Get-Item -LiteralPath $resolved -Force
    if ($item.PSIsContainer -or $item.Length -ne $entry.bytes) { throw 'File size changed' }
    if ((Get-FileHash -LiteralPath $resolved -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256) { throw 'File hash changed' }
    Remove-Item -LiteralPath $resolved -Force -ErrorAction Stop
    $freed += $entry.bytes
    @{path=$resolved;bytes=$entry.bytes;sha256=$entry.sha256;removed_at=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json -Compress | Add-Content -LiteralPath $log
}
Write-Output "Total actual bytes freed: $freed"
'''


def convert_tape(directory, files):
    """Byte restoration proof only; does not pretend to run the engine replay."""
    from . import tape_bundle
    original=Path(directory)
    bundle=tape_bundle.pack(original,files,tape_class='EXACT')
    with tape_bundle.materialize(bundle,files) as restored:
        for name,reference in bundle['files'].items():
            if sha_file(original/name)!=reference['sha256'] or sha_file(restored.parent/name)!=reference['sha256']:
                raise ArtifactError('CONVERSION_RESTORATION_DIFFERS')
    return {'bundle':bundle,'verification':{'byte_restoration':'PASSED','engine_replay':'NOT_RUN',
             'original_events':'UNCHANGED','originals_deleted':False}}
