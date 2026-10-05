# Exact-span intake recovery

A missing verbatim provenance quote now permits one separately admitted and charged
model correction. The correction requests exact ticket spans; it cannot waive quote,
figure precision, ambiguity, target or scope validation. A second invalid quote
returns NEEDS_INPUT. The existing ambiguous-figure recovery shares that single
correction allowance, rather than creating a retry loop. Both attempts are recorded.

The initial directory and wire payload are unchanged. Only a correction payload
adds the failed field and original producer response; its actual size is reserved
before dispatch. No estate reads or investigation runs occurred in this change.
Prior freezes are invalidated by the payload change; original tapes remain intact.

Validation: seven metered intake recovery tests, thirteen provenance tests and
thirty-six question intake tests passed, including model-only intake.
