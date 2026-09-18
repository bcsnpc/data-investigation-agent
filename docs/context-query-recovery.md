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

If SQL qualification fails and unqualified columns occur in multiple approved
source schemas, feedback names the columns and candidate table aliases. The
compiler never chooses an alias or silently rewrites an ambiguous query. Unknown
and out-of-scope objects are rejected before this feedback is constructed.
The prompt also states that asset search uses literal all-term matching, not OR.
Search can qualify an asset with its actual parent names, following bounded,
cycle-safe identity links. At least one term must match the asset's own name/type;
searching for a parent alone does not flood the results with all its children.

The user authorized input/output increases when needed. Dynamic workspace runs now
permit 384,000 cumulative input characters: at most 12 calls of 32,000 characters.
These are character reservations, not measured input tokens. The planner-call,
per-call payload, SQL/cloud-call and legacy-engine limits remain unchanged.
Output stays at 1,500 tokens per response; no output-truncation evidence justified
raising that cap. A temporary local daily allowance covers two bounded quality
trials; it does not reset prior usage or change SQL compute/quota settings.

## Validation

All 919 local regression tests passed on the final context/error changes. Coverage includes missing-schema rejection
without execution, explicit lookup recovery followed by one source read, recovery
target retention in a large catalog, partial large-definition projection, and input
budget boundary rejection. Ten dynamic browser checks passed with an injected
native transport and no browser errors; the rendered screenshot was inspected.

A stored-metadata probe reduced a notebook asset response from 23,744 to 2,850
characters with its identity preserved and completeness marked PARTIAL. No live
SQL, DAX or LLM call was involved in that probe.

## Live evidence

First known-domain run `51bd2b17-468b-465f-9927-91c0ebf502de` completed six
distinct lookups and one reader SQL query. It retrieved both relevant schemas,
searched the transformation definition, and queried the corresponding join. The
query returned valuation totals of 16,018 for issues and 41,025 for receipts.
These are observed source-query results, not proof of the intended valuation rule
or a reproduced Power BI value in this run.

Two subsequent queries repeated an ambiguous unqualified column and were rejected.
The tenth planner call failed with APIConnectionError. Final status was HELD /
PLANNER_FAILED / UNRESOLVED, with 183,072 reserved input characters and one cloud
call. The failed run and its reservations remain intact. This motivated specific
alias feedback; 31 focused tests passed after that correction.

Second run `e6ad340c-933f-4199-b18d-3c02b20aaa8a` ended HELD / TOOL_UNAVAILABLE
after five planner calls and one failed SQL attempt. The historical failed receipt
only retained SourceReadError. Flexible source receipts now retain validated
connection-attempt fields and allowlisted error categories, never exception text.
A separately budgeted operator retry returned SQL error 40615 at connection time.
Azure reported the database Online with useFreeLimit=true and exhaustion behavior
AutoPause. The current client IP was absent from its firewall allowlist.

The user approved one client-IP rule, `investigator-client-20260918`. After applying
it, reader receipt `13983c0d-7bcf-4c53-8afa-4f9815c63438` completed and returned
1,878 issued units and 5,783 received units. This operator retry restores access;
it is not an autonomous agent result. Database grants and free-limit settings were
not changed. [Microsoft documents error 40615 as an IP firewall rejection](https://learn.microsoft.com/en-us/azure/azure-sql/database/vnet-service-endpoint-rule-overview?view=azuresql#troubleshoot-errors-40914-and-40615).

A fresh post-firewall GPT-4.1 trial is running. A separate GPT-5.4 evaluation
deployment, investigator-quality-54 (2026-03-05, GlobalStandard capacity 10), is
prepared for a same-engine comparison. No production default changed. Its
secret-free settings are in `infra/llm/quality-gpt54.json`.
[GPT-5.4 supports structured tool calls](https://developers.openai.com/api/docs/models/gpt-5.4).
[Reasoning uses the output-token budget too](https://developers.openai.com/api/docs/guides/reasoning#controlling-costs);
this comparison initially keeps the existing 1,500-token cap and does not request
additional reasoning effort. Model availability alone is not quality evidence.

No new engine freeze or unfamiliar-domain acceptance is claimed by local tests,
metadata size measurements or a successful source read.
