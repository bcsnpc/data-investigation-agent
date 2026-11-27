"""Offline checks for the owner-approved local grader override."""
import copy
import hashlib
import importlib.util
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / 'scripts'))
from investigator.adapters import evaluation_anthropic as evaluation
spec = importlib.util.spec_from_file_location('healthnet_local_limit', Path(__file__).with_name('grading_packet_limit.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
source_file = Path(evaluation.__file__)
before = hashlib.sha256(source_file.read_bytes()).hexdigest()
original = evaluation.task
try:
    module.install(1000000)
    source = dict(protocol=evaluation.PROTOCOL, purpose='GRADE_GUIDED_ANSWER', case_id='healthnet-bound', expected={}, delivered={'rows': ['complete evidence'] * 30000})
    assert evaluation.task(source) == source
    params = evaluation.request_for(source, 'a' * 64)['params']
    import json
    assert json.loads(params['messages'][0]['content'])['source'] == source
    for invalid, reason in [
        ({**source, 'protocol': 'invalid'}, 'EVALUATION_PROTOCOL'),
        ({**source, 'delivered': {'evidence': 'x' * 1000000}}, 'EVALUATION_INPUT_BOUND'),
        (dict(protocol=evaluation.PROTOCOL, purpose='ASSESS_FAIRNESS', case_id='fairness-bound', ticket='x' * 25000, labels=[], criteria='unchanged'), 'EVALUATION_INPUT_BOUND'),
    ]:
        try:
            evaluation.task(invalid)
        except ValueError as error:
            assert str(error) == reason
        else:
            raise AssertionError(reason)
    assert hashlib.sha256(source_file.read_bytes()).hexdigest() == before
finally:
    evaluation.task = original
print('PASS: complete grading evidence, original non-grading bounds, protocol validation, unchanged engine file')
