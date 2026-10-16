# Claim catalog migration plan — offline inspection, 2026-10-13

There is no single merged historical claim catalog. The Round Seventeen pipeline
runner defaults to `.local/round-sixteen/fixture-readoption/estate.json`; its
catalog is the pipeline installation's authority. The setting-on comparison was
deliberately copied to `.local/round-seventeen/handoff-installation-v2/estate.json`
by `d-adopt.py` / `d-adopt-resume.py`. Both manifests declare environment
`unknown-domain-v4`, but they are different installations and were not merged.
The first `handoff-installation` is an earlier copied baseline, not a later
complete replacement. The closed Round Seventeen RESUME record says no live
operation remains; it does not promote either copy over the other.

Read-only SQLite inspection found:

| Source installation | Claim intakes | Revisions | Investigations | Glossary events | Handoffs |
|---|---:|---:|---:|---:|---:|
| `round-sixteen/fixture-readoption` (pipeline default) | 10 | 27 | 3 | 222 | table absent |
| `round-seventeen/handoff-installation` (older copy) | 3 | 6 | 3 | 222 | table absent |
| `round-seventeen/handoff-installation-v2` (setting on) | 7 | 13 | 3 | 441 | 0 |

All three share three byte-equal intake records and three byte-equal
investigation records. The pipeline adds seven intake IDs; handoff-v2 adds four
different IDs. A union would silently combine cohorts and glossary histories.
Even equal primary-key records can have different row IDs across installation
copies; the migration contract preserves row IDs and source tables exactly.

The exact **claim-table-only** source bundles, using
`shared-application-rows-v1`, original schemas/columns/row IDs and environment,
have these hashes:

- Pipeline: `ce167854d11a36795fc9f81ea941f8175e64fa10b66e009fdf0010e87eec3893`
  (262 rows across five claim tables).
- Handoff-v2: `7a97b98f0e3c4d626401a99ecc49718da3da9677fc9f415b333ea3c9fe6a9581`
  (464 rows across six claim tables).

These are application export hashes, not whole SQLite file hashes. They do not
include runtime tables, tapes, source data or credentials. No source was edited
and no migration was applied during this inspection.

Recommended plan:

1. Retain both installations independently in the private archive, pinned by
   their source manifests and hashes; do not rename environment fields or merge
   rows to manufacture one current catalog.
2. If continuing the pipeline installation is the intended cloud authority,
   explicitly record that selection and migrate its five claim tables only into
   the still-empty corresponding application-table keys. The existing whole
   primary-catalog migration must not be rerun or replaced. Use a distinct
   migration ID and the exact claim-only source hash above.
3. Before applying, verify that each of its three investigation session IDs
   refers to the intended runtime history already migrated. Compare immutable
   rows, not names. If a referenced runtime row is absent or differs, retain the
   case as historical evidence and report the gap; do not guess or merge it.
4. Run the existing exact migration function on that explicitly selected source
   subset. Its target-not-empty check and per-table row/hash proof remain in
   force. The production case writer runs in the same transaction. Keep the
   handoff-v2 cohort separately archived until an installation namespace is
   explicitly selected for it.

The current application authority is keyed by environment and table, so both
independent installation catalogs cannot be promoted under `unknown-domain-v4`
without a namespace decision. That is a recorded limitation, not permission to
rewrite their manifests, evidence or identities. Root owns selection and apply;
this document is a plan only.

## Runtime-reference check: blocked, 2026-10-13

Root selected the pipeline default for consideration, conditional on exact
runtime-reference agreement with `.local/unknown-domain-v4/catalog.sqlite`
(the source of the 23,568-row primary migration). Both databases were opened
read-only. That check failed because the referenced sessions are absent:

| Claim | Recorded status | Explicit session | Pipeline rows | Primary rows |
|---|---|---|---|---|
| `ce337237-0982-4b2e-add2-bb5b69da65dd` | COMPLETED | `c62ff14f-3af5-45dc-b907-cc4938c9057c` | session 1; synthesis 1; events 38 | 0 in each table |
| `ceb8d931-261d-4852-abf4-806f2fbf8a4c` | PARTIAL | `4ad161ad-500a-499c-acaf-517869adf5e7` | session 1; events 7 | 0 in each table |
| `06d18d76-d26d-4537-941f-663f71adb1ad` | HELD | no session/candidate-session reference | no runtime asserted | not applicable |

Canonical column-and-row hashes for the completed session in the pipeline are
`0d9091992dfa8892385e46837f154474fd10f5b1cb05b147ba28b8aa641efcea`
(`adaptive_sessions`),
`6d78e9466892095b0cd8c38ca19c610069e06c222b08bc8397a8e90cc104305e`
(`adaptive_syntheses`), and
`158f908a14dce6711e1dced05ca0db949b805cd8355122728cb375d3f0f12c6f`
(`adaptive_events`). The partial session hashes are
`45aab58449dfd6c4e93ab8b31e0a7b0edf0549a2604f9941b7b373047e1588af`
and `2d340ce2c47594f5e73735e5e93870613ab28fe858df0e0fadd5f6beed94789b`.
These hashes describe `SELECT *` rows in original row order plus their column
names; they are comparison receipts, not replacement migration hashes.

**No claims-only import payload was prepared and no merge was performed.**
The two nonempty runtime histories remain in their original pipeline catalog.
An isolated installation import preserving its entire claim/runtime namespace
would need an explicit namespace decision; adding these claims alone to the
primary authority would create dangling case references.
