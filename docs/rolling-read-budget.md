# Rolling read allowance and expiring batch credits

Date: 2026-09-27. Previous snapshot-attestation PR #278 merged as
`02da5fdce7eb87f3d23f484be0ff53030c61ca70` after all six checks passed.

## What the allowance protects

The ordinary allowance bounds initiated data/metadata read requests in one
catalog/environment over a rolling 24 hours. It is an operational request-rate
and blast-radius control, not a monetary cap, SQL scan-cost cap, or tenant-wide
network meter. LLM reservations retain their existing UTC-day rules. Identity
and permission SQL commands count as reads; OAuth and connection handshakes do
not. Separate discovery jobs retain their own scan budgets. Standalone operator
probes must use `UsageGovernor.metered_read`; invoking a raw adapter bypasses
investigation admission and is not evidence that this allowance was enforced.

The existing `daily_limits.cloud_calls` key is retained for config compatibility,
but now specifies the **ordinary rolling-24-hour allowance**, normally 60.
`read_allowance` in the control-plane snapshot exposes the window, charged slots,
available slots and separate batch balances. `reserved_today` is retained as a
historical UTC-day diagnostic, not the read admission predicate. No config or
live policy was changed for this implementation.

Admission holds an SQLite `BEGIN IMMEDIATE` transaction: the next reservation
must fit before the transport is released. At exhaustion it refuses the next
request; it never sends it and then charges an overrun. Each reservation ages out
of ordinary eligibility after 86,400 seconds, but its record remains. A backwards
clock movement conservatively retains reservations. Failed, interrupted and
uncertain work remains charged; nothing is reset or refunded. A first slot is
reserved before transport preparation, so an authentication/setup failure can
consume a slot without a remote read. These are conservative request reservations,
not a fabricated assertion that every reserved request reached the server.

## Batch and restoration rules

A separately recorded human approval assigns a finite number of credits to
specific run IDs, with an absolute expiry and approval reference. It never edits
the ordinary ceiling. Each run has its own earmarked allowance; it cannot borrow
from another run. A batch-assigned run spends only its assigned credits and never
falls back to ordinary allowance after exhaustion or expiry. Unrelated runs cannot
spend the batch. Consumed and expired credits remain in the record.

Investigation per-run envelope limits still apply, even with batch credits.
Restoration gets separate `RESTORATION` run IDs and earmarked credits at approval
time. Investigation admission cannot spend those credits. The operator-only
`restoration_read` wrapper uses them for baseline/restoration verification, even
when ordinary or investigation credits are exhausted. It refuses replay of a used
reservation key. This wrapper authorizes reads only, never a mutation. Credits
must be assigned before the run has any usage; there is no mid-run top-up.

Before a future reversible mutation, its approval must allocate enough
restoration credits and expiry time. Earmarking capacity cannot promise remote
availability or override expiry. No mutation, batch grant, renewal, policy
increase, counter reset or freshness-fixture retry was performed here.

Operator interface (local paths are examples):

```powershell
python scripts/read_budget.py --database <catalog.sqlite> --policy <usage-policy.json>
python scripts/read_budget.py --database <catalog.sqlite> --policy <usage-policy.json> --approval <approved-batch.json>
```

Inspection initializes additive budget tables if absent. The approval file is a
record of an explicit human decision, not a way for a planner to grant itself
credits. The command is not registered as an investigation tool.

Approval shape:

```json
{
  "environment": "configured-estate",
  "batch_id": "human-approved-batch-reference",
  "approved_by": "operator",
  "approval_reference": "recorded-human-approval",
  "expires_at": 1800000000,
  "runs": [
    {"session_id": "precreated-investigation-id", "purpose": "INVESTIGATION", "reads": 12},
    {"session_id": "reserved-restoration-id", "purpose": "RESTORATION", "reads": 4}
  ]
}
```

Those numbers are illustrative, not granted capacity. Approvals are immutable;
duplicate IDs, changed definitions, expired grants and already-started runs are
rejected. Total batch authorization is the sum of its per-run allocations.

## Physical requests and receipts

Previously a OneLake commit lookup charged one logical operation while issuing
two GETs. It now gates the listing and commit GET separately. If the listing
fails, there is no second request. If the second slot is unavailable, the child
waits for permission and is terminated without sending it.

The same audit found multiple SQL commands hidden inside each compiled probe:
Fabric SQL self-report, database permission check, one object-permission command
per referenced object, then the quantity command. Each now needs admission via a
bounded parent/child request protocol. All permission checks remain intact. Azure
SQL proposed-query checks use the same protocol. Native DAX and optional snapshot/
refresh calls issue one request each. Endpoint discovery uses the single-request
metadata worker rather than a CLI whose internal retries are outside this meter;
redirects are refused. Azure SQL connection-only auto-resume retries remain, but
never replay a submitted query.

Receipts are saved independently of later interpretation and validation, including
successful internal reads preceding a refused quantity. The scorer includes
physical SQL metadata commands in SQL read counts. Older receipts and ledger rows
are unchanged: their historical logical counts cannot retrospectively certify
physical request totals. Offline replay rewinds allocation links together with
usage **only in its disposable copy**, preserving the original catalog.

Existing per-run limits have not been raised. A one-object Fabric SQL probe now
needs four slots, not one. Future live batches must budget the actual request
sequence plus restoration before starting; old four-logical-read run totals are
not a sufficient physical-read estimate.

## Validation and limits

Sixteen focused tests cover midnight versus rolling expiry, the exact 24-hour
boundary, retained legacy records, atomic competing reservations, separate and
expiring grants, purpose isolation, protected restoration, no mid-run credits,
uncertain charges, no replay, pipe-protocol refusal before send, receipt survival,
per-run ceilings, SQL command gating and unchanged planner directory coverage.
All five offline session-replay tests pass after allocation reconstruction was
added. A 1,302-test full regression passed before the final receipt-retention and
cleanup adjustment; all sixteen focused tests pass after it. The final full suite
is in progress. Physical receipts retain the original logical receipt reference
or bounded metadata body, rather than replacing it with request counters.

The initial 1,298-test run failed (10 failures, 2 errors). It exposed a captured
subprocess runner bypassing mocks and stale allocation links in replay copies;
some other failures occurred while engine files changed and correctly tripped
fingerprint fencing. Its original log is retained under
`.local/rolling-read-budget/regression-initial.log`. Early focused-test failures
included an order-dependent test assertion and an incorrect test-harness catalog
call; neither is claimed as a passing result.

A fixture context comparison retained 2 directory entries, 1 SQL object and 7,540
payload characters, before and after; the regression asserts byte equality of
the complete planner payload. Budget reports are control-plane/recording data,
not extra directory content. No domain-specific code or query route was added.

No live cloud request, browser run, new identity, fixture mutation or unfamiliar-
domain acceptance attempt was made. Engine changes invalidate previous freezes.
The Microsoft snapshot limit is explicit in CLAUDE.md: the current adapter cannot
bind served versions to its value queries; other platforms may satisfy the
query-bound snapshot contract. SQL's empty metadata result is not relabelled as
an observed administrator-permission refusal.
