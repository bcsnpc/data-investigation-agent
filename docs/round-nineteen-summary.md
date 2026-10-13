# Round Nineteen ? final results

2026-10-13. Draft **#425**, based on draft #424; neither merged. The graph foundation is implemented, but the round's end-to-end success targets are **not earned**. Prior freezes are invalid.

## Foundation and reader

Part 0's fresh cloud verification stopped after one verification read/four physical requests: `Target types lack reader-owned guarded surface evidence`. Its original capture is retained. The offline correction uses the validated service principal identity rather than the old user label. The sole Part D retry also stopped before any request: `VERIFICATION_PREWARM_SOURCE_NOT_DECLARED`. The operator had selected an application source outside the 18-proposal batch. The guard correctly refused it; preflight had checked shape but missed that cross-reference. The offline admission check now catches that mistake before publication; original inputs are unchanged and no further retry ran. Both failures are sealed. **Cloud demo and exact verification replay NOT_RUN.**

The dedicated secretless investigator authenticates for all four required audience/tenant pairs. Scoped workspace Viewer/model Read+Build and database read roles are recorded, with SQL authentication left enabled when the owner was made Entra administrator. Authentication is not whole-estate readiness. Both workspace listings succeeded, but all **67 definition owners remain unavailable**: 11 HTTP401, 19 HTTP404, 36 unsupported kinds and one missing from the visible listing. No write grant or publisher substitution was used. Old user-cache secrets remain until replacement end-to-end proof exists.

Primary PostgreSQL migration is exact: **23,568 rows/20 tables**, source/target hashes equal; the production case writer participates in the transaction. Historical claim cohorts remain separate because two runtime references are absent from that primary catalog. Per-job SQLite elimination is therefore incomplete. See [migration evidence](claim-catalog-migration-plan.md).

Platform account keys are disabled; owner and worker identity PUT/GET checks passed. Screenshot retention is enforced for three configured prefixes at 30 days. The approved owner Blob Data Contributor grant applies only to `diaplatformd5dd7d65`.

## Graph and coverage

Retained definitions, original observation times and content hashes are stored privately by hash; PostgreSQL holds versioned graph records. Compact APIs enforce the admitted object slice. Change detection merges changed owners with the retained catalog, updates dependent partitions atomically and retains historical versions. An unavailable reader preserves prior data with an explicit health gap.

Node types (fixture/billing): columns 567/212; tables 130/35; measures 39/6; boundaries 127/34; query steps 123/56; reports 11/1; pages 18/3; visuals 64/7; slicers 12/0; filters 26/2; relationships 8/10; interactions 8/0; models 6/1; notebooks 6/0; pipelines 2/3; Copy activities 1/7; views 0/7; sources 15/4.

Fixture **1,163 nodes/1,696 edges**: 1,568 DECLARED, 128 UNKNOWN. Billing **388/759**: 725 DECLARED, 34 UNKNOWN. Edge kinds (fixture/billing): CONTAINS 970/341; COMPUTED_FROM 482/205; DERIVED_IN_STEP 176/189; FILTERED_BY 44/2; JOINED_VIA 16/22; INTERACTS_WITH 8/0. Full types, reasons and latest refresh dispositions: [coverage](round-nineteen-graph-coverage-final.json).

All **83 retained visual/slicer starts** return bounded paths with named stops, not complete source lineage. Missing engine-produced DAX dependencies block all six requested measure-path variants. INFO.CALCDEPENDENCY requires model Write; supported definition APIs also document write requirements. Reader permissions were not broadened. Runtime query/refresh/Delta-history collectors and some object forms remain unimplemented. Authoring-only procedure text is explicitly not deployment evidence.

Two actual interpreter calls produced seven INFERRED proposals, then `GRAPH_INTERPRETER_SPAN_DIFFERS`; the next input was not attempted. Exact captures survive, and no proposal was published or promoted. An earlier capture-directory failure before dispatch is separately retained. **Zero complete filtered or procedure paths VERIFIED**; the required two end-to-end successes remain unmet.

## Change detection, archive and cost

Real retained definitions passed the offline change/revert test: September 14 ? September 15 ? September 14, original as-of content/provenance preserved, unrelated model history unchanged. The live controlled edit was **not run**: the actual graph reader received 404 for its baseline. Changing it using a different reader would not test the required path. [Exact test evidence](round-nineteen-retained-definition-change.md).

The six-hour schedule is **applied**, provisioning Succeeded, with declared configuration and template read back. The first timed execution has not occurred; the manual scan above is the live evidence. The design uses the existing .5-vCPU/1-GiB job, maximum600seconds, zero retries and shared round/rolling guards. Gross compute bound **$1.08/30days**, without assuming the subscription's shared free allowance is unused; conservative platform allocation **$19.87/month**, conditional on the previously recorded PostgreSQL free eligibility. [Microsoft job billing](https://learn.microsoft.com/en-us/azure/container-apps/billing).

Archive remains **partial**: 1,308 original paths, 6,818,129,226 source bytes, 658,565,431 stored bytes, 294 controls; all readbacks hash-verified. Estimated archive cost is $0.05730 download + $0.00294 controls + $0.000652/month storage. Five failed staged uploads remain recorded. Deletion was blocked by policy; originals remain and an owner cleanup script is prepared. Opening disk12.65GB; closing disk11.13GB. No net disk gain is claimed; originals and new captures remain. [Checkpoint04](round-nineteen-archive-progress-04.json).

Closing counters08:47UTC: **36/1,500 physical**, rolling **312/3,000**, reserve **95 untouched**; two actual model calls **$0.088833**, shared **$108.046558**, ceiling **$132.957725** with protected **$10**. No open reservations or active live batch. Tested image passed eight cloud shards; latest Validation and guardrail CI passed after replacing an obsolete test double (201 claim tests pass). No new investigation/model admissions. The unfinished work is explicit: fresh reader collection, engine dependency coverage, verified paths, successful demo/replay, isolated claim migration, complete archive/privacy audit and projected cloud support. This round does not establish general estate readiness.


Dated closing-CI correction, 2026-10-13: workflow 38372381714 on 30cb27e replayed inferred 15/15 but archived 7/15. Eight archived cases stopped before events because the current replay harness expected `metadata_config.validate_config`; their historical engine validates inline in `load_config`. Fix c4602de preserves that original validator and imported aliases, adapting only lexical path joining during replay. Ten portability regressions pass, including original validation refusing invalid configuration. No tape, expectation or historical engine bytes changed; zero estate/model calls. The full thirty-case hosted rerun is pending.
