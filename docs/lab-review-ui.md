# Reviewed local lab investigations

Initialize the lab as described in [defect lab](defect-lab.md). Set
`INVESTIGATOR_API_TOKEN` to a private token of at least 32 ASCII characters, then run:

```powershell
python scripts/serve_lab_review.py
```

Open http://127.0.0.1:8772 and connect with that token. This server uses isolated review
and evidence databases under `.local/defect-lab/review`; it never uses the cloud queue,
Azure credentials or model deployment. Its explicit local report/measure catalog is a
fixture contract, not discovered cloud lineage.

Submit a ticket for **Lab Net Cash**, generate a draft, review the displayed Net Cash /
USD / all-orders scope and approve. The lab planner is deterministic; it does not infer
filters or intent from the narrative. The UI labels this limitation. An unsupported
report needs clarification; incompatible explicit fields cannot be approved.

The existing background worker processes one approved ticket per server session. A
READY lab can produce the scoped EXPECTED_BEHAVIOR finding. A prior operator
`inject-filter` can produce the verified TECHNICAL_DEFECT finding. Output deletion without
proof remains UNRESOLVED. The server never injects or resets defects; manage scenarios
separately with the lab CLI and avoid changing them during an active investigation.

Refresh the child ticket after execution. The evidence UI displays deterministic scope,
verified local cause when present, exact per-currency totals/differences, affected orders,
and verified capture/refund arithmetic. Classification remains distinct from COMPLETED
workflow status. No automatic bug or notification is sent.

Stop and restart deliberately for the next worker session. Token/port validation and
the existing authenticated API remain in effect. This is a local review experience, not
a deployed service or a general report investigation implementation.

Validation covers both classifications through real API planning, approval, worker and
saved-evidence paths. Browser verification exercised ticket submission through technical
defect display, including mobile layout. The local lab is reset after verification.
