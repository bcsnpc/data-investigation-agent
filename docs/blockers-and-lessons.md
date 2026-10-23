# Blockers and lessons

## Round 22, 2026-10-22: streaming snapshot deadline

Round 21's 96 MiB child-memory test exceeded 180 seconds during the four-way
main suite, then the unchanged complete module passed in 106.893 seconds
alone. Choose a 300-second test deadline (2.8 times the isolated duration),
rather than changing assertions or reducing the database. Source preservation,
concurrent-WAL consistency, unsafe-value refusal and the less-than-96-MiB
peak-growth assertion remain unchanged. Full parallel validation follows.

## Round 22: daily SQL worker deadline consumed by parent capture

Recovered the immutable Round 21 investigation event journal, SHA-256
`91a868ec379df1a425cbc7c52bcfd854e876101bb9512fe5de30f47aa6368614`.
All three lower workers started with a 150-second deadline. For the first,
identity completed at +7.887s, database guard at +31.752s, object guard at
+94.130s, and the quantity REQUEST arrived at +133.500s. Parent budget/capture
processing delayed ALLOW until +156.476s; flush then raised BrokenPipeError,
and WORKER_END retained -9. The other two repeat that sequence. The query
had not been admitted before the worker deadline. This is evidence of the
parent handshake timing failure, not evidence of an OOM or SQL denial.

Remote publication now waits until the physical worker has closed; the
unchanged original events still serialize, secret-audit and fsync immediately.
Every queued record must be acknowledged before the enclosing step returns or
seals. Published step-start remains evidence of an interrupted incomplete
step. No read-only guard, budget reservation, child timeout, result or expected
classification was relaxed. A real child-pipe test refuses publication while
the child is waiting; failure tests preserve the original error and prevent
an unpublished capture from sealing. Live three-run confirmation is pending.

The first new publication-failure test expected OSError from seal; the existing
seal correctly refused with CAPTURE_PUBLICATION_FAILED_NO_SEAL instead. Corrected
that test assertion to the stronger existing refusal; no implementation bypass.
