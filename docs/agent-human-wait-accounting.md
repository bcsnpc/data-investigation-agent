# Agent clarification active-time accounting

Dated decision, 2026-10-11 America/Chicago. DECIDED WITHOUT REVIEW: a retained WAITING_FOR_USER interval is human-response time, not active agent computation. Keeping the original 900-second clock running while the user reads and replies was rejected: a normal reply hours later could never continue, despite an unused active-work budget. The 900-second active-work allowance, cumulative step cap, model/read limits and original start timestamp remain unchanged.

The public agent-resume endpoint now admits AGENT and HYBRID, whose controller already supports the sealed pipeline predecessor. PIPELINE still uses the normal structured reply route. A real terminal HELD remains terminal. Revision, actual USER comment after the question, and one-time reply consumption remain mandatory.

Each pause begins at the original timestamped TOOL_RESULT that returned WAITING_FOR_USER and ends at the retained USER comment timestamp. The question's own timestamp, exact question/reply IDs, original waiting receipt ID and excluded seconds are recorded in the ticket and a HUMAN_WAIT_EXCLUDED journal event. On every continuation, the engine recomputes all intervals from original comments and hash-validated journal evidence. Missing, changed, reversed, future, overlapping or duplicate evidence refuses; saved duration fields never certify themselves.

The provider deadline extends by only those verified human-wait seconds. No decision is removed from the journal, no diagnostic or model count is reset, and no new step batch is created. Time after the user's reply again consumes the active allowance. A real step-cap or active-wall stop remains an honest hold.

The existing selected clarification packet contains 58 hash-checked questions: 33 HYBRID WAITING_FOR_USER questions and 25 PIPELINE structured CLARIFYING questions. This change does not rewrite their original artifacts. Missing current-context authority remains a block; the resume route adds no approval or context override.
