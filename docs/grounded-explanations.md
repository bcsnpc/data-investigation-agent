# Evidence-grounded explanations

The first release lets the Azure model select and order findings and suggested next
steps from a backend-derived catalog of saved investigation evidence. The backend
supplies the exact wording and evidence references. This is a constrained explanation,
not freeform root-cause reasoning. Existing deterministic evidence remains authoritative.

Generate explicitly from PowerShell in the repository:

```powershell
& .\.local\llm-env\Scripts\python.exe scripts/run_azure_ticket_planner.py --explain 9ef75410-0b9e-433b-b648-6b20b806c73a
```

Each invocation makes one model request without automatic retry. It reads saved
evidence; it does not query SQL or Fabric. Azure credentials are captured in process
memory by the existing launcher. Model usage and response ID are recorded when the
provider returns successfully, including locally rejected selections. A provider
failure before returning may have unknown usage.

Attempts are stored in `investigation_explanations` in the local workflow SQLite
database, with an evidence hash, version, classification, status and timestamp.
The authenticated investigation detail API returns the latest validated explanation
only if its hash and version match the current evidence. It revalidates the selection
and renders the wording again rather than trusting stored prose. Failed or stale latest
attempts return no explanation; the original evidence and summary remain available.
The local review UI displays highlights, next steps, limitations and expandable JSON
pointer references into the investigation detail. Generation is operator CLI only;
automatic worker integration is a later step.

Unknown IDs, added fields, duplicates, empty selections and selections without any
observation or comparison are rejected. Missing evidence and all boundary statuses
are mandatory even when omitted by the model. Numeric comparisons require matching
recorded currency and filters and finite decimal values. Equal values never establish
snapshot comparability. Classification is unchanged and automatic defect routing stays
disabled. No repair actions are offered.

Validation includes exact decimals, unavailable sources, unequal values, mismatched
scope, nonnumeric data, rejected claims, tampered stored wording and stale evidence.
Live validation uses saved run `9ef75410-0b9e-433b-b648-6b20b806c73a`: all five layers
returned one order and USD 1,529.64, but boundaries remain NOT_COMPARABLE and the
classification UNRESOLVED. The model-selected explanation preserves those limits.
