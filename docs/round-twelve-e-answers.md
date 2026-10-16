# Round Twelve E — answers from preserved records

2026-10-10. Read-only audit of the recorded results. No code, oracle, expectation,
receipt or prior result changed; no model call, estate request, test or new run.

## 1. All eighteen live tickets

“Match” below means the expected outcome was delivered, not an exact contract
match. A = refusal/incomplete answer where the contract expected more; B = a
confident wrong finding; C = supported finding with the wrong depth, detail or
answer coverage. A delivery crash is identified separately rather than disguised
as a valid refusal. Original I matches its outcome but has a C detail error.

| Ticket | Expected outcome | Actual outcome / delivery | Match | Mismatch classification and evidence |
|---|---|---|---|---|
| original A | TRANSFORMATION_LOGIC | TRANSFORMATION_LOGIC | Yes | Outcome matches; provenance differs. |
| original B | NO_KNOWN_PATTERN | NO_COMPARABLE_PATH | No | A: stops at the semantic layer with no stable discovered binding for the partition source; does not reach the expected analysis. |
| original C | No outcome; status HELD | No delivered outcome; ticket remains INVESTIGATING after delivery exception | No | Delivery failure, closest to A but **not** an answer-expected case: the contract expected a refusal. `Conflict: Saved synthesis has no assessment`. |
| original D | NO_COMPARABLE_PATH | NO_COMPARABLE_PATH | Yes | Outcome matches; report provenance and selection-field presence differ. |
| original E | TRANSFORMATION_LOGIC | TRANSFORMATION_LOGIC | Yes | Outcome matches; provenance differs. |
| original F | CONSISTENT_TO_BOUNDARY | CONSISTENT_TO_BOUNDARY | Yes | Outcome matches; provenance differs. |
| original G | TRANSFORMATION_LOGIC | TRANSFORMATION_LOGIC | Yes | Outcome matches; provenance differs. |
| original H | NO_KNOWN_PATTERN | NO_COMPARABLE_PATH | No | A: semantic-only stop at the unbound partition source; mechanism and business meaning explicitly not answered. |
| original I | TRANSFORMATION_LOGIC | TRANSFORMATION_LOGIC | Yes | C detail error despite matching outcome: expected NOT_ANSWERED, delivered PARTLY_ANSWERED for the business-meaning question. |
| rebuilt A | TRANSFORMATION_LOGIC | CONSISTENT_TO_BOUNDARY | No | C: real equal semantic-to-serving comparison, but stops one boundary too early; expected serving-to-refined divergence is unchecked. |
| rebuilt B | NO_KNOWN_PATTERN | NO_COMPARABLE_PATH | No | A: no executable lower quantity/binding; expected analysis not reached. |
| rebuilt C | No outcome; status HELD | No delivered outcome; ticket remains INVESTIGATING after delivery exception | No | Same delivery failure as original C; expected refusal, not an answer. |
| rebuilt D | NO_COMPARABLE_PATH | NO_COMPARABLE_PATH | Yes | Outcome matches; report provenance and selection-field presence differ. |
| rebuilt E | TRANSFORMATION_LOGIC | CONSISTENT_TO_BOUNDARY | No | C: equal semantic-to-serving values only; lower divergence not checked. It explicitly says freshness was not established, not that the report is current. |
| rebuilt F | CONSISTENT_TO_BOUNDARY | CONSISTENT_TO_BOUNDARY | Yes | Outcome matches; provenance differs. |
| rebuilt G | TRANSFORMATION_LOGIC | CONSISTENT_TO_BOUNDARY | No | C: supported equality at the shallower boundary; neither the lower divergence nor application records were established. |
| rebuilt H | NO_KNOWN_PATTERN | NO_KNOWN_PATTERN | Yes | Outcome matches; provenance differs. |
| rebuilt I | TRANSFORMATION_LOGIC | BUSINESS_QUESTION | No | C: business-owner referral fits the unresolved meaning, but the expected technical finding/depth was not reached; also overstates answer coverage as PARTLY_ANSWERED. |

**Conservative live harmful-answer count: 2/18 — original I and rebuilt I.**
Both say “Partly answered” even though the actual question is what Q49 means and
whether it should affect the metric. Their own limits say no authoritative
meaning or intended rule was established. Those are harmful answer-coverage
overclaims, classified C above; calling them detail errors does not make them
harmless. The saved business wording is:

> Answer to your question: Partly answered.

> Regarding business meaning and intended treatment: No authoritative business meaning or intended rule was established; a technical finding cannot supply it.

