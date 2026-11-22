# Round27 owner-selected pass3 evaluator

Owner steer,2026-11-22: pass3 uses the repair image with `r27_slim_evaluator=true`. Its factory default isfalse, preserving earlier modes. The pass3 profile sets full advisoryfalse; if both flags are supplied, slim semantics take precedence explicitly.

The evaluator still returns and records all four unmodified checks. `approved` and `would_reject` retain their all-check meaning. A separate `blocking_failures` field contains only a substantive failed `question` check; `support`, `target` and `claims` remain in `advisory_failures` when failed. Wording/completeness findings cannot force rewriting or downgrade. Invalid/truncated evaluator output is a format warning, not invented evidence of a wrong question.

An exact-question rejection returns its specific reason. The investigator gets at most two retries after the first rejection; a third failure produces an UNRESOLVED handoff retaining checked findings. Native operational deliveries use the same two saved-evidence rewrite opportunities. No new estate read is available to the native rewrite. A corrected exact answer may deliver even when other evaluator checks still fail. Existing native-reference, explicit-target, unique-match, primary-question, native-title, record-key, latency and record-only-context code checks stay on; slim mode bypasses none of them.

Pass3 is the deduplicated union of **all pass2 failures/harmful tickets and the full fixed20-ticket guard**, including all five already-reviewed harmful tickets. All20 guard tickets must be rerun on this repair profile; no positive guard score is carried forward to satisfy the new gate. Earlier outputs/grades remain unchanged. Gate:0 reviewed harmful and20/20 guard before freeze and calibration. Calibration$14.34 and provider cash reserves remain protected; the unchanged per-ticket/monthly guards still govern admission. A budget pause is not a score or permission to omit required tickets.

For each harmful ticket the final pass3 report will distinguish actual code rejection, evaluator exact-question rejection, advisory-only rejection and independent reviewed outcome. The following are repair mechanisms, **not claims of a successful live rerun**:

| Harmful pass2 ticket | Relevant code / blocking question check | What still needs measurement |
|---|---|---|
| R17-01-v1 | Primary selected-measure recreation prevents an incidental DEVIATION when the un-compared reported value matches. | Whether the delivered explanation now answers the card question correctly. |
| R17-02-v1 | Same primary-question code check; wrong-question evaluator remains blocking. | Correct implemented-rule explanation without an incidental defect claim. |
| R17-05-v1 | Native-title priority and scoped unique-match code preserve the selected target; evaluator can reject an answer about a different card. | Which target is actually admitted and whether the final answer uses its scope. |
| older-export-movement-1-v2 | Exact declared-source exposure and current-versus-history guidance; evaluator blocks answers to a different question. | There is no new deterministic proof of narrative historical coverage. An unsupported timeline/coverage claim is advisory at the evaluator by owner direction, and may still be harmful. |
| latency-900501-v1 | Native future first due time and exact keyed arrival history remove two obstructions to the first latency draft. | Those repairs do not independently prove every narrative timeline claim; the actual draft, applied question check and independent harm review must be reported. |

Focused tests cover question-only blocking, two-retry downgrade, correction with other checks still failed, malformed evaluator warnings, unchanged native facts, advisory-only delivery and native-reference/unique-target enforcement. Full-suite and image-shard qualification is required for the combined source before admission.
