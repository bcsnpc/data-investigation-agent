# Round Nineteen-B cloud demo

## Attempt 1, 2026-10-13

Offline scope/count admission passed18bindings/40verificationprobes/cap40. Input SHA256 `63b54443b87882555d9aae1469b8494c0874a5e2e2ab62372f595f43395754ca`. Current PGmodel matched the retained prior output. Prepare yielded context `bda23598-81cb-4e11-a050-92a345bc7d54`, hash `20dc43acf049c231015d7b394bba07f247a6bda8b02ff812404ea46dcb05f6ff`, candidate `3694fba165c316f9298f55e3b0cadc7cd61fadd36aeb2041ab9f6835b870dfeb`.

The first live worker attempt published that context, then refused `VERIFICATION_BUDGET_DIFFERS` before capture/estate dispatch: verification-spec still carried ROUND_NINETEEN while estate.json carried ROUND_NINETEEN_B. Zero estate requests and model calls. No demo ran. This is an operator input-preparation defect plus an incomplete offline admission check, not an estate capability finding. Original output SHA256 `a8dbbb9c3907b484a9b34fe24c4363c4e395eefee766df3a14065b23fb07bb92` is retained unchanged. The guard correctly refused; its whole-budget comparison will also run before publication. One live attempt remains.
