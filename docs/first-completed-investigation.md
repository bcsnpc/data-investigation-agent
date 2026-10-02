# First completed end-to-end investigation: c2658c88

2026-09-27 UTC. Known-domain regression, not unfamiliar-domain acceptance.
PR #262 merged after all six checks passed, at
`542ab0bf354d47eaac544681ce9e0c41a6b878d4`.

Run `c2658c88-bbcc-44fc-b066-7d950c742f92` is the first recorded investigation
that completed intake, a genuine cross-surface boundary comparison, and validated
synthesis. Its implementation and original evidence are preserved in the
[synthesis contract report](synthesis-narrative-contract.md),
[run receipt](runs/synthesis-narrative-live.json), and
[complete outputs](runs/synthesis-narrative-outputs.json). No historical run was
rewritten or rerun for this milestone.

## What completed, and what did not

- One ticket, one known domain. This is an execution milestone, not evidence of
  generality, repeatability, correct source entries, or intended business rules.
- One of four intended boundaries checked: semantic model to Gold. Both reads
  returned **8,765**. Gold to Silver, Silver to Bronze, and Bronze to application
  source were not compared. The intended chain is a target, not proof that all
  four physical bindings exist in this fixture.
- One verified cross-surface comparison; zero within-layer comparisons. Power BI
  DAX read the measure; Fabric SQL independently read the bound Gold table.
  Both reported the isolated reader identity. SQL also reported its database.
- Five surface fields remain unattested: Power BI connection, engine and object;
  Fabric SQL connection and engine. ?Verified? describes the admitted comparison,
  not complete attestation or source correctness.
- One intake call, **0 investigation planner calls**, one synthesis call.
  Synthesis completed and validated. The investigation itself followed the
  deterministic process procedure, not an observation-driven planner trial.
- One DAX read, one Fabric SQL read, one OneLake commit-metadata invocation
  (two HTTP requests). Commit presence is not an ingestion completeness check.
- Outcome: `CONSISTENT_TO_BOUNDARY`, stopping at Gold with deeper capability
  unavailable and presentation freshness skipped.
- **No divergence path exercised. `judge_definition` still never invoked in the
  recorded live process investigations, including this run.** This milestone
  does not validate transformation judgment, load-latency diagnosis, ingestion-gap
  diagnosis, or any explanation of a real disagreement.
  The unchanged 221-row ledger contains 18 rows with `definition_judgment`; all
  18 arrays are empty. This is the recorded process evidence, not a claim about
  unrecorded experiments or the older adaptive planner's reasoning.
- The output defects remain: business jargon and an irrelevant second number;
  no recommended action in either returned output; five attestation limits exist
  in structured records but are omitted from the technical narrative. This
  documentation preserves those defects verbatim rather than polishing history.

## Business explanation ? verbatim

> The displayed measure total and the displayed warehouse total agree at the checked aggregate level: the Activity measure shows 8765, and the SQL sum of units in movement_values also shows 8765. That means the investigation found agreement between the reported Handled Quantity total and the summed source-table total that was actually checked. The available ingestion metadata also shows movement_values as an available written table with 406 output rows in its recorded write. This supports aggregate agreement across the checked boundary, but it does not show whether any individual stock movement or inventory adjustment entry is correct, complete, or aligned with the intended business rule. No displayed evidence inspects individual movement rows or related adjustment rows.

## Technical explanation ? verbatim

> At the presentation surface, a bounded DAX query returned [Handled Quantity] = 8765. At the lower checked layer, a bounded SQL query returned SUM([units]) = 8765 from [dbo].[movement_values]. The comparison artifact reports these values as equal between the Activity surface and movement_values. Ingestion metadata for movement_values shows an available Delta commit for a WRITE operation with numOutputRows = 406. The displayed evidence therefore shows aggregate consistency from the Activity measure down to movement_values. It does not display row-level stock movement records, inventory adjustment tables, transformation definitions, or logic proving how adjustments should be included or excluded, so source correctness and business intent remain unverified by the shown evidence.

The linked complete output JSON also preserves every citation, structured fact,
mandatory limit and additional limitation exactly as returned. This page quotes
the two explanation strings without changing them.

## Next decision

The [whole-chain investigation](whole-chain-investigation.md) establishes the
shape of further work. It implements nothing. Output enforcement, mandatory
outcome-derived actions and explicit technical attestation fields remain queued
under Part 3, after the requested Part 2 report-and-stop checkpoint.


## Dated correction: surface verification (2026-10-02, America/Chicago)

The historical claims above about verified cross-surface comparisons must not be
read as satisfying the full-coverage standard merged in #299 (`955b3fe`). The
[receipt audit](retrospective-surface-attestation.md) found identity-only DAX self-reports and
identity/database-only SQL self-reports, with engine/connection (and the DAX
model object) unattested. Earlier MATCHED/CROSS_SURFACE_VERIFIED labels admitted
partial coverage; #299 now calls that PARTIAL and refuses verified boundary
eligibility. Snapshot alignment remains unestablished separately.

Run c2658c88 remains the first completed end-to-end **execution**, with two
observed values of 8,765 on independently declared routes; it did not establish
a fully attested verified boundary. Run 3d2c5bf0 observed 8,765, 8,765 and 7,661,
and invoked a judge that identified a compatible join mechanism; neither its
DAX/SQL boundary nor its SQL/SQL boundary satisfies #299. These observations
and the qualified mechanism remain useful, but do not prove actual duplicate
matches, current snapshots, intended semantics or verified transformation
attribution. Other historical comparisons using the same partial self-report
contract are subject to the same qualification. Original prose, outputs,
receipt bodies, counts and outcome labels are preserved, not retrospectively
regraded. Ledger corrections are annotations, not replacement runs.
