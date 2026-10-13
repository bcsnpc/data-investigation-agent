# Historical replay portability finding

The initial eight distinct cloud replay shards matched7/8. A separate diagnostic
rerun of shard4 matched0/1 and retained `TAPE_EVENT_DIFFERS:CLOCK:WORKER_SEND` in
its private diagnostic artifact. Windows replay of the same eight tapes matched8/8.
These earlier results are not rewritten by the correction.

`CLOCK` records an engine logical clock request, with a name such as `utc_now` or
`agent` and its recorded epoch value. It does not represent a response from a
worker or an inferred elapsed time. `Tape.take('CLOCK')` rejects when the pending
sealed event is `WORKER_SEND`; neither event may be skipped or reordered.

Only the failed tape contains worker transport events. Its first worker command
is the configured Windows Python executable. The historical descriptor used
`Path(value).name`. On Windows that yields `python.exe`; on Linux a Windows path's
backslashes are ordinary characters, so the same expression yields the whole path.
The descriptor therefore fails its existing normalization to `python` on Linux.
`WORKER_START` is consumed before its unequal body raises; subsequent failure
handling requests a clock and exposes the secondary CLOCK/WORKER_SEND mismatch.

The correction gives explicit Windows-drive and UNC paths their Windows lexical
meaning, independent of the replay host. It retains the existing normalization of
Python executable names and script basenames. Config operands remain real local
files whose complete contents are included in the descriptor. Other arguments
and worker request/response bytes are unchanged. Different executable names,
arguments and statement bytes still fail exact matching.

New code uses portable descriptor construction directly. Historical replay loads
a narrowly scoped compatibility helper around descriptor construction only while
an active tape is replaying. The original engine commit, tape events, seals,
expectations and event comparison rules remain unchanged. This does not claim the
original Linux execution passed: a post-correction cloud replay is a new measured
attempt, and must be reported separately.
