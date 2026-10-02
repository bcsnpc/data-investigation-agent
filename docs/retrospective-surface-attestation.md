# Retrospective surface-attestation correction after #299

Date: 2026-10-02 (America/Chicago). Examined merged `main` at `955b3fe`.
This answers section 0 only. No intake, wiring, engine, estate or configuration
change; no investigation or provider/cloud request was performed.

## Finding

**The first completed investigation and the divergence investigation had
partially attested comparisons, not verified comparisons under #299's standard.**
Their reads, values, receipt integrity and historical completion remain real.
The historical `MATCHED` and `CROSS_SURFACE_VERIFIED` labels overstated coverage.
They remain stored exactly as emitted; dated corrections qualify their meaning.

There is also a correction to the premise that every boundary had a semantic
surface on one side: the divergence run's second boundary was Gold-to-Silver,
SQL-to-SQL across different declared database objects. Both SQL probes were
partial too. This is not just a DAX limitation.

## What the merged code requires

From [process_debugging.py](../scripts/investigator/process_debugging.py),
`attest_surface()`:

```python
partial=bool(set(declared)-set(report))
return {'status':'CONTRADICTED' if contradictions else ('PARTIAL' if partial else 'MATCHED'),
        'consistency':'CONTRADICTED' if contradictions else 'MATCHED','coverage':'PARTIAL' if partial else 'FULL',
```

From [process_outcomes.py](../scripts/investigator/process_outcomes.py), validation
of `CROSS_SURFACE_VERIFIED`:

```python
if (not isinstance(attestation,dict) or attestation.get('status')!='MATCHED'
        or attestation.get('coverage')!='FULL' or attestation.get('consistency')!='MATCHED'
        or attestation.get('unattested_fields')):
    raise ValueError('A boundary comparison requires both surfaces to be attested')
```

The procedure also records incomplete cross-surface coverage as NOT_COMPARABLE,
with `SURFACE_COVERAGE_INSUFFICIENT_FOR_CROSS_SURFACE_COMPARISON`.
Client-selected route IDs and an intact receipt seal do not fill self-report gaps.
Surface coverage is separate from snapshot alignment; neither of these runs
establishes a common served snapshot or currency.

## First completion: c2658c88

Run `c2658c88-bbcc-44fc-b066-7d950c742f92` completed intake, reads, the historical
comparison procedure and validated synthesis. Its stored outcome remains
CONSISTENT_TO_BOUNDARY. The two sealed query receipts were read from the retained
catalog in read-only mode, and both integrity checks returned SEALED:

| Receipt | Local seal hash | Measured scalar |
| --- | --- | --- |
| `a44a4c48-87a2-4f21-abc6-2147573dd02e` | `7b39f90a1d16edabb46cfa90f18b573e2147140399e7da25bdeb291a0b39940f` | 8765 |
| `25182d69-3f7c-47dc-9dbe-419c70a78852` | `dcc845030ded860cc13c5657ccfca1445a3bab99587273952a0f6cde57c87438` | 8765 |

The DAX receipt's exact `surface_report`:

```json
{"identity": "investigator-reader@skynwhy.com"}
```

The SQL receipt's exact `surface_report`:

```json
{"identity": "investigator-reader@skynwhy.com", "object": "warehouse_gold_e1b8e1"}
```

The [stored run record](runs/synthesis-narrative-live.json) explicitly preserves:

```json
{"attestation": "MATCHED", "attested_fields": ["identity"], "unattested_fields": ["connection", "engine", "object"]}
```

for DAX, and:

```json
{"attestation": "MATCHED", "attested_fields": ["identity", "object"], "unattested_fields": ["connection", "engine"]}
```

for SQL. These are quoted field subsets, not replacement records.
Under #299 both are PARTIAL. What the run supports is observed equality of
two independently executed quantities on declared routes, with the named
self-report gaps. It remains the first completed end-to-end execution, not
the first fully attested verified boundary investigation. It establishes
neither source correctness, current data, the deeper chain nor a verified cause.

## Divergence and definition judgment: 3d2c5bf0

