"""Offline Round 17 intake recheck from immutable text and pinned definitions.

This does not run an investigation or revise any acceptance expectation.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from investigator.essentials_intake import retained_text
from investigator.onboarding import digest


def score(tickets, catalog, *, expected_catalog_hash):
    if digest(catalog)!=expected_catalog_hash:
        raise ValueError('RETAINED_INTAKE_CATALOG_PIN_DIFFERS')
    rows=[]
    for row in tickets['rows']:
        result=retained_text(row['ticket_text'],catalog,request_key=row['id'])
        rows.append({'id':row['id'],'split':row['split'],'topic':row['topic'],'ticket_text':row['ticket_text'],
                     'old_status':row['pipeline_status'],'result':result})
    statuses=Counter(r['result']['status'] for r in rows)
    return {'version':1,'evidence_class':'OFFLINE_INTAKE_ONLY_NOT_LIVE_INVESTIGATIONS',
            'catalog_hash':digest(catalog),'rows':rows,'admitted_to_investigator':statuses['READY'],
            'investigations_executed':0,'one_question':statuses['CLARIFYING'],'held':statuses['HELD'],
            'harmful_findings':0,'harmful_findings_note':'No investigation or technical finding was executed in this offline check.',
            'model_calls':0,'estate_requests':0}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog',required=True,type=Path)
    parser.add_argument('--catalog-hash',required=True)
    parser.add_argument('--tickets',type=Path,default=Path(__file__).resolve().parents[1]/'docs/round-seventeen-scored-results.json')
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    catalog=json.loads(args.catalog.read_bytes());tickets=json.loads(args.tickets.read_bytes())
    result=score(tickets,catalog,expected_catalog_hash=args.catalog_hash)
    result['source_files']={'catalog_sha256':hashlib.sha256(args.catalog.read_bytes()).hexdigest(),
                            'tickets_sha256':hashlib.sha256(args.tickets.read_bytes()).hexdigest()}
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:result[k] for k in ('admitted_to_investigator','investigations_executed','one_question','held','estate_requests','model_calls')}))


if __name__=='__main__':main()
