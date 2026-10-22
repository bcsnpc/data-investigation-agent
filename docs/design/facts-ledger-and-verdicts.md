# Facts ledger and evidence-checked verdicts

Owner design recorded 2026-10-21 for Round Twenty-One. **Design only: none of
the collectors, verdict migration or new investigation flow described here is
claimed implemented or validated by this document.** Round Twenty's runner,
Bronze, demo and value-verification work precedes this implementation.

## Scheduled collectors and the ledger

Collectors are scheduled code, not agents. They wake, collect timestamped facts
into PostgreSQL and exit. Job runs and refreshes use list calls every 15–60
minutes, including schedule-overdue detection in the same pass. Definition
changes use the existing graph change detection. Counts and checksums run once
after each load, only for key tables named in estate configuration. Use platform
events where Fabric exposes them.

Every fact carries `collected_at`, its observed subject, provenance and retained
evidence reference. An answer must make its observation time clear. At answering
time, code checks fact freshness; the investigator refreshes stale facts live
only for objects on the ticket's path, then writes the new facts back. Missing,
unreadable and stale observations must remain distinguishable from a successful
negative observation. Collectors and scheduled scans draw from their dedicated
1,000-request monthly line, preserving investigation capacity.

The graph plus runtime ledger facts on its nodes and edges is the substrate.
Query it first and read live sources to verify or fill gaps. The graph walk is
bounded by the configured per-client deepest accessible layer. The application
remains the system of record where declared and accessible; reaching a boundary
must not imply that an inaccessible application was checked.

## One flow for every channel

Ticket, web app, Teams, email and AI chat through MCP use the same procedure:

1. Model intake understands the question and screenshots and asks one question
   when necessary.
2. Code checks the ledger and the relevant graph path.
3. If the facts decide the question, return a quick answer; the model words the
   reply and does not invent facts.
4. Otherwise the guarded investigator recreates the user's number, recreates
   the comparison, walks the graph's layers and performs read-only queries to
   locate the cause.
5. The model proposes a verdict; code checks the supporting evidence.
6. Return a plain summary with an observation timestamp and a developer evidence
   pack through the same channel.
7. Save the case and all new facts.

Exactly one verdict is returned:

| Verdict | Intended question it settles |
|---|---|
| as per design | The observed behavior follows the retained design. |
| latency | Evidence establishes delayed propagation across the located boundary. |
| waiting on job | The relevant scheduled work has not yet run. |
| failed job | The relevant run failed. |
| refresh pending or stale | The serving model's refresh state explains the observation. |
| different question | The comparison used different scope, dates or filters. |
| access difference | RLS or permissions produce different accessible views. |
| source changed history | Back-dated or corrected source records changed history. |
| not located | The evidence or ticket budget does not locate the cause. |

These are the target product verdicts, not an untested alias table for the
current outcome taxonomy. Round Twenty-One must define and test each evidence
contract and migration before using the vocabulary for findings. A job's failure
or a refresh timestamp alone must not become an explanation unless linked to the
ticket's quantity and relevant path. RLS remains read-only investigation, with
no impersonation.

## One investigator, deterministic tools

Start with one investigator choosing among small graph-aware tools in a
reason-and-act loop. The model selects the next tool; deterministic tools perform
the work through the existing guards. Tool set:

- get node facts;
- compare two layers for a key;
- last run of a job;
- last refresh of a model;
- diff a measure or transformation definition between two dates;
- existing `path_to_source`, `visual_context`, `filters_on`, `table_columns`,
  `definition_of`, `freshness` and `as_of`.

The model lists and ranks hypotheses up front: for example a Silver job did not
run, Gold applies a date filter, the model was not refreshed, or ingestion from
the application to Bronze was late. Each hypothesis reducible to a graph or
ledger fact is checked by code in parallel without a model call. As evidence
arrives, the model re-ranks and investigates only what code cannot settle.
Hypotheses are checks, not separate agents.

