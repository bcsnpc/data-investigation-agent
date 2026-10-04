"""Consumer-derived bounds for client-declared, engine-rendered limitations."""
from .proposal_limits import ASSESSMENT_DETAIL
PREFIX='By configuration, '
STATEMENT_BOUND=ASSESSMENT_DETAIL-len(PREFIX)


def render(statement):
    from .evidence_prose import validate
    validate(statement,STATEMENT_BOUND)
    return PREFIX+statement
