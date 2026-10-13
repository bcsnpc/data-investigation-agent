# Part B path-verification admission — 2026-10-13

Both plans are **not admissible with the currently installed production
verification adapter**. No verification request was sent, and no existing
profile was relabelled as end-to-end verification. The exact retained target
IDs, metadata hashes and native scope declarations are in
[the offline plans](round-nineteen-b-path-verification-plans.json).

## Filtered fixture visual

The retained `Six active predicates` page contains a Handled Quantity card
with six page predicates: warehouse_id 1, product_id 1, movement_type RECEIPT,
event_day 2026-09-15, Locations.warehouse_name North and Items.product_name
Component 1. This is a concrete filtered target. Its card title says
“unfiltered”, but the page predicates are present in the definition and must
apply. Its title is not scope evidence. A fresh inventory must also account
for any report, visual and slicer declarations before admission.

`BindingVerificationRoute.compile()` accepts a `BINDING_SAMPLE` containing
one key range or date window. It passes that sample to `compile_quantity()`;
it does not receive the report's active restriction inventory. Its successful
execution explicitly labels the scope `BINDING_SAMPLE`. The graph attachment
resolver recompiles these same statements and checks their sealed receipts.
That proves the bounded column sample, not preservation of all six report
predicates through every layer. Adding extra report predicates to the sample
is rejected before any query, as the new regression test confirms.

The installed graph binding resolver also supports only exact column edges.
It cannot verify the visual-to-measure and measure-to-column hops. The generic
`verify_path()` callback interface does not supply a production compiler for
those hops. Fresh INFO metadata can establish DECLARED dependencies, but it
does not itself supply scope-bound value verification.

## Billing MRR

The retained `MRR All Plans` card uses:

```dax
CALCULATE(SUMX(FILTER(Subscriptions, Subscriptions[status] = "ACTIVE"), RELATED(Plans[monthly_price])), REMOVEFILTERS(Plans))
```

The native partitions name `gold.subscriptions` and `gold.plans`. The four
interpreter inputs contain two distinct **invoice** recipes; neither is an
observed MRR procedure hop. Both carry the explicit fixture-authoring-only
qualification. Interpreting these recipes cannot establish that an MRR stored
procedure exists or ran. Required evidence is a reader-observed deployed
definition and producer binding for those two Gold objects, followed by a
scope compiler that preserves the iterator, relationship lookup and
REMOVEFILTERS semantics. Equal output values cannot fill these gaps.

## Attestation and next action

Existing bounded column verification accepts the established attested,
distinct-serving-object contract and retains `SNAPSHOT_UNVERIFIED` where
query-bound versions are absent. No stronger four-field identity requirement
was added. The obstacles above concern dependency and scope coverage, not a
new attestation policy.

After the fresh scanner result, repin these plans to the new graph and report
which metadata gaps closed. Keep the production verification gaps explicit
unless an actual compiled and sealed read path addresses them. The eighteen
retained lower-edge profiles remain useful evidence for their own bounded
scope only. No new identity, permission, credential or limit is requested by
these plans.
