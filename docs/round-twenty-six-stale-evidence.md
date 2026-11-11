# Round 26: Direct Lake refresh evidence

Documentation checked 2026-11-02 UTC; native fixture controls remain separate from investigator evidence.

Microsoft documents the model-level **Keep your Direct Lake data up to date** setting in the portal's Refresh section. It controls automatic framing after underlying table changes. If disabled, an explicit refresh can frame newer data. This is distinct from a scheduled refresh. [How Direct Lake works](https://learn.microsoft.com/en-us/fabric/fundamentals/direct-lake-how-it-works#automatic-updates).

A schedule has a documented read endpoint: `GET /groups/{groupId}/datasets/{datasetId}/refreshSchedule`. Its response includes `enabled`, days, times and time zone; documented scopes include Dataset.Read.All. Documentation is not evidence that a particular installed reader passed authorization. Collect the real response or its unavailability under the existing scanner/reader scopes. [Get Refresh Schedule In Group](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/get-refresh-schedule-in-group).

The Fabric semantic-model GET supports read access, but its documented SemanticModel response does not include the automatic-update switch. No supported reader GET for that switch was established in this review; absence from this response is not proof that no API exists anywhere. [Get Semantic Model](https://learn.microsoft.com/en-us/rest/api/fabric/semanticmodel/items/get-semantic-model).

When the setting is unavailable to the investigator, the Round 26 answer contract uses observed last-refresh/update time and newer-load/data time, and points to automatic-update and refresh settings. It must not invent the switch value. The owner's UI OFF receipt establishes a test fixture, not extra investigator access. Native portal observation before the stale cohort was On / schedule Off, with Apply disabled; nothing was changed during that observation.

The new held-out oracle receives this owner-defined fallback before the stale pair is authored or sealed. Existing v2 and R22 expectations are unchanged.
