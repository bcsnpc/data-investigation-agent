"""Print PASS/FAIL/MISSING prerequisites without starting a ticket or model run."""
import argparse
import json
from pathlib import Path
from investigator.cloud_preflight import result,shared_state_probe


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest',required=True)
    p.add_argument('--platform',required=True,help='Secret-free platform declaration JSON')
    p.add_argument('--output',required=True)
    p.add_argument('--platform-health-receipt',nargs=2,metavar=('PATH','SHA256'),help='Import exact retained platform control facts; no new calls')
    p.add_argument('--authentication-receipt',nargs=2,metavar=('PATH','SHA256'),help='Retain credential authentication separately from permissions; no new calls')
    p.add_argument('--check-shared-state',action='store_true',help='One read-only check of the tool PostgreSQL schema/imports through managed identity and gateway; no estate/model calls')
    args=p.parse_args(argv)
    manifest=json.loads(Path(args.manifest).read_text(encoding='utf-8-sig'))
    platform=json.loads(Path(args.platform).read_text(encoding='utf-8-sig'))
    output=Path(args.output)
    if output.exists():p.error('Output exists; preserve it and choose a new path')
    probes={}
    from investigator.adapters.platform_preflight_receipts import load,health_probes,authentication_facts
    facts=[];imports=[]
    if args.platform_health_receipt:
        receipt,identity=load(*args.platform_health_receipt,'PLATFORM_HEALTH')
        probes.update(health_probes(platform,receipt,identity));imports.append(identity)
    if args.authentication_receipt:
        receipt,identity=load(*args.authentication_receipt,'PLATFORM_AUTH_PREFLIGHT')
        facts=authentication_facts(manifest,receipt,identity);imports.append(identity)
    if args.check_shared_state:probes['postgres.schema_and_migration']=lambda:shared_state_probe(platform)
    report=result(manifest,platform=platform,probes=probes)
    report['control_operations']=1 if args.check_shared_state else 0
    report['imported_control_receipts']=imports
    report['authentication_facts']=facts
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    for check in report['checks']:
        print(check['status']+' '+check['id']+': '+check['detail']+' Fix: '+check['fix'])
    print('OVERALL '+report['status'])
    return 0 if report['status']=='READY' else 2


if __name__=='__main__':raise SystemExit(main())
