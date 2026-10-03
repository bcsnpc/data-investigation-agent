# Quantity-bound DAX self-report composition

2026-10-02 America/Chicago (2026-10-03 UTC). PR B; PR A #316 merged
at 59043c7 after six green checks. Its corrected local suite passed 1,591 tests.
The initial 1,591-test run had one obsolete MISSING assertion, preserved in the
PR A record; PARTIAL with a missing required object still refuses binding.

## Bounded live probe set

No engine change during the set. Three physical REST/DAX requests, all HTTP 200,
using investigator-reader@skynwhy.com on the existing model and endpoint.
No automatic retries, grants, config/policy/cap changes or fixture mutation.
Ordinary rolling use 24 to 27 of 60. Zero model calls. One ledger row for the set.
A default-interpreter preflight failed for absent msal before any request; the
existing Fabric virtualenv executed the set. All statements, responses, request
IDs, response hashes, property names and control hashes are preserved in
[the probe record](runs/dax-composition-probes.json).

1. `EVALUATE FILTER(INFO.PROPERTIES(),[PropertyName]="ProviderName")`
   returned the native labels `[PropertyName]`, `[PropertyDescription]`,
   `[PropertyType]`, `[PropertyAccessType]`, `[IsRequired]`, `[Value]`.
   The ProviderName row's Value was `OLAP Server`.
2. Names-only SELECTCOLUMNS enumerated the exact property names, including
   `ProviderName` and `Catalog`. No other property values were requested.
3. The first scalar composition answered, so the set stopped. One EVALUATE
   returned `[quantity]`: 8765, `[surface_identity]`:
   investigator-reader@skynwhy.com, `[surface_engine]`: OLAP Server,
   `[surface_object]`: 3484a2bc-98c5-4cef-be5c-a6215484075e.

```dax
EVALUATE ROW(
 "quantity", 'Activity'[Handled Quantity],
 "surface_identity", USERPRINCIPALNAME(),
 "surface_engine", CONCATENATEX(SELECTCOLUMNS(
   FILTER(INFO.PROPERTIES(),[PropertyName]="ProviderName"),
   "ReportValue",[Value]),[ReportValue],""),
 "surface_object", CONCATENATEX(SELECTCOLUMNS(
   FILTER(INFO.PROPERTIES(),[PropertyName]="Catalog"),
   "ReportValue",[Value]),[ReportValue],"")
)
```

This directly establishes that the projected-rowset scalarisation answers on
this reader/model/endpoint. It does not establish why the previous MAXX form
returned null; no claim about that internal cause is made.

## Compiler wiring and refusal

One adapter function adds identity, engine and object columns to every quantity
probe: ordinary/filtered baselines, declared-context/cell reads and value-existence
reads. Existing table expressions use ADDCOLUMNS with the same demonstrated
scalarisation. The parser admits only these two bounded property expressions,
shared from the adapter; generic INFO access and secret-property substitutions
still fail closed. No default self-report value is substituted for a null.

Parsed constructor output columns are recorded independently of scalar text.
A requested self-report column absent from the compiled output refuses before
execution, receipt creation or metering. The new hostile test found the ordinary
baseline was metered before local admission; it now preflights before metering,
like declared and existence probes. No permission or required-field check weakens.

Five new tests cover shared compilation, missing each column with zero reads,
scalar-label impersonation, adapter bypass attempts and executed probe statements.
Existing declared adapter46, scoped16, graded13 and flexible39 tests pass.
Full local and exact-head six-check CI results are recorded on the PR.

Identity/engine/object answers may establish graded differences where both
quantity-bound reports support them. Workspace connection remains UNATTESTED;
snapshot identity remains SNAPSHOT_UNVERIFIED. This is one composition probe,
not a reproduction, cross-surface comparison or unfamiliar-domain acceptance.
Prior receipts and failed runs remain unchanged. All engine freezes invalidated.

Stop after PR B. Baseline memoisation/order/cap reporting (PR C), the scoped
inventory consumer and R1 output defects (PR D), and reruns remain pending.
The fixture change waits.

Dated accounting correction, 2026-10-02: the planning snapshot was 24/60,
but one existing reservation aged out before the executed set. Its actual
before/after control reads are **23 to 26 of 60**, with three initiated requests.
The ledger retains the original mistaken 24?27 summary and appends this correction;
no counter reset, refund or policy change occurred. The probe source commit is
59043c7. The evidence's engine_hash is explicitly a reconstructed Git-blob
manifest, not an observed runtime fingerprint; these operator API probes did
not enter the investigation engine. Approval-normalised config hash remains
19e2ef0b0b5cb6bfd8df38c5fded6c1eaac40718b3926248ac62c61abf0cf8b6.

Validation correction: the initial full suite completed 1,596 tests with 13 errors across legacy adapter doubles that mocked execution but not the newly earlier admission. Their DAX admission is now explicitly mocked; the independent lower-read harness still uses real SQL admission. Dedicated hostile tests exercise real DAX admission with zero-meter/zero-execution assertions. Failure logs remain in .local; final full-suite/CI results follow on the PR.
