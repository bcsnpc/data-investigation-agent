"""Approved read grants, limited to a journaled new benchmark estate."""
import argparse
import json
from pathlib import Path
import subprocess
from .owner_sql import DATABASES,SERVER
from .factory import qualified,quoted

NAME='dia-investigator-round19'
FABRIC_PRINCIPAL='439ceb25-d200-4f02-95cf-4b1318faca62'


def grant(plan_path,journal_path,azure_python,cli_packages,receipt_path):
    import pytds,certifi
    from fixtures.hospital.owner_fabric import OwnerFabric
    plan=json.loads(Path(plan_path).read_text());db=plan['database']
    if db not in DATABASES:raise ValueError('New benchmark databases only')
    owner=OwnerFabric(journal_path,cli_packages)
    workspace=owner.state['benchmark_'+plan['estate']+'_workspace']['id']
    receipt=Path(receipt_path)
    if receipt.exists():raise ValueError('Read prior grant receipt before retrying')
    result=dict(database=db,workspace=workspace,approved='Owner 2026-11-26 scan-benchmark-estates.md',
        sql={},fabric={},new_roles=[],write_grants=0)
    def save():receipt.write_text(json.dumps(result,indent=2,default=str)+'\n')
    save()
    az=[str(Path(azure_python).resolve()),'-m','azure.cli']
    def token():
        r=subprocess.run(az+['account','get-access-token','--resource','https://database.windows.net/','-o','json'],check=True,capture_output=True,text=True,timeout=120)
        return json.loads(r.stdout)['accessToken']
    with pytds.connect(server=SERVER,database=db,access_token_callable=token,cafile=certifi.where(),timeout=60,login_timeout=60,autocommit=True,appname='Scan-benchmark-approved-read-grants')as connection:
        cur=connection.cursor()
        def rows(sql):
            cur.execute(sql)
            return [dict(zip([c[0]for c in cur.description],r))for r in cur.fetchall()]if cur.description else []
        lookup="SELECT p.name,p.type_desc,r.name role_name FROM sys.database_principals p LEFT JOIN sys.database_role_members m ON m.member_principal_id=p.principal_id LEFT JOIN sys.database_principals r ON m.role_principal_id=r.principal_id WHERE p.name=N'dia-investigator-round19'"
        before=rows(lookup);result['sql']['before']=before;save()
        if before:raise ValueError('Existing unjournaled principal; inspect first')
        commands=['CREATE USER ['+NAME+'] FROM EXTERNAL PROVIDER;']
        if plan['permissions']=='read_only':commands+=['ALTER ROLE [db_datareader] ADD MEMBER ['+NAME+'];','GRANT VIEW DEFINITION TO ['+NAME+'];']
        else:
            schemas=sorted({o['address'].split('.')[0]for o in plan['objects']}-{'private'})
            commands += ['GRANT SELECT, VIEW DEFINITION ON SCHEMA::'+quoted(s)+' TO ['+NAME+'];'for s in schemas]
        result['sql']['commands']=commands;save()
        for command in commands:rows(command)
        result['sql']['after']=rows(lookup)
        result['sql']['permissions']=rows("SELECT permission_name,state_desc,class_desc,major_id FROM sys.database_permissions WHERE grantee_principal_id=DATABASE_PRINCIPAL_ID(N'dia-investigator-round19')")
        if any(r['role_name']not in(None,'db_datareader')for r in result['sql']['after']):raise ValueError('Unexpected role')
        save()
    path=f'workspaces/{workspace}/roleAssignments'
    result['fabric']['before']=owner.call(path);save()
    if any(r.get('principal',{}).get('id')==FABRIC_PRINCIPAL for r in result['fabric']['before']['value']):raise ValueError('Unjournaled existing workspace grant')
    owner.call(path,dict(principal=dict(id=FABRIC_PRINCIPAL,type='ServicePrincipal'),role='Viewer'))
    result['fabric']['after']=owner.call(path)
    found=[r for r in result['fabric']['after']['value']if r.get('principal',{}).get('id')==FABRIC_PRINCIPAL]
    if len(found)!=1 or found[0]['role']!='Viewer':raise ValueError('Viewer readback mismatch')
    result['status']='READ_GRANTS_VERIFIED';save();return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('plan','journal','azure-python','cli-packages','receipt'):p.add_argument('--'+name,required=True)
    a=p.parse_args();r=grant(a.plan,a.journal,a.azure_python,a.cli_packages,a.receipt)
    print(json.dumps(dict(database=r['database'],workspace=r['workspace'],status=r['status'],write_grants=0)))


if __name__=='__main__':main()
