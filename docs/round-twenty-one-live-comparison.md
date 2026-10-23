# Live comparison

The retained pipeline form and new investigator ticket have byte-identical description text:

> In Inventory Health e1b8e1, Handled Quantity appears higher than the source stock movements total. Investigate the current global value and explain any observed difference.

The pipeline form selects the original Global card; the new ticket binds that same visual through the exact approved retained context. Both carry the application/source comparison. Neither changes that request into a claim that the application was read.

| Measure | Established pipeline A03 | New investigator A05 |
|---|---|---|
| Azure execution |Succeeded|Succeeded|
| End to end |1955s|353s|
| Finding |TRANSFORMATION_LOGIC|as designed: technical implementation only|
| Measured boundary |Silver7661 -> Gold8765|Silver7661 -> Gold8765|
| Explanation |Retained product-rate join can multiply carried units|Same intermediate join mechanism|
| Application comparison |Not established|Explicitly partly answered; application target unavailable|
| Provider calls |3|6, including one rejected decision response|
| Provider ledger charge |USD0.038923|USD0.248779|
| Original replay |2/3 same-image MATCHED; one CONFIGURATION:BUDGET difference retained|Native tape captured; no exact native replay result claimed|

The new result is faster and explains the observed intermediate difference, but does not earn a complete source answer or a general performance claim. Verification-not-verified, limited DAX principal attestation, retained-definition age and SNAPSHOT_UNVERIFIED remain labels. Original failed new-investigator attempts A01/A02 (provider transport), A03 (budget reached), A04 (premature stop) are preserved; A05 does not erase them.

The separate ledger-only ticket asks whether the latest retained pipeline run failed. New investigator F01 answered its recorded SUCCEEDED status in32s (ledger step2.02s),0model calls/0estate value reads. Its closed verdict is not found, explicitly scoped to no failed/waiting incident, not an unexplained numerical discrepancy. There is no equivalent pipeline job-status-only ticket route or paired pipeline execution recorded; do not present it as a second matched pair.

Exact both outputs and evidence: [pipeline](runs/round-twenty-one-part0-A-03.json), [new A05](runs/round-twenty-one-new-investigator-A-05.json), [quick status ticket](runs/round-twenty-one-new-investigator-F-01.json). Live request counts in each pack distinguish investigation from access-audit/control overhead; monthly totals come from the shared ledger.