**B-class confident wrong causal/business findings: 0/18 identified in the
recorded outputs.** The rebuilt A/E/G prose scopes agreement to the checked
boundary and names the unchecked connection; it does not claim the whole chain
or application is sound. This distinction is why their wrong outcome relative
to the sealed expectation is C, not B. The two I coverage errors still count as
harmful above. This is an explicit retrospective audit classification, not a
previously computed live harmful-error metric. The earlier zero-harmful number
was **dev intake**, not live answers.

Totals remain 16/18 delivered, 9/18 outcome matches, 0/18 exact contracts. The C
failures had completed registered-refusal synthesis with no assessment, then
crashed while sharing it. No corrected offline delivery is substituted here.

Pointers: [live comparison record](round-twelve-e-live-results.json),
[live table](round-twelve-e-live-results.md). Exact original outputs are retained
under `.local/round-twelve-e/live-forms-c377331/{estate}-family-{letter}/result.json`.

## 2. What “exact contract match: 0” means

These are structured acceptance projections, not verbatim prose comparisons.
The saved mismatching fields across the sixteen deliveries are:

| Field | Tickets | Difference | Meaning |
|---|---|---|---|
| `resolutions.report_binding` | All sixteen delivered | STATED versus USER_SUPPLIED_FORM | Different authority/provenance: the sealed contract came from text intake, the live submission supplied form picks. Correct form provenance must not be relabelled to pass. This is contract/input-shape alignment, not a wrong measured value. |
| `resolutions.selection` | Both D | Expected key present with null; actual key absent | Field-presence difference, not evidence that a different selection was used. |
| `outcome` | original B/H; rebuilt A/B/E/G/I | Labels shown in the table above | Substantive refusal, routing or depth differences. |
| `answer_category` | Both I | NOT_ANSWERED versus PARTLY_ANSWERED | Substantive overstatement of question coverage. |
| `boundaries` | rebuilt A/E/G/I | Expected equal semantic-to-serving **and** divergent serving-to-refined; actual only the equal first boundary | Substantive missing comparison. |
| `layers_reached` | rebuilt A/E/G/I | Expected semantic, serving, refined; actual semantic and serving | Substantive shorter walk. |

There is no recorded mismatch in `reproduction` for these sixteen deliveries.
The two C deliveries never yielded a full comparable projection; they are
failures, not provenance-only mismatches.

One complete compact example, **original A**, side by side:

| Contract field | Sealed expectation | Saved actual projection |
|---|---|---|
| status | COMPLETED | COMPLETED |
| outcome | TRANSFORMATION_LOGIC | TRANSFORMATION_LOGIC |
| answer_category | PARTLY_ANSWERED | PARTLY_ANSWERED |
| resolutions.report_binding | STATED | USER_SUPPLIED_FORM |
| boundaries | Semantic/serving equal; serving/refined different | Same two boundaries, equalities and grades |
| layers_reached | Semantic, serving, refined surfaces | Same three engine/connection/object triples |
| reproduction | null | null |

Original A fails exact equality **only** on authority/provenance. That does not
explain away the other tickets' missing boundaries or wrong coverage. Therefore
“0 exact” is **both contract/input-shape and substance**, not just formatting.
No expectation is changed in this audit.

## 3. Dev coverage losses and three non-settling complete forms

Every one of the twelve not-measurable attempts stopped before provider calls
with `QUESTIONNAIRE_NOT_MEASURABLE: required report/page not determined; no pick
invented`. The more specific construction reasons are below. All are original
estate records.

| Record | Recorded reason / construction | Caused by removed value field? | Caused by removed measure-only choice? |
|---|---|---|---|
| family-E-noisy | Explicit legacy MEASURE_TEXT freshness request; its construction clears report/page/visual. The authored text names a report but no page. | No | Yes |
| family-E-terse | Same measure-only construction; no authored page. | No | Yes |
| family-E-typo | Same measure-only construction; no authored page. | No | Yes |
| question-stale-no-sla | MEASURE_TEXT currency request, no visual/page; route STALE was already known. | No | Yes |
| refusal-business-benchmark | MEASURE_TEXT business-threshold question; no page/visual applies to the authored question. | No | Yes |
| refusal-business-intent | MEASURE_TEXT business-rule question; no page/visual applies. | No | Yes |
| refusal-business-q49 | MEASURE_TEXT business-meaning question; no page/visual applies. | No | Yes |
| question-change-days | Report known, page absent; target and figure undetermined; CHANGE_OVER_TIME comparator not offered by the construction. Missing page is the immediate stop. | No | No; already incomplete picks |
| refusal-two-figures | Report known, page absent; two genuinely ambiguous figures, target/comparator undetermined. Missing page stops mapping before the ambiguity can be asked. | No; ambiguity already exists | No; already incomplete picks |
| refusal-unidentified-visual | Report/page and target undetermined; no page pick can be copied. | No | No; already incomplete picks |
| refusal-unsupported-filter | Report known, page absent; target and comparator undetermined. Missing page stops mapping before the unsupported-filter decision. | No | No; already incomplete picks |
| refusal-unsupported-relative | Report known, page absent; target and comparator undetermined. Missing page stops mapping before the unsupported-relative decision. | No | No; already incomplete picks |

