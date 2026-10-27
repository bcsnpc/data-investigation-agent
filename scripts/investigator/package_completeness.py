"""Check internal Python imports in the staged cloud package without executing it."""
import ast
from pathlib import Path


def check(staged,source):
    staged,source=Path(staged),Path(source)
    roots=(Path('scripts'),Path('acceptance'))
    missing=[]
    for root in roots:
        for entry in (staged/root).rglob('*.py'):
            relative=entry.relative_to(staged)
            tree=ast.parse(entry.read_bytes(),filename=str(relative))
            for node in ast.walk(tree):
                candidates=[]
                if isinstance(node,ast.Import):
                    candidates=[Path('scripts',*alias.name.split('.')) for alias in node.names]
                elif isinstance(node,ast.ImportFrom):
                    if node.level:
                        parent=relative.parent
                        for _ in range(node.level-1):parent=parent.parent
                        base=parent.joinpath(*(node.module or '').split('.'))
                    else:base=Path('scripts',*(node.module or '').split('.'))
                    candidates=[base,*[base/alias.name for alias in node.names if alias.name!='*']]
                for candidate in candidates:
                    # Only repo-owned imports, not installed dependencies or
                    # attributes imported from a module, need staged source.
                    options=[candidate.with_suffix('.py'),candidate/'__init__.py']
                    owned=[p for p in options if (source/p).is_file()]
                    if owned and not any((staged/p).is_file() for p in owned):
                        missing.append({'importer':str(relative),'module':str(candidate)})
    if missing:raise ValueError('CLOUD_PACKAGE_INTERNAL_IMPORTS_MISSING: '+repr(missing[:20]))
    return {'status':'PASS','missing':0}
