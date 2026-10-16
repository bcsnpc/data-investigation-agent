# Historical earned gate and current narrative audit ? 2026-10-10

The current checker reproduced the hosted failure counts from the hash-verified original earned42 without replay or network access: shards8/11,10/11,11/11,9/9. Structured outcomes and answer categories still match. The four failures are stripped family-B-noisy, family-B-terse, family-B-typo and family-H-noisy. Their original mechanism paragraphs say "stops before", an engine-owned refusal/status phrase newly banned by6ce5b4f in Round Thirteen. These current-policy failures remain visible; the original paragraphs are not rewritten or deleted.

The workflow calls its check "Replay earned historical producers against sealed expectations", and replay already selects each recorded producer revision. However, its final grade imported today's narrative validator, retroactively applying an expanded policy to archived outputs. Historical exact replay and current prose conformance are different tests.

## Exact policy provenance

Retained hosted run37724611630 completed all four earned jobs successfully on2026-10-08 at commit0a577fae9fa54093b18318a568e7a1b28db1b059. The saved control-plane result is `.local/round-ten-20261007/part-b/earned-hosted-37724611630.json`. This real checker revision is pinned in `acceptance/round_ten/historical-policy.json`, along with the exact Git archive/checker/module SHA-256 values, each of the four complete roster hashes, and every selected run/tape hash. Windows checkout newline conversion is disabled for the archived Git blobs so their byte identity is portable; no code is altered inside the archived policy.

The current gate verifies the selected run and tape bytes before invoking the historical checker. Only an exact pinned roster and entry can select it. The checker executes the real archived `acceptance/round_ten/check.py.grade` with that commit's dependencies in a separate process where socket connections are refused. New or unpinned rosters use today's checker. Structured expectations remain unchanged, and a changed outcome still fails both policies.

A separate `CURRENT_POLICY_AUDIT` is always included in scores and printed in the hosted console. It reports today's exact errors, including the four archived "stops before" paragraphs. Historical acceptance is not claimed as present-day narrative conformance. New captures cannot inherit this old-policy exemption by filename or copied prose: the complete roster and sealed entry hashes must match the exact archived cohort.

## DECIDED WITHOUT REVIEW

Decision: separate exact historical-cohort acceptance from the current narrative-policy audit, with the actual prior successful gate revision as the historical policy pin. Root reviewed the provenance and implementation direction before edits. Alternative rejected: re-synthesising or replacing archived mechanisms until they satisfy today's prose rules. That would alter the evidence of what the historical producer said and erase the current-policy negative finding. No expectation value, original run, tape, engine module, identity, permission or budget was changed. No model call or estate read was made.

The first four-test check had two archive/checker-hash errors due Windows newline conversion and two passes; that failed check is preserved as a finding. After explicitly selecting exact Git blobs, four tests passed. Final checks additionally verify every pinned module hash; their result is recorded separately by the delivery report.
