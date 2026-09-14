# Review-only routing approval

The isolated lab server exposes routing review for a completed investigation. In the
evidence section choose **Prepare routing review**. The backend creates or reuses a
draft from saved evidence and the current ownership policy. Missing owners and ineligible
findings display their hold reason rather than an approval action.

With an explicitly configured owner, review the title, team, severity placeholder,
scope, impact and proposed notification text. Check the confirmation box and choose
**Approve routing draft**. This records a local operator decision only. Issue creation,
notifications and automatic remediation remain disabled. The default real owner map
is still empty; browser tests use an isolated fixture policy.

Authenticated endpoints:

- `POST /api/investigations/{id}/routing`: exact body `{"confirm":true}`.
- `GET /api/routing/{id}`: returns record, displayed-draft hash and existing approval.
- `POST /api/routing/{id}/approve`: exact body with `confirm:true` and `draft_hash`.

Preparation and approval require JSON with a bounded body. Approval recomputes the draft
against current saved evidence and policy, compares the displayed hash, then rechecks
stored draft bytes inside the approval transaction. Repeated/concurrent approval records
one decision. Changed evidence, ownership or displayed content is rejected.

Approvals are stored in routing_approvals with the hash, timestamp and the shared-token
reviewer assertion `local-api-operator`. This is not individual enterprise identity.
Historical approval is not authorization to send later changed content: future delivery
must revalidate evidence/policy, recipient configuration and the approved payload.

Validation covers concurrent approval, stale evidence/owner/hash, missing owner,
authentication, confirmation and body limits. Browser verification checks preparation
and explicit approval with a fixture team and no provider calls. This feature is enabled
on the isolated lab server only; cloud review integration remains future work.
