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
