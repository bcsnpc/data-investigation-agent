# Round Sixteen B ? governed saved-text extraction audit

The 85 retained Round Fifteen prompt records were attempted without estate data reads or new investigations. This audit does **not** establish that the 60 historically avoidable asks were fixed, nor that all 22 repeated pipeline asks disappeared. It checks extracted fact shape and a narrow old-question-field guard; current billing routing is not measurable in the chosen current catalog.

The input contains original user text and, for secondary prompts, the exact prior USER reply. Assistant questions are kept only in audit metadata. An initial plan that mixed the assistant question into user tokens was rejected before any admission and preserved as superseded. No ticket, golden record, expectation or original tape was rewritten.

## Observed results

| Population | Records | Valid-shape extraction | Validation failure | Timeout |
|---|---:|---:|---:|---:|
| Pre-schema served inputs, source3672e53 |5|0|4 plus1 retry-admission hold|0|
| Remaining inputs, first provider attempts under1359e89 |80|30|48|2|
| Combined, kept separate by source |85|30|53|2|

The 30 extractions passed shape/provenance/precision validation. They have **not** been human-graded as semantically correct. Exact spans can still select a date or assign a wrong observation role; for example a date numeral may be emitted as a context figure. No technical finding was emitted, and harmful technical-investigation accuracy was not scored.

Five inputs, rather than the initially assumed four, reached the provider before the structural schema correction:005,006,007 and058-round-two each used two requests;008 used one, then its retry reservation hit the planner concurrency guard. Their nine requests and outcomes remain immutable. Eighty other first-wave inputs had zero provider requests, proved by their sealed tapes, and were then admitted once after the correction. The inherited governor allowed four model requests in flight; eight worker threads now wait behind those existing four slots. No limit was widened.

The original producer schema allowed every enum on every field, while the consumer correctly rejected cross-field symbols. The corrected schema uses field-discriminated variants: each enum belongs to its field and text fields require null. A regression tests every valid and invalid field/symbol combination. The five previously served inputs were not resampled.

The remaining 48 validation failures are not all genuine user ambiguity. Common failures include qualitative expectations such as ?I expected a label that tells me which before I put it into the billing notes? being encoded as numeric EXPECTED observations; nonnumeric explanatory context encoded as a quantity; and several component amounts encoded as one figure span. Overlapping evidence classifications are {"MULTIPLE_COMPONENTS_ENCODED_AS_SINGLE_QUANTITY": 15, "NON_NUMERIC_CONTEXT_ENCODED_AS_QUANTITY": 30, "PRE_SCHEMA_FIELD_SYMBOL_OR_RETRY_ADMISSION_FAILURE": 5, "PROVIDER_TIMEOUT_USAGE_UNKNOWN": 2, "QUALITATIVE_EXPECTATION_ENCODED_AS_QUANTITY": 43}. The quantitative/EMPTY observation contract cannot express these qualitative expectations as that observation type. No code was changed mid-batch to make the results pass.

## What the question check measures

The helper invokes `validate_question` on the **old question?s typed field** using current extracted facts. It does not invoke the current controller to count actual new questions. Across85:16 old asks were blocked by that guard,9 had no settled fact or a conflict,5 old questions were not typed by the audit,55 failed extraction. Among the22 repeated pipeline asks:7 were guard-blocked,1 did not have a settled typed fact,14 failed extraction. These are not a claim of7 correct new resolutions or0 re-asks. The earlier historical judgment remains22 avoidable repeats. For the separate 60 historically avoidable asks, the new number still asked is NOT_MEASURABLE: no complete, semantically graded current-controller comparison was obtained. The 16 field-guard refusals are not a 16/60 reduction.

A separate `policy.plan` projection was made from the real canonical retained catalog: `.local/unknown-domain-v4/catalog.sqlite`, read-only, catalog/context digest`2b6f2ee3eff203a2f4c3e4598529bece0b3ac2d03c2194d22bd7309939e545eb`. This chosen current catalog has one enabled model and no enabled billing target. It is distinct from A0?s isolated fixture-readoption catalog and does not imply all fixture models are disabled. The new unapproved billing context was not promoted into authority. All30 successful extractions therefore remain NOT_MEASURABLE_CURRENT_CATALOG for current billing next-question routing;55 remain NOT_MEASURABLE_EXTRACTOR_FAILED. Projected next questions are retained privately, not treated as executed admissions.

