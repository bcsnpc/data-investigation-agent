# Synthesis wire schema and citation preflight

Date: 2026-10-03. Autonomous round A5. #332 merged with six green checks;
1,648 local regressions passed. Engine bytes change here, invalidating prior
freezes. No investigation run, estate read, model call or run ledger row.

## D: the request was wrong

The recorded provider rejection was:

> Invalid schema for function 'evidence_narrative': In context=('properties', 'business_output', 'properties', 'text'), " is not allowed in string literals for structured outputs (strict=true).

Error code: `invalid_function_parameters`. The deterministic business explanation
had been sent as an enum literal containing quoted visual names. Copying that
engine-owned prose through the model was unnecessary. The live wire now requests
only the technical mechanism and citations. Business composition remains local,
validated against the original supported assessment and its complete evidence.

The outbound synthesis schema has a conservative adapter-side offline preflight:
required fields, closed objects, supported types/keywords, property/depth limits
and the observed quote/newline enum restriction. This runs before reservation or
provider dispatch. [Microsoft's documented structured-output subset](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/structured-outputs#json-schema-support-and-limitations)
excludes type-specific bounds and patterns. Those constraints remain in the local
consumer schema and are enforced without truncation. The producer receives the
character allowance generated from that same consumer constant; the provider
schema itself does not guarantee length or completed prose. Invalid responses
still fail validation, with numeric provider usage retained. This finding is not
a claim that every existing intake/judge schema complies with that subset; those
other interfaces were not changed in this work item.

## H: dated correction to the proposed diagnosis

The original response invented `00aaaf06-761e-4960-abd5-9ddc-46837a333936`;
the actual receipt was `00aaaf06-761e-4960-abd5-9ca8aa450bae`. It combined
pieces of displayed identities. The preserved response fails its own wire enum.
**It was not a dangling reference supplied by the spine.** The offline audit
resolved every structured D/H spine reference against the original completed
observations. Original tapes and failed runs remain unchanged.

Every structured spine receipt reference is now resolved before a synthesis call,
against both the displayed evidence set and the original evidence store. A missing
reference names its ID and refuses locally. The provider sees short, enumerated
citation handles; only exact handles decode to original receipt IDs. An unknown
handle is rejected, never guessed or repaired. Correct ID syntax does not establish
semantic support for a claim; original-evidence validation remains authoritative.

## Context cost and tests

On the preserved D spine, provider payload characters change **10,427 → 8,365**;
17 evidence entries, two candidates and zero boundaries remain. H changes
**8,317 → 6,888**; 12 evidence entries, two candidates and zero boundaries remain.
These are synthesis views, without investigation directory/SQL-object directories.
No investigation planner payload changes. The removed business text remains in
local composition; shortening receipt handles does not remove evidence entries.

Seven hostile-producer/preflight tests cover dangling receipt/definition/read/
comparison references, missing or failed original evidence, invented response
citations, conserved view coverage, quoted enum refusal, unsupported schema
keywords, consumer-owned prose bounds, and preserved numeric usage on decode
failure. Existing synthesis contract, original-evidence and spine tests continue
to run offline. Full regression and all six CI results are recorded on the PR.
The unchanged nine-family estate measurement remains next; no live claim here.
