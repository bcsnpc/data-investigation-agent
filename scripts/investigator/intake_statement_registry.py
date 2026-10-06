"""Consumer-owned closed forms for explicitly reported states, never tolerances."""
import re

EMPTY_FORMS=('blank','empty','nothing','no data','no value','no rows','dash','shows none')
# Dash is a shown value, not a minus sign, date separator or identifier suffix.
SHOWN_MARKER=r'\b(?:shows?|displays?|returns?|reads?|reports|visual|card|chart|cell|shown value|reported figure|reported value)\b'
NUMBER=r'[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\s*[KMBkmb]?(?![\w/-]|\.\d)'
NUMBER_MARKER=r'\b(?:shows?|displays?|returns?|reads?|reports|(?:figure|value|number|total|amount)\s*(?:is|=|:))\s*(?:exactly\s+|about\s+|around\s+|roughly\s+|approximately\s+)?[\"\']?'


def empty_matches(text):
    words='|'.join(re.escape(v) for v in sorted(EMPTY_FORMS,key=len,reverse=True))
    return list(re.finditer(r'\b(?:'+words+r')\b|(?<![\w/.-])-(?![\w/-]|\.\d)',text,re.I))


def explicit_statements(ticket):
    """Only omissions are refused. Interpretation still supplies the figure span."""
    found=[]
    for match in empty_matches(ticket):
        # A definition mentioning a blank is not a statement of a shown value.
        prefix=ticket[max(0,match.start()-100):match.start()]
        prefix=re.split(r'[.!?\n]',prefix)[-1]
        if not re.search(SHOWN_MARKER,prefix,re.I) and match.group().casefold()!='shows none':continue
        found.append({'kind':'EMPTY','source':{'start':match.start(),'end':match.end(),'quote':match.group()}})
    for match in re.finditer(NUMBER_MARKER+'(?P<figure>'+NUMBER+')',ticket,re.I):
        start,end=match.span('figure');quote=ticket[start:end].rstrip();end=start+len(quote)
        found.append({'kind':'NUMBER','source':{'start':start,'end':end,'quote':quote}})
    return sorted(found,key=lambda row:row['source']['start'])


class OmittedExplicitStatement(ValueError):
    def __init__(self,statements):
        self.statements=statements
        self.repair={'reason':'INTAKE_OMITTED_EXPLICIT_STATEMENT','statements':statements}
        super().__init__('INTAKE_OMITTED_EXPLICIT_STATEMENT: '+', '.join(repr(r['source']['quote']) for r in statements))


def validate(decision,ticket):
    # ASK already fences execution; do not manufacture a figure to remove it.
    if not isinstance(decision,dict):raise ValueError('Intake decision must be an object')
    if decision.get('action')!='PROPOSE':return
    reported=decision.get('reported_figure')
    if not isinstance(reported,dict):raise ValueError('Reported figure requires an explicit state')
    if reported.get('state')!='UNSPECIFIED':return
    statements=explicit_statements(ticket)
    if statements:raise OmittedExplicitStatement(statements)
