# Round Eighteen — checkpoint, not closed

Recorded 2026-10-13 UTC, through the 04:05 control ledger checkpoint and the later
offline setup audit. Draft **#424** targets draft **#423**; neither is merged.
The previous freeze is invalid. Cloud verification/demo work continues; this is
not a claim that the round's targets have all been earned.

## Platform and safety

Created platform resources include `pg-dia-d5dd7d65` (PostgreSQL B1ms, 32 GB,
no HA, database `investigator`), `diaplatformd5dd7d65` (Standard LRS private Blob),
`kv-dia-d5dd7d65` (Standard Key Vault), `id-dia-worker` and the consumption
Container Apps environment/job `job-dia-worker`. PostgreSQL/compute use South
Central US after the approved regional fallback; storage/vault/identity remain
East US. No always-running API, paid registry or Log Analytics workspace was
provisioned. The conditional operating estimate remains **$13.74/month**,
including the confirmed free PostgreSQL entitlement and bounded compute/storage
assumptions; it is not an invoice or a hard Azure spending stop. Without that
free entitlement, South Central US PostgreSQL alone is estimated $19.308/month.
See [the estimate](cloud-cost-estimate.md).

Worker MI health passed PostgreSQL, immutable Blob PUT/GET and vault metadata.
The existing read-only user authenticated separately for Power BI and SQL through
its approved versioned cache references. No extra estate role follows from
moving credentials. Application-source workstation authentication remains
unavailable in the cloud. Code-reader Contributor credentials never serve
quantities. Cross-tenant MI federation remains a future proposal.

Part A's integrated gateway/literal/MI/Linux gate passed **43 tests / 47
subtests**. The literal audit covers **358 installed files**, removed one
fixture-specific prompt example, and keeps historical fixture builders outside
the product boundary. The frozen `4377cbf` full suite passed **3,983 tests**,
46 skipped and 1,407 subtests in 796.43 seconds. Later changes have separate
focused results; this old full run does not certify every later commit.
The gateway is an application boundary, not an OS firewall.

## State, recordings and disk

Shared PostgreSQL is authoritative for cloud tickets/case sections, published
catalog/readiness and budgets. Migration preserved **10,022 usage rows**, all
statuses including one historical reserved row, monetary totals and request
keys. The document import retained **1,043 tickets, 291 contexts and nine
models**. Graph tables were queried: **zero nodes / zero edges**. Private SQLite
remains for per-job replay and offline execution; projected PostgreSQL live
persistence refuses rather than leaking raw state.

The pilot and eight selected tapes were slimmed. The eight tapes' 1,958,359,736
original bytes added 23,394,768 bytes to the shared content-addressed store,
which reached **48,595,256 bytes**. All 32 reconstructed files matched exactly;
all eight local pinned-engine replays matched. Broader history conversion is
unfinished. The verified archive pilot covered 45 files; a later 32-file batch
initially failed with connection reset, then verified and completed cleanup.
Original failures remain. The later cleanup removed 1,958,359,736 logical bytes;
D: free afterward was **14,078,382,080 bytes**. The 10 GB floor stays enforced.
The initial 45-file cleanup freed 96,485,376 allocated bytes. Logical and
allocated space must not be combined into a fabricated saving.

A dated correction records that the initial SDK per-call hook was ignored;
its inferred request count was not measured. The replacement transport recorded
460 dispatches/responses for CAS publication and 192 for the retried archive,
with zero errors in those completed batches. See
[the control ledger](round-eighteen-control-ledger.md) for retained failures,
checksums and exact scope changes.

## Cloud and guide evidence

The first eight-way cloud historical replay was **7/8**; later failing-shard
diagnostics retained Windows-path portability mismatches. Corrected Linux
verification remains due at this checkpoint. The comparable eight-worker laptop
baseline is **198.253 seconds**. No valid cloud speedup is claimed from a cohort
with a failed member.

The new cloud workflow prepares an image-local context candidate, requires its
reviewed hash before single-model publication, then checks 18 bindings and one
native boundary within the unchanged **40-probe verification cap**. It replays
and derives six-stage readiness before admitting one form. Its audited input
package is 47,305,616 compressed bytes / 461,153,892 expanded bytes. Preparation,
verification, readiness and a successful live demo are distinct; the actual
demo finding is **not yet earned** here.

Retained-control preflight: fixture **8 PASS / 0 FAIL / 24 MISSING**; billing
**8 PASS / 0 FAIL / 13 MISSING**. The first billing candidate's schema failure
is preserved. An independent billing guide recheck reproduced the corrected
counts with zero new requests. These are **NOT_READY**, and billing's example
covers its declared semantic model, not a full end-to-end billing onboarding.
The guide now fixes configuration paths, regions, credential-reference
consistency, and hash-bound control imports. Clean-client deployment through
teardown is not claimed tested. See [Part D](round-eighteen-part-d.md).

Sampled inventory schemas contain metadata/observations; sampled diagnostics
retain bounded value rows, up to 249. A universal audit of every historical tape
for bulk data remains incomplete. The storage document explicitly names that
limit rather than asserting all recordings are metadata-only.

## Budget and remaining work

At the ledger checkpoint, new estate/model admissions were **zero**. Shared model
opening spend is **$107.957725**; new-round allowance is **$10**, admission ceiling
**$127.957725** with protected **$10** margin (spend stop $117.957725). Pot remains
**2,839/4,000**, restoration **95 remaining**, investigation diagnostic cap **12**.
Rolling opening usage was 198/3,000; the final rolling value must come from the
closing ledger, not an assumed unchanged time window.

Remaining: corrected Linux replay result; reviewed cloud candidate and fresh
route proofs; one actual cloud demo/capture/replay; final spend/timing/disk
measurements; broader conversion/content-audit backlog. No new owner approval is
requested by the guide checkpoint. Existing deferred authority boundaries remain
listed in [owner-actions.md](owner-actions.md).
