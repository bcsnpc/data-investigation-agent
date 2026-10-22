# Capture publication after shared transactions

Family A demo attempt 02 stopped with
`NETWORK_DURING_SHARED_STATE_TRANSACTION`. The capture observer tried to upload
a native event synchronously while shared application state held its transaction.
The gateway correctly refused that request. This was capture egress, not an
unapproved estate read or a missing report-list grant.

`SharedState.after_transaction` now provides a completion queue. Native records
are still created locally with exclusive creation and fsync immediately. Only
their remote publication is queued. On commit or rollback, the connection closes
and the transaction marker resets before queued publications run, in their
original order and before the transaction context returns. Rolled-back attempts
remain observations and are retained. No gateway exception was added.

Publication failures remain visible and prevent a successful seal. Local files
and their original hashes remain available. If an operation already failed, a
publication failure is attached as a secondary exception note rather than
replacing the primary error. Sealing during an active transaction refuses.

Regression tests use a real SQLite SharedState transaction and a publication
spy that independently acquires a write lock and reads committed/rolled-back
state. They check ordering, hashes, seal conservation, failure retention and the
unchanged network guard.
