# Fixture rebuild groundwork

Recorded 2026-10-06 America/Chicago. No publication or `--apply` operation.
This is a completed seed/template extraction step, not the completed rebuild
command required by Round Nine.

[seed.py](../scripts/fixture/seed.py) reads the single literal `source_rows`
assignment in the committed notebook through AST and JSON parsing. It never
imports or executes the notebook. Table/column identities, types, row shapes
and bounds are validated. SQL insert plans retain values as bound parameters
and require a new object; no existing table is overwritten.

| Committed synthetic table | Rows |
| --- | ---: |
| Warehouse locations | 3 |
| Inventory products | 8 |
| Product rates | 9 |
| Stock movements | 360 |
| Purchase orders | 60 |
| Inventory adjustments | 30 |

Independent arithmetic over the committed literals gives 7,661 movement units.
The recorded product-only left join against versioned product rates yields 406
rows and 8,765 units. These are fixture arithmetic, not investigation receipts
or proof that the business rule is correct. They are never supplied to a model
as an answer to reproduce.

The notebook template accepts three explicit distinct container IDs and one
workspace ID. It changes only the `paths` declaration. A test compares every
other AST statement against the recorded notebook, including the seeded rows,
deduplication and join. Invalid or repeated container IDs refuse. Four focused
tests pass, including a notebook with an unrelated file-writing instruction
that remains unexecuted.

The current manifest contains two distinct paths. The original model has
serving/refined/landing layers. The later application-copy fixture has its own
model, landing and application layers, plus the Warehouse audit. Rebuilding
only the three original lakehouses would omit the application-copy path and
could not restore its gap, latency and source-consistency states. The committed
seed notebook supplies the original path; it must not be relabelled as evidence
of application ingestion.

The remaining rebuild steps must use separately committed, parameterized
recorded definitions for the Copy Job, audit pipeline, Warehouse audit schema,
both model paths and report predicates/bookmarks. They must preserve explicit
connection provenance and use the copy activity's own accounting. New IDs need
a new manifest and discovery approval; old context approvals and sealed runs
cannot be reused as fresh-tenant acceptance.

| Step | Identity needed when an explicitly approved future apply runs |
| --- | --- |
| Azure SQL seed tables | Application control writer with DDL/insert on new fixture objects; never the diagnostic SQL reader |
| Lakehouses and notebook publication/execution | Fixture publisher on the new workspace and writable fixture containers |
| Copy Job and connection binding | Fixture publisher with access to the explicitly declared source/destination connections |
| Warehouse audit and audit-writer pipeline | Fixture control writer for that Warehouse and pipeline publication/execution |
| Models and report publication | Fixture publisher; diagnostic Build grants remain separate human scope decisions |
| Fixture-state declarations and manifest | Local artifact writer; no permissions implied and no discovery approval manufactured |

Every mutating apply step needs a durable journal before dispatch, bounded
operation polling, and refusal to retry an uncertain mutation. The existing
create-only publisher journal is a reusable primitive, not authority to apply
anything now. The complete rebuild script, full plan output and mocked tests
for those remaining steps are still pending.

Dated follow-up, 2026-10-06 America/Chicago: notebook literals and externally
supplied SQL insert plans now use one complete seed validator. Insert planning
previously checked column names/types but did not enforce the same row shape,
value types, duplicate-column or extra-field rules. A hostile-producer test
rejects Boolean-as-integer, string-as-integer, wrong row width, duplicate
columns, non-string identities and undeclared fields; returned parameters are
independent of the caller's object. Five focused tests pass. This is still
publication-only groundwork; no apply, SQL connection or fixture mutation.


Dated 2026-10-07 Round Nine checkpoint: privacy installation commit f1389a9 passed all 2,241 local regressions. Atomic synthetic capture/replay leaves no raw sensitive value in evidence-store history, planner sidecars, tape or output; sealed dependent identities validate after cold load. No projected-estate live claim. Five scoped translation tests now compile integral cell predicates only through independently verified key correspondence; stale/missing proofs, ambiguous SQL and string semantics refuse. The existing lower-walk filtered refusal remains. Recorded model-step CI scoring passes intake 94.86%, reader 100%, tightened synthesis 100%, translation 100%; original human grades and superseded prose remain. Seven trace and one footer tests pass. `scripts/fixture/rebuild.py --plan --manifest ...` supplies both fixture paths and parameterized retained model/report/Copy Job/audit-pipeline templates; apply is deliberately absent per the latest plan-only instruction. Four plan tests pass. Zero estate requests for this checkpoint; live section6 and final demo verification remain pending, prior freezes invalid.
