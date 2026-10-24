# Refresh-stale control preparation

Owner date: 2026-10-23. Observations continued after midnight UTC on 2026-10-24.

The signed-in publisher portal shows **Keep your Direct Lake data up to date = ON**, and scheduled refresh = OFF, for both Warehouse Operations e1b8e1 (`3484a2bc-98c5-4cef-be5c-a6215484075e`) and the isolated Application load fixture 20261003 (`0c89889c-6fe6-49ab-91e9-4b00a51070e6`) in the existing fixture workspace. No setting was changed. The displayed owner is admin@skynwhy.com. These are portal observations, not investigator diagnostic receipts.

Microsoft documents automatic framing on detected Delta changes and explains that disabling automatic updates can support controlled data-preparation windows. `DirectLakeBehavior` controls DirectQuery fallback; it is not the automatic-update setting. An old refresh-history timestamp alone does not prove stale served data. A real control must retain a successful prior frame, a subsequent attested upstream load, and differing values while the old frame is still served. [Microsoft Learn: How Direct Lake works](https://learn.microsoft.com/en-us/fabric/fundamentals/direct-lake-how-it-works).

Before any mutation, a bounded native DAX control was prepared for the existing investigator on the isolated model:

```dax
EVALUATE ROW("quantity",[Movement Units],"surface_identity",USERPRINCIPALNAME())
```

The measure's retained definition is `SUM('Movements'[units])`. The manifest already declares that model's Movements table as a reachable semantic layer; no new role or credential was requested or applied. This is a preparation read, not a scored ticket or a refresh-stale verdict.

The first execution, `job-dia-worker-97c55p7`, ended Succeeded at the Azure wrapper but returned HELD / CHECK_ACCESS_FAILED before native dispatch. Its reduced input archive omitted the existing permission-map and access-bindings files. The original capture is retained with seal `8eb791879052012c92ba3071727615da7097fced2c5ba6aaf7ccb7795bf22cff`. It establishes an input-packaging error, not a model-access refusal or an unavailable data source.

A new immutable input adds those two unchanged existing files. Its SHA-256 is `f1939881c7c156a5b8fdd25894c9892aed43a7098cae7acd3b2c6c036793d939`. The access check remains enabled, the four-request native authorization bound is unchanged, and no model setting or reader scope changed. The next control result is pending; it must be recorded separately rather than replacing the first.
