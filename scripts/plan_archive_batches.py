"""Bounded offline compression sampling and whole-capture batch selection.

Samples never leave this process; only sizes, offsets and hashes are recorded.
Sampling is descriptive, not privacy approval or a guaranteed compression ratio.
"""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
from investigator.archive_migration import ROUNDS, bounded_path, plan
from investigator.artifact_store import canonical, digest


def discover(root, cutoff):
    root = Path(root).resolve(strict=True)
    found = []
    for folder in sorted((root / '.local').iterdir()):
        if folder.name != 'process-tapes' and not any(folder.name == 'round-' + n or folder.name.startswith('round-' + n + '-') for n in ROUNDS):
            continue
        if folder.is_symlink() or getattr(folder.lstat(),'st_file_attributes',0)&0x400: continue
        for directory, dirs, files in os.walk(folder,followlinks=False):
            dirs[:] = [name for name in dirs if not (Path(directory)/name).is_symlink()
                       and not getattr((Path(directory)/name).lstat(),'st_file_attributes',0)&0x400]
            for name in files:
                path=Path(directory)/name
                if path.is_symlink():continue
                info=path.stat()
                if info.st_mtime>cutoff:continue
                kind=name if name in ('tape.json','catalog.sqlite','inventory.sqlite') else 'other'
                found.append((path,folder.name,kind,info.st_size))
    return found


