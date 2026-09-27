"""Reject incomplete/oversized evidence prose; never repair it by cutting."""
import re
from .onboarding import text
from . import proposal_limits as limits

# A terminal sentence mark, optionally followed by a closing quote/bracket.
# The preceding character excludes ellipses and punctuation-only endings.
SENTENCE_END = r'''^[^\u0000]*[^\u0000.!?\s…][.!?]["')\]]?$'''


def schema(bound):
    return {'type':'string',**limits.text_bound(bound),'pattern':SENTENCE_END,
            'description':'Fit the entire explanation within this bound. End in a complete sentence; never cut a word, sentence, or limitation to fit.'}


def validate(value,bound):
    text(value,bound)
    if (not re.search(SENTENCE_END,value) or 'TRUNCATED_TO_PUBLISHED_LIMIT' in value
            or re.search(r'\b(?:and|or|but|because|although|including|such as)[.!?]["\')\]]?$',value,re.I)):
        raise ValueError('Evidence prose must end in a complete sentence; truncation is not accepted')
    return value


def diagnostic_detail(value,limit):
    """Do not publish a cut diagnostic as though its missing tail were harmless."""
    value=str(value)
    if len(value)<=limit:return value
    return 'Diagnostic detail omitted because it exceeds the display bound; the proposal remains rejected.'
