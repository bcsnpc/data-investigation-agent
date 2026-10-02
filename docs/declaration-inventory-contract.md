# Required neutral declaration inventory (PR A)

Date: 2026-10-01. Extends the #294 contract; adapter PR #295 remains unmerged.

The engine requires a declaration inventory, validates conservation against its
supplied discovery manifest, and refuses an incomplete inventory before any
quantity read. Exactly one disposition is required per discovered source;
every ACTIVE entry has nonempty restrictions, and the multiset of all active
entry restrictions must equal the complete active set. Missing, duplicate,
untraced and excluded-but-active restrictions are contract violations.
Any UNSUPPORTED entry blocks eligibility, including an apparently unrelated one.
Its refusal names the neutral unsupported-declaration form and stable declaration
IDs; original opaque native provenance stays available in evidence for audit.

Inventory source identity is a location plus SHA-256 content hash; the engine
derives the ID from a canonical encoding of those fields. It verifies supplied
IDs and canonicalizes inventory order, so input reordering cannot change identity.
The adapter must provide the declaration's actual source location and content hash.
The consumer schema owns enumerated disposition, volatility and assumption values.
There is no free-form qualification from an adapter. Native provenance is opaque.

The supplied manifest is not proof that extraction found every native declaration.
A neutral engine cannot parse an arbitrary platform to independently rediscover
omitted declarations. It detects an entry omitted from that manifest's disposition
inventory and every active-set inconsistency. PR B must prove native extraction
conservation and the unknown-kind UNSUPPORTED default; this PR does not certify
that adapter. The old adapter has no required inventory and now fails closed.

Saved defaults are ACTIVE, VIEWER_CHANGEABLE and SAVED_DEFAULT. The engine renders
the assumed default and unestablished current position in both outputs; a mismatch
explicitly names a moved saved-default selection. Conditional alternatives add an
invocation-not-established limit. Original inventory and provenance remain in the
retained definition observation; synthesis validates those originals and hands the
model only neutral declaration fields, never native provenance or source location.
Changing opaque strings leaves decisions, marker bytes and rendered qualifications
unchanged. Receipt hashes still identify the distinct original evidence records.
The mechanism remains model-written; qualifications and comparison facts are not.

Dated correction, 2026-10-01: #294's previous implementation/merge checkpoint
established intersection, attestation and reproduction roles, but its declaration
contract was insufficient to establish exhaustive disposition or qualify volatile
saved defaults. This required inventory extends it rather than working around it
inside #295. The original audit and status statements remain preserved.

Validation: all 1,386 final regression tests passed in 260.120 seconds, including
25 inventory tests and 34 reproduction tests. Six CI checks are tracked on PR A. Planner context shaping is unchanged;
11 exact golden directory/wire coverage tests pass (28 directory entries, 11 SQL objects, 5,543 projected characters). No investigation, offline
replay, estate read, provider call, fixture ticket, budget change or ledger row.
Engine bytes change, invalidating prior freezes. PR A ends after merge and report;
PR B (the adapter) and PR3 (runs) have not started.
