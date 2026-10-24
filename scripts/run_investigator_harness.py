"""Run a declared ticket through dia run, poll Azure and retain its sealed outcome."""
import argparse,json,shutil
from pathlib import Path
from investigator.investigator_harness import AzureCLIUser,CaseLog,RunHarness
from investigator.adapters.runner_deployment import input_policy_preflight

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--estate',type=Path,required=True)
    parser.add_argument('--ticket',type=Path,required=True)
    parser.add_argument('--log',type=Path,required=True)
    parser.add_argument('--timeout-seconds',type=int,default=4200)
    parser.add_argument('--baseline',action='store_true',help='Explicit legacy comparison only')
    args=parser.parse_args(argv)
    log=CaseLog(args.log)
    user=AzureCLIUser(args.estate,baseline=args.baseline,control=lambda value:log.append('CONTROL_READ',value))
    def admit(ticket):
        input_policy_preflight(user.config)
        args.log.parent.mkdir(parents=True,exist_ok=True)
        if shutil.disk_usage(args.log.parent).free<11*1024**3:raise ValueError('DISK_HEADROOM_NOT_ESTABLISHED')
    result=RunHarness(user,log,admit=admit).run(json.loads(args.ticket.read_bytes()),timeout_seconds=args.timeout_seconds)
    print(json.dumps({'log':str(args.log),'execution_status':result.get('execution',{}).get('status'),
                      'verdict':result.get('result',{}).get('verdict'),'capture_seal':result.get('capture_seal')}))
    return 0

if __name__=='__main__':raise SystemExit(main())
