"""Read-only runtime-reference inventory for archive selection, never file removal."""
from pathlib import Path
import re
from investigator.artifact_store import ArtifactError

IDENTITY=re.compile(rb'(?<![0-9a-f])[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}(?![0-9a-f])',re.I)


def reference_ids(paths):
    """Stream only explicitly selected code/config files, not arbitrary .local."""
    references={};seen=set()
    for value in paths:
        path=Path(value)
        if str(path).casefold() in seen:continue
        seen.add(str(path).casefold());before=path.stat();found=set();tail=b''
        with path.open('rb') as stream:
            while block:=stream.read(1024*1024):
                body=tail+block
                found.update(m.group().decode('ascii').lower() for m in IDENTITY.finditer(body))
                tail=body[-64:]
        after=path.stat()
        if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):raise ArtifactError('ARCHIVE_RUNTIME_REFERENCE_CHANGED')
        for identity in found:references.setdefault(identity,[]).append(str(path))
    return {'scanned_files':len(seen),'references':references}


def held_parents(paths,references):
    result={}
    for value in paths:
        path=Path(value);parts=path.parent.parts
        for part in parts:
            if part.lower() in references:
                parent=path.parent.as_posix();result[parent]=references[part.lower()]
    return result
