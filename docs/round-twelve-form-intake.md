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
