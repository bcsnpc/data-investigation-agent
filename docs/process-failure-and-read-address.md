# Process failure diagnostics, quantity addresses and approval-hash audit

Date: 2026-10-03, America/Chicago. Previous evidence:
[fixture-authored numeric runs](fixture-numeric-reproduction.md).
#328 merged as `57884e3` after all six checks passed. Original runs R4/R5,
receipts, outputs and ledger rows remain unchanged. No estate reads, provider
calls, fixture/configuration changes, credits or cap increases in this work.
Engine changes invalidate every prior freeze.

## The saved ValueError

Both R4 (`46826851…`) and R5 (`3469a7bb…`) reproduce this failure offline:

```text
ValueError: NO_COMPARABLE_PATH requires an established presentation baseline
process_outcomes.py:223
assessment_support.py:52 -> process_outcomes.validate
```

The four-read allowance was spent on three addressed visual quantities and a
shared undeclared-context quantity. The subsequent presentation-baseline probe
was not executed. Its original `PROBE_NOT_EXECUTED` receipt says that the
diagnostic cap stopped it. The original observations also retain three
NOT_COMPARABLE boundary markers. Neither run established a vertical baseline.
Nevertheless, the zero-verified-boundaries branch of `vertical()` produced
NO_COMPARABLE_PATH, whose contract requires an established baseline. The support
validator correctly refused that assessment. This was a procedure producer bug,
not a filtered-scope refusal and not a platform capability finding.

The offline reconstruction uses the pinned revision-5 context, original completed
reproduction/selection evidence, a read-only catalog connection, and a zero-remaining-
reads adapter. Network and execution transports are forbidden. An archived copy
of the merged pre-fix engine reproduces the same message and line for both runs.
This is a reconstruction of the failed decision/support validation, not a
byte-exact provider replay or a new investigation against the estate.

The small fix returns the existing NO_KNOWN_PATTERN capability-gap assessment
with the specific missing-baseline reason. It does not fabricate a baseline,
increase the cap, or weaken NO_COMPARABLE_PATH validation. A synthetic regression
validates that assessment against the unchanged consumer.

Rechecking the original observations under the new required-address contract
instead refuses their missing `read_address`. That is expected: these older
receipts were not backfilled. It is recorded separately, not offered as a
successful retrospective regrade. Fresh-producer tests establish the repaired
decision branch and address invariant together.

## Failures stay failures

The runtime now records PROCESS_FAILED with exception type, safe message,
module and line, and uses that stop category rather than TOOL_UNAVAILABLE.
Both refusal outputs explicitly say “Process failure” and carry the message,
even when completed reproduction cells still answer part of the ticket.
Technical output additionally renders type and location.

Exception locals, statements, responses and arbitrary interpolated exception
messages are never serialized. Exact source-authored literal exception messages
are retained; a message that may contain runtime/business data is explicitly
redacted, with `message_redacted=true`. Its type and failing location remain.
The synthetic walk test retains all three diagnostics; another test proves
runtime data does not leak. Redaction is a stated limitation, not silent loss.

The catch audit found one additional broad catch: the definition-judgment wrapper
turned any exception into an unavailable capability. Unexpected judgment failures
now propagate into the same process-failure recorder. Already-declared optional
timing enrichment failures remain nonblocking and visibly unavailable; they never
establish a timing finding. Physical-read exceptions remain charged and recorded
before propagation. Synthesis has its separate failure record. Existing explicit
target/path refusals and noncompleted read receipts remain refusals. This audit
does not claim every possible pre-walk setup exception has a process receipt.

## Address kinds and memoisation

Quantity reads now carry `read_address`:

```json
{"kind":"BASELINE","restrictions":[]}
```

or CELL with the complete existing cell address (including keyed values or TOTAL).
Baseline predicates are recorded as evaluated; the existing query compiler still
owns predicate validation. The compiled request seals the address; synthesis
checks it against the observation. Reproduction validation rejects an omitted
kind, a wrong baseline restriction set, or a cell differing from its definition.
The existing native `cell_address` remains alongside CELL for compatibility.

Memoisation and cost estimation use the same full address in addition to the
compiled quantity fingerprint and report binding. A baseline and an unrestricted
cell execute as two distinct probes even when their query text is identical.
Identical reads at an identical address still reuse the prior receipt/result with
the distinct zero-read refusal event. The permanent test exercises both the
identical-query/different-address case and missing-kind refusal.

Generic legacy/open-query receipts remain readable; the new required kind is
enforced for process quantity producers and reproduction consumption. No standing
historical migration or address inference was added.

## What the approval hash actually covers

`onboarding.py` defines:

```python
def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))

def digest(value):
    return hashlib.sha256(encoded(value).encode()).hexdigest()
```

`enterprise_discovery.py`, constructor:

```python
self.policy_hash=digest(config)
```

The projected context pins it separately:

```python
'discovery':{'policy_hash':self.policy_hash,'definition_available':ready}
db.execute('INSERT INTO model_contexts VALUES(?,?,?,?,?,?)',
    (context['id'],mid,context['scan_id'],encoded(context),digest(context),utc()))
```

Thus `19e2ef0b0b5cb6bfd8df38c5fded6c1eaac40718b3926248ac62c61abf0cf8b6`
is the canonical loaded approval configuration digest, not collected-content
identity. It correctly stayed unchanged when the report predicate changed.
The database already retains separate context integrity and source-content hashes:

| Context | Context-body hash |
| --- | --- |
| `3ae7607b…` | `d6f3841fc02368a066f2de2d2e8bb4c22579b02d3bce3a95e441996091d5784f` |
| `35461b1d…` | `8ac06cfb33b4a3a3b82e725f331c9af2885c436fdfc0dde7677b02c3e1379f0b` |

Two source hashes changed; this is not a content-hash collision. Context-body
integrity includes context/scan identities and is not a conclusion-time remote
freshness test. Roadmap gap: establish a separate canonical collected-parts/
predicates content identity for conclusion-time freshness, alongside approval
configuration identity and explicit recollection coverage. Never build that check
on `policy_hash`. No new hashing or freshness mechanism was implemented here.

## Independently derived numeric evidence

The retained fixture arithmetic chain is **360 → 270 → 107 → 6 → 2**:
360 seeded movements; the page's RECEIPT predicate retains 270; the ACTIVE saved
North slicer retains 107; the ACTIVE saved Component 1 slicer retains six; the
visual's 15 September predicate retains two. Their units are 4 and 12, yielding
16. Both saved slicer defaults are part of the active set. The derivation used
seeded rows and independent arithmetic, not the compiled reproduction query.
It shares documented transformation assumptions, so it is not independent
verification of business correctness or live source snapshots.

Empty and numeric reproduction have executed with fixture-authored, independently
derived figures and query-bound engine/identity/object reports on every probe.
Connection remains unattested and snapshots unverified. No real-user validation,
general reproduction capability or unfamiliar-domain acceptance is established.

## Validation and checkpoint

Regression validation and six-check merge evidence are recorded on the PR.
Offline diagnostic attempts are appended to the ledger with zero reads and calls;
original live records are unchanged. The next nine-family widening remains a
separate user-authorized task. No live run was attempted here.
