# HealthNet test-set authoring (revision 1, superseded below)

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

## Revision 2 - reviewer feedback, 2026-11-26

The active set now contains **27 tickets**: 15 static (including **3 defined-only
static DEVIATION controls**), seven defined-only operational faults, three
business/unanswerable cases, and **two screenshot cases**. Input formats are
13 forms, 12 free-text and two screenshots. **Seven of the 12 free-text tickets**
use informal names, rounded numbers or missing details. Cause hints were removed
as requested. The revised hash manifest supersedes revision 1; its encrypted
answers remain available in Git history and its plaintext inputs/review are
retained locally as superseded evidence.

Nineteen original expected records are unchanged. The authorized changes are
three replacement static questions and three operational verdict classifications.
R27 canonical operational classes and independent verdict/layer/cause grading are
mapped explicitly in the local review packet and encrypted answers. Physical
layer boundaries remain truthful to HealthNet rather than copying the fixture's
layer names. Existing technical causes for the operational cases are unchanged.

The three proposed static defects were projected with one additional read-only
SQL query and two additional DAX queries; **no definition or data was changed**.
Each encrypted plan specifies exact target/predicate, baseline evidence, independent
fresh admission and restoration/hash checks. They are future controlled cases,
not claims of existing defects. Authoring totals are 35 successful SQL SELECT
reads and nine DAX queries, plus native definitions and export metadata.

Screenshot cases use **real Power BI service-rendered baseline report pages**.
PNG export returned tenant-disabled403; no setting was changed. Native PDF exports
succeeded and were rasterized without editing in an isolated local PDF dependency
folder; both images were visually inspected and their visible values match the
measured baselines. The user mentions the number instead of a fabricated circle.
Images, plaintext tickets, source PDFs and reviewer packet remain local; only
encrypted answers and hashes are committed as test-set artifacts. Image hashes
are included in hashes.json and embedded in their ticket attachment references.

All833 engine/runtime and69 prompt-bearing files remain unchanged. No DIA run,
AI call, permission/tenant-setting change, injection, merge or tag was performed.
Config remains disabled; reviewer approval is pending. The existing Key Vault key
version was reused in memory with a fresh AES-GCM nonce and authenticated revision
and ticket hash; independent decrypt-and-compare verification passed.

Active SHA-256:

- `tests/tickets/healthnet/tickets.json`: `963338bf68093d451b118d516c4b05b748b8ec08e3714e57b59d9a85c9a506bc`
- `tests/tickets/healthnet/expected-answers.enc.json`: `fd850945e439d15f821905be2456fa72bc330ba7ce3267cbafe5233d572f0407`
