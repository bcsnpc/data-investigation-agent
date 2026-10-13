# Cloud foundation cost estimate ? before provisioning

Owner date 2026-10-12; rates retrieved 2026-10-13 UTC. Region eastus; `rg-dia-platform` does not exist, so there is no existing group location to override it. USD, consumption prices, no reservation or paid commitment. The subscription is pay-as-you-go with an active `freetier` promotion ending 2027-10-12T21:13:18Z; current inventory contains no PostgreSQL server consuming that allowance. Subscription response and inventory are retained locally.

## Free eligibility and decision

Microsoft's [PostgreSQL team](https://techcommunity.microsoft.com/blog/adforpostgresql/whats-new-with-postgres-at-microsoft-2025-edition/4410710/) specifies 750 B1ms hours, 32 GB storage and 32 GB backup per month for the first 12 months. [Upgrading to pay-as-you-go retains the free services](https://learn.microsoft.com/en-us/azure/cost-management-billing/manage/avoid-charges-free-account). The active subscription promotion plus no existing PostgreSQL usage establishes eligibility for the specified single B1ms/32-GB server, within those quantities. This is configuration/offer evidence, not a guarantee about a future invoice. We will not enlarge the SKU, enable autogrow/HA/geo backup, or deploy a second server. Seven-day local backups must remain within allowance; check actual usage after deployment. Review before the promotion expires.

At 744 maximum hours per calendar month, a single B1ms is below750. Retail without the allowance: $0.017/hour x730 = $12.41 compute; 32GB x$0.115 = $3.68 storage; total $16.09 before backup overage. **Without confirmed free eligibility, PostgreSQL alone exceeds the $15 ceiling and creation is blocked.**

## Monthly operating envelope

| Component | Assumption / measured retail unit | Estimated USD/month |
|---|---|---:|
| PostgreSQL | One B1ms,32GB,HA disabled; free allowance applies | 0.00 |
| Hot Blob snapshots/tapes/captures/screenshots | Conservative250GB x$0.0208/GB-month; Standard LRS | 5.20 |
| Archive originals | 250GB x$0.00099/GB-month | 0.25 |
| Blob operations | 100k hot writes@$0.05/10k +40k archive writes@$0.10/10k +100k reads@$0.004/10k | 0.94 |
| Key Vault Standard | 10k secret operations@$0.03/10k; no HSM or certificate renewals | 0.03 |
| Container Apps jobs | 40vCPU-hours@$0.000024/sec +80GiB-hours@$0.000003/GiB-sec | 4.32 |
| Egress allowance | $1 contingency for small exports; no bulk download/rehydration in steady state | 1.00 |
| RG / user-assigned identity | No billed capacity | 0.00 |
| Log Analytics | Not provisioned: environment logging destination `none`; evidence persists in Blob | 0.00 |
| Contingency | Additional operating headroom | 2.00 |
| **Conservative total** | Rounded; no Container Apps free grant deducted | **13.74** |

**PASS: $13.74 <= $15.** Creation is authorized only for this envelope. The [Container Apps grant](https://learn.microsoft.com/en-us/azure/container-apps/billing) can reduce the estimate further (180k vCPU-seconds and360k GiB-seconds); it is deliberately not relied on here. Consumption-only environment and manual jobs have no always-running replica. No dedicated profile, private endpoint, planned-maintenance feature, optional API app, registry or paid logging workspace is needed. [Disabling saved platform logs is supported](https://learn.microsoft.com/en-us/azure/container-apps/log-options); application evidence remains persisted.

Archive tier is per blob, not per container. Upload and verify in Hot, then set Archive, retaining checksum/ETag receipts. Archive has rehydration delay, retrieval charges and minimum-retention/early-deletion charges; cleanup is not a cloud-delete operation. Routine CI uses Hot deduplicated snapshots, not Archive. Initial upload is ingress; verification reads avoid repeated full downloads. The finite operation allowance must be checked against the manifest before upload.

Forecast excludes existing estates and existing model calls: those retain their own caps, and this round's new model spend is <=$10. The cloud envelope is not an Azure hard-stop billing feature. If inventory, usage, entitlement, or the deployment plan exceeds it, do not create/scale additional resources. No prices assume the previous $200 credit.

## Evidence and decisions

[Selected retail meter IDs and units](cloud-retail-rates.json) come from the [Azure Retail Prices API](https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices). Full responses are local at `.local/round-eighteen/pricing/`. Subscription and empty PostgreSQL listing were read with the existing owner CLI; no resource has yet been created.

DECIDED WITHOUT REVIEW: omit the optional API app and Log Analytics workspace. Rejected an always-on API or daily-cap-only logging estimate because both add uncontrolled idle/ingestion costs; persistent evidence is written to Blob. This is within the optional-app and conditional-logging approvals.


Region amendment (owner approved 2026-10-12): East US PostgreSQL provisioning is restricted. South Central US advertises OfferRestricted=Disabled and Standard_B1ms; PostgreSQL and future Container Apps use that region. Storage, vault and identity stay East US. The queried South Central US PostgreSQL retail rates are $0.0204/hour and $0.138/GB-month; the same active 12-month free eligibility applies. Container Apps active rates remain $0.000024/vCPU-second and $0.000003/GiB-second. The $13.74/month estimate is unchanged, including its $1 transfer contingency. Without the free allowance, PostgreSQL alone is $19.308/month; do not silently continue at paid pricing. Exact response retained locally in pricing/southcentralus.json.
