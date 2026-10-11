# Bounded fixture export helpers

These inert helpers export a small, declared fixture table into SQLite after a guarded read. They do not execute a cloud request on import. An operator must supply the approved configuration, current shared usage governor, declared table schema, bounded plan and reader transport. There is no automatic execution CLI in this package.

`exporter.py` preserves integers, exact decimal text, binary bytes, NULL and ISO timestamps including seven fractional digits. It refuses truncated responses and cap overruns. Every fully validated table commits independently; a later failure leaves a BLOCKED partial manifest rather than a complete-export claim. Context and estate authority pins are required. Native engine equivalence and cross-layer snapshot alignment are not established by copying rows.

`sql_compile.py` builds SELECT-only requests from discovered schema. The dedicated PowerShell readers cap each export control at 10,000 rows and 16 MiB. They retain the existing principal, database and object read-only checks. The investigation readers remain capped at 251 rows. `guarded_controls.py` routes each child request through the shared physical governor, adds a bounded export allocation, and accepts an owner-stop callback before logical and physical admissions. It never raises ordinary pot, restoration reserve or rolling limits.

A projected writer applies projection before serialization, but the native export transport currently refuses PRIVACY_PROJECTED estates before admission: a writer-only projection must not be mistaken for capture-wide privacy. EXACT synthetic estates require their declared authority. A failed or stopped export is not usable as an approved local estate.

Run the offline tests from the repository root:

```powershell
python -m unittest discover -s acceptance/local_export -p "test*.py"
```

The Round Thirteen owner stopped the initial private exporter. Its controls and interrupted database remain private and unchanged; seven successful table reads are not a completed export. The later partial-commit and owner-stop improvements were tested only and were not used to resume that attempt. No private source routes, authority definitions, raw rows, execution plans, identities, credentials or control executors belong in this helper package.
