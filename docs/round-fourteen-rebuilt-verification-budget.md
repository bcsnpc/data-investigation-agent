# Rebuilt verification stopped at its cap

2026-10-11. Current context6b9b2beb-bde4-498b-a955-94b3a482aac5, hash64038644876ed3decee626f3fd57ceaed7984aab90e8205547da1e7de6daefc2, whole config435d5b1bd64c5bdaaf95935c8f98db122e77444e5a735cd1348cbbb7a878601b. No metadata recollection, scope, identity or credential change.

{
  "experiment": "ROUND_FOURTEEN_REBUILT_FRESH_VERIFICATION_CLOSED",
  "recorded_at": "2026-10-11T13:20:46.421540+00:00",
  "status": "HELD",
  "verification_reads": 35,
  "verification_cap": 35,
  "admitted_by_kind": {
    "METADATA": 4,
    "TARGET": 16,
    "SOURCE": 15
  },
  "physical_requests": 83,
  "verification_physical_requests": 81,
  "controls": 2,
  "diagnostic_reads": 0,
  "model_calls": 0,
  "pending_reservations": 0,
  "partial_verifications": {
    "VERIFIED": 15,
    "UNVERIFIED": 1
  },
  "profile_publication": "NOT_PUBLISHED: existing publisher requires COMPLETED pass and exact replay; original empty profile and older witnesses untouched.",
  "cap_raised": false,
  "physical_estimate": 82,
  "estimate_difference": "+1: two prewarm control attempts instead of one estimated.",
  "pot_before": 2294,
  "pot_after": 2377,
  "pot_cap": 4000,
  "restoration_reserve": 95,
  "rolling_after": 1227,
  "rolling_cap": 3000,
  "capture_sha256": "04c8e71ad2f2800f8f9496705a8e8c2f72d7d12f426759ef774fea882e26bc13",
  "artifact": ".local\\round-fourteen\\rebuilt-agent-fresh-verification\\round-fourteen-current-context-reader-20261011T125722-portable",
  "replay": "RUNNING_OFFLINE",
  "next": "Rebuilt ordinary runs deferred pending qualified current profile; continue independent semantic-only billing section. No replacement or cap refill."
}

The capture preserves15 VERIFIED sampled bindings and1 UNVERIFIED entry; none has been promoted from this incomplete pass. Its HELD result is not a qualification pass. The next source probe was refused before its physical requests. The default cap was2per16bindings plus3metadata, but actual metadata admissions were 4. This is an evidenced budget-sizing gap, not permission to silently increase it. No claims of query-bound snapshot alignment: SNAPSHOT_UNVERIFIED remains.

Rebuilt investigation slots remain unattempted pending qualification. Billing is independently configured semantic-only and can continue without these inferred witnesses. The final round map must name the rebuilt slots that did not run.

Appended closure, 2026-10-11: exact offline replay stopped with `TAPE_EVENT_DIFFERS:FINAL:CLOCK`, zero estate reads and zero model calls. The earlier RUNNING_OFFLINE status above is historical. No matcher was relaxed and no partial profile was promoted. The saved budget refusal and all 83 physical requests remain recorded.
