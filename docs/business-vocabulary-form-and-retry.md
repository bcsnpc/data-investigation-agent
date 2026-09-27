# Business vocabulary form and one judge composition retry

2026-09-27. PR #271 merged after six passing checks at `6570db1`.

Business nouns are admitted by form and exact definition provenance, independent
of catalog names. Sales and Customers remain usable when those are the physical
table names too. Qualified names, underscores, bracketed identifiers, GUID/hash
suffixes, receipt identifiers and paths are rejected. Generic placeholders remain
rejected. Existing exact definition span, operation and hash checks still apply.

Only incomplete-prose validation triggers one additional definition judgment.
Both attempts have separate recordings, reservations and events. The first
response remains rejected; successful retry is explicitly marked retried. Two
failed compositions hold the run. An unavailable or budget/deadline-blocked
second attempt also holds; no third attempt or repeated data read occurs.
Other provider/shape/size failures do not trigger this retry. Received invalid
prose retains provider usage. Producer instructions and bounds are unchanged;
the retry receives identical evidence.

## Read allowance correction

The preceding batch began at 54 reads and ended at 62. It exceeded the standing
ceiling of 60 by two before restoring the policy to 60. Earlier explicit temporary
approval was 68; the batch stayed inside that temporary allowance. Both facts
remain recorded. The user's review says the run should have stopped at 60 and
rejects a standing increase. Append-only ledger annotations record the crossing
and instruction. No counters were reset or refunded. The later request is denied.

The current ceiling remains 60. No new live run has started. The prepared batch
is two known-domain repeats, at most four cloud reads each (one native, two Fabric
SQL and one endpoint-metadata read in preceding runs). Judge retry adds only a
metered model call. At usage62, eight additional reads would need a separately
approved one-off ceiling70, restored to60 after the batch, or a new UTC allowance.
Neither is assumed approved.

## Validation

Sixteen focused vocabulary/retry tests pass: Sales/Customers, separate events and
recordings, double failure, no retry for unrelated errors, per-attempt reservations,
and call/daily/deadline limits. All 1,253 local regression tests passed in 399.188 seconds. No directory or judge-payload
shaping was added. Live outputs and live retry reliability remain untested.

Offline fixture context check (not a live tape): directory entries 11 -> 11, SQL objects 11 -> 11, payload characters 2,408 -> 2,408 through output-schema construction. The coverage-preservation test passes.

2026-09-27 subsequent result: the user approved exactly eight additional reads, four per run. Both live repeats completed with validated synthesis and first-attempt judges. Usage62 ->70; ceiling restored60 immediately. A separately authorized one-call reader freshness audit returned403. See [full report and verbatim outputs](vocabulary-form-live-and-latency-audit.md). Earlier pending statements describe the pre-approval checkpoint.
