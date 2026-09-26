# data-investigation-agent — charter for AI implementers

Read this before changing anything. It is not style guidance. Every rule below
exists because breaking it previously produced a false conclusion that survived
review.

## What this system is

A technical debugger for reported number discrepancies across a data stack.
Given a complaint that a number is wrong, it traces that number through the
layers that produce it, locates where behaviour explains the difference, and
classifies what it found.

It reports whether behaviour is **by design, latency, failure, or defect**.

## What it is NOT

**It never judges whether a number is business-correct.** This is the governing
non-goal. The system states the mechanism and its category; the user decides
whether the design is right. A filter in a transformation is not a bug and not a
non-bug — it is a design choice, reported as such, with an enhancement request
as the available action.

It also does not explain business causation. "Why did discounts rise" is not
answerable from pipeline evidence.

## Non-negotiables

1. **Evidence must be produced by the thing it claims to be evidence about.**
   Where it cannot be, the output is an explicit unavailability, never a
   plausible substitute. A stub that returns `{'status': 'UNAVAILABLE'}` is not
   a finding and must never be consumed as one.

2. **Eligibility to run is not eligibility to conclude.** A procedure may be
   applicable and still be barred from an outcome because the evidence contract
   for that outcome was not satisfied. Capability gating enforces this; do not
   route around it.

3. **Cross-surface invariant.** Two quantities compared across a boundary must
   come from different execution surfaces. Same engine, same connection, same
   object is a within-layer check and must be labelled
   `WITHIN_LAYER_CHECK` / `NO_INDEPENDENT_LOWER_READ`. It is never a boundary
   comparison, however the values come out.

4. **Faithful equivalence or nothing.** If a quantity cannot be expressed
   faithfully at a lower surface, the boundary is `NOT_COMPARABLE`. Never
   approximate, never guess an equivalence, never infer a binding from name
   similarity.

5. **Platform neutrality above the adapter layer.** Nothing in the engine,
   prompts or configuration may name a platform, product, layer convention,
   domain table, metric formula, expected value, or required investigation
   route. Whether a layer is a Delta table, a Snowflake view, a dbt model or a
   semantic model is the adapter's concern alone.

6. **Provenance is explicit.** `DECLARED_BY_DEFINITION`, `INFERRED_FROM_CODE`
   and discovered bindings are distinct and must stay visibly distinct to the
   planner. An inferred binding is a hypothesis about the estate, not a fact.

7. **No credentials, keys or tokens in source.** Local run artifacts stay under
   `.local/` and are not committed.

8. **No app registration is created or amended, and no identity gains a new
   audience or scope, without an explicit human decision.** Report what would be
   required and stop.

## Evidence discipline

- Preserve every failed, partial, interrupted and rejected run exactly as it
  happened. Never edit a frozen artifact, a stored receipt or recorded run
  evidence to make something pass.
- Corrections are **appended and dated**, never written over the original claim.
  If an earlier document asserted something later found false, add a dated
  correction; do not rewrite the original.
- Never upgrade a partial result into a verified cause, a general capability or
  an acceptance pass. Observed agreement is not proven continuity.

## Where the model is used, and where it is not

**Deterministic:** walking the path, evaluating quantities, comparing values,
locating the divergent boundary, retrieving definitions and run history,
producing the evidence chain.

**Model judgment:** interpreting the ticket into a measure and scope; choosing
vertical versus horizontal; deciding whether a retrieved definition actually
explains the observed difference; naming the mechanism in words; writing both
outputs.

**Never the model:** choosing which layer to look at next, inventing queries to
search with, or deciding whether a design is correct.

The model translates; it does not explore. A required layer order is banned —
requirements live in the support contract, not in an enforced sequence.

## Recording discipline — applies to every PR

A PR that changes behaviour and does not update these is incomplete.

- **`docs/runs/ledger.jsonl`** — exactly one appended line per run, live or
  offline. Never rewrite or delete existing lines, including failures. Counts,
  identifiers and outcomes only; never query text, result values, business data
  or provider message contents.
- **`README.md`** — must be true as of every commit. "What works today" states
  only what is implemented and verified now. Never describe an aspiration, a
  plan or a single successful trial as a current general capability.
- **`docs/current-delivery-status.md`** — owns implementation and verification
  claims.
- Failed, partial and blocked outcomes are recorded with the same detail as
  successes, including the stop reason and what was NOT established.
- If engine bytes changed, state explicitly that the current freeze is
  invalidated.

## Per-PR checklist

- [ ] One work item only
- [ ] Tests added that fail if the item's invariant is removed
- [ ] CI green: Python tests, PowerShell syntax, portal tests, build
- [ ] No domain names, metric formulas, expected values or required route in
      engine code, prompts or configuration
- [ ] No frozen artifact, stored receipt or recorded run evidence modified
- [ ] No secrets added; `.local/` artifacts not committed
- [ ] Ledger row appended for any run performed
- [ ] README true as of this commit
- [ ] `docs/current-delivery-status.md` updated
- [ ] Freeze invalidation stated if engine bytes changed

## Current state (update this section as it changes)

- The outcome taxonomy and the vertical procedure are implemented in
  `scripts/investigator/process_debugging.py`.
- Capability declaration and gating work: `REQUIRED_CAPABILITIES`,
  `OPTIONAL_CAPABILITIES`, `applicability()`, and the pre-`DEFECT` gate that
  refuses a defect claim when competing explanations were not checked.
- The offline replay harness (`acceptance/unknown_domain/session_replay.py`)
  blocks network at socket level and matches requests byte-exactly.
- **No investigation has yet completed end to end.** The model's
  `judge_definition` call has never been invoked in a live run.
- The Fabric SQL analytics endpoint is reachable through the isolated Azure CLI
  profile (`.local/azure-fabric-sql`, used by `scripts/fabric_sql_auth.py`). No
  app registration is required. This was established only as the tenant
  administrator, with a trivial `SELECT 1`. **Which identity should hold this
  access is an open human decision.** No least-privilege reader has been tested,
  and no table permission is established. The Fabric CLI client still fails with
  `AADSTS65002`. The endpoint IDs `701ab1fc…` and `77c49180…` are unreconciled.
- Horizontal comparison, recurrence learning, declared business context and the
  known-issues register are **proposal-only**. Do not implement them
  opportunistically.

## Known past failures — do not reintroduce

- Stubbed adapter methods were consumed as findings, making a false `DEFECT`
  reachable. Fixed by capability gating (#231).
- Same-engine aggregates were presented as cross-boundary comparisons. Fixed by
  the cross-surface invariant (#235).
- `CONSISTENT_TO_BOUNDARY` was claimable after zero successful comparisons.
  Fixed by requiring at least one, and by adding `NO_COMPARABLE_PATH`.
- An evaluator opened the wrong discovery context, invalidating a "structural
  limitation" conclusion. Fixed by a fail-closed environment requirement (#232).
- An ownership-label change caused a silent context regression (directory
  entries 28 to 11, SQL objects 11 to 3, SQL reads 3 to 0). Any change that adds
  content to planner context must report directory entry counts, SQL-object
  counts and payload characters before and after, with a coverage test.