## Capture and usage

All165 first-wave/post-schema operation tapes are sealed, including80 original pre-provider reservation holds. Exact helper replay is **BLOCKED**, not green. Two attempted post-schema replays matched the provider request/response prefix, then failed with `TAPE_BUDGET_DECISION_DIFFERS`: the private capture bootstrap omitted `provider_transport_retries:2`, so the historical replay branch skipped the first recorded owner settlement. This is a capture-protocol defect; it is not a network violation and prefix agreement is not full replay. The marker was not backfilled, no matching guard was relaxed, and no served input was replaced. Production `run_recording` retains the marker; this defect is in the private audit helper.

145 provider requests were recorded:9 before the structural fix,136 after. There were0 estate data reads and2 separately metered existing-operator ARM key-bootstrap controls; keys stayed in RAM. Conservative rate-card charge moved$94.704272?$102.932940, a new$8.228668. Provider usage returned218,076 input tokens and492,574 output tokens across the measured calls. Two new timeouts retain full reservations/estimated charges of$0.145668 and$0.149145; their token usage is unknown. The13 historical UNCERTAIN rows remain unchanged; there are now15 UNCERTAIN rows and0 open RESERVED rows. All model-ledger reservations are closed. No timeout was resampled.

DECIDED WITHOUT REVIEW: the planning-only subtask guard was revised$4?$12 because observed first-wave cost$0.568895 for five served inputs/nine requests disproved the original estimate. This includes the first wave from the same$94.704272 baseline. The owner?s shared$119.704272 ceiling and$10 protected margin, every estate cap and identity scope stayed unchanged. The final charge is below the revised subtask guard.

Exact working source1359e89 was archived with all326 fingerprint files; engine hash`ee755e4bd6f7c8aacdc5aba2bf0ff4b18555d156e7eea5730f53b9d787e03132` matches the archive. Source3672e53 was separately archived. Models/counters are not backfilled or copied for live admission. Closed audit-only SQLite files were hash-verified and compressed as controls:189 native commands, all exit0, all logical hashes unchanged; shared ledgers excluded, no deletion. Free space moved11,285,700,608?11,285,626,880 bytes; they were already substantially compressed.

## Per-record column

