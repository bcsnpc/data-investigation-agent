# Field-aware quote provenance (PR C)

Date: 2026-10-02. Report-scoped cells merged in [#309](https://github.com/bcsnpc/data-investigation-agent/pull/309) at `05a63bf`, after six green checks and 1,550 local tests. No live investigation has yet exercised that path.

Repeated measure, column and selection quotes identify the same extracted referent. The consumer computes every occurrence from the untouched ticket and saves them as `quote_provenance`; the existing exact-span contract retains the first occurrence as its canonical span. No quote is normalised, guessed or replaced. Report-name quotes use the same occurrence accounting; exact report-catalog uniqueness remains independently required.

A repeated reported-figure quote remains ambiguous. Intake permits exactly one separate quote-repair call. Its wire schema contains only reported-candidate quotes; the first call's measure, report and selection cannot change. The repair must be longer, include the original quote and occur verbatim. If still duplicated, the NEEDS_INPUT reason names every ticket span. A nonverbatim or non-longer repair refuses with no third call. Distinct plausible figure candidates retain their existing ambiguity refusal. Precision is still derived from the final ticket span; no tolerance is chosen.

Each attempt has its own reservation, metering and recording event. The first is settled before admitting the retry, without refunds or counter resets. A blocked retry makes no provider call. User cancellation fences late responses and settles an in-flight retry conservatively. The retry is not a retry for a timeout or an invalid general proposal.

## Validation and context cost

Twelve quote tests and five admission/retry tests pass. They cover repeated entity occurrences, field-based treatment of the same numeric text, unique longer figure context, still-duplicate context, nonverbatim repair, separate accounting, idempotent request keys and refusal at the allowance. Intake, immutable family fixtures and recording tests are also exercised; historical tapes are unchanged. The first full-suite execution was interrupted before a final result; its partial log is preserved. A separate resumed full suite supplies the final result before merge.

All twelve first-attempt intake payloads remain byte-identical (1,050?1,952 characters); their catalogs and wire schemas are unchanged. Instruction constants change 4,442 -> 4,513 characters. Golden directory coverage remains 28 -> 28 entries and 11 -> 11 SQL objects. The second call adds bounded consumer-generated quote-repair context and is reserved independently. No directory compaction budget changes.

No investigation run, ledger row, provider/estate read, fixture mutation, permission, credit grant or policy change occurs in this PR. Engine bytes changed, invalidating all prior freezes. Three exact saved tickets run only after this PR merges; their prior failures remain unchanged. The date-predicate fixture change remains deferred.
