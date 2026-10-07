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
