# Calculation and change questions

`dia ask "How is Handled Quantity calculated?" --estate <config>` and
`investigator.explain_questions.ask(question, graph, ...)` are the two entry
points. The API function is suitable for a future MCP tool: the graph and
optional reader ports are bound by trusted deployment code, never supplied by
the question. No new UI, provider, model call, refresh or job trigger is involved.

The standalone configuration is explicit:

```json
{
  "version": "dia-graph-ask-v1",
  "estate": "fixture-example",
  "identity": "existing-graph-reader-channel",
  "allowed_objects": ["<admitted visual>", "<admitted measure>", "<admitted source>"],
  "subject": "<admitted visual>"
}
```

`subject` is optional; if supplied, it cannot override a conflicting named
target in the question. A unified runner configuration may carry the same
object under `explain`. `as_of`, `max_nodes`, `max_edges` and `max_bytes` are
optional bounds. The CLI uses only `configured_state()` and the existing
gateway. There is no SQLite, owner-login or CLI-credential fallback. An approved
configuration is not a grant: the graph gateway separately checks every named
object and the worker's ordinary PostgreSQL transport checks still apply.

Name matching uses only admitted nodes, with the essentials matcher's exact
names and available enrichment synonyms. Unknown subjects and real ties return
HELD with actual named candidates. Question text never becomes SQL, a path,
an endpoint, a git command or a module to load. Calculation walks use the new
public `GraphAPI.calculation_path` method and the existing history-aware bounded
adjacency reader. They never decode the entire historical graph.

For each calculation step the output carries the exact retained definition,
span/hash provenance, graph confidence, and any current explanation. Missing
enrichment is an explicit gap, not a generated paraphrase. The CLI reads
`EnrichmentStore.projection` only for admitted subjects and their current
definition hashes. Stale human text and recorded stubs are excluded; inferred
explanations, hidden-logic notes and graph links remain visibly INFERRED.
Human-confirmed text is a description, not proof of business correctness.

Optional existing values require a trusted code callback returning the existing
typed `Probe`. The engine re-runs ordinary surface attestation and retains all
qualifications, including the owner-approved tenant-only warning. A dictionary
claiming `attested: true` cannot supply a value. BLANK remains distinct from
zero and unavailable. The CLI does not introduce a new value query. Numerical
agreement is not inferred from a definition or explanation.

Change answers use observed metadata and explicit `HistoryPort` callbacks for
activity and git observations. Callbacks receive only the already admitted
subject; they must be implemented through approved reader/gateway ports. None
is installed implicitly. Missing permissions, unavailable sources and empty
results remain coverage gaps. Item metadata must include observation provenance
before a modified-by/time is reported. Ownership and the graph scanner's
collection time never become an actor or a modification time. An item-modified
observation is expressly weaker than identifying a particular formula change.
Events later than `as_of` are excluded. If no reason was recorded, both the
plain answer and evidence say that; no motive is inferred.

Every answer includes a timestamp, provenance, a technical pack and coverage
gaps. Incomplete paths are PARTIAL, not "as designed" or an assertion of business
correctness. These explain-type answers do not impersonate the investigator's
evidence-gated numerical verdicts.

Offline tests cover a normal calculation, a measure start, exact code citations,
admitted-path isolation, unauthorized neighbors, missing actors/reasons,
explicit activity/git observations, historical cutoffs, inferred link/prose
labels, stale/stub exclusions, typed attested BLANK and CLI dispatch. They prove
implementation behavior, not a new live activity-log permission or successful
live explanation. No live reads, model calls, scope changes or secrets were
used to build this part.