Run `3d2c5bf0-9e5c-4fcc-ba19-8b017a47e4b7` completed historical synthesis with
TRANSFORMATION_LOGIC. `judge_definition` ran and returned EXPLAINS.
All three query receipts remain SEALED:

| Receipt | Local seal hash | Measured scalar |
| --- | --- | --- |
| `66413822-628a-4740-8f4b-967480346081` | `41457a3fc929926e633c682c7d3101093b407c3036379e71881cfcd2974c7ad8` | 8765 |
| `34382890-fcd5-4d02-9f3e-034530989fda` | `42a1055488d4ac8837addcae1b32d4f0796181921495ae4fce7275417547fb67` | 8765 |
| `b57c29c6-7777-45d6-8f12-d24658b9819d` | `6e59153348cf85ca9a9df41d3d26c41353ae2498f62184976290cd1f9879abbc` | 7661 |

Their exact `surface_report` objects, respectively:

```json
{"identity": "investigator-reader@skynwhy.com"}
{"identity": "investigator-reader@skynwhy.com", "object": "warehouse_gold_e1b8e1"}
{"identity": "investigator-reader@skynwhy.com", "object": "warehouse_silver_e1b8e1"}
```

The [stored record](runs/contract-ledger-output-live.json) labels both boundaries
CROSS_SURFACE_VERIFIED; its linked ledger row records the same three DAX/SQL
attestation gaps quoted above. **Neither boundary satisfies #299.**
The [recorded judge](contract-ledger-output-rerun.md#definition-judge---verbatim)
said:

> The definition shows a mechanism that can cause the increase, but it does not establish that duplicate matches actually occurred, which products caused them, or whether both sides are from a common snapshot.

The supported interpretation remains two observed equal quantities and a third
different quantity, plus a definition-compatible left-join multiplicity mechanism.
It is not a fully surface-verified attribution of that difference to the
transformation, proof of actual duplicate matches, intended semantics or exclusion
of timing. The historical outcome is not changed or regraded as a new run.

## Overstatements and appended corrections

- README and current delivery status describe the first real comparison and
  the later two comparisons as verified, and call a returned number verified.
  The quantities were observed; complete surface verification was not achieved.
  Their appended corrections explicitly supersede those verification readings.
- The first-completion delivery record says "One verified cross-surface
  comparison" and explains that "Verified" means the admitted comparison.
  That admission is exactly the reading #299 changed. Its original text and
  verbatim outputs remain, followed by the correction.
- The divergence delivery record says "two verified cross-surface comparisons"
  and its table retains CROSS_SURFACE_VERIFIED. A dated correction qualifies
  both boundaries and the definition judgment without altering the original.
- Twelve detailed ledger rows directly record nineteen CROSS_SURFACE_VERIFIED
  comparisons alongside nonempty self-report gaps. Each receives a separate
  correction annotation keyed by the original row hash. Outcome labels remain
  historical decisions under the then-current contract, not assertions that
  the evidence satisfies #299. Original rows, counts and receipts are untouched.
- Later condensed ledger rows do not include that detailed comparison payload.
  The linked output/batch reports also receive the same dated qualification;
  their saved outcomes and original output files are not rewritten. No claim
  is made that an omitted attestation in a condensed row was full coverage.
- The root handoff and chronological progress record receive an appended
  correction directing readers to this audit. The root handoff did not itself
  claim these two runs were fully verified; its current-status link now resolves
  to a record with explicit qualification.

This audit does not make a new no-comparable-path outcome for a past run, undo
successful execution, or collapse independent-route measurements into a
within-layer query. It corrects evidence strength. No code, new freeze, run,
ledger run row, fixture, permission, budget or discovery revision is introduced.
Intake resolution and wiring await the requested section-0 report checkpoint.

Validation: all 271 pre-existing ledger lines are unchanged. Twelve appended
annotations qualify nineteen comparisons that explicitly paired the old verified
label with missing surface fields. All twenty corrected documents retain their
original byte prefixes; all 484 local links in the audit/corrected documents
resolve, and `git diff --check` passes. No saved run/output JSON or engine file
was edited. This documentation-only audit changes no engine bytes and introduces
no additional freeze invalidation beyond #299's existing invalidation.
