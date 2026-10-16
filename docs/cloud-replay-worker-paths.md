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

The first post-portability Linux attempt also failed with CLOCK/WORKER_SEND. That
result is retained; the lexical-path correction alone has not earned a Linux
match. A private-only diagnostic wrapper now preserves the first TapeError at
Tape.event, including before/after indices and exact WORKER_START request bytes,
even when engine error handling later raises a second mismatch. Every exception
is re-raised and byte comparison is unchanged. The cloud summary remains counts
and error type only; first-error details follow the existing approved private
artifact channel. A regression deliberately creates a first request-byte mismatch
then the secondary clock mismatch and proves both semantics and original details
are retained. No further cloud replay was performed by this helper.

The private first-error capture established a second host-path dependency:
historical `metadata_config.validate_config` resolved the three configured path
fields using `str((ROOT / value).resolve())`. Linux treated the retained absolute
Windows paths as relative and prefixed the extracted repository directory. The
first mismatch is therefore WORKER_START request bytes; CLOCK/WORKER_SEND remains
a secondary error. Executable argv normalization alone could not fix configuration
contents.

Historical replay now wraps that validator's root only for the duration of a
validation call while a replay tape is active. Fully qualified Windows drive/UNC
paths retain Windows lexical absolute-path semantics; native absolute and relative
paths retain host resolution. Drive-relative Windows paths refuse because their
meaning needs a drive working directory. The original validator still checks all
fields. This does not inspect expected tape bytes, strip an observed temporary
prefix, rewrite statements, or change comparison rules. Live validation is
unchanged. Regression executes the real validator against Windows configuration
strings with a POSIX root, and tests relative paths, POSIX absolute paths, UNC
paths, drive-relative refusal and the unchanged live root. A new Linux measurement
is still required; all earlier failed attempts remain in the record.
