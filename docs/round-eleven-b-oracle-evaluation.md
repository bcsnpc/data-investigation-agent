# Round Eleven B: fixed conversational oracle

Owner Chiranjeevi Bhogireddy and independent reviewer Claude approval was
confirmed by the human on 2026-10-09. The accepted diff is now sealed. Its exact
reviewed file remains unchanged, including the historical draft labels; approval
is the separate `acceptance/oracle/oracle-seal.json` record.

Approved oracle SHA-256:
`be029b56a6de27195dac507bfb5010f0ce7abc2732702d9a230e5f4a8d38406c`.
The original 40-development / 28-held-out split and all golden records are
unchanged. No further oracle amendments are permitted in this phase.

The evaluator uses only approved answers, refuses unapproved or non-unique
choices, checks adopted target, cell keys, scope, figure, precision and route,
and counts illegitimate questions separately. Adoption does not prove correctness.
Keyed scope is compared through the consumer's validated singleton filters.
Visual equivalence requires the reviewed complete-definition proof, not merely
a shared measure. Transport and budget holds receive no semantic refusal credit.

Historical responses from frozen 44490b4 are rescored separately in
`round-eleven-oracle-historical-baseline.json`. This is a historical baseline,
not a fresh run of the corrected engine, and its consequential differences are
audit flags rather than silently declared causal harmful errors. Original tapes
and prior scores remain intact. Development work uses development cases only;
held-out is reserved for the final frozen pass.

Eleven oracle approval/scorer tests pass. Zero model calls and estate reads at
this checkpoint. Initial test invocation used the wrong import root and failed;
the corrected native invocation from `scripts` passed. The quality gate is not
cleared; #423 remains draft. Engine changes invalidate the earlier freeze.

DECIDED WITHOUT REVIEW: retain exact approved artifact bytes and attach approval
in a hash-checking sidecar rather than rewriting historical draft metadata. This
keeps the reviewed hash and every substantive record immutable.
