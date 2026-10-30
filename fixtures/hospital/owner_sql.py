"""Load hospital sources using the existing Azure owner's Entra sign-in.

No passwords, grants, identities or authentication settings are changed.
Only the two explicitly approved HealthNet databases can be targets.
"""
import argparse
from datetime import datetime
import json
from pathlib import Path
import sqlite3
import subprocess
from .schema import CLINICAL,BILLING,columns,ddl

SERVER='sql-orderops-9696025.database.windows.net'


def load(directory,azure_python):
    import certifi
    import pytds
    directory=Path(directory)
    if not json.loads((directory/'verification.json').read_text())['all_passed']:raise ValueError('Source verification must pass first')
    az=[str(azure_python),'-m','azure.cli']
    def token():
        return json.loads(subprocess.check_output(az+['account','get-access-token','--resource','https://database.windows.net/','-o','json']))['accessToken']
    journal_path=directory/'sql-load.json'
    journal=json.loads(journal_path.read_text())if journal_path.exists()else{'tables':{},'identity':'existing Azure owner; Entra access token in memory only'}
    def save():journal_path.write_text(json.dumps(journal,indent=2)+'\n',encoding='utf8')
    for system,definitions in [('clinical',CLINICAL),('billing',BILLING)]:
        database='hn_'+system
        with pytds.connect(server=SERVER,database=database,access_token_callable=token,cafile=certifi.where(),
                          timeout=180,login_timeout=60,appname='HealthNet-owner-build')as target:
            cursor=target.cursor()
            cursor.execute("SELECT COUNT(*)FROM sys.tables WHERE schema_id=SCHEMA_ID('app')")
            existing=cursor.fetchone()[0]
            if not existing:
                cursor.execute(ddl(system,'azure'));target.commit()
            elif not journal.get('schema_'+system):
                raise ValueError('Unjournaled existing schema; inspect rather than overwrite')
            journal['schema_'+system]=True;save()
            with sqlite3.connect(directory/(database+'.sqlite'))as source:
                for table,definition in definitions.items():
                    key=system+'.'+table
                    cursor.execute('SELECT COUNT(*),COALESCE(MAX(id),0)FROM [app].['+table+']')
                    count,last_id=cursor.fetchone()
                    expected=source.execute('SELECT COUNT(*)FROM ['+table+']').fetchone()[0]
                    if count!=last_id:raise ValueError(('Noncontiguous load; no automatic repair',key,count,last_id))
                    if count>expected:raise ValueError(('Unexpected target population',key))
                    names=[c[0]for c in columns(definition)]
                    timestamps=[i for i,name in enumerate(names)if name.endswith('_utc')or name in('created_at','updated_at')]
                    rows=source.execute('SELECT * FROM ['+table+'] WHERE id>? ORDER BY id',(last_id,))
                    while True:
                        batch=rows.fetchmany(5000)
                        if not batch:break
                        converted=[]
                        for raw in batch:
                            row=list(raw)
                            for i in timestamps:
                                if row[i]is not None:row[i]=datetime.fromisoformat(row[i]).replace(tzinfo=None)
                            converted.append(tuple(row))
                        cursor.copy_to(table_or_view=table,schema='app',columns=names,data=converted,check_constraints=True,keep_nulls=True,rows_per_batch=5000)
                        target.commit()
                        count+=len(batch)
                        journal['tables'][key]={'rows_committed':count,'expected':expected,'complete':False};save()
                    cursor.execute('SELECT COUNT(*)FROM [app].['+table+']');actual=cursor.fetchone()[0]
                    if actual!=expected:raise ValueError(('Row reconciliation failed',key,expected,actual))
                    journal['tables'][key]={'rows_committed':actual,'expected':expected,'complete':True};save()
            cursor.execute("SELECT t.name,t.temporal_type_desc,t.history_retention_period,t.history_retention_period_unit_desc FROM sys.tables t WHERE t.schema_id=SCHEMA_ID('app')AND t.temporal_type=2")
            journal['temporal_'+system]=[list(r)for r in cursor.fetchall()];save()
    journal['complete']=True;save()
    return journal


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--directory',required=True)
    p.add_argument('--azure-python',required=True)
    a=p.parse_args()
    print(json.dumps(load(a.directory,a.azure_python),indent=2))
