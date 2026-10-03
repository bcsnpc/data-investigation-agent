# Selection value and nonbinding descriptor

Date: 2026-10-02. Follows merged refusal delivery #312 (`2578165`).

The current producer wire requires a descriptor variant alongside the value
quote: SEPARATED carries its own verbatim quote; VALUE_ONLY and UNSEPARATED
carry no descriptor quote. State and source cannot vary independently.
Consumer-computed spans preserve both provenances; claimed separation with
overlapping spans is refused. An UNSEPARATED phrase is tried whole, with an
explicit qualification, rather than trimmed heuristically. Historical consumer
requests remain readable without inventing a descriptor retrospectively.

The procedure still resolves only from exact ACTIVE declarations or complete
receipt-backed existence lookup over report-scoped grouping columns. The lookup
receives value_source only. Descriptor notes are computed AFTER binding, from
exact word tokens in the chosen column's display name; TEXT_AGREEMENT and
TEXT_DISAGREEMENT are lexical observations, not semantic mapping evidence. A
missing name leaves the hint NOT_EVALUATED. No descriptor chooses a candidate,
changes a restriction, enlarges scope, or bypasses a refusal. The request and
nonbinding note stay in the original resolution receipt and its validated
digest; they are visible in technical narrative and structured evidence.

Tests cover warehouse North as two quotes, a bare value, explicit inability to
separate, hostile overlap, invalid state/source pairs, a disagreeing hint with
unchanged query and resolution, post-resolution agreement and no-grouping
refusal despite a descriptor matching the column name. Immutable intake-family
fixtures remain untouched; their test-time wire expectation is migrated to the
new contract. No investigation run or ledger row in this implementation PR.

## Context cost and coverage

The measurements reconstruct the prior R1 intake request from its preserved
recording; no provider call or estate read. The catalog payload is byte-identical.

| Measurement | Before | After |
| --- | ---: | ---: |
| Catalog payload characters | 27,134 | 27,134 |
| Wire schema characters | 3,763 | 4,419 |
| Actual request instructions characters | 4,583 | 5,123 |
| Serialized request bytes | 40,719 | 41,916 |
| Models | 5 | 5 |
| Catalog columns | 91 | 91 |
| Reports | 9 | 9 |
| Planner directory entries | 28 | 28 |
| Planner SQL objects | 11 | 11 |

The schema/instruction increase is bounded protocol cost, not catalog pruning.
The planner directory and SQL-object figures are the unchanged 28/11 golden
view; the planner payload code is unchanged. Tests assert catalog/report/column
coverage does not fall. Synthesis additionally retains one bounded selection
request and hint per resolved selection, rather than labels on every directory
entry; refusal delivery makes no model call. Recorded pre-change tapes cannot
be used as byte-exact replays of the new producer request.

## Prior read-count finding

R1 had a scoped grouping column, so it attempted one existence lookup of the
whole phrase. R2/R3 had no grouping columns and no ACTIVE predicate with that
whole literal, so they refused before dispatch. This was not memoization. The
separate compiled-quantity cache is run-local and was never reached; a new adapter
starts an empty cache, and changed context/policy is independently fenced by
admission. Existing runs and counts remain exactly as recorded.

README/status updated. No fixture, permission, config, cap or policy change.
Engine bytes changed; all earlier freezes remain invalidated. Full regression
and final-head six-check CI are recorded on the PR. Three unchanged tickets are
rerun only after this merges; reproduction and EMPTY handling are still not
claimed as live-verified.

## Dated producer integration finding

A new positive value-existence -> resolution -> synthesis integration test failed
with `KeyError: request_hash` before any live rerun. The adapter's existence
receipt omitted the compiled-request hash although the query runner returned it;
synthesis was right to require it. The producer now carries that exact hash,
with no default. The registry's common query contract requires original hash and
result fields for EVERY registered query shape and names a missing field before
rendering. The same real adapter test now reaches sealed-receipt synthesis;
hostile missing-field tests enumerate every query shape. The failing test log
remains local. This is part of making the newly separated value's positive
lookup usable, not a relaxation of existence or attestation checks.

Fourteen new descriptor/integration tests pass. Earlier full suites passed
1,576 and 1,578 tests before the final producer integration correction; final
full-suite and exact-head CI results are recorded on the PR. No live runs here.
