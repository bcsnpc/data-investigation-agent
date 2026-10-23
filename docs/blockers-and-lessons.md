# Blockers and lessons

## Round 22, 2026-10-22: streaming snapshot deadline

Round 21's 96 MiB child-memory test exceeded 180 seconds during the four-way
main suite, then the unchanged complete module passed in 106.893 seconds
alone. Choose a 300-second test deadline (2.8 times the isolated duration),
rather than changing assertions or reducing the database. Source preservation,
concurrent-WAL consistency, unsafe-value refusal and the less-than-96-MiB
peak-growth assertion remain unchanged. Full parallel validation follows.