Seven are a coverage regression from removing the measure-only path. Five are
incomplete controls that cannot be submitted unchanged through a report/page-
required questionnaire. This is not proof that they need estate reads. Nor does
“report/page not determined” mean every report was unknown: the legacy
MEASURE_TEXT construction deliberately removed report authority, and several
other records have a known report but no page. No replacement page was authored.

The three remaining complete failures are:

| Record | Exact retained refusal | What was lost or failed | Value-field / measure-only attribution |
|---|---|---|---|
| original:visual-3 | TARGET_UNRESOLVED: Every grouping column requires a stated cell key. | Old input supplied KEYED with North and Component 1 keys. New input retained the matrix but sent no mode/keys. The description did contain both labels and 149; extraction recovered NUMBER 149 / EXACT but no selections/groupings/filters, so the keyed address was not admitted. | **Not the value field:** 149 was extracted. **Not measure-only:** report/page/visual were supplied. It is cell-key extraction after removal of explicit cell controls. |
| original:family-D | No executable retained choice for NUMBER | Old input supplied KEYED with warehouse North. New input supplied the matrix, mode null and no cell keys. The proposal resolved Handled Quantity and a North filter, but no selection; admission did not settle the cell and its fallback offered no executable NUMBER choice. | **Not the value field:** the old authored form also had no reported figure. **Not measure-only.** The keyed-cell admission/fallback failed after explicit cell controls were removed. |
| rebuilt:family-D | No executable retained choice for NUMBER | Same recorded shape and North-filter-versus-unsettled-cell failure on rebuilt IDs. | Same attribution as original D. |

The three failures are therefore not evidence that the user omitted the measure
or number. “Complete” describes the old oracle-derived form, whose explicit
cell address was omitted by the new questionnaire design. The description path
did not reconstruct it successfully. Nothing was approximated or substituted.

Final affected-dev column: complete 25/28 settled with zero questions; skipped
4/6; both groups zero illegitimate questions and zero harmful admissions; twelve
not measurable. This combines 45 unchanged rows from 1e1fb33 with one fresh
H-noisy row from 02cff87, not a full new frozen pass.

Pointers: [dev report](round-twelve-e-questionnaire-dev.md),
[structured dev scores](round-twelve-e-questionnaire-dev.json). Individual old
inputs, questionnaire mappings, extracted proposals and refusals are preserved
in `.local/round-eleven/round-twelve-forms-1e1fb33-grouped-dev-e-questionnaire/`.

## 4. Status checklist

| Item | Yes/no | Recorded evidence |
|---|---|---|
| A1 exact diff and new oracle hash | **Yes** | [A1 amendment](oracle-amendment-a1.md): A/E/G-mention only, explicit displayed 8765 with original spans; new SHA-256 `bc2819f1ab12ae93d2203a519a6318a6f9ecbc1a3220a466e664a00c495a9a6b`. Superseded original hash `be029b56a6de27195dac507bfb5010f0ce7abc2732702d9a230e5f4a8d38406c` retained. |
| Old and amended saved-output scores | **Yes** | Same A1 file, table reproduced below. Re-score only, no fresh held-out calls. |
| Billing review file pushed | **Yes** | [billing-unplanned-tickets-for-review.md](billing-unplanned-tickets-for-review.md), introduced in 572c70d and present on the pushed #423 branch at 5f1b5cd; blob `993303ead691bbe66949bf2ae34c0be1e1e2c857`. Tickets 07–12 verbatim, both rendering issues, causes unproved. |
| Reservation reconciliation fixed | **Yes**, with unknown-usage bounds retained | [Reservation correction](round-twelve-e-simple-intake.md): same 274 calls before/after, gross 1,899,500 versus actual charged 198,965; zero active and unknown-output charges. Latest saved snapshot: 390 calls, gross 2,710,500 versus actual 284,657; active 0, unknown-output charge 0. Immutable rows/counters and the acknowledged 1,500-reserved/2,504-used violation remain. Unknown usage after failure/timeout conservatively retains its reservation; it is not silently refunded to zero. |
| Retained discovery policy re-adopted with scope unchanged | **Yes** | [Session budget and discovery controls](round-twelve-e-simple-intake.md), and RETAINED_DISCOVERY_APPROVAL rows in [ledger](runs/ledger.jsonl). Exact adapter, identity, layer/resource-access scope checks passed. Zero metadata reads; retained adoption, not recollection. |
| Why original models were disabled established | **Yes** | Same report: our rebuild's `enterprise_discovery.publish` scoped projection disabled enabled models absent from the rebuilt-only collection. This was local catalog configuration, not platform permission revocation. Model revision32 last recorded enabled at 2026-10-08T02:08:46.604774Z; revision33 disabled after the rebuilt collection. No separate disable event/exact disable instant is retained. |