| Prompt | Recorded source | Extraction | Old-field guard | Current next-question measurement |
|---|---|---|---|---|
| clarification-001 | 1359e89_POST_SCHEMA | EXTRACTED | RULE_BLOCKS_REASK | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-003 | 1359e89_POST_SCHEMA | EXTRACTED | FACT_NOT_SETTLED_OR_CONFLICTED | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-004 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-002 | 1359e89_POST_SCHEMA | EXTRACTED | NOT_TYPED_QUESTION | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-009 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-010 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-012 | 1359e89_POST_SCHEMA | EXTRACTED | FACT_NOT_SETTLED_OR_CONFLICTED | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-011 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-013 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-014 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-015 | 1359e89_POST_SCHEMA | EXTRACTED | NOT_TYPED_QUESTION | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-016 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-017 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-018 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-019 | 1359e89_POST_SCHEMA | EXTRACTED | FACT_NOT_SETTLED_OR_CONFLICTED | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-020 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-021 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-022 | 1359e89_POST_SCHEMA | EXTRACTED | RULE_BLOCKS_REASK | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-023 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-024 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-025 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-026 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-027 | 1359e89_POST_SCHEMA | EXTRACTED | FACT_NOT_SETTLED_OR_CONFLICTED | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-028 | 1359e89_POST_SCHEMA | EXTRACTED | FACT_NOT_SETTLED_OR_CONFLICTED | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-029 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-030 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-031 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-032 | 1359e89_POST_SCHEMA | EXTRACTED | NOT_TYPED_QUESTION | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-033 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-034 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-035 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-036 | 1359e89_POST_SCHEMA | EXTRACTED | RULE_BLOCKS_REASK | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-037 | 1359e89_POST_SCHEMA | EXTRACTED | RULE_BLOCKS_REASK | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-038 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-039 | 1359e89_POST_SCHEMA | EXTRACTED | FACT_NOT_SETTLED_OR_CONFLICTED | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-040 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-041 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-042 | 1359e89_POST_SCHEMA | EXTRACTED | RULE_BLOCKS_REASK | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-043 | 1359e89_POST_SCHEMA | EXTRACTED | RULE_BLOCKS_REASK | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-044 | 1359e89_POST_SCHEMA | EXTRACTED | RULE_BLOCKS_REASK | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-045 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-046 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-047 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-048 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-049 | 1359e89_POST_SCHEMA | EXTRACTED | FACT_NOT_SETTLED_OR_CONFLICTED | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-050 | 1359e89_POST_SCHEMA | EXTRACTED | RULE_BLOCKS_REASK | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-051 | 1359e89_POST_SCHEMA | EXTRACTED | RULE_BLOCKS_REASK | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-052 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-053 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-054 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-055 | 1359e89_POST_SCHEMA | EXTRACTED | FACT_NOT_SETTLED_OR_CONFLICTED | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-056 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-058 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-057 | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-036-round-two | 1359e89_POST_SCHEMA | EXTRACTED | RULE_BLOCKS_REASK | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-037-round-two | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-038-round-two | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-041-round-two | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-039-round-two | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-042-round-two | 1359e89_POST_SCHEMA | EXTRACTED | RULE_BLOCKS_REASK | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-043-round-two | 1359e89_POST_SCHEMA | EXTRACTED | RULE_BLOCKS_REASK | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-044-round-two | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-045-round-two | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-046-round-two | 1359e89_POST_SCHEMA | EXTRACTED | RULE_BLOCKS_REASK | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-047-round-two | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-048-round-two | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-049-round-two | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-050-round-two | 1359e89_POST_SCHEMA | EXTRACTED | RULE_BLOCKS_REASK | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-051-round-two | 1359e89_POST_SCHEMA | EXTRACTED | RULE_BLOCKS_REASK | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-052-round-two | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-053-round-two | 1359e89_POST_SCHEMA | EXTRACTED | FACT_NOT_SETTLED_OR_CONFLICTED | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-054-round-two | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-055-round-two | 1359e89_POST_SCHEMA | EXTRACTED | RULE_BLOCKS_REASK | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-056-round-two | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-057-round-two | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-008 | 3672e53_PRE_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-003-round-two | 1359e89_POST_SCHEMA | EXTRACTED | NOT_TYPED_QUESTION | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-010-round-two | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-011-round-two | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-022-round-two | 1359e89_POST_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-029-round-two | 1359e89_POST_SCHEMA | EXTRACTED | NOT_TYPED_QUESTION | NOT_MEASURABLE_CURRENT_CATALOG |
| clarification-005 | 3672e53_PRE_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-007 | 3672e53_PRE_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-006 | 3672e53_PRE_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |
| clarification-058-round-two | 3672e53_PRE_SCHEMA | HELD_OR_FAILED | Extraction failed | NOT_MEASURABLE_EXTRACTOR_FAILED |

Private full map `.local/round-sixteen/b-model-question-audit-final.json`, SHA-256`d0f37f0e27c23f04075879b38e951ce44c2fc0fc03e51dbd2ff5fdea63793e16`. User-source fragments, raw provider bodies and failure messages stay private. Helper SHA-256`bb75dc0a565ce9e11047c8edf05ae63508686947c32d1cd86e376f7929e0fc84`; corrected scheduler helper SHA-256`da49bbfe3b0e1a51c637af79e77359c356a33b13bee8d54265ee318c6ac844d5`. Corrected85-input plan SHA-256`01b19276316224505869b1206ffb4373aa3c8211f94f7d62fe6001e99ca24859`;80-input resume plan SHA-256`64c181aeac37c6809ebc760bb292d3d91eed821f21e53296268f157130db7ce4`.
