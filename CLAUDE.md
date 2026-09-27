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

## Known platform limits: served-snapshot metadata (2026-09-27)

These are tested limits of the current least-privilege Fabric/Power BI reader,
not a to-do to acquire elevated execution permissions. The reader can read
values but cannot establish which data version those reads served through the
tested routes.

| Route | Tested reader result | Constraint |
| --- | --- | --- |
| Power BI REST refresh history | HTTP403 | Requires dataset Write. |
| XMLA TMSCHEMA partition refresh metadata | Refused | Requires administrator metadata access. |
| DAX `INFO.DELTATABLEMETADATASTORAGES()` | Refused | Requires administrator; no framed Delta version returned. |
| DAX `TABLETRAITS()` | Refused | Requires administrator; no fallback-mode indicator returned. |
| Fabric SQL `sys.dm_db_external_tables_log_status` filtered to the source table | Accepted, zero rows | No Delta version returned. Empty results do not establish a permission denial or identify why the row was absent. |

Evidence: [refresh-history/partition probes](docs/job-history-path-and-refresh-probes.md)
and [snapshot-version/fallback probes](docs/snapshot-alignment-audit.md), including
exact requests, responses and identity provenance. These results constrain the
current reader; they do not assert that every identity or estate lacks the APIs.

Do not elevate the execution reader or keep retrying these routes to make a
comparison appear verified. Distinct execution surfaces do not establish aligned
snapshots. Equal values do not establish currency; different values do not exclude
timing as the reason for the difference. A latest OneLake commit observed by the
separate metadata/fixture-owner identity is not the version served by a SQL or DAX
quantity read and must never be represented as reader attestation.

Snapshot attestation now defaults to SNAPSHOT_UNVERIFIED; see
[the implementation and limits](docs/snapshot-attestation.md). A separately
configured metadata identity may enrich the record, but a standalone metadata
query does not attest which version a quantity read served. Only genuinely
query-bound, aligned reports can produce SNAPSHOT_VERIFIED. No live verification
or freshness-fixture success is implied.

## Refresh timing permission finding (2026-09-27)

The least-privilege reader was tested and refused by both routes: Power BI REST
refresh history requires dataset Write, and XMLA TMSCHEMA partition metadata
requires administrator. See docs/job-history-path-and-refresh-probes.md for exact
receipts. Do not elevate the execution reader or keep probing these routes.
The engine does not rely on refresh timestamps. A positively established unchanged
declared-source boundary may support comparison-based REFRESH_LATENCY after two
independent, attested quantities diverge. Missing timestamps and non-shared read
snapshots limit that claim. Optional estate-configured metadata timing uses its own
explicit identity provenance, never substitutes for quantity-reader evidence and
never selects an outcome.

## Evidence discipline

Reachable depth is a property of the estate, not the engine. The operator's
configured boundary depth is a CEILING, never a reachability or completeness
claim. Every lower layer still needs a declared binding, faithful quantity,
successful isolated read and surface attestation. Most estates will not expose
their source application. Early termination is a conclusion scoped to the named
verified depth, with every unchecked boundary and its reason in the limits of
both outputs. Never approximate a quantity to meet the configured depth.

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

Dated correction, 2026-09-27: the historical statements below about no completed
investigation and no table read are superseded by run c2658c88, the first completed
known-domain investigation through one independently compared boundary and
validated synthesis. It did not exercise divergence or definition judgment.
See docs/current-delivery-status.md for subsequent work and current evidence.

- The outcome taxonomy and the vertical procedure are implemented in
  `scripts/investigator/process_debugging.py`.
- Capability declaration and gating work: `REQUIRED_CAPABILITIES`,
  `OPTIONAL_CAPABILITIES`, `applicability()`, and the pre-`DEFECT` gate that
  refuses a defect claim when competing explanations were not checked.
- The offline replay harness (`acceptance/unknown_domain/session_replay.py`)
  blocks network at socket level and matches requests byte-exactly.