Stop when evidence supports one verdict or the ticket's budget is reached. A
budget stop returns `not located` with the last established point and remaining
split, rather than a guessed cause. Split into focused agents only if a side by
side evaluation demonstrates a benefit over this single investigator.

## Other questions and human decisions

“How is this calculated?” follows the graph from visual to source and explains
definitions in plain language, optionally with quantities at each step. Inferred
links are visibly labelled.

“Who changed this, and when?” uses activity logs, item metadata and git history,
with gaps named rather than filled by inference.

“Why was it decided?” and “Should we change it?” route to the human owner. The
tool prepares the current logic, history, numbers and impact analysis, never
changes business logic itself, and saves the human answer as a business-rule
note on that object.

## Case bundle, API and product surface

Every investigation writes a Markdown report and a JSON record containing the
ticket, hypotheses considered, queries and values per hypothesis, tool calls
with timings and cost, final verdict and stop reason. These records feed
evaluation, tracing and the submit-and-poll API. The evidence pack retains
provenance and limits; model prose never replaces the evidence.

Later, “ask any node” reuses the same tools for questions such as what happened
to `Gold.Orders` on a date. It is a graph question entry point exposed through
MCP, with no new UI required.

The free product is a local MCP server exposing graph tools and guarded read-only
queries. The paid product is a hosted MCP connector plus the ledger, collectors,
graph, case history, audit and identity backend, available to AI chat apps and
the web app.

## Inspiration and implementation boundary

The owner identified architectural ideas from
[MiroFish](https://github.com/666ghj/MiroFish): graph-first investigation,
ranked hypotheses and evidence-backed run bundles. MiroFish is AGPL-3.0. Use
these ideas only; copy no code. This document does not import its code,
dependencies, prompts or implementation. Implementation is deferred to Round
Twenty-One and must preserve the project's read-only, evidence, privacy,
identity-approval and budget controls.

## Ticket-path verification loading (owner direction, 2026-10-21)

Verification must load only the evidence for the ticket's own path, never the whole historical catalog. Resolve the admitted target to explicit object and boundary IDs first, then load only their definitions, bindings, surface attestations and referenced evidence. Retain those IDs and hashes in the capture so scope completeness is checked without importing unrelated history. Budget admission uses counters rather than historical evidence payloads. Historical tapes remain unchanged. This is a required Round Twenty-One design constraint; it is not a claim that the current verifier already loads by path.

## Round Twenty-One permission and prerequisite map

Owner-approved additions, 2026-10-21; execution details in
[the control record](../round-twenty-owner-unblock.md).

| Prerequisite | Authority and boundary | Observed status |
| --- | --- | --- |
| Model connection = fixed identity | Owner binds an existing read-only identity; investigator retains Read/Build, never write. Fixed identity and connection ID must be recorded separately from caller identity. | Approved, NOT APPLIED: fixture still default Entra SSO; connection portal authentication blocked. Billing requires its own binding readback. |
| Budget account exists for current month | Owner creates calendar-month $40 policy; worker consumes it without INSERT policy rights. | VERIFIED: October and November2026 accounts exist, $0 charged each at 2026-10-22T00:26:37Z. December onward requires owner provisioning until rollover is implemented. |

Permission-map presence is not proof of a successful DAX read or demo. Missing
monthly policy must name the owner setup action rather than widening the worker.


Dated prerequisite update,2026-10-21 (UTC October22): model connection=fixed identity now VERIFIED for both fixture and billing. ShareableCloud IDs2f322058-f720-40a0-bd1e-d174b8e7f5da and5099b9ff-1f27-488c-98c5-01c030dc4f3c; existing read-only investigator ServicePrincipal, SSO None, encrypted. Earlier blocked entry above remains historical. Current-month policy already verified; live value authorization still requires the recorded reruns. See ../runs/round-twenty-fixed-identity-controls.json.
