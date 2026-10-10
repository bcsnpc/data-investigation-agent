# Round Twelve checkpoint — 2026-10-09

The ten retained mismatches were inspected under the owner's explicit diagnosis-only permission. The sealed oracle, split, goldens and historical tapes are unchanged. The complete field values, ticket text, nominations and gate attribution are in [the diagnosis](round-twelve-question-gate-diagnosis.json). No estate or model calls were made for this audit.

| Partition / ticket | Field | Oracle | Used | Finding |
|---|---|---|---|---|
| held / original A | comparison | APPLICATION | STALE | “current global value” overrode the nominated figure-difference kind |
| held / rebuilt A | comparison | APPLICATION | STALE | same rule |
| held / original F | comparison | LOOKS_WRONG | STALE | “current total” was read as freshness |
| held / rebuilt F | comparison | LOOKS_WRONG | STALE | same rule |
| held / original F terse | comparison | LOOKS_WRONG | APPLICATION | “source mechanism” was read as a comparator |
| held / original F typo | comparison | LOOKS_WRONG | APPLICATION | same rule |
| held / original F noisy | comparison | LOOKS_WRONG | APPLICATION | same rule |
| held / original A mention | reported figure | NOT_STATED | NUMBER | ticket explicitly says the quantity currently shows a number |
| held / original G mention | reported figure | NOT_STATED | NUMBER | same sealed-oracle/text conflict |
| dev / original E mention | reported figure | NOT_STATED | NUMBER | same sealed-oracle/text conflict |

For the seven routing defects, `from_request(code_gate=True)` supplied a new kind from keywords and the gate recorded `COMPARISON_ESTABLISHED_FROM_REQUEST`, dropping the comparison question. For the three figure disagreements, `VALIDATED_REFERENT_AND_SCOPE` accepted a verbatim displayed figure. The evidence does **not** establish an omitted corrective question: removing that figure would contradict the ticket. These three are findings, not permission to modify the oracle or to suppress a stated value.

The correction requires agreement between a nominated route and an unambiguous textual cue. “Current total” does not establish freshness. A bare “source mechanism” does not establish an application comparator. Conflicting cues and absent cues leave the comparison question open. Configured defaults remain policy evidence for legacy contracts; they cannot suppress a question in smart intake. Adoption revalidates using the same corrected gate, so an earlier ungated path cannot bypass it.

## DECIDED WITHOUT REVIEW

Keep all three clearly reported figures. Rejected alternative: erase a displayed number or introduce a special-case question solely to match NOT_STATED in the sealed oracle. That would manufacture score improvement rather than preserve user intent. A zero-mismatch score may remain unattainable for these records under the fixed oracle; the fresh result must report that honestly.

No billing rebuild: its existing published report and audit remain preserved. Form implementation/scoring, live lists, subsequent domain work and the one-command form demo are pending. Current engine freeze is invalidated by the gate correction; #423 remains draft. No new permission, identity, secret, fixture or allowance change.

## Live-list access research

Power BI's [report-page listing](https://learn.microsoft.com/en-us/rest/api/power-bi/reports/get-pages-in-group) accepts Report.Read.All. Fabric's [report-definition endpoint](https://learn.microsoft.com/en-us/rest/api/fabric/report/items/get-report-definition?tabs=HTTP) explicitly requires read and write permission on the report. Therefore live report/page lists and live visual-title extraction have different permission requirements. The reader's actual listing access still needs a metered probe. No extra grant will be taken: if live definition retrieval is refused, visual-title selection remains unavailable and the form uses the permitted optional-target path. Retained definitions must not be passed off as a live list.

Later governance requirement: authenticated Entra users' lists must be filtered using their own access, not merely the configured diagnostic reader's scope; report names are sensitive. Cache entries must be scoped to estate and identity, have a configurable five-minute default TTL and allow manual refresh. A newly listed report without approved discovery context may be selected but must hold rather than borrowing another report's metadata.

## Single held-out re-score — 2026-10-10 UTC

The code was frozen at `580726b`, engine hash `b118329c4359a5aeda1fb00d2dc054cde0cdf0930af6d1e4fbc2e6929f81fa4e`. All 28 records were freshly scored once, after the UTC model allowance reset. There was no model allowance increase and no post-score tuning. Exact before/after metrics and the complete column are in [the retained result](round-twelve-held-results.json).

| Held-out metric | Before | After |
|---|---:|---:|
| One-round settlement | 16/28 | 17/28 |
| Consequential-field mismatches | 9 | 2 |
| Questions | 5 | 12 |
| Questions per ticket | 0.179 | 0.429 |
| Illegitimate questions under sealed oracle | 3 | 10 |

| Class | Settled | Questions | Illegitimate questions | Mismatches |
|---|---:|---:|---:|---:|
| family | 11/22 | 10 | 10 | 2 |
| question | 1/1 | 0 | 0 | 0 |
| refusal | 3/3 | 2 | 0 | 0 |
| visual | 2/2 | 0 | 0 | 0 |

All seven route mismatches disappeared. Six comparison questions now remain open where the nomination and text disagree; the oracle has no legitimate question/authorised answer there, so its simulator abstains. Four NUMBER questions also remain scored illegitimate. This is a safety-versus-question-cost result, not a zero-error pass or a claim that those questions are ideal. The new pass still exposes free-text target-resolution misses. No further held-out-based tuning was performed.

The two remaining scored harmful admissions are `original:family-A-mention` and `original:family-G-mention`, both `reported_figure`. Each ticket explicitly states that the global quantity currently shows a number; its fixed oracle says NOT_STATED. Both figures remain in the intake record. The dev E-mention conflict was diagnosed but dev was not freshly rescored. **The required zero-mismatch gate FAILED.** Neither the score nor the oracle was altered to remove these flags.

Recorded cost: 32 provider calls, 400,030 input characters, zero estate requests for the evaluation. Every case, including holds, has its own original tape and appended ledger row; all 28 tape hashes were checked. Intake-only settlement is not an end-to-end investigation or an evaluated business outcome.

## Actual live-list controls

The existing `investigator-reader@skynwhy.com` served the scoped workspace's report list with HTTP 200. The initial broad name check found several Inventory reports and stopped rather than choosing one; that control receipt remains preserved. A continuation selected the exact returned `Inventory Health e1b8e1` identity, without repeating the listing, and served its pages with HTTP 200: page `688de76fce97549d9756`, display name `Inventory Health`.

For report `692f3ead-d1d1-4f7f-984b-51e54f3e7497`, reader POST `getDefinition` returned HTTP 404, `EntityNotFound`, message **“The requested resource could not be found”**, request ID `43a6d2c3-0dbf-45f3-8642-51b4b1fae655`, `isRetriable: false`. That establishes no served visual definition, not proof of a particular permission denial. No publisher/code-reader fallback was used and no scope changed.

Receipts are `.local/round-twelve-list-probes.json` and `.local/round-twelve-list-probes-continuation.json`, with identity/audience, exact requests/responses, seals and budget snapshots. Combined actual usage: three physical requests, zero diagnostic reads, zero model calls. Pot before 1,114, after 1,117 of 1,500; restoration reserve remains 95, leaving 288 ordinary requests. Rolling allowance remains 3,000. Metadata-list controls are separate from investigation diagnostic counts.
