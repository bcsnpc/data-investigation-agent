# Structured context and query recovery

Tracking: [#199](https://github.com/bcsnpc/data-investigation-agent/issues/199).
This milestone follows [quality engineering](investigation-quality-engineering.md).
Current delivery claims belong in [delivery status](current-delivery-status.md).

## Problem and implementation

The prior live run found transformation text but could not recover from a missing
source-schema prerequisite. Large asset responses became opaque JSON excerpts,
discarding navigable identities, while query rejection named no recovery targets.

Dynamic strategy v4 keeps structured asset metadata when reducing large lookups.
It bounds adjacent edges, omits verbose history, and replaces long definition text
with an explicitly partial preview plus access through the existing content/find
tools. Earlier source schemas retain up to 40 named columns and explicit truncation;
definition search matches survive later context compaction. This is metadata
navigation, not proof that a proposed mapping or interpretation is correct.

After ordinary parser and scope admission, a proposed SQL query missing retrieved
schemas returns the exact missing discovered object identities. These recovery
targets receive priority in the provider's bounded handle dictionary. The planner
can retrieve them and retry; the runtime does not execute rejected queries or grant
permissions. No domain names, expected values or scenario-specific path are added.

The user authorized input/output increases when needed. Dynamic workspace runs now
permit 384,000 cumulative input characters: at most 12 calls of 32,000 characters.
These are character reservations, not measured input tokens. The planner-call,
per-call payload, SQL/cloud-call and legacy-engine limits remain unchanged.
Output stays at 1,500 tokens per response; no output-truncation evidence justified
raising that cap. A temporary local daily allowance covers two bounded quality
trials; it does not reset prior usage or change SQL compute/quota settings.

## Validation

All 916 local regression tests passed. Coverage includes missing-schema rejection
without execution, explicit lookup recovery followed by one source read, recovery
target retention in a large catalog, partial large-definition projection, and input
budget boundary rejection. Ten dynamic browser checks passed with an injected
native transport and no browser errors; the rendered screenshot was inspected.

A stored-metadata probe reduced a notebook asset response from 23,744 to 2,850
characters with its identity preserved and completeness marked PARTIAL. No live
SQL, DAX or LLM call was involved in that probe.

## Live evidence

Known-domain trial results will be recorded here after completion. No new engine
freeze or unfamiliar-domain acceptance is claimed by local tests or metadata size
measurements.
