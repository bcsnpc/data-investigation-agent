"""Local grading harness only. No worker/engine source modification."""
import ast, inspect
from investigator.adapters import evaluation_anthropic as evaluation

def install(limit):
    original = evaluation.task
    if getattr(original, '_healthnet_limit', None) == limit:
        return
    tree = ast.parse(inspect.getsource(original))
    replacements = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and node.value == 24000:
            node.value = limit
            replacements += 1
    assert replacements == 1
    scope = dict(evaluation.__dict__)
    exec(compile(tree, '<local-healthnet-grading-bound>', 'exec'), scope)
    expanded = scope['task']
    def grading_only(value):
        if isinstance(value, dict) and value.get('purpose') in ('GRADE_ANSWER', 'GRADE_GUIDED_ANSWER'):
            return expanded(value)
        return original(value)
    grading_only._healthnet_limit = limit
    evaluation.task = grading_only
