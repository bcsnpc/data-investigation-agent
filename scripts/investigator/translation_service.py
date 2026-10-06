"""One proposal, immutable verification, and cell-specific reuse.

The installed adapter supplies native compilation and isolated execution. A
cached expression is never returned for reliance without a current cell proof.
"""
from .translation_proposer import propose, verify
from .lineage_binding import VerificationHold


def run(request, *, proposer, model_call, ledger, cells, compiler, execute,
        budget, cross_boundary=False, native_observation=None):
    from .lineage_binding import seal
    witnesses = [ledger.reusable(request, cell) for cell in cells]
    cached = witnesses[0] if witnesses else None
    if cached is not None and all(row is not None and seal(row) == seal(cached) for row in witnesses):
        return {'source': 'REUSED_VERIFICATION', 'verification': cached}
    # A falsification is an explicit stop, not permission to ask for a new
    # candidate until the same definition happens to match.
    if any(row['status'] == 'FALSIFIED' for row in ledger.view(request)):
        return {'source': 'PRESERVED_FALSIFICATION', 'verification': next(
            row for row in reversed(ledger.view(request)) if row['status'] == 'FALSIFIED')}
    candidate = ledger.candidate(request)
    if request['kind'] == 'MEASURE' and len(cells) == 1 and candidate is None:
        raise ValueError('New-cell extension requires an existing verified sample before a model call')
    source = 'REUSED_PROPOSAL' if candidate is not None else 'MODEL_PROPOSAL'
    if candidate is None: candidate = propose(request, proposer, model_call)
    extension = request['kind'] == 'MEASURE' and len(cells) == 1
    try:
        result = verify(candidate, request, cells=cells, compiler=compiler,
            execute=execute, budget=budget, cross_boundary=cross_boundary,
            extension=extension, native_observation=native_observation)
    except VerificationHold as exc:
        ledger.append(exc.verification)
        raise
    ledger.append(result)
    return {'source': source, 'verification': result}
