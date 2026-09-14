"""Evidence-bound routing preparation only. No external delivery or automatic repair."""
import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
from typing import Protocol
from uuid import uuid4
from investigation_evidence_api import EvidenceStore
from lab_investigator import reconcile
from ticket_workflow import TicketStore


class IssueTrackerProvider(Protocol):
    def create_issue(self,draft:dict,idempotency_key:str)->dict:...


class NotificationProvider(Protocol):
    def send_notification(self,draft:dict,issue_reference:dict,idempotency_key:str)->dict:...


def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,default=str).encode()).hexdigest()


def validate_policy(policy):
    if set(policy)!={'version','owners'} or policy['version']!=1 or not isinstance(policy['owners'],list):raise ValueError('Invalid ownership policy')
    seen=set()
    for entry in policy['owners']:
        if set(entry)!={'kind','upstream','downstream','team'} or any(not isinstance(v,str) or not v.strip() or len(v)>200 for v in entry.values()):raise ValueError('Invalid owner entry')
        key=(entry['kind'],entry['upstream'],entry['downstream'])
        if key in seen:raise ValueError('Ambiguous ownership')
        seen.add(key)


def prepare(item,policy):
    validate_policy(policy)
    result=item['result'];request=item['request'];classification=item['classification']
    base={'investigation_id':item['id'],'classification':classification,'evidence_hash':digest(item),
          'policy_hash':digest(policy),'automatic_delivery':False,'human_review_required':True}
    if classification!=result.get('classification'):return dict(base,status='HUMAN_TRIAGE',reason='Inconsistent saved classification')
    if classification=='EXPECTED_BEHAVIOR':return dict(base,status='NO_BUG',reason='Expected behavior does not create a bug')
    if classification!='TECHNICAL_DEFECT':return dict(base,status='HUMAN_TRIAGE',reason='Classification is not eligible for technical bug preparation')
    try:
        from defect_lab import filter_query
        cause=request['cause_evidence'];payload=request['lab_evidence']
        verified=(request['kind']=='lab_record_reconciliation' and result['root_cause_verified'] is True
            and cause['verified'] is True and cause['cause']==result['root_cause']
            and cause['query_text']==filter_query() and cause['filtered_replay_matches'] is True
            and cause['unfiltered_replay_reconciles'] is True)
        evidence_hash=digest({k:request.get(k) for k in ('lab_evidence','business_context','cause_evidence')})
        observed=reconcile(payload)
        verified=verified and evidence_hash==request['evidence_hash'] and observed['comparison_status']=='MISMATCH'
        verified=verified and all(result[k]==observed[k] for k in ('impact_by_currency','affected_records','compared_boundary'))
        if not verified:raise ValueError('Evidence mismatch')
    except (KeyError,ValueError,TypeError):return dict(base,status='HUMAN_TRIAGE',reason='Supported cause and impact evidence could not be validated')
    boundary=result['compared_boundary']
    owners=[e for e in policy['owners'] if (e['kind'],e['upstream'],e['downstream'])==(request['kind'],boundary['upstream'],boundary['downstream'])]
    if not owners:return dict(base,status='NEEDS_OWNER',reason='No explicit owner for the verified scope and boundary')
    draft={'title':'[Local lab] '+result['root_cause'],'team':owners[0]['team'],
           'severity':'UNASSESSED','scope':result['limitation'],'boundary':boundary,
           'impact_by_currency':result['impact_by_currency'],'affected_records':result['affected_records'],
           'evidence_reference':'/api/investigations/'+item['id'],
           'notification_text':'Review local investigation '+item['id']+': '+result['root_cause'],
           'triage_after_delivery':'AWAITING_HUMAN_TRIAGE'}
    return dict(base,status='DRAFT_REQUIRES_REVIEW',draft=draft,
                reason='Local cause only; no production first-boundary or automatic-routing claim')


def save(store,item,policy):
    record=prepare(item,policy);key=digest(record)
    with closing(store.connect()) as db:
        db.execute('CREATE TABLE IF NOT EXISTS routing_drafts(fingerprint TEXT PRIMARY KEY,id TEXT UNIQUE,record TEXT)');db.commit()
        db.execute('BEGIN IMMEDIATE')
        old=db.execute('SELECT record FROM routing_drafts WHERE fingerprint=?',(key,)).fetchone()
        if old:return json.loads(old[0])
        record['id']=str(uuid4());db.execute('INSERT INTO routing_drafts VALUES(?,?,?)',(key,record['id'],json.dumps(record)));db.commit()
    return record


if __name__=='__main__':
    from defect_lab import ROOT
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run-id',required=True)
    parser.add_argument('--database',type=Path,default=ROOT/'.local/defect-lab/evidence.sqlite')
    parser.add_argument('--ownership',type=Path,default=ROOT/'infra/routing/ownership.json');args=parser.parse_args()
    item=EvidenceStore(args.database).get(args.run_id)
    if item is None:parser.error('Investigation not found')
    record=save(TicketStore(args.database.with_name('routing.sqlite')),item,json.loads(args.ownership.read_text()))
    print(json.dumps(record,indent=2))
