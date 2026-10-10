# Form integration notes — 2026-10-10

Implementation remains in progress; this is not a runnable form or a scored capability. The asymmetric text-gate evaluation stays frozen in a separate worktree while form work is developed here.

The live-list foundation has eleven passing offline tests. It obtains report/page names from an injected read-only transport, confines every request to configured workspace IDs, checks that a requested report is in the current live list, caches per service identity and estate scope, expires after five minutes by default, and permits manual refresh. A failed refresh never presents expired metadata as current. Cache results are defensive copies. Unknown report types stay visible as unsupported and cannot silently disappear or be opened. This foundation still needs the governed runtime transport and authenticated API/UI wiring.

The real reader probes served report and page lists. Live visual-definition retrieval returned EntityNotFound; it supplied no visual titles. Retained definitions remain available for approved investigation context, but cannot be labelled as a live title list. The optional target path must remain available without any elevation.

## Authoritative form contract

The form needs a closed, consumer-validated selection record, not more generated prose appended to the optional description. Keep report, page, target, comparison and entered figure with their original field pointers, input hash and the identities of the live list entries the user selected. Resolve native report/page/visual identities through the adapter's existing bindings into approved retained metadata. A newly listed report without approved context holds; do not borrow metadata from a similarly named report.

The engine must revalidate those selections at adoption. An optional description may contribute typed selections, keys and the question subject, but never overwrite selected report/page/target or comparison. Conflict is an explicit combined choice, retained before accepting an answer; absent authority cannot be replaced with the model's preference. An otherwise complete form starts through the existing preview, approved discovery, budgets and isolated readers. A form is not discovery approval.

For a matrix or chart, naming the visual is not necessarily naming a cell. A target is complete only when its address is established. If value/page evidence leaves differently scoped candidates, offer one click question containing the candidate addresses. Never choose another visual by an observed matching value. Preserve the wrong-cell and comparison-span regressions.

The entered value uses the existing reported-figure precision/EMPTY contract. Blank input is absence, EMPTY is an explicit reported state, and neither is zero. Do not generate tolerance. Description/field disagreement remains visible rather than silently erasing an explicit figure. The three sealed-oracle/text conflicts diagnosed in section 0 must remain findings in any form derivation/scoring.

The sixty-eight derived submissions must carry the unchanged oracle and source-record hashes. Only determined dropdown fields are filled; unknown or inapplicable fields remain absent. Original descriptions survive verbatim. Oracle fields are evaluator input only and never reach runtime resolution. Score dev and held-out separately, with correct holds distinct from harmful admission and from unanswered questions.

## Route and delivery constraints

The configured comparison choices and ordering are consumer-owned. The separate two-report route must either compare faithful quantities through a first shared layer or remain visibly coming soon and HOLD; it cannot substitute the one-report walk. No current two-report implementation is claimed.

The later Entra sign-in work must filter lists using each signed-in user's actual access. The configured reader's visible report names are sensitive and are not proof that every portal user is entitled to see them.

No billing rebuild. Its remaining runtime manifest, new discovery approval and collector verification follow the form work. Billing/logistics tester tickets require a fresh isolated session with neither defect lists nor engine/tape access. The stronger explicit prohibition on authoring one's own billing tickets takes precedence over the document's later conditional fallback.

## Continuation checkpoint ? 2026-10-10 UTC

The existing approved code-reader has now retrieved the original report's 13 definition parts. This supersedes the earlier statement that no live definition path was available; the diagnostic reader still cannot retrieve it. See `round-twelve-definition-access.md` for exact identity-specific results and accounting.

The first consumer-owned form binding port is implemented in `scripts/investigator/form_intake.py`, with twelve offline tests. It validates a closed selection envelope, confines a visual to the selected report/page, preserves the explicitly selected card rather than replacing it with a same-measure matrix, keeps an absent figure distinct from EMPTY and zero, and derives only the precision supplied by the user. An unresolved target produces one question batch; a keyed address still requires keys. The OTHER_REPORT route explicitly holds as coming soon. Description interpretation remains required when text is present: this port does not erase or silently accept conflicts. The binding is metadata only, expressly `execution_authorized: false`, and is not yet wired into the authenticated API/UI or lifecycle. No form-scoring/live completion claim is made.

