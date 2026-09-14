# Demo finish line and remaining product work

The isolated demo finish line is: ticket submission -> reviewed scope -> approved
worker execution -> saved finding with verified local double-refund cause and
USD 99 impact -> review-only defect draft -> baseline reset.

This scope intentionally closes the demo rather than requiring every production
capability first. Additional feature work is not a prerequisite for presenting it.

| Area | Current boundary | Remaining after demo |
| --- | --- | --- |
| Live report investigation | Native definitions retained; one-order currency DAX diagnostic matched | Comparable source versions, broader DAX/filter/relationship and RLS evidence; production slicer holds remain |
| AI | Existing AI planning work is separate; this demo uses a fixed scope | Demonstrate and evaluate LLM-led hypothesis/tool selection across broader questions |
| Defects | Supported isolated scenarios include filter, refund arithmetic and freshness | Broader defects, unknown cases and cross-estate cause verification |
| Ticket context | Text, PNG attachments retained in the business demo, selected report context | Automatic screenshot interpretation and richer inherited report context |
| Delivery | Reviewed drafts and local/provider adapter work | Configure real owners/destinations and perform authorized issue/email acceptance |
| Hosting | Orders portal deployed; investigator demo runs on loopback | Enterprise investigator hosting, identity/permissions, monitoring and recovery |
| Acceptance | Isolated demo API/worker and browser path | Full live, multi-user end-to-end product acceptance |

Do not claim live production root-cause automation, real notification delivery or
general report parity from the isolated demo. Select the next product milestone
after the presentation rather than extending this demo with unrelated PRs.
