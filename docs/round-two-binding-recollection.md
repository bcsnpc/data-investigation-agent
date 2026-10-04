# Round Two: current binding, discovery and budget

2026-10-04. The source reader account, declared system of record and audit source
were configured; no identity scope was expanded by this configuration.
The normalized whole-config approval changed from
`19e2ef0b0b5cb6bfd8df38c5fded6c1eaac40718b3926248ac62c61abf0cf8b6` to
`2c4dea1994356f9969c22567f96918a550a502ab4ccab5ca0a797b7c13b06f32`.

The application asset is
`sql://sql-orderops-9696025.database.windows.net/ordersops/object/1938105945`.
The delivery is Copy Job `57e128c3-6ba0-4aaf-9464-81164ecdc782`; the producer is
pipeline `b4871498-bd35-45be-916c-9a642568012c`; its declared audit source is
`fabric://149f8d99-1c66-4a0a-9624-759be002bb60/33618b8d-46eb-4fe7-b80b-122c331260a3/table/dbo.load_run_audit`.

Seven isolated SQL catalog commands retrieved current metadata. Recollection
then made 113 physical metadata requests (114 logical operations including the
reused catalog). Cloud acquisition succeeded, but local publication failed with
`ModuleNotFoundError: sqlglot` in the metadata Python environment. That failed
scan and its receipts remain unchanged.

A separately recorded offline recovery consumed the sealed responses with exact
endpoint/method/audience and response-hash checks, using the runtime environment
that has sqlglot. It made zero cloud requests and preserved prior investigation
records. The completed discovery version is
`023b8b09-a2e7-4f6f-bfe1-4a3eaff407bb`; inventory scan
`a2fbb7db-c564-44be-8d32-8125d6f429e9`. The isolated model's current context is
`f12ddca6-543a-4e68-9ca2-8dc14cd57741` and pins the full new policy hash above.
This reused the acquisition times; it is not a claim of new offline cloud reads.

Dated accounting correction: the recovery helper's SQL-operation field copied
`executed_catalog_commands=7` from the collection helper. Actual recovery
execution was zero; the seven commands were reused from the prior receipt.
The original artifact is untouched and a zero-request correction is appended.

The discovered Copy Job connection resolves the exact approved source, and the
offline path compiles presentation -> isolated Bronze -> application. This is
an isolated new path; the old literal-seeded family E estate is unchanged.
The current catalog automatically projected the new model; no runtime ID was
registered by hand. Source delivery classifications have not been exercised.

## Authorized Part B increase

The human explicitly approved Part B 300 -> 500. Before and after configuration
reads are recorded under `.local/round-two-20261003/part-b-ceiling-500-control-plane.json`,
with a ledger note. Rolling allowance remains 600 and per-run diagnostic cap 12.
No usage counter or reservation was reset. The recorded Part B charge before
this change is 282; the last observed rolling charge is 434. This change has
zero physical requests. Prior freezes remain invalid.
