# Ten synthesis readability reviews

These are exact model-written mechanisms from the sealed inferred-column tapes. The checked boundary facts are supplied separately; they are not model prose. Human grades were supplied on 2026-10-06 by Claude, independent reviewer; approved by Chaitu.

For each item, record three booleans: `names_layer_by_role`, `one_mechanism`, `no_hedge_twice`, plus the human grader in [the structured review](synthesis-human-review.json). These flags assess readability, not causal truth.

## family-A

Between L2 (REFINED) and L1 (SERVING), the retained definition shows a left join on product_id, then a derived value column is added. If several rate rows match one movement row, that join can repeat movement rows while the carried additive quantity stays on each repeated row. Summing after that step can therefore produce a larger total in L1 (SERVING) than in L2 (REFINED). The checked comparison also shows L1 (SERVING) matching L0 (SEMANTIC), so that carried total is preserved into L0 (SEMANTIC).

Allowed roles: L0 (SEMANTIC), L1 (SERVING), L2 (REFINED).

- Checked input L1 (SERVING): 8,765; output L0 (SEMANTIC): 8,765; values equal: True.
- Checked input L2 (REFINED): 7,661; output L1 (SERVING): 8,765; values equal: False.

Human flags: names_layer_by_role=true, one_mechanism=true, no_hedge_twice=false. Reviewer note: hedged twice: 'can repeat' and 'can therefore produce'

## family-B

The recorded operation reaches the Activity partition source label and finds no stable discovered asset binding for that label, so the engine compiles no quantity for the declared scope from that source.

Allowed roles: None declared.


Human flags: names_layer_by_role=true, one_mechanism=true, no_hedge_twice=true. Reviewer note: no roles declared on spine

## family-D

The investigation reproduced a warehouse-keyed cell under a recorded warehouse restriction for North, using the Handled Quantity definition and a within-layer read for that keyed cell. It also reproduced the same definition for the total and ungrouped cells, which yielded the broader visual-context value. The declared trace reaches the Activity measure and then continues through quantity-preserving steps, but the recorded chain does not carry the North warehouse restriction through the later entities, so the warehouse-keyed scope and the broader scope are both present while their translation into the declared source chain stops at the measure layer.

Allowed roles: None declared.


Human flags: names_layer_by_role=false, one_mechanism=false, no_hedge_twice=true. Reviewer note: 'measure layer' is not a role; reproduction thread and chain-stop thread mixed

## family-E

Between L2 (REFINED) and L1 (SERVING), the retained definition evidence records a left join from movements to rates on product_id, with matching rows allowed to multiply when uniqueness is not assumed. The traced quantity is carried as an unchanged additive column through that join, while a separate value column is derived from units and unit cost. Under that recorded operation, repeated matches at the join can duplicate movement rows and raise the carried total in L1 (SERVING) relative to L2 (REFINED).

Allowed roles: L0 (SEMANTIC), L1 (SERVING), L2 (REFINED).

- Checked input L1 (SERVING): 8,765; output L0 (SEMANTIC): 8,765; values equal: True.
- Checked input L2 (REFINED): 7,661; output L1 (SERVING): 8,765; values equal: False.

Human flags: names_layer_by_role=true, one_mechanism=true, no_hedge_twice=false. Reviewer note: hedged twice: 'allowed to multiply' and 'can duplicate'

## family-F

The displayed record contains a comparison between L1 (SERVING) and L0 (SEMANTIC), and it records equal quantity across that pair. No retained operation definition is displayed beyond that comparison.

Allowed roles: L0 (SEMANTIC), L1 (SERVING).

- Checked input L1 (SERVING): 57,043; output L0 (SEMANTIC): 57,043; values equal: True.

Human flags: names_layer_by_role=true, one_mechanism=true, no_hedge_twice=true.

## family-G

Between L2 (REFINED) and L1 (SERVING), the retained definition shows a left join on product_id from movements to rates, and the join notes that matching rows may multiply because uniqueness is not assumed. The units column is kept as an unchanged additive column through that step, so repeated matches can raise the carried total at L1 (SERVING). The checked comparison also shows L1 (SERVING) aligning with L0 (SEMANTIC), placing the divergence at that join step.

Allowed roles: L0 (SEMANTIC), L1 (SERVING), L2 (REFINED).

- Checked input L1 (SERVING): 8,765; output L0 (SEMANTIC): 8,765; values equal: True.
- Checked input L2 (REFINED): 7,661; output L1 (SERVING): 8,765; values equal: False.

Human flags: names_layer_by_role=true, one_mechanism=true, no_hedge_twice=false. Reviewer note: hedged twice: 'may multiply' and 'can raise'

## family-H

The recorded logic maps the measure through Activity and relies on a partition source label for that table. For the cited label, the retained record has no stable discovered asset binding, so the compilation step for a lower-layer quantity under the declared scope does not proceed.

Allowed roles: None declared.


Human flags: names_layer_by_role=false, one_mechanism=true, no_hedge_twice=true. Reviewer note: 'lower-layer' is a position word; no roles declared on spine

## family-I

A left join on product_id combines movement rows with rates before the result is written, and the retained definition states that matching rows may multiply because uniqueness is not assumed. When a movement row matches more than one rate row, the carried units total can rise between L2 (REFINED) and L1 (SERVING). The checked comparison then shows L1 (SERVING) passing the same total through to L0 (SEMANTIC).

Allowed roles: L0 (SEMANTIC), L1 (SERVING), L2 (REFINED).

- Checked input L1 (SERVING): 8,765; output L0 (SEMANTIC): 8,765; values equal: True.
- Checked input L2 (REFINED): 7,661; output L1 (SERVING): 8,765; values equal: False.

Human flags: names_layer_by_role=true, one_mechanism=true, no_hedge_twice=false. Reviewer note: hedged twice: 'may multiply' and 'can rise'

## reproduction-16

The recorded check compares several declared-context candidates for the same visual. One candidate applies saved declarations for day, movement type, product, and warehouse, and that candidate reproduces the reported figure. Broader candidates that omit the day declaration, or omit the saved declarations entirely, return different declared-context results while the undeclared-context result remains the larger value. This means the recorded operation narrows the visual through those saved declarations when reproducing the figure.

Allowed roles: None declared.


Human flags: names_layer_by_role=true, one_mechanism=true, no_hedge_twice=true. Reviewer note: no roles declared on spine

## reproduction-empty

The recorded check evaluated the card at three scopes. With the saved declared predicates captured for that cell, the measure read returned an empty result. When the date predicate was absent, the same measure read returned a value, and the broader undeclared scope also returned a value. This records that the empty card aligns with the combined warehouse, product, movement type, and date predicates attached to that visual state.

Allowed roles: None declared.


Human flags: names_layer_by_role=true, one_mechanism=true, no_hedge_twice=true. Reviewer note: no roles declared on spine
