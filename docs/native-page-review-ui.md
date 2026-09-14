# Native page selection in review UI

The authenticated context endpoint lists retained report pages from the current lineage scan.
The new-ticket form filters those choices by report name or ID and accepts an explicit order ID.
Page choices are retained metadata, not certification that every page filter is supported.
Changing the report clears the selected page. Both fields are optional for existing workflows.

Selected native_page and explicit order_id are saved on the ticket and included in its existing
idempotency hash. Page paths are restricted to native page paths, not filesystem locations.
The standard Azure planner launcher now supplies the configured metadata database; the planner
automatically enforces a saved ticket page and rejects a conflicting explicit override. Lab
planners without native metadata fail closed for a supplied native page.

The draft review displays native context status, page and runtime limitations. Missing order
context remains NEEDS_INPUT and approval is unavailable. The order value is explicit structured
input, not inferred from narrative. Filling a missing value requires a new ticket/plan under the
existing immutable ticket workflow.

This adds page selection and context display. It does not execute the report, evaluate general
filters or DAX, prove order existence or deploy the investigator. Existing bounded worker scope
and approval checks remain unchanged.

Validation: 327 script tests passed, including three new UI-context backend tests. Existing
planning tests also run with named page metadata. Browser verification uses an isolated local
fixture and deterministic planner; no cloud, SQL business queries, LLM or delivery calls.

Browser result: retained Order details selection persisted through ticket submission and draft
creation. Missing order context displayed NEEDS INPUT, the order clarification and no approval
control. The isolated fixture uses a supplied lineage graph and deterministic planner; browser
console errors were empty. Native page names are displayed instead of definition paths, and
required-but-missing order IDs are labelled Not specified.