- **The reader's Direct Lake access is restored** (2026-09-27 00:33 UTC).
  - **The fault:** the password reset at 2026-09-26T20:42:20Z left a stale
    service-side grant (`AADSTS50173`), masked by Execute Queries as
    `0xC1450012`.
  - **The fix:** it was cleared only by an interactive sign-in to the Power BI
    portal as the reader. A client MSAL sign-in and OneLake role membership did
    not clear it. No API exposed the remedy.
  - **Current state:** live DAX baselines as the reader are `OBSERVED` again,
    and the DAX self-report attests the reader's identity live. The reader holds
    no OneLake role membership.
- **No investigation has yet completed end to end.** The model's
  `judge_definition` call has never been invoked in a live run.
- The Gold Fabric SQL analytics endpoint the process path needs (`77c49180…`,
  `warehouse_gold_e1b8e1` in workspace `149f8d99…`) is reachable by the
  least-privilege reader `investigator-reader@skynwhy.com` (workspace `Viewer`).
  The reader signs in through its own isolated Azure CLI profile
  (`.local/azure-reader-sql`), with no new permission and no app registration.
  The server confirmed the identity and the database (2026-09-26). Not yet
  established:
  - No table has been read.
  - No explicit `DENY` has been checked.
  - Viewer is broader than needed.

  `evaluate()` reads a faithfully declared `declared_source` layer on this
  endpoint as the reader (item 2b). Otherwise `NO_INDEPENDENT_LOWER_READ` still
  applies. No comparison run has been performed yet. The Fabric CLI client
  still fails with `AADSTS65002`. The "isolated metadata identity" is the tenant
  administrator (`admin@skynwhy.com`), so its receipts are admin receipts.
- **Surface self-report is enforced and consumed** (`process_debugging.attest()`).
  - **Attestation:** a probe that claims a surface is `OBSERVED` only if the
    surface's own answer includes an identity, reports every field the probe
    declares it is able to report, and contradicts nothing declared. Otherwise
    it is `UNAVAILABLE`, with the missing report or the contradiction recorded
    and its prior status kept.
  - **Consumption:** every field a compared surface could not report is named
    in the claim's limits and in both outputs (`unattested_surface_fields`).
    Outcome validation refuses a comparison without a `MATCHED` attestation on
    both sides, or a claim that omits an unattested field.
  - **Fabric SQL:** answers with `SUSER_SNAME()`/`DB_NAME()`. Verified live
    once, as the reader, on `warehouse_gold_e1b8e1`.
  - **DAX:** answers identity only, via `USERPRINCIPALNAME()`; the model object
    is not attested. Not yet verified live: on 2026-09-26 the Power BI surface
    rejected even the unchanged baseline query (HTTP 400, Analysis Services
    `0xC1450012`), so every DAX baseline is currently `UNAVAILABLE`.
  - **SQL sessions:** `scripts/fabric_sql_auth.py` takes its account and profile
    from configuration (`fabric.sql_session`, `fabric.sql_reader`) and never
    falls back between them.
- Horizontal comparison, recurrence learning, declared business context and the
  known-issues register are **proposal-only**. Do not implement them
  opportunistically.

## Known past failures — do not reintroduce

- Adding reader and transport sections to an environment's config changed the
  whole-config digest that discovery approval pins, so every catalog-mediated
  investigation was refused (2026-09-26 onward). Checks that call the adapter
  directly did not notice. After any config change, confirm discovery approval
  still matches before running.
- The engine fingerprint hashed only `scripts/investigator/*.py`, so adapter- and
  transport-only changes left the tag unchanged, and a freeze could certify
  changed behaviour. Fixed: it now covers the package recursively and every
  transport. Every earlier tag is invalidated.
- A surface reported a failure only generically (Execute Queries:
  `DatasetExecuteQueriesError` / `0xC1450012`). A full day went into wrong
  hypotheses while the specific error (`AADSTS50173`) was available from XMLA.
  Fixed by `refine_failure()`: a generic failure is refined through another
  interface to the same surface before it is reported, and the status is never
  upgraded. Verified live on 2026-09-26, when XMLA supplied `AADSTS50173`
  behind the masked error. The refinement is sealed as its own `failure_detail`
  receipt, verified in tests only.
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
