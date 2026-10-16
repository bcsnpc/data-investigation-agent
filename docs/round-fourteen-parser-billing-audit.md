# Trailing-period repair and billing pipeline rerun

The shared figure parser incorrectly rejected the sentence `The card shows 950.` because its numeral boundary excluded sentence punctuation. Commit 5b77962 accepts that boundary without accepting malformed decimals, qualified identifiers, competing figures or inferred tolerance. Three new regression tests and the full 3,284-test suite passed.

The pure-agent billing ticket-01 attempt reached this precise parser failure after replacing its ambiguous `950` quote with the full sentence. It remains a failed attempt, not retrospectively upgraded. Ticket-02 instead retained competing reported/comparison candidates and held; the punctuation repair does not remove that refusal.

## Round Thirteen attribution

Of 27 recorded billing attempts, six failed before intake and 21 held during intake. None is established as caused by this trailing-period defect:

| Tickets / repeats | Retained refusal before the repair |
|---|---|
| 01, 02, 03 / repeats 2 and 3 | Numeral source quote occurred twice; unique provenance was not established. |
| 04 / repeats 2 and 3 | Business-rule decision requires a domain specialist. |
| 05 / repeats 2 and 3 | Non-verbatim provenance, then a numeral quote occurring three times. |
| 06 / repeats 2 and 3 | Non-verbatim provenance. |
| 13 / repeats 1–3 | Non-verbatim provenance. |
| 14 / repeats 1–3 | Unresolved subject, unclear precision, non-verbatim provenance respectively. |
| 15 / repeats 1–3 | Unresolved subject, competing 600/100/250 candidates, unresolved subject respectively. |

The ticket-14 precision refusal was examined in its retained extraction: it included word-number candidates (`zero invoices`, `zero payments`, `four invoices`) alongside 950 and 550. It is not evidence of a trailing sentence period being rejected. The original rows, model responses and tapes remain unchanged. The source is `docs/round-thirteen-billing-final.json` and the sealed native artifacts it hashes.

The owner requested a fresh pipeline run of all nine sealed billing tickets after the repair. That run is in progress; only newly retained results will establish whether anything improves. No independent tester ticket, natural-language answer contract or expectation has been edited.


## Fresh pipeline result, 2026-10-11

All nine attempted once after the repair; all nine held at intake, zero delivered findings and zero harmful delivered claims. Total 16 model calls, zero physical requests and zero investigation diagnostics.

| Ticket | Exact refusal | Model calls | Physical requests |
|---|---|---:|---:|
| ticket-01.txt | Reported-figure quote occurs 2 times at ticket spans 157:160, 396:399; supply a longer unique verbatim quote. | 2 | 0 |
| ticket-02.txt | Reported-figure quote occurs 2 times at ticket spans 87:90, 253:256; supply a longer unique verbatim quote. | 2 | 0 |
| ticket-03.txt | Reported-figure quote occurs 2 times at ticket spans 204:207, 407:410; supply a longer unique verbatim quote. | 2 | 0 |
| ticket-04.txt | The requested business-rule decision requires a domain specialist; technical process evidence cannot decide whether the rule is correct. | 1 | 0 |
| ticket-05.txt | Provenance quote not found verbatim in the ticket. | 2 | 0 |
| ticket-06.txt | Provenance quote not found verbatim in the ticket. | 2 | 0 |
| ticket-13.txt | Ambiguous reported figure: more than one resolved value requires clarification: 950 from '950'; 550 from '550'; 600 from '600' | 1 | 0 |
| ticket-14.txt | Provenance quote not found verbatim in the ticket. | 2 | 0 |
| ticket-15.txt | DESCRIPTION_SUBJECT_UNRESOLVED: the selected Nothing comparison is retained; no description route could be admitted. Restate the question; the comparator will not be asked again. | 2 | 0 |

No fresh attempt reached the repaired sentence-boundary failure. All original inputs, response bodies and sealed captures were retained. These results do not establish that punctuation caused the earlier zero-findings billing result.
