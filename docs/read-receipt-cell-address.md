# Definition shape and per-read cell addressing

Dated implementation, 2026-10-03 America/Chicago. Engine and adapter bytes changed; prior freezes invalidated.

The defect exposed by R1 was an invalid one-cell-per-definition assumption. A definition now carries its visual target, measure and grouping columns. Each declared value read carries its own complete cell address in the compiled request and sealed receipt. Synthesis compares the marker against that read address and verifies the address against the shared definition shape. Missing addresses refuse, rather than being inferred from a marker or defaulted to total.

Hostile tests cover two independently validated cells sharing one definition, a missing read address, and a forged grouping column even when marker/read agree. The original cell contract continues to require one key value per grouping column; TOTAL requires grouping metadata with no keys. Synthesis also checks the observation address against its sealed request.

Memoisation now includes the complete cell address, including target and mode, alongside compiled context/policy/reader/report identity. KEYED, TOTAL and different addressed cells cannot consume a cached result as the same probe. Baselines have no addressed-cell key and remain reusable across candidates. Admission estimates use the same key and explicit probe purpose. This can spend more diagnosis slots than #318's cross-cell reuse; no cap was raised. Three candidate cells now cost three declared reads plus one shared baseline, rather than sharing one declared read across separate cell addresses. Existing assertions that depended on that conflation were changed to retain named cap-stop evidence.

The 2026-10-03 preserved runs predate the new field. No original receipt or run is rewritten. Re-synthesis requires an explicit decision about independently derived historical bindings versus preservation of missing-address refusals; a post-hoc marker is not a substitute for read evidence. No re-synthesis, investigation or ledger row was produced in this implementation PR.

PR #321's rendered-spine change merged as a279028 with six green checks. Tests, CI and historical bridge decision are recorded on this PR. README/current status updated; fixture/config/policy/grants/caps unchanged.

Dated historical-binding authorisation: the user approved separately recorded retrospective bindings for these three preserved runs only. Each address must independently regenerate from retained context and compile to a byte-identical sealed statement. No match means no binding. Both offline outputs name the derived rather than natively recorded identity. This is a one-time local migration, not an engine backfill path; originals remain untouched. No re-synthesis before this PR merges.
