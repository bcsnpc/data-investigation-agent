"""Explicit operator delivery CLI. Never called by review servers or workers."""
import argparse
import json
import os
from pathlib import Path
from delivery_transports import GithubTransport,SmtpTransport
from github_issue_adapter import GithubIssueAdapter
from email_delivery_adapter import EmailAdapter
from envelope_workflow import EnvelopeWorkflow
from routing_review import RoutingReview
from investigation_evidence_api import EvidenceStore
from ticket_workflow import TicketStore,Conflict


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('create-issue','reconcile-issue','send-email'))
    parser.add_argument('--workflow',type=Path,required=True);parser.add_argument('--evidence',type=Path,required=True)
    parser.add_argument('--ownership',type=Path,required=True)
    parser.add_argument('--draft-id');parser.add_argument('--draft-hash');parser.add_argument('--envelope-hash')
    parser.add_argument('--confirm-external',action='store_true')
    args=parser.parse_args()
    if not args.confirm_external: parser.error('Explicit --confirm-external required; review the exact destination/content first')
    if not all(p.is_file() for p in (args.workflow,args.evidence,args.ownership)):parser.error('Existing local files required')
    if args.action!='send-email' and not all((args.draft_id,args.draft_hash)):parser.error('Exact draft-id and approved draft-hash required')
    if args.action=='send-email' and not args.envelope_hash:parser.error('Reviewed envelope-hash required')
    try:
        review=RoutingReview(TicketStore(args.workflow),EvidenceStore(args.evidence),lambda:json.loads(args.ownership.read_text()))
        if args.action=='send-email':
            smtp=SmtpTransport(os.environ.get('INVESTIGATOR_SMTP_HOST',''),int(os.environ.get('INVESTIGATOR_SMTP_PORT','465')),
                               os.environ.get('INVESTIGATOR_SMTP_USERNAME',''),os.environ.get('INVESTIGATOR_SMTP_PASSWORD',''))
            result=EnvelopeWorkflow(EmailAdapter(review,smtp),delivery_enabled=True).execute(args.envelope_hash)
        else:
            adapter=GithubIssueAdapter(review,GithubTransport(os.environ.get('INVESTIGATOR_GITHUB_TOKEN','')))
            result=(adapter.create_issue if args.action=='create-issue' else adapter.reconcile)(args.draft_id,authorized_hash=args.draft_hash)
        print(json.dumps(result,indent=2))
    except Exception:
        parser.exit(1,'Delivery did not complete. Inspect persisted attempt status before taking further action; no automatic replay.\n')


if __name__=='__main__':main()
