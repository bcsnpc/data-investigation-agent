# Round Fifteen - retained readiness wording correction

Dated 2026-10-12T04:33:09.770477+00:00, 2026-10-11 Central. This is a read-only local evidence check, with zero estate requests and zero model calls. The frozen `docs/round-fifteen-readiness-restored-fixture.json` receipt from `cd9ac62` remains unchanged.

Its generic wrapper interpretation copied the billing wording: "Retained re-assessment under current source and restored PIPELINE approval. Same actual PARTIAL collection; missing onboarding stages remain missing."

The fixture command used its original retained Round Fourteen approval, not the newly restored billing approval. Its exact CLI result is `BLOCKED / NOT_SCORED`, with `ONBOARDING_EVIDENCE_INDEX_MISSING_OR_STALE` on all six stages. That result establishes a missing or stale onboarding evidence index; it does not itself establish collection status.

A separate local read now confirms the approved fixture context's retained `enterprise_scans.status` is `PARTIAL`. The row exactly matches the approval's context hash and configuration hash:

```json
{
  "id": "a6b6b130-e955-432d-8433-f2f7203302a2",
  "environment": "unknown-domain-v4",
  "hash": "e3cce421b4b694b005d9643c40dd0c66035e7a35cf0b3af0495ae655ff3e9dd5",
  "policy_hash": "bc6ef21fdf3a2fef1cdcebdda0b48dee83c19c2bce9db567ac07a87689dbd172",
  "status": "PARTIAL",
  "started": "2026-10-11T11:11:42.996299+00:00"
}
```

The context body's JSON contains no top-level `status` field. `PARTIAL` above is the explicit persisted scan-row status, not inferred from that absence, not copied from billing, and not a promotion or demotion. This check does not create an onboarding index or decide which six-stage receipts the fixture can supply. Therefore the generic phrase "PARTIAL collection" happens to agree with the explicit retained scan state, but "restored PIPELINE approval" applies to billing only. For the fixture, read it as **current-source assessment of the original retained PARTIAL context and approval**.

Read-only query: `SELECT id,environment,hash,policy_hash,status,started FROM enterprise_scans WHERE id=?` with context parameter `a6b6b130-e955-432d-8433-f2f7203302a2`. Catalog: `D:\data_investigation_agent\.local\unknown-domain-v4\catalog.sqlite`. Retained check receipt: `D:\dia-round-eleven-links\.local\round-fifteen\retained-fixture-context-status.json`; SHA-256 `b6c3a5f9bdced320380db8789480b3eeebec23af2434a12ef0bf1a570ea237a2`. Original approval SHA-256: `70cd46cb462b95ce843b3a9d139ef2138d377254353a509c22aa8904890667d8`. No activation, recollection, grant, code change or new run occurred.
