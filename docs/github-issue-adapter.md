# GitHub issue adapter (not activated)

The transport-injected adapter creates the exact reviewed issue title/body in its configured
repository. It is not connected to the UI, worker or a live transport. It performs no network
calls unless a caller supplies a transport and invokes it. No defect issue has been sent.

The caller passes the explicitly authorized approved draft hash. The adapter checks the
saved approval and recomputes current evidence/ownership/content before attempting creation.
The hash argument is a caller contract, not an authentication boundary; a future hosted
service must enforce external-delivery permission separately from local draft review.

The proposed issue body now includes a deterministic operation marker before approval.
Existing previews require regeneration/review because their content changed. No hidden marker
is appended after approval. Notification content is unchanged. Provider markup and mentions
still require policy before live activation.

A durable github_issue_attempts record claims the draft and unique content key before POST.
The attempt is UNCERTAIN until a valid response is saved. A successful repeated call returns
the saved receipt. A timeout, error response or malformed receipt stays held and cannot create
again automatically. Even definite rejection requires operator handling; there is no retry API.

Explicit reconciliation reads at most five pages of 100 repository issues, including closed
issues and excluding pull requests. It requires exactly one marker match with the exact
reviewed title/body and the expected repository issue URL. Duplicate, absent, edited or
incomplete results remain held. Matching receipts across pages are deduplicated by issue number.
GitHub does not provide an atomic snapshot of this listing; local marker lookup is not a
server-enforced exactly-once guarantee. Concurrent edits, repository activity, spoofed/copied
markers or operations outside this shared database remain limitations. No match never grants
a retry. Real provider recovery needs operational verification before activation.

Transport contract: callable(method, relative_path, payload) returns (status, decoded_json).
A real implementation must pin api.github.com, use scoped credentials, bounded timeouts and
raw JSON responses, and disable automatic POST retries. Provider exceptions are replaced by
a generic held-outcome error; no response body or credential is persisted in the receipt.
The adapter stores only repository, issue number and validated URL after success.

The API mapping follows [GitHub's issue REST documentation](https://docs.github.com/en/rest/issues/issues):
POST repository issues for creation, GET repository issues for bounded recovery, with title/body
and issue number/HTML URL validation. Tests use injected responses for success, concurrency,
timeout recovery, duplicate/edited/missing receipts, bounded pagination, stale authorization
and invalid references. No live GitHub delivery, email delivery or SQL/LLM usage is exercised.

Remaining: real transport and credentials, repository/recipient authorization, email adapter,
operator recovery UI, hosted identity, final provider encoding policy and an explicitly
authorized live delivery acceptance test.
