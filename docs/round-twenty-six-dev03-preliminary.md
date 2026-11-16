# Preliminary corrected-image subset

Two tickets ran on source d401c5a0, image e6850f0e, before the remaining queue was admitted. Both returned NEEDS_INPUT with zero physical data reads: R17-01 ($0.393981) and R17-04 ($0.317976). Independent primary, secondary, strict and saved-evidence-projection review all score0/2, harmful0; these are not passes and are not environment exclusions. Original outcomes and seals remain unchanged in the dev03 capture set.

R17-01 exposed a catalog bug: an inferred synonym on another page defeated the explicitly named page. Native scope proves the selected page contains exactly one visual using the named measure. The generic correction scopes alias lookup to the named page, still rejects a contradictory exact native title and never uses a model-inferred page as user scope. Question choices also stop displaying opaque native visual names. Two synthetic regressions cover these behaviors;258 focused tests passed. the original saved proposal resolves offline to the same visual with zero new estate/model calls.

The next complete failed-only cohort must use one newly qualified image. Preserve this two-ticket subset separately; no mixing scores across images.
