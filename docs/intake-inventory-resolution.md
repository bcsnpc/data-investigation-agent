# Intake inventory resolution and procedure wiring

2026-10-02. PR B, based on merged #303 (`e1828a7`).

## Translation and deterministic resolution

The model extracts an exact ticket span for a stated selection; it cannot emit
an EVIDENCE resolution. A consumer lookup reads conserved inventories extracted
by the adapter from the pinned model context. Exactly one ACTIVE declaration
carrying that literal resolves the column as EVIDENCE with its entry ID. Zero
matches, conditional-only matches and multiple matching declarations refuse as
Target ambiguity, with candidates retained. The same declaration occurring in
several visual contexts is counted once; different declarations on the same
column remain distinct. No fuzzy value matching, semantic inference or tolerance
is added.

An explicitly named catalog column yields STATED with its exact ticket span.
The lookup still runs and records STATED_ACTIVE_MATCH or STATED_NO_ACTIVE_MATCH.
The latter is not permission to reproduce: the adapter independently requires a
unique applicable visual context and ACTIVE restriction for that column. Missing
or ambiguous visual context remains a named refusal. The lookup does not make
an unfamiliar form supported or turn a CONDITIONAL bookmark into an active one.

Dated clarification to #303's candidate terminology: REFUSED candidates are
opaque declaration/column-pair identities, with both entry and column listed in
the lookup audit. The earlier description called these column IDs. Pair identity
is necessary to preserve the user's exactly-one-entry rule when two different
ACTIVE declarations carry the same value on the same column. The existing closed
contract already accepts opaque IDs; its shape and refusal cardinality do not
change. The original #303 description is retained.

## Procedure and visible refusal

Preview and procedure_scope forward the saved target and NUMBER/EMPTY/UNSPECIFIED
figure server-side. The adapter consumes that contract, rechecks its provenance
against retained inventories, and selects a unique visual. The old scope selector
is explicitly refused, not used as a fallback. Genuine target ambiguity remains
unavailability, not a guessed target.

UNSPECIFIED reaches the no-reported-figure result before target extraction or
inventory validation. The business output now explicitly says that the number
shown was not supplied; the technical output retains the exact reason. Tests use
the real adapter path and ensure malformed target data cannot replace that
reason. Existing precision/EMPTY/BLANK tests and server-only forwarding remain;
this change neither invents nor widens tolerance.

## #299 sweep audit

The other audited refusal sites are probe absence/receipt, typed quantity,
reported figure/precision, attestation coverage, missing active set, source
partition type, completed presentation/definition judgment, successful job
completion, commit content, freshness/baseline/snapshot, bindings/retrieval hints,
and observation construction. No additional demonstrated refusal in these sites
has currently available resolving evidence that this inventory lookup can use.
The declaration-value ambiguity was the evidenced gap. A missing partition type,
unknown timestamp alignment or missing successful job record cannot be supplied
by page-filter evidence. Those refusals remain. This is a scoped code audit,
not a claim that every estate ambiguity is resolvable or that all future gaps
are absent.

## Context cost and validation

The twelve immutable intake fixtures retain byte-identical context payloads,
1,050-1,952 characters; Family D remains 1,103/1,103. Single-model fixtures retain
one model and two columns; the two-model ambiguity fixture retains two models
and four columns. New instructions add 655 characters. The single-model wire
schema grows 1,661 to 2,463 characters; the two-model schema grows 1,715 to 2,531.
Inventory lookup happens locally after translation and adds no inventory to the
model request. Existing investigation-planner goldens retain 28 directory entries
and 11 SQL objects; no investigation payload-shaping code is changed. Coverage
and exact intake-context tests would fail on catalog loss.

Sixteen new tests cover one/zero/multiple/conditional matches, duplicate entry
identity, same-column ambiguity, named-column no-match auditing, hostile value
provenance, adapter replay, visual ambiguity, visible no-figure attribution,
review forwarding, model extraction and context coverage. Earlier local test
attempts exposed synthetic fixture setup mistakes; failed logs remain local.
Full regression and final-head CI results are recorded on the implementation PR.

README and current status updated. Engine bytes invalidate prior freezes.
No investigation run, live model/cloud request, ledger row, fixture, approval,
permission or budget change. Family D runs and historical evidence remain
unchanged; draft #297 remains open. The next runs require a separate prompt.


## Dated correction: report scope (2026-10-02, America/Chicago)

The #304 account above resolved selections against model-wide inventories. That
was wrong in scope: a declaration on another report cannot establish the context
of a figure on the report named by the ticket. Inventory Health e1b8e1 contains
zero retained predicate nodes; the ACTIVE North predicate belongs to Declared
predicate fixture 20261001. Matching the same column/value across those reports
is not report binding. Earlier claims of working evidence resolution describe
an implemented lookup, not valid report-scoped resolution. Those claims and
all original runs are preserved; this correction does not regrade them.

The new consumer contract requires exact, provenance-backed report binding and
per-report declaration conservation, and distinguishes declared EVIDENCE from
receipt-backed OBSERVED value presence. Adapter wiring, general cell addressing,
quote handling and the three live reruns are pending in that order. No live
verification or replacement result is claimed. See [report-scoping contract](report-scoping-contract.md).
