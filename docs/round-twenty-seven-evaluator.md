# Round 27 delivery evaluator

Owner amendment2026-11-20 implemented before scored admission. A separate Opus call checks exact question, native support for verdict/cause, explicit/uniquely matched target, and unsupported claims. Only ticket, structured draft and recursively cited native evidence are sent. Investigation messages/model-response records and uncited catalog are excluded. Tool results are validated as four booleans with specific reasons; malformed responses reject.

Rejected drafts return specific reasons to the loop. Three rejections (initial plus two retries) stop delivery of that draft and produce a structured UNRESOLVED handoff retaining checked facts. Native operational facts also get isolated evaluation before delivery; a rejection preserves the native facts but withholds the rejected confident answer. A safety/budget stop cannot authorize an unchecked confident finding. Evaluator unavailability is recorded rather than silently called approval.

Each call has EVALUATOR purpose in the shared cost ledger; normalized usage records and case trace retain model, usage, cost, verdict, reasons, attempt and retry. Same Opus selection, same case actual3USD ceiling and existing monthly envelope; no grading purpose enabled on Anthropic. Independent Nova/Sol scoring remains separate. The gateway explicitly allows these local/read-only tools and still refuses write tools.

Focused tests cover four checks, exact-question versus incidental Silver/Gold difference, explicit-target override language, no reasoning leakage, recursive native citations, malformed output, return-to-loop, and downgrade after two retries. These are offline synthetic tests, not evidence of live quality. Full qualification remains required for the amended image.
