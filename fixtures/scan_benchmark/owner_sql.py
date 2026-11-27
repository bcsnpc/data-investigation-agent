"""Owner-only deployment to four *new* benchmark databases; never DIA I/O.

One transaction per fresh database. A saved receipt pins the exact plan. An
existing unreceipted population is refused, not overwritten after uncertainty.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess

DATABASES=frozenset({'sb_wholesale','sb_insurance','sb_erp','sb_education'})
SERVER='sql-orderops-9696025.database.windows.net'


def deploy(plan_path, receipt, azure_python):
    import certifi
    import pytds
    plan_path=Path(plan_path);receipt=Path(receipt)
    raw=plan_path.read_bytes();plan=json.loads(raw)
    database=plan['database']
    if database not in DATABASES:raise ValueError('New benchmark database only')
    if receipt.exists():
        prior=json.loads(receipt.read_text())
        if prior.get('status')=='DEPLOYED_VERIFIED':
            if prior['plan_sha256']!=hashlib.sha256(raw).hexdigest():raise ValueError('Deployed plan changed')
            return prior
        raise ValueError('Reconcile prior deployment before retrying')
    az=[str(Path(azure_python).resolve()),'-m','azure.cli']
    policy=json.loads(subprocess.check_output(az+['sql','db','show','-g','rg-investigator-dev','-s',SERVER.split('.')[0],'-n',database,
        '--query','{free:useFreeLimit,exhaustion:freeLimitExhaustionBehavior,pause:autoPauseDelay}','-o','json']))
    if policy!={'free':True,'exhaustion':'AutoPause','pause':60}:raise ValueError('Free-only database policy differs')
    def token():
        p=subprocess.run(az+['account','get-access-token','--resource','https://database.windows.net/','-o','json'],capture_output=True,text=True,timeout=120,check=True)
        return json.loads(p.stdout)['accessToken']
    r=dict(database=database,server=SERVER,plan_sha256=hashlib.sha256(raw).hexdigest(),free_policy=policy,
        started_at=datetime.now(timezone.utc).isoformat(),identity='existing Azure owner',status='STARTED')
    receipt.parent.mkdir(parents=True,exist_ok=True)
    receipt.write_text(json.dumps(r,indent=2)+'\n')
    try:
        with pytds.connect(server=SERVER,database=database,access_token_callable=token,
                cafile=certifi.where(),timeout=120,login_timeout=60,appname='Scan-benchmark-owner-build')as db:
            c=db.cursor();c.execute("SELECT COUNT(*) FROM sys.tables WHERE is_ms_shipped=0")
            if c.fetchone()[0]:raise ValueError('Unreceipted existing tables; refuse overwrite')
            for batch in plan['batches']:c.execute(batch)
            db.commit()
            c.execute("SELECT s.name,o.name,o.type_desc,c.name,t.name,c.is_nullable FROM sys.objects o JOIN sys.schemas s ON o.schema_id=s.schema_id LEFT JOIN sys.columns c ON c.object_id=o.object_id LEFT JOIN sys.types t ON t.user_type_id=c.user_type_id WHERE o.is_ms_shipped=0 AND o.type IN ('U','V','P') ORDER BY s.name,o.name,c.column_id")
            r['catalog_rows']=[list(row)for row in c.fetchall()]
            r['status']='DEPLOYED_VERIFIED'
    except Exception as error:
        r.update(status='DEPLOYMENT_FAILED_OR_UNCERTAIN',error_type=type(error).__name__,error=str(error)[:1500])
    receipt.write_text(json.dumps(r,indent=2)+'\n')
    return r


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan',required=True);p.add_argument('--receipt',required=True);p.add_argument('--azure-python',required=True)
    a=p.parse_args();r=deploy(a.plan,a.receipt,a.azure_python)
    print(json.dumps({k:v for k,v in r.items()if k!='catalog_rows'},indent=2))
    return 0 if r['status']=='DEPLOYED_VERIFIED'else 1


if __name__=='__main__':raise SystemExit(main())
