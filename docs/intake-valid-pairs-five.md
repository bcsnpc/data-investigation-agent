# Intake valid-pair schema and five same-ticket trials

2026-09-27. Tracking #193. Known-domain intake/preview regression only.

## Contract change

The provider wire schema replaces independent `ticket_shape` and
`comparison_mode` enums with one `triage` enum:

- `MISMATCH_COMPLAINT:VERTICAL`
- `MISMATCH_COMPLAINT:HORIZONTAL`
- `BUSINESS_QUESTION:NONE`
- null for ASK (decoded to the historical pair of nulls).

The decoder restores the existing persisted proposal fields. The application
validator uses the same valid-pair table and remains in force for non-provider
callers. Shape/mode fields are absent from the new wire schema and extra fields
are forbidden. Unknown triage strings fail closed even if a provider ignores its
schema. The change adds no retries or semantic routing heuristics.

Unrepresentable non-null pairs are `MISMATCH_COMPLAINT + NONE`,
`BUSINESS_QUESTION + VERTICAL`, and `BUSINESS_QUESTION + HORIZONTAL`.
None were legitimate: each was rejected by the existing application contract.
Partial-null pairs are also unrepresentable. All three previously valid pairs,
and the all-null clarification representation, remain available. ASK/PROPOSE,
metric selection, scope and requested clarification still receive application
validation; this does not guarantee the model chooses the right valid route.

Prompt routing definitions and ambiguity guidance are unchanged. Only field-name
references in the output-format instructions were mechanically updated for the
single serialized field. This is a schema change, not a prompt reliability fix.
Historical provider recordings and v1 synthetic fixtures remain unchanged. The
synthetic tests explicitly adapt response serialization and assert all request
content/settings except schema and those field references remain golden-exact.
Historical live request tapes cannot be replayed byte-exact against a new schema.

## Context and conditions

Before/after catalog: 5 models, 37 measures, 91 columns, 28,658 input characters;
the input string is byte-identical. Intake has no investigation asset directory
or SQL-object directory (0/0 before and after). Serialized provider request size
changes from 38,020 to 37,993 bytes. No catalog coverage is removed. Twelve
synthetic golden cases and eleven planner projection checks protect context.

Five attempts use the same original G ticket, environment, catalog, profile,
read/input limits and recording configuration. They run intake and preview only,
without starting investigation execution. Each fresh attempt makes at most one
intake provider call; pacing between attempts is retained. No permission, policy,
model setting, deadline or quota change; no refunds or counter resets.
The intake endpoint still uses its 1,500-output-token allowance and default
reasoning, independently of the investigation profile's 8,000-token/medium setting.

## Results

| Trial | Shape | Mode | Intake | Preview |
| --- | --- | --- | --- | --- |
| I1 | MISMATCH_COMPLAINT | VERTICAL | PROPOSED | Passed |
| I2 | MISMATCH_COMPLAINT | VERTICAL | PROPOSED | Passed |
| I3 | MISMATCH_COMPLAINT | VERTICAL | PROPOSED | Passed |
| I4 | MISMATCH_COMPLAINT | VERTICAL | PROPOSED | Passed |
| I5 | MISMATCH_COMPLAINT | VERTICAL | PROPOSED | Passed |

All five selected `MISMATCH_COMPLAINT:VERTICAL`; all five passed preview.
They also selected the same model, measure, verbatim metric quote and empty scope.
The five requests are byte-identical to each other (37,993 bytes), and all five
parsed wire decisions are identical. Their request SHA-256 is
`70d48c17435ad07ed20f162f583beb78becf38d0796efcb2c7b422b3bd102938`. Provider-generated IDs, timing and cache usage
may differ; this is consistency of decisions, not byte-identical responses.
All five manifests verify and their actual outputs pass the actual wire schema.

The original three trials had 2/3 incompatible-pair holds; this batch has 0/5
holds or route changes. The observed failure disappeared rather than moving to
clarification, another valid route, metric selection or preview in these five
attempts. This small sample does not prove general determinism or correct routing
for other tickets. Other semantic and scope constraints remain application checks.
No investigation or synthesis ran; no end-to-end success is claimed.

Engine `da5184d`, fingerprint `db74f9946a64e9c52efe5bcd9962f0ed2e717219433a764b0e3e50f3924b162e`.
Daily reservation deltas: 5 intake calls,
212,395 input characters, 7,500 output
tokens, 0 cloud reads. All settled; original usage retained.
Measured token reference cost: USD 0.054201, not an
Azure billing statement. Five ledger rows appended; all 213 prior rows preserved.

Validation: 47 focused intake/family/golden/generator tests passed; full unittest
suite **1,190 passed** in 258.926 seconds with Python exit 0. ResourceWarnings
remain in the local log. The initial synthetic-golden run correctly failed against
v1 schema expectations; its explicit v2 serialization adaptation now passes without
rewriting the historical fixtures. No engine/settings changes occurred during the
five trials. Normalization is separately reviewed in PR #257; this isolated intake
branch derives from main after #254/#255 integration, not that pending PR.

- [Five run summaries](runs/intake-valid-pairs-five.json)
- [Manifest, per-call decisions, schema validation and usage](runs/intake-valid-pairs-audit.json)
- Local artifacts: `.local/intake-valid-pairs-five-20260927/` and the five immutable
  recordings named in the machine-readable audit.

