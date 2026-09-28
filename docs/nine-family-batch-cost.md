# Nine-family batch: cost and current completion limits

2026-09-28 UTC. Design/audit only; no batch executed or credits granted.

## Basis and scope

Estimate one attempt for each existing A-I ticket in
`.local/unknown-domain-v2/tickets/`, against the same approved catalog/environment
used for run 778bcd6f. This is the known e1b8e1 domain, not a fresh variant. No
fixture publication, new discovery scan, re-approval, permission or restoration
work is included. A different ticket set or context needs a new estimate.

Conditions remain four diagnostic operations per investigation, at most three
boundaries, the existing 12 investigation-model-call ceiling, the same model
profile, one intake call and at most one synthesis call. No presentation retry
is added. The existing definition-judge incomplete-prose retry is still a
separately charged attempt and fits inside the investigation-call ceiling.

Costs below count estate requests admitted by the existing governor, not provider
billing, authentication-token exchanges, SQL compute or every network packet.

## Conditional route estimates

These are code/path estimates, not measured results for all nine families. The
only current measured complete path is the G run: 4 diagnostics, 10 physical
requests, 3 total model calls (intake, judge, synthesis). Other rows assume intake
selects the named anchor and the vertical/NONE route, except H's explicit range.
ASK, a provider refusal, another scope or a horizontal selection changes cost.
An incomplete or refused ticket is not counted as a successful investigation.

| Family | Existing anchor/question | Diagnostics | Physical requests | Total model calls | Completion limitation |
| --- | --- | ---: | ---: | ---: | --- |
| A discrepancy | Handled Quantity | 4 | 10 | 3 | Same quantity/path as the measured G run; conditional on the same observed divergence. |
| B ratio | Inbound Fraction | 1 | 1 | 2 | Presentation-only path; current procedure does not decompose the ratio into its components. |
| C derived | Quantity Balance | 0 | 0 | 1 | Local resolver raises `Measure path exceeds bounded projection` at 12,000 characters before a read; no synthesis completion expected on that path. |
| D visual/filter | Handled Quantity, North | 1 | 1 | 2 | Filtered baseline is readable; lower-layer filter translation is refused as NOT_COMPARABLE, not approximated. |
| E freshness | Handled Quantity | 4 | 10 | 3 | Same conditional divergence path; this does not supply refresh timestamps or an SLA. |
| F transformation | Extended Value | 3 | 7 | 2 | Presentation + declared source, then ingestion metadata if equal. Derived value has no faithful deeper compiled path. |
| G source/application | Handled Quantity | 4 | 10 | 3 | Measured 778bcd6f path; application-source binding remains unresolved. |
| H expected behavior | Inbound/Outbound Quantity | 1-4 | 1-16 | 2-14 | NONE can yield one anchored baseline; HORIZONTAL routes to the older dynamic planner, with up to 12 investigation calls. |
| I unknown business meaning | Handled Quantity / Q49 | 4 | 10 | 3 | Conditional process route; may instead ASK at intake. A process explanation does not establish the unknown code's meaning. |
| **Total of these conditional estimates** | | **22-25** | **50-65** | **21-33** | **Not nine end-to-end successes.** |

A successful lower read on a new SQL database/object costs four physical
requests: identity, database permissions, object permissions, and quantity.
The first declared source is resolved from retained metadata. Each deeper
quantity additionally needs one endpoint metadata lookup. The OneLake ingestion
check costs one diagnostic operation but two HTTP GETs. Job history currently
uses retained discovery observations and adds no new estate request.

Thus G is DAX 1 + first SQL 4 + deeper endpoint lookup 1 + second SQL 4 = 10
physical requests for four diagnostics. F's equal presentation/source path is
DAX 1 + SQL 4 + OneLake 2 = 7 physical requests for three diagnostics. Reused SQL
guards could reduce cost; this estimate assumes no reuse. A direct-source
presentation divergence could terminate earlier. A changed equal deeper path
can hit the four-diagnostic cap before finishing; it must HOLD, not gain a cap.

Evidence: `MicrosoftProcessAdapter.resolve_path/evaluate/ingestion`,
`process_debugging.vertical`, `Workspace.preview`, the local retained catalog
resolver audit, and [the measured single run](narrative-form-live-result.md).
The resolver audit inspected definitions and paths only, not values; it made no
query/model call and generated no ticket outcomes.

## Proposed hard batch envelope ? not granted

Intake decisions are not known in advance, so the conditional total is not a safe
admission ceiling. Propose **144 expiring physical credits: 16 for each of nine
named sessions, one attempt per family, six-hour common batch expiry**. Four
SQL diagnostics with three guards apiece fit within 16 physical requests; the
current vertical route ordinarily uses fewer. This covers an admitted horizontal
route without assuming every family chooses the cheap path.

- Diagnostic ceiling remains **4 per run / 36 across nine runs**.
- Model ceiling remains **12 investigation attempts + 1 intake + 1 synthesis per
  family = 14 per family / 126 total**; typical vertical paths need 2-3. Every
  existing retry consumes an attempt; this proposal adds no retry allowance.
- Ordinary rolling allowance stays **60**. No global ceiling change, counter
  reset, refund, refill or transfer between sessions. Unused credits expire.
- No restoration capacity is needed because this batch authorizes no mutations.
- If intake asks, permission fails, a provider refuses or a cap is reached,
  preserve that result and stop that family. There is no replacement run.
- If execution discovers a need beyond a session's credits/cap, it stops. The
  proposal is an upper bound on authorized work, not a guarantee of completion.

Six hours covers the existing 30-minute per-run deadline across nine sequential
attempts plus intake/synthesis overhead. Exact session IDs and the UTC expiry
would be recorded before their first estate request after approval. No policy
or profile setting has been changed to stage this proposal.

**A guaranteed nine-family end-to-end completion cost cannot yet be quoted.**
B/C/D and application-source reachability have concrete structural limits. More
credits do not fix them. This batch would measure current behavior and preserve
partial/blocked outcomes, not establish unfamiliar-domain acceptance.
