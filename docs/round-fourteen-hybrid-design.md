# Pipeline-first hybrid execution

DECIDED WITHOUT REVIEW, 2026-10-11: implement the owner's Part Two architecture as a controller around the existing pipeline, rather than making the model rediscover its stages. PIPELINE remains the default; pure AGENT remains a research mode. HYBRID first submits through the unchanged form/text intake and executes the normal walk and synthesis. A validated, answered result bypasses the model fallback. Named intake refusals, incomplete execution, capability gaps and unaddressed question parts supply the fallback's starting state.

The starting state retains the complete pipeline result, original observations and receipt IDs, plus the exact unresolved question or refusal. It is not a rewritten evidence projection. The fallback has twelve decisions, uses the same admission, claim, coverage and narrative validators, and carries diagnostics already spent; starting the fallback cannot reset the ticket's diagnostic allowance. A partial pipeline finding remains recorded even if the fallback cannot close its gap.

The high-level `run_standard_investigation` tool accepts only registered target and scope identifiers from trusted admission. Its execution uses the same deterministic walk and original support validation. Where that exact admitted target and scope were already walked, it returns the retained result instead of buying the same reads again. Low-level tools remain available for a named gap, not as a replacement for an already successful walk. No native query is model-authored.

Rejected alternative: a second standalone pure-agent investigation after every refusal. That discards what was established and can silently reset caps. Rejected alternative: treating every snapshot qualification as a reason to rerun. A limitation on a scoped answer is not automatically a missing answer; deterministic question coverage owns that distinction.

The owner approved a separate approval-verification cap of 40 on 2026-10-11 (previously 35; the retained attempt needed 36). Investigation diagnostics remain 12. Rebuilt witnesses will be published only after the newly recorded verifier's exact offline replay matches; the earlier budget-held run and replay failure remain evidence.

Status: design recorded; implementation and live hybrid acceptance pending. No adoption claimed. Draft #423 remains draft and delivery freezes remain invalid.
