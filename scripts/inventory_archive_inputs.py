"""Read-only file-name/size inventory. This is not privacy approval or a seal audit."""
import argparse
from collections import defaultdict
import json
import os
from pathlib import Path
import stat
from investigator.archive_migration import ROUNDS, approved_scope, bounded_path, protected_path, sha_file


def allocated_bytes(path, info):
    if os.name != 'nt':
        return info.st_blocks * 512 if hasattr(info, 'st_blocks') else None
    import ctypes
    from ctypes import wintypes
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    function = kernel.GetCompressedFileSizeW
    function.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(wintypes.DWORD)]
    function.restype = wintypes.DWORD
    high = wintypes.DWORD()
    ctypes.set_last_error(0)
    low = function(str(path), ctypes.byref(high))
    if low == 0xFFFFFFFF and ctypes.get_last_error():
        raise ctypes.WinError(ctypes.get_last_error())
    return (high.value << 32) | low


def inventory(workspace, source_export_roots=()):
    root = Path(workspace).resolve(strict=True)
    local = root / '.local'
    groups, errors, exports = {}, [], []
    allocations = {}
    selected = [p for p in local.iterdir() if p.name == 'process-tapes' or
                any(p.name == 'round-' + n or p.name.startswith('round-' + n + '-') for n in ROUNDS)]
    for folder in selected:
        totals = {'files': 0, 'logical_bytes': 0, 'allocated_bytes': 0, 'protected_name_files': 0, 'opaque_files': 0}
        for directory, dirs, files in os.walk(folder, followlinks=False):
            safe = []
            for name in dirs:
                child = Path(directory) / name
                if getattr(child.lstat(), 'st_file_attributes', 0) & 0x400 or child.is_symlink():
                    errors.append({'path': str(child.relative_to(root)), 'reason': 'REPARSE_POINT_SKIPPED'})
                else:
                    safe.append(name)
            dirs[:] = safe
            for name in files:
                path = Path(directory) / name
                try:
                    value = path.lstat()
                    if getattr(value, 'st_file_attributes', 0) & 0x400:
                        raise ValueError('REPARSE_POINT_SKIPPED')
                    totals['files'] += 1
                    totals['logical_bytes'] += value.st_size
                    allocated = allocated_bytes(path, value)
                    if allocated is not None:
                        totals['allocated_bytes'] += allocated
                        allocations.setdefault((value.st_dev, value.st_ino), allocated)
                    totals['protected_name_files'] += int(protected_path(path.relative_to(root), []))
                    totals['opaque_files'] += int(path.suffix.lower() in ('.zip', '.gz', '.7z', '.tar', '.enc'))
                except (OSError, ValueError) as error:
                    errors.append({'path': str(path.relative_to(root)), 'reason': type(error).__name__})
        groups[folder.name] = totals
    for relative in source_export_roots:
        approved_scope(relative + '/manifest.json', [relative])
        folder = root / relative
        for path in sorted(folder.iterdir()):
            if path.is_file():
                path = bounded_path(root, path.relative_to(root))
                exports.append({'path': path.relative_to(root).as_posix(), 'bytes': path.stat().st_size,
                                'sha256': sha_file(path)})
    unique = {}
    for entry in exports:
        unique.setdefault((entry['sha256'], entry['bytes']), []).append(entry['path'])
    return {'version': 1, 'scope': str(root), 'classification': 'SIZE_INVENTORY_NOT_PRIVACY_APPROVAL',
            'allocation_method': 'GetCompressedFileSizeW' if os.name == 'nt' else 'st_blocks_times_512',
            'unique_file_id_allocated_bytes': sum(allocations.values()),
            'groups': groups, 'errors': errors, 'source_exports': exports,
            'source_export_logical_bytes': sum(e['bytes'] for e in exports),
            'source_export_unique_bytes': sum(size for _, size in unique),
            'duplicate_sets': [paths for paths in unique.values() if len(paths) > 1],
            'archive_originals_untouched': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', required=True, type=Path)
    parser.add_argument('--source-export-roots', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    result = inventory(args.workspace, json.loads(args.source_export_roots.read_bytes()) if args.source_export_roots else ())
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps({'files': sum(g['files'] for g in result['groups'].values()),
                      'logical_bytes': sum(g['logical_bytes'] for g in result['groups'].values()),
                      'errors': len(result['errors']), 'source_unique_bytes': result['source_export_unique_bytes']}))


if __name__ == '__main__':
    main()
