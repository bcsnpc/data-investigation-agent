"""Catch explicit semantic contradictions; never manufacture a replacement record."""
import re

SUBJECT_INSTRUCTIONS = ('\nPreserve the primary ask and its stated setup referent: an explicit request to reproduce a saved or declared '
    'display is VISUAL_CONTENT; an explicit discrepancy allegation is MISMATCH_COMPLAINT; '
    'a sole request to decide a business rule is BUSINESS_MEANING and is refused before any '
    'technical procedure. Mixed questions retain a technical question kind and answer the '
    'technical part, explicitly declining business meaning. Requests about the implemented '
    'effect of adjustments on a metric or whether a difference follows definitions are '
    'technical asks even when authoritative meaning is also requested. Explaining selected or declared '
    'report/filter scope is technical context, not authoritative business meaning. '
    'A sole request to check whether a business rule is correct remains BUSINESS_MEANING; the verb check '
    'alone does not make it technical.')
INSTRUCTIONS = SUBJECT_INSTRUCTIONS + (' A quoted value explicitly selected by the user must be SELECTION, '
    'not SUBJECT or MENTION. Tracking references are not expected-record identifiers. '
    'A request asking which restriction hides rows is FILTER_EFFECT, not a pipeline question. '
    'Comparison of earlier and later states is TEMPORAL_COMPARISON, not business meaning. '
    'Keep the question classified even when its route is unavailable.')


class RuleViolation(ValueError):
    def __init__(self, code, requirement):
        self.code=code
        self.repair={'code':code,'requirement':requirement}
        super().__init__(code+': '+requirement)


def technical_ask(ticket):
    """Explicit technical work, not a mere metric mentioned in an intent question."""
    operations=re.finditer(r'\b(?:inspect|investigate|reproduce|check)\b([^.!?\n]*)',ticket,re.I)
    if any(not re.search(r'\bbusiness\s+(?:rule|intent|meaning)\b',
            re.split(r'\b(?:and|but|then)\b',m.group(1),maxsplit=1,flags=re.I)[0],re.I) for m in operations):
        return True
    return bool(re.search(
        r'\bexplain\b[^.!?\n]*\b(?:selected|declared|filter)\b[^.!?\n]*\bscope\b|'
        r'\b(?:explain|whether)\b[^.!?\n]*\b(?:definitions?|observed difference)\b|'
        r'\bfollows?\b[^.!?\n]*\bdefinitions?\b|'
        r'\baffect\b[^.!?\n]*\b(?:metric|measure|quantity)\b', ticket, re.I))


def validate(value, ticket):
    if value.get('action') != 'PROPOSE':return
    kind=(value.get('question_kind') or {}).get('kind')
    if kind == 'BUSINESS_MEANING' and technical_ask(ticket):
        raise RuleViolation('MIXED_TECHNICAL_SUBJECT_REQUIRED',
            'Answer the explicit technical part under its technical question kind; decline authoritative business meaning separately. Do not refuse the mixed ticket as a sole business-rule decision.')
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
    if re.search(r'\b(?:decide|determine|check)\b[^.!?\n]*\bbusiness rule\b',ticket,re.I) and not technical_ask(ticket):
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
