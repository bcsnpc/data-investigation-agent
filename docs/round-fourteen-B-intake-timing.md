# B-r1: wall-limit diagnosis

2026-10-11. B's transcript ended HELD/AGENT_WALL_LIMIT after 986.626 seconds, against the unchanged 900-second loop limit. It made 18 model calls, zero physical requests and never waited for a user. The limit is checked between operations, so a running operation can finish after the deadline; this is not a raised limit.

Governor reservation to decoded-decision persistence totals 289.950 seconds (5.528â€“36.617 seconds per call). This includes provider response and local decoding/persistence; it is not a pure network measurement. The remaining 696.676 seconds include catalog admission, tool execution, journal/capture work and setup/closure. The transcript cannot isolate these further retroactively.

Six decisions called resolve_ticket, eleven called get_evidence, one listed visuals; five identical evidence calls returned already-obtained feedback rather than executing again. The initial extraction had a non-verbatim quote. The next attempts repeatedly used the background complaint â€œInbound Fraction looks highâ€ as the primary quote, omitting the actual request to check the global value and explain the numerator and denominator. The consumer correctly refused because that quoted span established neither the selected comparison nor the declared subject. This was repeated unsuccessful extraction, not a wait for credentials or user input.

An offline profile of one unchanged native catalog snapshot took 10.899 seconds. It fetched full model records redundantly and loaded the same current context once per model. The repair removes these duplicate retrievals while keeping fresh metadata reads, integrity checking and context-change refusal. The agent tool also receives the existing pipeline primary-question instructions from one shared constant. The pipeline instruction bytes remain identical. We reject weakening the subject validator or raising the time cap. These repairs have focused regression tests; no claim is made that guidance guarantees model compliance.

DECIDED WITHOUT REVIEW: share the consumer's existing primary-span instructions rather than invent a new intake rule. Remove duplicate retrievals rather than cache mutable metadata across steps. Both preserve the evidence and refusal contract. The 900-second wall and 25-step limits remain unchanged.

