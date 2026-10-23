# Decisions

## 2026-10-22 - refresh facts use the existing scanner, not the investigator

Owner approval carried forward from Round 21 permits these two refresh-fact
calls only, for a workspace/model explicitly declared in the scanner policy:

- `GET https://api.powerbi.com/v1.0/myorg/groups/{workspace}/datasets/{model}/refreshes?$top=20`
- `GET https://api.powerbi.com/v1.0/myorg/groups/{workspace}/datasets/{model}/refreshSchedule`

The investigator remains Viewer. No new identity or permission grant is made.
History requires dataset Write permission, which the existing scanner already
holds; the investigator's original 403 remains evidence. Schedule GET has a
separate receipt; the old history failure did not establish a schedule failure.
The scanner's pre-existing definition/metadata reads remain unchanged.

`adapters/scanner_policy.py` enforces the two closed refresh URL forms, method,
query, no body and declared scope. `adapters/scanner_refresh.py` binds the exact
two URLs and permits scanner credentials only inside the scanner job context.
Refresh triggers and other writes are refused. Any widening of these refresh
calls requires a new entry here before code changes; a new audience or identity
scope additionally requires the explicit human decision required by CLAUDE.md.