### Fresh tester preparation

At the owner's explicit request, verified all 25 old source files against their preserved OWNER_AUTHORED copies before removal. Removed 18 ticket files, summary and six screenshots from `D:\dia-billing-tester`; removed the empty screenshot directory and retained the empty tickets directory. Its only files are README.md and tester-session-billing.md, byte-identical before/after. README SHA256 `da8d08a14a446de89b9e50af06d07225cb0adad3b0ee03e0a3563b71fe87fd51`; instructions SHA256 `e39a2628d84755ddae5ba103a4b14d91b5b26e4d0e4cb69e3a017a53fc8f608f`. The initial broad recursive cleanup command was blocked by automatic policy review before execution; the narrower explicit-file deletion succeeded. No fresh tester ticket was authored or run.

Twelve form-port tests and 64 existing visual-target, comparison-gate, neutral-platform and question-gate tests passed. The initial full regression ran2,754 tests and ended with15 errors: tape tests refused the uncommitted engine tree (`TAPE_UNCOMMITTED_ENGINE`). The original log is retained at `.local/round-twelve-form-full-regression.txt`. After committing the tested implementation, all four affected suites passed: process-tape33, transformation-service tape1, code-definition5 and Git-code3 (42 tests). All other initial full-suite tests passed. The subsequently added empty-versus-numeric ambiguity regression passed separately. Zero new model calls or estate requests in this continuation; last recorded pot 1,142/1,500, reserve95 and rolling allowance3,000 unchanged. No investigation or ledger row for file cleanup/offline tests. Prior freeze invalid; #423 stays draft.

The final keyed-address check uses the existing NUMBER clarification field, with CELL_KEYS_UNRESOLVED as its reason, rather than inventing a new clarification field. Twelve final form-port tests pass. This remains a metadata-binding port, not an API/UI or investigation admission.
# Form API/UI implementation checkpoint — 2026-10-10 UTC

The closed form contract now reaches durable tickets, authenticated API and UI,
and the existing preview/start/findings lifecycle. Selected identifiers carry
recomputable USER_SUPPLIED_FORM authority; they are not fabricated text quotes.
The input document labels field provenance and preserves the description.
The legacy authority hash remains unchanged for legacy tickets.

Live report/page lists use the existing reader in an isolated, metered worker,
with the five-minute cache and explicit refresh. Exact native identifiers bind
live entries to approved context. Unbound entries remain visible with a reason;
names never substitute for identifiers. List requests are CONTROL_METADATA,
charged physically against the existing rolling/round budget, not diagnostic
investigation reads. A host without that transport explicitly labels its list
as retained approved context. No new identity or permission is taken.

The UI retains typed grouped-cell keys and EMPTY versus zero. Another report
holds as coming soon. Business meaning records a handoff to a configured owner.
Missing choices use the existing clarification lifecycle. Description conflicts
currently hold explicitly; the required one-click conflict resolution remains
incomplete. Model-only and comparator-free tickets also need evaluation against
the actual form coverage; no target or comparison will be invented for them.

DECIDED WITHOUT REVIEW: selected IDs are validated against the approved context
on submission; a second unconditional page-list HTTP call is not required on
every submit. Rejected alternative: repeat metadata requests on every submit,
which couples admission/replay to an unrelated cache state. List retrieval is
metered and recorded when performed, stale catalog authority refuses, and value
probes still require the existing surface attestation.

Validation: 182 focused tests passed, then 66 focused tests after tape-operation
registration and UI reset refinements. Both JavaScript files pass node --check.
This is not a browser completion, form accuracy or live-investigation claim.
Full regression and the 68-form scoring remain pending. Zero new estate/model
requests at this checkpoint; last round pot 1,142/1,500, restoration reserve95,
rolling allowance3,000 and diagnostic cap12 unchanged. Prior freeze invalid;
draft #423 remains draft. No oracle, golden, acceptance expectation or billing
ticket was edited.
