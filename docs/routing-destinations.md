# Destination-bound routing review

An ownership entry may optionally include a destination with an explicit GitHub repository
and email recipients. No real owner or recipient has been configured by this change.
The existing empty ownership policy remains unchanged.

Example using fixtures only:

```json
{
  "version": 1,
  "owners": [{
    "kind": "lab_record_reconciliation",
    "upstream": "silver",
    "downstream": "gold",
    "team": "Fixture Data Team",
    "destination": {
      "issue": {"provider": "github", "repository": "fixture-org/fixture-issues"},
      "notification": {"provider": "email", "recipients": ["triage@example.invalid"]}
    }
  }]
}
```

Repository values must be owner/name, not URLs. Recipient lists contain one to twenty
unique plain email addresses. Unsupported fields/providers, header injection, duplicate
recipients and malformed configuration are rejected. This is conservative syntax
validation only; it does not verify repository access, mailbox ownership or deliverability.

For an eligible technical finding the draft includes a deterministic destination preview:
issue repository, title/body, email recipients, subject/body, scope, impact, affected records
and local evidence reference. The review UI presents these as readable sections before
approval. It explicitly identifies reviews with no destinations as finding-only reviews.

The existing draft and policy hashes include this content. Adding or changing destinations
produces a new draft requiring approval; stale drafts cannot be approved or advanced through
the rehearsal. The rehearsal retains the reviewed preview in its saved payloads. Legacy
owner entries remain supported and do not gain destination approval implicitly.

These are proposed content contracts, not executable provider requests. No send API,
credentials or provider adapter is introduced. Provider-specific encoding/mention handling,
permissions, recipient authorization, hosted evidence URLs and actual delivery/reconciliation
remain pending. No actual issue URL is inserted into the proposed email; adding content later
must be covered by an explicit approval contract. The local shared-token approval is not an
enterprise reviewer identity or permission to send externally.

Validation: six tests cover legacy behavior, deterministic previews, repository/recipient
changes invalidating approval, malformed destinations and rehearsal payload retention.
Browser verification uses only fixture destinations and saved local lab evidence.
