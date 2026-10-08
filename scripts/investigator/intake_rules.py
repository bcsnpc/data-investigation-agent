"""Catch explicit semantic contradictions; never manufacture a replacement record."""
import re

INSTRUCTIONS = ('\nPreserve the primary ask: an explicit request to reproduce a saved or declared '
    'display is VISUAL_CONTENT; an explicit discrepancy allegation is MISMATCH_COMPLAINT; '
    'a request to decide a business rule is BUSINESS_MEANING and is refused before any '
    'technical procedure. A quoted value explicitly selected by the user must be SELECTION, '
    'not SUBJECT or MENTION. Tracking references are not expected-record identifiers. '
    'A request asking which restriction hides rows is FILTER_EFFECT, not a pipeline question. '
    'Comparison of earlier and later states is TEMPORAL_COMPARISON, not business meaning. '
    'Keep the question classified even when its route is unavailable.')


class RuleViolation(ValueError):
    def __init__(self, code, requirement):
        self.code=code
        self.repair={'code':code,'requirement':requirement}
        super().__init__(code+': '+requirement)


def validate(value, ticket):
    if value.get('action') != 'PROPOSE':return
    kind=(value.get('question_kind') or {}).get('kind')
    if re.search(r'\bwhich\s+(?:saved\s+)?filters?\b[^.!?\n]*\bhid(?:e|es|ing)\b',ticket,re.I) and kind!='FILTER_EFFECT':
        raise RuleViolation('FILTER_EFFECT_SUBJECT_REQUIRED',
            'Which filters hide rows is FILTER_EFFECT; reproduction does not authorize a pipeline walk.')
    if re.search(r'\b(?:change|changed|compare)\b[^.!?\n]*\b(?:between|last week)\b',ticket,re.I) and kind!='TEMPORAL_COMPARISON':
        raise RuleViolation('TEMPORAL_COMPARISON_SUBJECT_REQUIRED',
            'Comparing earlier and later states is TEMPORAL_COMPARISON. Do not substitute a current global walk or business-meaning answer.')
    if re.search(r'\b(?:can|does|do|could)\b[^?!.\n]*\b(?:declared|saved)\b[^?!.\n]*\breproduc\w*\b',ticket,re.I):
        if kind != 'VISUAL_CONTENT':
            raise RuleViolation('REPRODUCTION_SUBJECT_REQUIRED',
                'An explicit request to reproduce a displayed figure is VISUAL_CONTENT, not a pipeline discrepancy. Preserve its exact referent.')
    if re.search(r'\b(?:overstated|understated|discrepancy|differs|disagrees)\b',ticket,re.I):
        if value.get('ticket_shape') != 'MISMATCH_COMPLAINT':
            raise RuleViolation('MISMATCH_SHAPE_REQUIRED',
                'An explicit discrepancy allegation is MISMATCH_COMPLAINT. It cannot use BUSINESS_QUESTION:NONE.')
    if re.search(r'\b(?:decide|determine)\b[^.!?\n]*\bbusiness rule\b',ticket,re.I):
        if kind != 'BUSINESS_MEANING':
            raise RuleViolation('BUSINESS_RULE_SUBJECT_REQUIRED',
                'The primary request to decide a business rule is BUSINESS_MEANING. Technical process evidence cannot decide business correctness.')
    for mention in value.get('value_mentions',[]):
        quote=mention['source']['quote']
        for match in re.finditer(re.escape(quote),ticket):
            prefix=ticket[max(0,match.start()-80):match.start()]
            if re.search(r'\bI\s+(?:selected|chose|filtered\s+to)\s*$',prefix,re.I) and mention['role']!='SELECTION':
                raise RuleViolation('EXPLICIT_SELECTION_ROLE_REQUIRED',
                    'A value immediately following an explicit user selection must carry SELECTION. Do not interpret the value as a mere subject.')
