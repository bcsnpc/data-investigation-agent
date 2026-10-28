"""Owner CLI maintenance; native cost response stays local. No role/resource creation."""
import argparse
import copy
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from decimal import Decimal, ROUND_CEILING
from pathlib import Path
from investigator.adapters.runner_deployment import writable_template

JOBS=('job-dia-worker','job-dia-graph-scan','job-dia-collectors')


def cost_only_template(job, observation):
    template=writable_template(job['properties']['template'])
    changed=False
    for container in template.get('containers',[]):
        for env in container.get('env',[]):
            if env['name']!='DIA_RUNNER_ESTATE_JSON':continue
            config=json.loads(env['value'])
            if 'platform_cost_observation'not in config:continue
            config['platform_cost_observation']=copy.deepcopy(observation)
            env['value']=json.dumps(config,sort_keys=True,separators=(',',':'))
            changed=True
    return template,changed


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true',help='Read native costs; default only prints the plan.')
    parser.add_argument('--publish-schedules',action='store_true',help='Replace only existing cost observations in the three existing jobs.')
    parser.add_argument('--output',type=Path,default=Path('.local/round-twenty-five/cost-maintenance'))
    args=parser.parse_args(argv)
    if not args.apply:
        print(json.dumps({'plan_only':True,'cost_query':'Native subscription month-to-date ActualCost by ServiceName, same existing non-Foundry basis','jobs':JOBS if args.publish_schedules else [],'role_identity_resource_changes':False,'prints_financial_amounts_or_tokens':False}));return 0
    args.output.mkdir(parents=True,exist_ok=True)
    stamp=datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    folder=args.output/stamp;folder.mkdir(exist_ok=False)
    cli=[str(Path('.local/azure-cli-env/Scripts/python.exe').resolve()),'-m','azure.cli']
    def az(arguments):
        for attempt in range(3):
            result=subprocess.run(cli+arguments+['--output','json','--only-show-errors'],capture_output=True,text=True,timeout=120)
            if result.returncode==0:return json.loads(result.stdout)if result.stdout.strip()else None
            # No credential/token output. Retry only a documented throttling response.
            (folder/('error-'+str(time.time_ns())+'.log')).write_text(result.stderr,encoding='utf8')
            if attempt<2 and any(x in result.stderr for x in ('429','TooManyRequests','Too Many Requests')):time.sleep(30*(attempt+1));continue
            raise RuntimeError('NATIVE_OWNER_CONTROL_READ_FAILED; private error retained; no role or timestamp changed')
    account=az(['account','show'])
    query={'type':'ActualCost','timeframe':'MonthToDate','dataset':{'granularity':'None','aggregation':{'totalCost':{'name':'PreTaxCost','function':'Sum'}},'grouping':[{'type':'Dimension','name':'ServiceName'}]}}
    path=folder/'query.json';path.write_text(json.dumps(query))
    response=az(['rest','--method','POST','--url','https://management.azure.com/subscriptions/'+account['id']+'/providers/Microsoft.CostManagement/query?api-version=2025-03-01','--body','@'+str(path.resolve())])
    raw=json.dumps(response,sort_keys=True).encode();native=folder/'native-response.json';native.write_bytes(raw)
    assert not response['properties'].get('nextLink'),'Incomplete cost response; no observation published'
    names=[c['name']for c in response['properties']['columns']]
    rows=[dict(zip(names,row))for row in response['properties']['rows']]
    assert all(x.get('Currency')=='USD'for x in rows),'Existing USD cap requires native USD costs'
    amount=sum((Decimal(str(x['PreTaxCost']))for x in rows if x.get('ServiceName')!='Foundry Models'),Decimal(0))
    observation={'charged_microdollars':int((amount*1000000).to_integral_value(rounding=ROUND_CEILING)),'observed_at':time.time(),'source':str(native.resolve())}
    assert observation['charged_microdollars']<20000000,'AZURE_PLATFORM_MONTHLY_CAP_REACHED; no cap bypass'
    receipt={'observation':observation,'native_response_sha256':hashlib.sha256(raw).hexdigest(),'billing_data_may_lag':True,'currency':'USD','scope':'Existing subscription non-Foundry month-to-date basis; model budget separate'}
    (args.output.parent/'platform-cost-observation-current.json').write_text(json.dumps(receipt,indent=2))
    updates=[]
    if args.publish_schedules:
        for name in JOBS:
            before=az(['containerapp','job','show','-g','rg-dia-platform','-n',name])
            template,changed=cost_only_template(before,observation)
            if not changed:updates.append({'job':name,'status':'NO_EXISTING_OBSERVATION_NO_CHANGE'});continue
            body={'properties':{'template':template}}
            patch=folder/(name+'-patch.json');patch.write_text(json.dumps(body))
            az(['rest','--method','PATCH','--url','https://management.azure.com'+before['id']+'?api-version=2025-01-01','--body','@'+str(patch.resolve())])
            after=az(['containerapp','job','show','-g','rg-dia-platform','-n',name])
            assert after['properties']['configuration']==before['properties']['configuration']
            assert after['identity']==before['identity']
            assert writable_template(after['properties']['template'])==template
            updates.append({'job':name,'status':'NATIVE_COST_ONLY_READBACK_MATCHED','configuration_identity_image_resources_unchanged':True,'patch_sha256':hashlib.sha256(patch.read_bytes()).hexdigest()})
    public={'observed_at_utc':datetime.fromtimestamp(observation['observed_at'],timezone.utc).isoformat(),'native_response_sha256':receipt['native_response_sha256'],'under_existing_platform_cap':True,'jobs':updates,'no_role_identity_resource_creation':True,'no_model_calls':True,'financial_response_is_local_only':True}
    (folder/'maintenance-receipt.json').write_text(json.dumps(public,indent=2));print(json.dumps(public));return 0


if __name__=='__main__':raise SystemExit(main())
