# Question coverage in investigation outputs

#288 merged after all six checks passed, at `f8f61926e2c4613561bb53bb8fc8c784bab0148d`.

Both narratives now start with an engine-rendered account of the original ticket,
its answer coverage, the missing evidence, and a transition to the finding.
The model still writes mechanism only. The account is recomputed from the original
state during final synthesis validation; removing or changing it from either
output fails validation. The outcome, support, observations and original limits
are unchanged.

## Coverage contract and limits

The original ticket is quoted exactly, including its own vocabulary. Explicit
text markers identify currency, meaning, definitions/components and comparison
requests. Completed evidence roles and independent comparison receipts establish
partial coverage; an outcome label alone cannot establish an answer. Unknown
wording explicitly reports that completion has not been established.

This is conservative evidence coverage, not general semantic intent resolution.
Historical envelopes do not carry a complete set of question obligations. No
current branch promotes a question to fully ANSWERED solely from text recognition.
A definition receipt does not prove all requested components were explained, and
a comparison does not prove all requested scope was checked. This limitation is
visible rather than silently treating the finding as the answer. No extra model
classification, caveat field, prompt or provider payload was added.

## Saved E: offline production assembly

Original session: `c274890f-e041-4261-b364-c4c3d6c2bcc8`. Reused its recorded synthesis
response and payload with sockets disabled; the complete current output assembler
and question-account validator succeeded. This is offline rendering validation,
not a fresh live investigation or a new model response.

E remains TRANSFORMATION_LOGIC, with question coverage NOT_ANSWERED. Its prefix in
both outputs says:

> You asked: Inventory Health e1b8e1 Handled Quantity may be stale. Inspect the available refresh and processing history and explain whether freshness can be established. I have not supplied a freshness SLA.
> Answer to your question: Not answered.
> Regarding whether the reported information is current: No completed currency check establishes whether the reported information is current. Refresh history was unavailable to the diagnostic reader. Processing history was not assessed before the investigation stopped.
> What was found instead:

The finding then follows. Full regenerated [business output](runs/question-account-E-business.txt)
and [technical output](runs/question-account-E-technical.txt) are separate artifacts;
original outputs are preserved. An offline ledger row records zero physical reads
and zero model calls. An initial local audit script assumed output_text instead of
function_call and failed while decoding the tape, before assembly or any calls;
correcting the audit script did not alter the engine or recorded response.

| Context measure | Before | After |
| --- | ---: | ---: |
| Saved synthesis payload characters (same JSON serializer) | 15,405 | 15,405 |
| Directory entries | 0 | 0 |
| SQL directory objects | 0 | 0 |

Synthesis has an evidence payload, not a planner directory. Exact payload equality
and source-state equality were asserted around assembly. Source artifact SHA-256:
`9f46f06f293e5686702594da5944106593e531fceaaa4d77c5f7b345e83b09ae`.

## Validation

The first full run executed 1,324 tests and reported 16 errors because older
narrative fixtures omitted the original envelope. Those fixtures now explicitly
supply their question; all 34 tests in the three affected modules pass. Production
does not invent or default a missing question. The failed run is retained in
`.local/question-account-regressions.log`.

Five focused question-account tests passed, covering mandatory subject/status in
each output, different questions with the same finding, incomplete timing evidence,
unknown/multiple requests, and tampered account rejection. The final full regression run passed all
1,324 tests (451.851 seconds, exit 0); resource warnings remain visible in its log. No live run, credit grant, policy change or
acceptance claim. Engine changes invalidate earlier freezes.
