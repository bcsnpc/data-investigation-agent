"""Export retained prompt literals and dynamic builders without importing adapters.

AST inspection avoids credentials, environment reads and model dispatch. Dynamic
builders are exported as source because their rendered text contains case data.
"""
import ast
from pathlib import Path


def inventory(root):
    rows = []
    for path in sorted(Path(root).rglob('*.py')):
        source = path.read_text(encoding='utf-8-sig')
        tree = ast.parse(source)
        parents = {}
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                parents[child] = node
        selected = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                names = [t.id for t in targets if isinstance(t, ast.Name)]
                if not any(any(word in n.lower() for word in ('instruction', 'prompt', 'system', 'guidance')) for n in names):
                    continue
                if not any(isinstance(n, ast.Constant) and isinstance(n.value, str) and len(n.value) > 60
                           for n in ast.walk(node)):
                    continue
                selected[node.lineno] = node
            if isinstance(node, ast.Call):
                name = node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id if isinstance(node.func, ast.Name) else ''
                keys = {k.arg for k in node.keywords}
                if name not in ('complete', 'azure_generate', 'generate') or not keys.intersection(('system', 'instructions')):
                    continue
                parent = node
                while parent in parents and not isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    parent = parents[parent]
                if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    selected[parent.lineno] = parent
            if isinstance(node, ast.FunctionDef) and node.name in ('toolbox', 'extraction_tools', 'described_schema', 'request_for', 'instructions'):
                selected[node.lineno] = node
        for line, node in sorted(selected.items()):
            rows.append({'path': path.as_posix(), 'line': line,
                         'kind': 'builder' if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else 'assignment',
                         'source': ast.get_source_segment(source, node)})
    return rows


def render(rows):
    return '\n'.join('\n'.join([f"### {r['path']}:{r['line']} ({r['kind']})", '',
                                '```python', r['source'], '```', '']) for r in rows)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default='scripts/investigator')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    Path(args.output).write_text(render(inventory(args.root)), encoding='utf-8')
