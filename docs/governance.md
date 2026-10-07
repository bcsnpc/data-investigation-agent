# Investigation governance

These are implemented controls, not a claim of a compliance certification.
Installation declarations name an estate and identities; they never create
permissions. Explicit human scope decisions are recorded under CLAUDE.md §8.

| Control | How enforced | Where recorded | Who approves |
| --- | --- | --- | --- |
| Execution identities and scope | Manifest references exact readers; SQL permission guards and query-bound surface reports refuse unestablished access. Publisher/control identities do not substitute for readers. | Manifest identity inventory, original receipts, dated scope-change ledger entries | Human estate owner for every scope change |
| Approved discovery | Whole configuration/manifest approval hash and pinned context are checked before investigation. A stale approval refuses. | Context versions, approval records, configuration hashes | Human authorized operator |
| Read-only diagnosis | Compiler grammar, object allowlists, SQL guards and isolated execution profiles constrain reads. | Compiled requests, guard establishment/reuse receipts | Approved estate scope; engine validates every request |
| Bounded estate work | Rolling physical allowance and expiring credits bound actual requests; diagnostic caps exclude separately recorded guards. Restoration reserve is separate. | Usage reservations, physical receipts, run ledger | Human for bounded changes/credits |
| Data stays in the estate | Reads are bounded; providers receive bounded metadata/evidence. Business output rejects technical identifier forms. This is not an assurance that query results never contain sensitive data. | Provider request tapes and output validation | Estate owner selects scope and provider |
| Evidence and snapshot limits | Original observations validate conclusions. Missing query-bound versions produce SNAPSHOT_UNVERIFIED; equal values never establish currency by themselves. | Receipts, attestation, engine-rendered limits | Engine; optional metadata identity requires human scope approval |
| AI proposals | Closed consumer-owned schemas, explicit enum vocabularies and parser-governed compilation; verification qualifies proposed translations. Unsupported/ambiguous states refuse. | Provider bodies, proposal/verification ledgers, HOLD/NEEDS_INPUT | Engine admission; human reviews unresolved business meaning |
| Auditability | Sealed tapes retain requests/responses, usage, failures and engine revision. Existing tapes replay under their recorded version. Failed attempts are preserved. | Private tapes, receipts, append-only investigation ledger and delivery records | Changes to evidence hosting/secrets require §8 decision |
| Change control | Regression checks and sealed two-column acceptance replay gate; expectations change only with explicit evidence/reason. Model-step evals are still being built. | CI, acceptance files, neutrality list, PRs | Reviewed PR; no red-gate merge |
| Retention | Default indefinite. Explicit manifest periods plus `dia retain --apply` expire local tape files/ledger rows; recheck hashes before mutation and record removed hashes in a separate durable deletion audit. Unknown dates/sidecars stay. | Manifest retention policy and separate retention audit | Estate owner configures policy; operator explicitly applies |
| Redaction | The approved separate privacy-projected codec has synthetic capture/replay tests; keyed projection occurs before its durable write. Full installation capture remains unwired and refuses execution instead of falling back to raw tapes or database copies. Existing gate tapes stay exact. | Manifest recording class, projection policy/key binding, [capture audit](round-nine-redaction-contract-audit.md) | Human approved the separate class; estate owner declares exact columns and provisions an estate key in the existing secret store |
| Provider and region | Manifest pins provider/deployment/endpoint and may declare a region with supporting evidence. Recorder configuration carries those terms without credentials; absent region is explicitly UNDECLARED, historical tapes are UNRECORDED. Hostnames never establish region or residency. | Manifest `model.region`, tape bootstrap/configuration `_estate.provider_terms` | Estate owner selects installation/provider and verifies its deployment terms |

Retention is off by default for both archived fixtures and investigation ledgers.
For example, `python scripts/dia.py retain --manifest <estate.json> --root <local-root>
--tapes <local-root>/process-tapes --ledger <local-root>/ledger.jsonl
--audit <local-root>/retention-audit.jsonl` prints the plan without changing files.
Adding `--apply` performs it. The audit file is separate and is not itself expired
by this command. Retention cannot delete a remotely published acceptance bundle;
those immutable bundles have their own recorded evidence-hosting decision.
