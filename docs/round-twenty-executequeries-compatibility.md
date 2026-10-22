# ExecuteQueries self-report compatibility (2026-10-21)

Microsoft documents that the REST ExecuteQueries API does not support INFO
functions or DMV queries. New semantic quantity requests now append only
`USERPRINCIPALNAME()` as `surface_identity`; they never append `INFO.PROPERTIES`
for engine or model catalog. The adapter declares identity as its only reportable
field. Engine, connection and object remain explicitly unattested, so the
attestation is PARTIAL. No route, identity, permission or endpoint was added.

Source: [Execute Queries In Group limitations](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/execute-queries-in-group).

This fixes an independently established request-compatibility defect. It does
**not** explain the retained HTTP401: the separate data-only probe also failed
with HTTP401, so the root cause of that authorization failure remains unproved.

The exact old `SCALARS` grammar remains recognized for historical sealed
requests. It is no longer emitted by the REST composer. A regression compiles
the historical request while still rejecting arbitrary INFO calls, altered
property names and altered metadata columns.

Full verification and page-consistency contracts are unchanged. Page observation
requires query-bound identity, engine and object; identity-only REST receipts
therefore cannot establish a checked page visual. A compiler-to-receipt-to-page
regression checks this explicit UNAVAILABLE/NOT_COMPARABLE result. The generic
page-consumer positive tests use an explicitly synthetic full-self-report
transport with the historical grammar; they do not claim that REST supplies it.

The eight affected page-consumer cases were: differing declared filters;
differing values; numeric-looking string versus number; incomplete multimetric
visual; confirmed claim with typed filters; real catalog/compiler/sealed receipt;
scalar summary; and borrowing a receipt from another visual. Their consumer
assertions remain tested under the synthetic full-report fixture. The actual
REST route remains unavailable for these full page comparisons until an
appropriate query-bound evidence surface exists. No golden records, acceptance
expectations or tapes were changed.

Ordinary quantity and declared-context reads retain query-bound principal
identity and report their partial coverage. Semantic read reuse checks the same
declared reportable fields; SQL probes still require their existing fields.
