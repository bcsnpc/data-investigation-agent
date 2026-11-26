# HealthNet test-set authoring

Owner-approved 2026-11-26 on draft PR #436. Engine was frozen before reads and
authoring at `9fb0190b11a5e2a83579de4ed5bdb58c5ac73300`; all 833 runtime files and
69 prompt-bearing files remain hash-identical. No HealthNet-specific engine,
prompt or rule change is permitted. A future engine change needs practice-fixture
evidence and a decision log.

There are **25 tickets**: **15 static**, **7 future fault controls**, and **3 business
judgment/unanswerable handoffs**; **13 forms / 12 free-text**. Inputs include disputed
numbers, definitions/dates/filters, missing records, transaction grain, security
questions, and vague requests. This owner-approved authoring session has seen the
answers: it is **not operator-blind or independently authored**. Reviewer approval
is pending; future results need independent grading and this disclosure.

Expected answers use **34 successful owner-side SQL SELECT reads** across both
source databases, raw lakehouse and warehouse; **7 live DAX queries**; and live
model/report/pipeline definitions. Source/raw/mart/model aggregates were reconciled
with signed arithmetic, claim/version predicates, date relationships, MPI mapping,
transaction IDs, bookmark filters and role definitions. No other user was
impersonated. An actual user's missing effective-role/scope evidence stays unresolved,
rather than treating an owner control as proof. Five failed SQL connection attempts
are retained locally: one source timeout on wake and four Python Fabric TDS failures;
the source retry and existing .NET owner reader subsequently succeeded. No firewall
or permission change was made.

Every expected record contains verdict, layer, cause, key numbers, evidence IDs,
full-credit requirements and useful-handoff requirements. Exact live evidence and
definitions are encrypted with the answers. Fault expectations are **conditional**:
their numeric deltas are arithmetic projections of verified live baselines, not
observed faults. No injection was applied. Their encrypted plans specify mutation,
native job/refresh evidence, fresh admission, safe restoration and business/definition
hash checks. Invalid or drifting fixtures must not be counted as engine failures.
Fault execution requires a separately authorized control window.

Encryption: AES-256-GCM, random 256-bit key held only in the approved Key Vault secret
`healthnet-answers-key`, pinned by version. Authenticated metadata binds the ticket
hash and frozen engine commit. Key readback and decryption roundtrip were verified;
no key value was printed or written to disk. This is a byte-integrity seal with
**OWNER_REVIEW_PENDING** status, not an owner-approved answer oracle yet.

Per "commit only the encrypted answers plus SHA-256 hashes of both files",
`tests/tickets/healthnet/tickets.json` is present locally but excluded from Git.
Only `expected-answers.enc.json` and `hashes.json` contain test-set artifacts in the
commit; freeze/verification documentation contains no answer bodies. The local
review packet is `D:\data_investigation_agent\.local\healthnet-review-packet.md`.
Do not provide that packet or the decrypted evidence to the investigator.

`config/estates/healthnet.json` already contains the two named source connections
from the preceding multi-database change. Offline validation still returns
`DRAFT_DISABLED`, no secret resolution and zero network calls. It deliberately
retains placeholders for approved DIA reader scopes/bindings and funding; no DIA
access was granted and it cannot execute. The answer key is not an estate runtime
secret reference. No DIA runs, AI calls, source changes, merge or tag were made.

SHA-256:

- `tests/tickets/healthnet/tickets.json`: `85e3fc4e0f94d3127279a5082d32fe818cbdaf151213e6042300bb0190b64c67`
- `tests/tickets/healthnet/expected-answers.enc.json`: `7254f2f7abe08f84d94593f27b6ce716d62e96d3df56526dd15802f091df1815`

See [freeze](healthnet-testset-freeze.md), [verification](healthnet-testset-verification.json) and [hash manifest](../tests/tickets/healthnet/hashes.json).
