# Contributing

Use a feature branch and pull request for changes after repository bootstrap.
Reference a tracking issue. Keep generated datasets and credentials under `.local/`.
Do not commit credentials, environment files, database dumps or generated datasets.

Run generator tests before submitting changes:

```powershell
python -m unittest discover -s scripts -p test_generate_orders.py
```

SQL changes require review of constraints and a relevant development-database
validation. CI intentionally does not connect to Azure or modify cloud data.
Record live verification separately when relevant. Update `docs/progress.md`
when milestone status or scope changes.

Group cohesive milestones into substantial PRs with implementation, meaningful
verification and tracker updates together. Avoid a chain of helper-only PRs;
record acceptance boundaries and remaining work for each grouped milestone.

The controlling direction is `SELF_DISCOVERING_ENTERPRISE_INVESTIGATOR_PLAN.md`.
After every meaningful stage, review the entire README for stale claims and update
`docs/current-delivery-status.md`, `docs/progress.md` and relevant architecture/
milestone documents. Current status belongs in the delivery-status page; retain
historical evidence without treating old next-step paragraphs as the current plan.
Behavior on assets introduced after engine freeze is the primary acceptance signal;
new supported assets must not require investigator-specific Python branches.

Every change that adds planner context must report directory entry count, SQL-object
count and payload characters before and after in its PR. Golden-view coverage tests
must assert that directory coverage did not fall. Run these offline before live
evaluation; increasing a context limit is not a substitute for reporting the cost.
