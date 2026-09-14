# Reviewed multi-layer ticket execution

The separate local server uses the report Lab Three-layer Net Cash and a distinct lineage ID.
It runs the same review/approval/child-ticket queue as the existing lab, but approved jobs
capture Bronze/Silver/Gold in one read transaction and persist multi-layer findings. Scope
is fixed to Net Cash, USD and all orders. It makes no cloud or LLM calls.

```powershell
python scripts/serve_multilayer_review.py --lab <existing-three-layer-lab.duckdb> --review-folder <new-review-folder>
```

Set INVESTIGATOR_API_TOKEN locally as for the other review server. The default loopback port
is 8774. After connecting, submit report Lab Three-layer Net Cash, generate the fixed draft,
review and approve it, then refresh the child ticket. One approved job runs per server session.
Matching three-layer results remain UNRESOLVED without a verified business explanation.

The server never initializes or injects defects. Use an existing fixture produced by the
multi-layer lab tooling; its default run resets to baseline. The review folder records its
mode and resolved source path. A different mode or source path requires a new folder; old
approvals are not silently reused. Distinct lineage/report IDs also separate two-layer plans.
The source's contents are observed at execution time, not frozen by draft approval.

Tests cover authenticated intake, planning, approval, bounded worker execution, persisted
three-layer evidence, affected boundary and reset for the propagated discrepancy. Additional
tests reject mode/path changes. Browser verification uses a separate matching baseline and
checks fixed-scope approval, completion and displayed evidence. The existing two-layer lab
remains supported. No live business data, provider credentials or delivery behavior changes.

Pending: broader transformation/model scenarios and proof, multi-layer evaluation expansion,
live freshness/snapshot contracts, hosted authentication/permissions and full acceptance.