| Saved-output group | Old settled | A1 amended settled | Old harmful | Amended harmful |
|---|---:|---:|---:|---:|
| dev complete | 27/28 | 28/28 | 1 | 0 |
| dev skipped | 4/5 | 4/5 | 0 | 0 |
| dev incomplete controls | 4/12 | 4/12 | 0 | 0 |
| held complete | 18/21 | 20/21 | 2 | 0 |
| held skipped | 2/2 | 2/2 | 0 | 0 |
| held incomplete controls | 1/7 | 1/7 | 0 | 0 |

Initial live approvals: original context `b8d15e64-a003-41bf-924a-0ab9006599d0`,
config `b240cef651374de86fbf2d43708d412641097e1ee40071eb5122eda550460661`;
rebuilt `2f662903-b06e-407e-b5a1-de1eaded8968`, config
`adebadf73fe62d6f8cab4001a9081e6cd95804767fc4bcf2eb6e15dafe721c33`.

After restoring the original manifest ceilings, unchanged retained scope was
re-adopted under the restored whole-config hashes: original context
`0bc41d66-4fd8-4902-8931-d5609cd8d615`, config
`c9a27319e94d12e27ba797104a3b31f072d98f7302b1666f18937c91c93b65c0`;
rebuilt `73852267-63fb-4e2d-ac57-288a249979da`, config
`5e2a45cb0d9c21d688d8f1aec6f7cd4e56dab01638e4139aac3af30dab58d3b7`.
The restoration key collision and zero-read retry are recorded, not omitted.

## 5. Why 1,800, and what used it

Approval: the owner's 2026-10-10 session-only permission to increase limits.
The recorded reason was a conservative physical-request estimate of 18 × 16 =
288. At 1,150/1,500 with reserve95, ordinary usable remainder was255. The
300-slot temporary increase covered the33-slot estimated shortfall plus live-list
controls. Reserve95, rolling3,000, diagnostic12 and model allowances did not rise.

Actual consumption was **104 requests**:100 from the eighteen investigations,
plus4 from two application pre-warms, counted as controls. They moved the pot
1,150 → 1,254. Dev/model-only passes and retained discovery re-adoption used
**zero estate requests**. Receipt totals for the investigations were44 diagnostic
reads and42 guards; those are components/classifications, not extra requests to
add on top of100. The C runs had no diagnostic receipt counter, not an invented
zero counter. Per-ticket physical usage is:

| Family | Original | Rebuilt |
|---|---:|---:|
| A | 10 | 8 |
| B | 1 | 2 |
| C | 0 | 0 |
| D | 3 | 4 |
| E | 10 | 8 |
| F | 7 | 8 |
| G | 10 | 8 |
| H | 1 | 2 |
| I | 10 | 8 |
| Investigation total | 52 | 48 |

**None of the extra 300 slots was actually needed or consumed.** Actual104 fit
inside the original255 usable slots. The ceiling was raised against the estimate,
not because an actual run reached the old ceiling. Both manifests were restored
to1,500 with counters intact; final pot1,254/1,500, reserve95, usable151. Rolling
usage137 → 241/3,000. See SESSION_LIMIT_CHANGE, SESSION_LIMIT_RESTORED and final
ROUND_REPORT entries in [the ledger](runs/ledger.jsonl).

This document records answers only. #423 remains draft; no code changes, new
runs or expectation changes accompany it.
