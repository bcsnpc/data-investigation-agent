# Lab record reconciliation and impact

`python scripts/lab_investigator.py` reads the local lab business projection and saves
a deterministic investigation in `.local/defect-lab/evidence.sqlite`. The evidence
database uses the existing investigation_runs schema and is readable by EvidenceStore
and the read-only evidence API. It is separate from the cloud metadata/workflow stores;
no live lineage identity is invented. Ticket-worker/UI integration of this lab-specific
investigation kind remains a follow-up.

The projection uses a full outer join by order and currency. Explicit presence flags
distinguish absent records from valid zero amounts. Extra Gold keys remain visible.
The investigator detects missing, extra and changed records, retains evidence pointers,
and sums exact decimal differences independently for each currency. Duplicate keys,
inconsistent presence, invalid money and unsupported precision are rejected.

For aggregate impact only, absent rows contribute zero. Their absence is still reported
as a key mismatch, including zero-valued rows. Offset errors can produce zero net impact
while the comparison remains MISMATCH. Do not sum different currencies.

The investigator consumes neither scenario labels nor evaluator ground truth. It reports
the compared Silver/Gold boundary, not a first broken boundary across an unobserved
estate. Classification remains UNRESOLVED, root_cause_verified is false, and automatic
routing is disabled. Data differences alone do not explain why rows were omitted, and
matching records alone do not prove expected business behavior.

Validation includes exact omission impact, additional Gold keys, currency separation,
zero-valued missing rows, duplicate/invalid evidence, value changes, reset reconciliation
and saved evidence round-trip. A local injection/investigation/reset cycle found
ORD-000001 missing from Gold with USD -99.0000 downstream-minus-upstream impact and
left the lab READY. No cloud queries or model calls are required.

Next: verify business drivers for a no-defect case and obtain cause-specific evidence
for defect classification. Expand beyond this local boundary only when corresponding
query, snapshot and lineage evidence is available.
