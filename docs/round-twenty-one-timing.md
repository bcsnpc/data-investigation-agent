# Runtime observations and Round 22 candidates

The owner approved a 3,600-second manual worker/demo window and the same window
for the daily smoke when it includes the earned A demo. A health-only daily
smoke and the independent graph scan retain 1,800 seconds. Their resources,
identities and cron expressions are unchanged. The demo's absolute run deadline
uses the same hour and still honours an earlier explicit deadline. A larger
maximum does not establish the duration or cost of a completed execution;
actual runtime and the platform estimate must be reported separately.

Each new runner execution publishes an immutable `timing-summary.json` after
the ordinary `run-record.json` seal. The sidecar names that seal and has its own
SHA-256 receipt. It is observational metadata, outside the semantic tape and the
sealed record list, and excludes its own publication duration. A failure to
publish the optional timing sidecar produces a warning without erasing an
already sealed finding. Original tapes and captures are never rewritten.

The sidecar records each outer step's wall time, local serialization/audit/fsync
time, actual outer transport/publication time and final sealing time. Provider
wire durations are derived only from paired existing native tape
`PROVIDER_REQUEST` and response/failure timestamps. Reversed timestamps are
unknown, rather than clamped to a claimed zero. The model wire time is not a
measurement of model computation alone. Inclusive investigation, publication
and model durations overlap and must not be added together.

Azure provisioning/image-pull startup is unavailable inside this worker.
Intake is also unavailable unless a separate intake step was observed. Those
fields remain null with a reason. A timing summary from a future instrumented
execution is not evidence about an earlier interrupted run.

The first three Round 22 runtime changes to evaluate are:

1. Materialize and audit only the admitted ticket's path and pinned
   dependencies. The retained input currently carries a large historical
   catalog; copying, inflating and repeatedly auditing unrelated history adds
   dependency work and memory pressure. Keep the full original evidence in CAS,
   and retain a hash-checked, smaller execution dependency manifest.
2. Reduce repeated remote capture publications while preserving durable
   checkpoints and complete original bytes. Use the new publication counter and
   elapsed time to choose bounded append/chunk/checkpoint publication rather
   than one synchronous round trip for every small protocol event. Do not trade
   away the independent durable result or original failed partial captures.
3. Settle simple current operational questions from the facts ledger and keep
   model context compact. Measure provider wire time and call count separately;
   avoid calling a model to rediscover a known status or resend evidence already
   addressed by ID. More capable or faster models are a separate owner decision,
   not an assumed change in this round.

These are investigation priorities, not measured savings or implemented Round
22 features. Rank and quantify them from an instrumented live timing sidecar;
do not invent missing per-phase times for existing captures.