def sample(root, cutoff, *, max_sample_bytes=256*1024*1024):
    found=discover(root,cutoff)
    strata=defaultdict(list)
    for row in found:strata[(row[1],row[2])].append(row)
    results=[];read=0
    for (folder,kind),rows in sorted(strata.items()):
        ordered=sorted(rows,key=lambda row:(row[3],str(row[0])))
        picks={0,len(ordered)//2,len(ordered)-1}
        samples=[]
        for index in sorted(picks):
            path,_,_,size=ordered[index]
            width=min(size,512*1024)
            for offset in sorted({0,max(0,size//2-width//2),max(0,size-width)}):
                if read+width>max_sample_bytes:break
                with path.open('rb') as stream:stream.seek(offset);body=stream.read(width)
                read+=len(body)
                samples.append({'path':str(path.relative_to(root)),'offset':offset,'bytes':len(body),
                                'sha256':hashlib.sha256(body).hexdigest(),'gzip_bytes':len(gzip.compress(body,mtime=0))})
        raw=sum(row['bytes'] for row in samples);compressed=sum(row['gzip_bytes'] for row in samples)
        results.append({'folder':folder,'class':kind,'files':len(rows),'logical_bytes':sum(row[3] for row in rows),
                        'sample_bytes':raw,'sample_gzip_bytes':compressed,
                        'sample_ratio':compressed/raw if raw else None,'samples':samples})
    return {'version':1,'classification':'STRATIFIED_SAMPLE_NOT_A_COMPRESSION_GUARANTEE_OR_PRIVACY_APPROVAL',
            'cutoff_epoch':cutoff,'sample_bytes':read,'max_sample_bytes':max_sample_bytes,'strata':results,
            'estate_reads':0,'model_calls':0,'local_deletion':False}


def batch(root,cutoff,*,max_original_bytes,max_files,protected,skip_paths=()):
    rows=discover(root,cutoff);files={path: size for path,_,_,size in rows}
    by_parent=defaultdict(list)
    for path in sorted(files):by_parent[path.parent].append(path)
    candidates=[]
    for path,folder,kind,_ in rows:
        if kind!='tape.json':continue
        group=by_parent[path.parent]
        if any(p.relative_to(root).as_posix() in skip_paths for p in group):continue
        # Preserve every file in the capture directory, including failures and
        # sidecars. Nested children must be handled in a separate audited plan.
        if any(child.is_dir() for child in path.parent.iterdir()):continue
        if any(child.is_file() and child not in files for child in path.parent.iterdir()):continue
        candidates.append((sum(files[p] for p in group),folder,str(path),group))
    # Take each round's smallest complete capture in turn. A directory with
    # many tiny model-only captures must not consume the whole admission.
    queues=defaultdict(list)
    for candidate in sorted(candidates):queues[candidate[1]].append(candidate)
    balanced=[]
    while any(queues.values()):
        for folder in sorted(queues):
            if queues[folder]:balanced.append(queues[folder].pop(0))
    selected=[];size=0
    for total,folder,name,group in balanced:
        if size+total>max_original_bytes or len(selected)+len(group)>max_files:continue
        selected.extend(group);size+=total
    manifest=plan(root,[p.relative_to(root).as_posix() for p in selected],protected=protected,
                   finished_statement='Owner Round Nineteen finished historical archive; cutoff excludes current captures; privacy review still required.',storage_encoding='gzip')
    if manifest['excluded']:
        # Do not silently archive half a capture. Excluded directories are held.
        blocked={str(Path(row['path']).parent) for row in manifest['excluded']}
        removed=[e for e in manifest['entries'] if str(Path(e['path']).parent) in blocked]
        manifest['entries']=[e for e in manifest['entries'] if str(Path(e['path']).parent) not in blocked]
        manifest['excluded'] +=[{**e,'reason':'CAPTURE_PEER_QUARANTINED'} for e in removed]
    return manifest


def partition(manifest, source_sha, *, max_original_bytes, max_files):
    """Partition a pinned selection, preserving every complete capture exactly."""
    if digest(canonical(manifest)) != source_sha:
        raise ValueError('PARTITION_MANIFEST_SHA_DIFFERS')
    if max_original_bytes < 1 or max_files < 1:
        raise ValueError('PARTITION_BOUND')
    groups=defaultdict(list)
    for entry in manifest['entries']:
        groups[str(Path(entry['path']).parent)].append(entry)
    parts=[];entries=[];size=0
    for name,group in sorted(groups.items()):
        total=sum(row['bytes'] for row in group)
        if total>max_original_bytes or len(group)>max_files:
            raise ValueError('PARTITION_CAPTURE_EXCEEDS_BOUND: '+name)
        if entries and (size+total>max_original_bytes or len(entries)+len(group)>max_files):
            parts.append(entries);entries=[];size=0
        entries.extend(group);size+=total
    if entries:parts.append(entries)
    return [{**manifest,'created_at':datetime.now(timezone.utc).isoformat(),
             'entries':rows,'excluded':[],
             'partition_source_sha256':source_sha,'partition_index':index,
             'partition_count':len(parts),'parent_excluded_count':len(manifest['excluded'])}
            for index,rows in enumerate(parts)]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['sample','batch','partition'])
    parser.add_argument('--workspace',required=True,type=Path)
    parser.add_argument('--cutoff',help='ISO UTC time from round opening receipt')
    parser.add_argument('--source-manifest',type=Path)
    parser.add_argument('--source-manifest-sha256')
    parser.add_argument('--partition-index',type=int)
    parser.add_argument('--max-original-bytes',type=int,default=1024*1024*1024)
    parser.add_argument('--max-files',type=int,default=200)
    parser.add_argument('--protected-paths',type=Path)
    parser.add_argument('--previous-plans',type=Path,help='JSON list of {path,sha256}; skip retained prior selections/holds without changing them')
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();root=args.workspace.resolve(strict=True)
    from investigator.archive_migration import load_pinned
    if args.action=='partition':
        if args.source_manifest is None or args.source_manifest_sha256 is None or args.partition_index is None:
            raise ValueError('PARTITION_SOURCE_REQUIRED')
        source=load_pinned(args.source_manifest,args.source_manifest_sha256)
        if Path(source['workspace']).resolve(strict=True)!=root:raise ValueError('PARTITION_WORKSPACE_DIFFERS')
        parts=partition(source,args.source_manifest_sha256,max_original_bytes=args.max_original_bytes,max_files=args.max_files)
        if args.partition_index<0 or args.partition_index>=len(parts):raise ValueError('PARTITION_INDEX')
        value=parts[args.partition_index]
    elif args.action=='sample':
        if not args.cutoff:raise ValueError('CUTOFF_REQUIRED')
        value=sample(root,datetime.fromisoformat(args.cutoff).timestamp())
    else:
        if not args.cutoff:raise ValueError('CUTOFF_REQUIRED')
        cutoff=datetime.fromisoformat(args.cutoff).timestamp()
        if args.protected_paths is None:raise ValueError('PROTECTED_PATHS_REQUIRED')
        from investigator.archive_migration import load_pinned
        previous=json.loads(args.previous_plans.read_bytes()) if args.previous_plans else []
        skip=set()
        for row in previous:
            prior=load_pinned(row['path'],row['sha256'])
            skip.update(e['path'] for e in prior['entries']+prior['excluded'])
        value=batch(root,cutoff,max_original_bytes=args.max_original_bytes,max_files=args.max_files,
                    protected=json.loads(args.protected_paths.read_bytes()),skip_paths=skip)
        value['previous_plans']=previous
    with args.output.open('xb') as stream:stream.write(canonical(value))
    print(json.dumps({'sha256':digest(canonical(value)),'sample_bytes':value.get('sample_bytes'),
                      'files':len(value.get('entries',[])),'excluded':len(value.get('excluded',[]))}))


if __name__=='__main__':main()
