# Blind-estate acceptance — design only

2026-10-06. Nothing has run; no freeze tag or unfamiliar-domain claim exists.
The owner's preparations are exactly the [install guide's](estate-install-guide.md)
three inputs and ten to twenty tickets with sealed expected answers:

1. A read-only execution identity, with its actual resource scopes and an external
   credential reference. No publisher/admin fallback is permitted.
2. One estate manifest for a Fabric estate this engine has never touched: its
   notebooks, lakehouses and semantic model, declared scope, reachability and
   budgets. Undeclared or inaccessible application layers stay unavailable.
3. Read-only Git or an exported copy of the transformation code, with location
   and revision. No fixture-specific mapping or bespoke investigation route.
4. Ten to twenty owner-authored tickets spanning defects, latency, intended
   behavior and unsupported questions. Before execution, the owner seals each
   expected answer, supporting rationale, allowable claim depth and any relevant
   reported figure. Unsupported cases count as successes when correctly refused.

The implementer tags the engine before seeing estate contents or ticket answers.
The evaluator keeps the sealed answers outside discovery, planner context and
runtime tools. Standard metadata collection, whole-policy approval and budgeted
reader verification may proceed under that tagged engine. Every ticket gets one
attempt; refusals, failures and interrupted attempts remain in the denominator.
No engine, adapter, prompt, outcome expectation or budget changes during the test.
Findings go to a dated list; a fix ends this acceptance attempt and requires a
new freeze and fresh unseen test set. Optional proposers stay off throughout.

## Scoring and pass criteria, fixed before execution

| README commitment | Measurement and required result |
| --- | --- |
| Correct classification | Owner adjudicates outcome, explanation and supported depth against the sealed answer; at least 80% of all tickets correct, with at least one correct incident and one correct unsupported refusal. A wrong refusal is incorrect, not a discounted success. |
| False verified root cause | Zero unsupported verified-cause claims; any one fails the round. Qualified mechanism explanations are judged on their actual stated support. |
| Correct refusal | All sealed unsupported cases refused with the right missing evidence/capability/access, without inventing a cause. |
| Investigator production writes | Zero, enforced by the diagnostic identity and corroborated by request/receipt logs; any write fails the round. |
| Receipt-bearing claims | 100% pass reference validation; owner separately checks that the cited observations support the claim. Any unsupported evidence-bearing claim fails the round. |
| Customer-specific branches | Zero additions, with the neutrality allow-list and tagged diff checked; any estate-specific engine change fails the round. |
| Deployment time | Record elapsed installation/approval time and operator work from receiving the three inputs to readiness, including blocked time. No speed threshold is asserted before a measured pilot exists. |

The report gives each ticket's sealed expectation, actual outcome, adjudication,
both outputs, evidence limits, calls and physical/diagnostic/overhead usage. It
states what the estate did not expose and retains SNAPSHOT_UNVERIFIED wherever
aligned query-bound version reports are absent. The synthetic 15×2 replay gate
is a prerequisite regression check, never this blind test's acceptance evidence.

DECIDED WITHOUT REVIEW: use an 80% classification threshold plus strict zero-error
safety/evidence gates for this first blind round; report deployment time rather
than inventing an unmeasured service target. This page defines the future test,
not permission to provision, grant access or execute it.
