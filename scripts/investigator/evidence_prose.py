"""Reject incomplete/oversized evidence prose; never repair it by cutting."""
import re
from .onboarding import text
from . import proposal_limits as limits

# A terminal sentence mark, optionally followed by a closing quote/bracket.
# The preceding character excludes ellipses and punctuation-only endings.
SENTENCE_END = r'''^[^\u0000`]*[^\u0000`.!?\s…][.!?]["')\]]?$'''


def schema(bound):
    return {'type':'string',**limits.text_bound(bound),'pattern':SENTENCE_END,
            'description':'Plain text without backticks. Fit the entire explanation within this bound. End in a complete sentence; never cut a word, sentence, or limitation to fit.'}


def validate(value,bound):
    text(value,bound)
    if (not re.search(SENTENCE_END,value) or 'TRUNCATED_TO_PUBLISHED_LIMIT' in value
            or re.search(r'\b(?:and|or|but|because|although|including|such as|can|could|may|might|must|should|would|will|to|with|from|between|if|when|where|than)[.!?]["\')\]]?$',value,re.I)):
        raise ValueError('Evidence prose must end in a complete sentence; truncation is not accepted')
    # Unfinished formatting and subordinate tails are not complete prose merely
    # because a decoder supplies a final period. Do not repair either in place.
    for opening,closing in (('(',')'),('[',']')):
        depth=0
        for char in value:
            depth+=(char==opening)-(char==closing)
            if depth<0:raise ValueError('Evidence prose contains unfinished delimiters')
        if depth:raise ValueError('Evidence prose contains unfinished delimiters')
    if value.count('"')%2:raise ValueError('Evidence prose contains an unfinished quotation')
    last=re.split(r'(?<=[.!?])\s+',value.strip())[-1]
    if re.match(r'^(?:If|When|Although|Because|Unless|While|Whenever)\b',last,re.I):
        clauses=last.split(',',1)
        if len(clauses)!=2 or len(re.findall(r'\b[A-Za-z]+\b',clauses[1]))<3:
            raise ValueError('Evidence prose ends in an unfinished subordinate sentence')
    return value


def diagnostic_detail(value,limit):
    """Do not publish a cut diagnostic as though its missing tail were harmless."""
    value=str(value)
    if len(value)<=limit:return value
    return 'Diagnostic detail omitted because it exceeds the display bound; the proposal remains rejected.'
