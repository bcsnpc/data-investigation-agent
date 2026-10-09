"""Shared descriptive-field bounds for repair, wire schema and validation."""
QUESTION = 500
HYPOTHESIS_CLAIM = 400
ASSESSMENT_CLAIM = 1000
ASSESSMENT_DETAIL = 500
# Deterministic walks retain each boundary, attestation and unchecked-depth limit.
# This does not enlarge the open planner's six-limit / twelve-reference contract.
PROCESS_EVIDENCE_ITEMS = 256

# Consumer-owned public field limits. Schemas, validators and repairs import these.
HYPOTHESIS_ID = 80
HYPOTHESIS_UPDATES = 8
HYPOTHESIS_TOTAL = 16
HYPOTHESIS_REFS = 10
ASSESSMENT_REFS = 12
ASSESSMENT_LIST = 6
SUPPORT_REFS = 8
QUERY_TEXT = 16000
QUERY_ROWS = 250
CONTEXT_TEXT = 200
CONTEXT_ID = 2000
CONTENT_OFFSET = 1000000
INTAKE_QUOTE = 500
INTAKE_TEXT = 2000
INTAKE_FILTERS = 6
INTAKE_DIMENSIONS = 1
FILTER_VALUES = 50
FILTER_STRING = 200
SCREENSHOT_TEXT = 1600
SCREENSHOT_UNCERTAINTIES = 4
SCREENSHOT_UNCERTAINTY = 200
LEGACY_PLAN_FIELD = 250
LEGACY_PLAN_QUESTIONS = 10
EXACT_INTEGER = 2**53 - 1
# Same lexical contract as onboarding.text: at least one non-whitespace
# character and no NUL, while allowing meaningful whitespace inside the text.
TEXT_PATTERN = r'^(?=[\s\S]*\S)[^\u0000]*$'

def text_bound(maximum):
    return {'minLength':1,'maxLength':maximum,'pattern':TEXT_PATTERN}
