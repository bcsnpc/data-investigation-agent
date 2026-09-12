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
