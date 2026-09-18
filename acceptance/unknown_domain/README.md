# Post-freeze unfamiliar-domain publisher and evaluator

These scripts are operator/evaluator tooling. The investigator never imports them
or reads the publisher manifest, seed, private expected values or grading labels.
Run after a committed freeze and an ordinary discovery scan showing the domain absent.
Freeze tags and attempt results are recorded in
[the challenge record](../../docs/unknown-domain-challenge.md); issue #199 tracks acceptance.

`publish.py generate` creates a fresh random related warehouse variant locally.
`sql` creates new suffixed tables in the already approved SQL schema and reads
them back. `fabric` creates isolated Bronze/Silver/Gold lakehouses and a notebook
that loads those SQL readback rows and transforms them. `run` starts one journalled
notebook job; `status` reads its state. `publish_reports.py` creates a Direct Lake
model and two native reports. Publication never registers their IDs in the runtime.
No existing application table is modified. Keep the generated artifacts in `.local`.

The SQL publisher uses a transaction and does not retry existing names. If commit
succeeds but readback fails, inspect remote state and export the existing tables;
do not rerun its CREATE statements. Fabric mutations have durable journal keys;
uncertain outcomes require inspection before any resubmission. A corrected report
definition was submitted only after the first operation reported terminal failure.

After ordinary discovery, `run_ticket.py` uses business-question resolution and the
same scope preview as the workspace. Without `--execute-reviewed-scope` it only
resolves/previews; use that flag after the evaluator reviews the proposed scope.
It loads no expected value or per-model ID. The ticket text may naturally name the
report/metric the business user is asking about. Its outputs are acceptance receipts,
not authoritative grading or proof of generality.

For a constrained Azure model deployment, use `--minimum-llm-interval 65` to pace
calls in the evaluator harness. This counts toward the existing run deadline;
it does not retry failed calls, increase quota or change engine prompts/policies.
Record rate-limited attempts as blocked and preserve them before fresh trials.

The challenge must cover all nine architecture families, hidden variants, repeated
LLM trials, changed/added/removed assets and permission/partial scans. Unrun cases
remain pending. Reader denial is a blocker, never a reason to use publisher credentials.
The deployment APIs follow Microsoft's [lakehouse creation](https://learn.microsoft.com/en-us/rest/api/fabric/lakehouse/items/create-lakehouse)
and [notebook execution](https://learn.microsoft.com/en-us/rest/api/fabric/core/job-scheduler/run-on-demand-item-job)
contracts. The publisher uses the existing report/model definition conventions.
