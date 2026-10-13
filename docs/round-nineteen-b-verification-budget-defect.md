# Part C attempt 1: mismatched round policy

2026-10-13. The prepared manifest used `ROUND_NINETEEN_B`; the verification
specification still contained `ROUND_NINETEEN`. This was a configuration defect
in the offline preparation, not an estate failure. The earlier preparation
report checked the probe count and prewarm scope but incorrectly described
admission as complete.

The verification-stage preflight did not compare the whole budget object, so
the model candidate was published. The actual verification runner then refused
with `VERIFICATION_BUDGET_DIFFERS` before estate or model calls. The failed output
remains unchanged at `.local/round-nineteen-b/cloud-stage-verify-01/output.zip`,
SHA-256 `a8dbbb9c3907b484a9b34fe24c4363c4e395eefee766df3a14065b23fb07bb92`.
Publication changed the model hash from
`43f8405e5719855b7e4b1cc30cb8d952f77fbd26e908032d75dff9799b74f4de` to
`8e01c661d54a1c1555617b9fedb647c24afac1f0157293b2698dac4ae31ac8e9`;
publication earned no readiness or verification.

Preflight now requires the complete manifest budget and refuses any unequal
specification budget before object resolution or candidate publication. The
runtime's existing exact comparison remains in place. A regression checks
round, rolling and additional policy-field differences; a stage-level regression
asserts neither publication nor verification executes on mismatch. The focused
verifier, prewarm and stage suites pass 23 tests and six subtests.

Only one live attempt remains. Its input must start from attempt 1's published
output, use exactly the manifest's whole budget in the verification specification,
update the specification hash in the operator plan, and receive a new image,
engine/context approval and current-PG comparison. No prior readiness or live
result is transferred. The first input, publication and failure remain historical
evidence; they are not repaired in place.
