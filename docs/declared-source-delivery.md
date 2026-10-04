# Declared source delivery evidence

2026-10-04. Part B implementation, known-domain work; prior engine freezes are
invalidated. No unfamiliar-domain acceptance claim.

The estate may explicitly declare discovered source-column identities for a
unique key, copied version token and UTC last-modified time. The Microsoft
adapter follows the existing full-table Copy Job mapping, reads the declared
audit first, and compiles bounded ordered source/destination pages with the
existing governed SQL compiler and reader guards. It never substitutes a
recount for the activity's own counters. Filtered lower comparisons remain
refused. Five pages per surface is a ceiling, not completeness evidence; only
a short final page with conserved ordering establishes enumeration.

Missing/different-version rows whose changes all follow the completed load
support LOAD_LATENCY. Changes all preceding its start support INGESTION_GAP.
Changes during the load, mixed intervals, incomplete enumeration, failed or
malformed audit accounting, or unavailable reader attestation remain
unavailable. The engine reclassifies original sealed audit rows and original
membership pages; it does not trust an adapter-supplied outcome. Fabric SQL
endpoint synchronization remains explicitly unexcluded, with
SNAPSHOT_UNVERIFIED. This is qualified evidence, not an assertion that a
particular copy activity lost rows.

An estate may declare its authoritative layer unreachable. The walk stops
before reading that layer, names the unchecked hop, and retrieves declared
load accounting without earning a source/latency/gap claim. No application
read means no application-boundary outcome.

Two integration defects in the earlier audit reader were exposed during this
work: it expected endpoint properties at the wrong depth and passed typed
query cells to a primitive-row classifier. The tests now use the transport's
actual endpoint shape and typed cells. Successful completion is distinct from
currency; missing timestamps or counters are never defaulted.

Validation includes neutral hostile-producer tests, original-receipt mutation
refusals, sub-microsecond timestamp preservation, mixed-cause refusal, compiled
pagination and configured-unreachable source tests. A stable rerun of the one
broad-suite failure passed; the earlier broad run (1,713 tests, one failure)
occurred while engine files changed and is retained as a failed check, without
claiming its cause. A subsequent stable focused run passed 142 tests; the final source/audit/flexible run passed 55. Final CI is recorded on the PR.

Planner directory projection is unchanged: the existing golden fixture retains
28 directory entries, 11 SQL objects and 5,543 payload characters. No open
planner route, scenario-specific branch, default model, permission, schedule,
budget ceiling or ordinary allowance changes here. Source-role configuration
and live scenarios are separate recorded work; these tests are offline.
