# Structural discovery for unfamiliar investigations

This extends the existing investigation loop; the frozen unknown-domain challenge
remains the main acceptance gate. It introduces no domain or metric registry.

## Automatic context

Discovery derives a bounded profile when publishing each discovered model context.
Declared relationship cardinalities suggest possible fact/bridge or dimension/entity
roles and candidate key columns. Typed columns identify possible dates and numeric
fields; measure identities and the existing dependency graph remain available.
Absent cardinality, business grain, additivity, intended dates/rate rules and SLAs
remain unknown. Roles are structural hypotheses, not verified business semantics.
Removed assets are excluded; truncation is explicit. Older immutable contexts are
not rewritten: the planner can derive the same profile from their retained metadata.

A scan does not execute data profiling queries. The investigator autonomously
chooses relevant bounded profiling reads during a ticket using the existing reader,
parser, call/time budgets and receipts. This avoids a separate background query
sweep or a mandatory checklist before useful investigation. Automatic background
data profiling for every discovered table is not delivered by this milestone.

## Tool capabilities and structural experiments

SQL and DAX adapters advertise their validator versions, actual syntax/function
sets, prerequisites, limits and structural experiment categories. Runtime adds local
eligibility from the approved reader/catalog configuration. Permission remains
unknown until dispatch and is always rechecked; metadata cannot grant access.
Existing typed candidates remain available alongside these query capabilities.
This is an initial capability contract for these adapters, not a universal connector
plugin protocol or proof that every advertised operation succeeds remotely.

The planner can test uniqueness/nulls, composite grain, functional-dependency
counterexamples, join fanout/unmatched keys, date ranges and observed freshness,
and native measure behavior by dimension/time. It chooses tests relevant to a live
hypothesis, records observations and revises hypotheses through the existing runtime.
It must distinguish source rows from joined rows, samples from whole-scope evidence,
and observed behavior from intended rules. Numeric data does not automatically
become a business measure, and absence of sampled counterexamples proves no global
constraint. No new execution path bypasses the SQL/DAX validators.

## Acceptance

Local tests verify inferred roles follow declared relationships rather than names,
missing metadata stays unknown, removed assets and large profiles are handled,
capability advertisements match validators, unavailable connectors do not claim
execution, and generic structural SQL stays bound to approved objects.

Known-domain ratio session `f2663513-4c17-4821-b757-12262fff2697` completed
with EXPECTED_BEHAVIOR after two planner calls and one native read. It evaluated
Inbound Fraction 0.733029092983457, Inbound Quantity 6,425 and Handled Quantity
8,765 together. Its claim explained the observed formula and explicitly left
whether the ratio was too high relative to business expectations unknown. This
is component/formula explanation, not proof that upstream inputs are correct.

Known-domain ambiguity session `4bcefca5-cedb-47ba-9008-7f46d1097b6a` stopped
NEEDS_INPUT / CLARIFICATION_REQUIRED after one planner call and no data reads.
It asked for the meaning/codebook of Q49 rather than inventing one. It did not
search all available source documentation; this is uncertainty handling, not
proof that no codebook exists. Neither trial proves autonomous structural data
profiling or passes the frozen unfamiliar-domain challenge.

The original daily policy remains in place, with all reservations retained. The
UTC allowance had reset naturally; these two trials needed no effective increase.
The 6,000-character discovered profile has a separate 2,500-character planner
projection prioritizing the selected measure's table, with explicit truncation.

Fresh-freeze status is tracked in the current delivery status and challenge record.

Validation before freeze: 928 regression tests passed after the final planner
projection change. Ten dynamic browser checks passed with injected transport
before that final metadata-size adjustment; no UI code changed. The rendered
screenshot was inspected. Live native evidence is recorded separately above.
