"""Read-only native source reconciliation against the seeded source hashes."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sqlite3
from contextlib import closing
from .schema import CLINICAL,BILLING,columns
from .owner_sql import SERVER


def source_row(row,expected=None):
    """Restore the generator's UTC string representation after DATETIME2 reads."""
    result=[]
    for index,value in enumerate(row):
        if isinstance(value,datetime):
            native=value.replace(tzinfo=timezone.utc)if value.tzinfo is None else value.astimezone(timezone.utc)
            original=expected[index]if expected is not None else None
            # Source audit stamps can be date-only or full UTC ISO. Preserve
            # their lexical form only after proving the native instant equal.
            if isinstance(original,str):
                parsed=datetime.fromisoformat(original)
                parsed=parsed.replace(tzinfo=timezone.utc)if parsed.tzinfo is None else parsed.astimezone(timezone.utc)
                if parsed==native:
                    result.append(original);continue
            value=native.isoformat(timespec='microseconds'if native.microsecond else'seconds')
        result.append(value)
    return tuple(result)


def hash_rows(rows,expected_rows=None):
    digest=hashlib.sha256();count=0
    expected_rows=iter(expected_rows)if expected_rows is not None else None
    for row in rows:
        expected=next(expected_rows,None)if expected_rows is not None else None
        digest.update(json.dumps(source_row(row,expected),ensure_ascii=True,separators=(',',':')).encode()+b'\n')
        count+=1
    return count,digest.hexdigest()


def reconcile(directory,azure_python):
    import certifi
    import pytds
    directory=Path(directory)
    load=json.loads((directory/'sql-load.json').read_text())
    if not load.get('complete'):raise ValueError('Wait for the existing source load to complete')
    generated=json.loads((directory/'generation.json').read_text())
    path=directory/'native-source-reconciliation.json'
    result=json.loads(path.read_text())if path.exists()else{'tables':{},'identity':'existing Azure owner; read-only reconciliation'}
    def token():
        return json.loads(subprocess.check_output([str(azure_python),'-m','azure.cli','account',
            'get-access-token','--resource','https://database.windows.net/','-o','json']))['accessToken']
    for system,definitions in [('clinical',CLINICAL),('billing',BILLING)]:
        with closing(sqlite3.connect(directory/('hn_'+system+'.sqlite')))as source,pytds.connect(server=SERVER,database='hn_'+system,access_token_callable=token,
                          cafile=certifi.where(),timeout=180,login_timeout=60,
                          appname='HealthNet-owner-readonly-reconciliation')as connection:
            cursor=connection.cursor()
            for table,definition in definitions.items():
                key=system+'.'+table
                if result['tables'].get(key,{}).get('matches'):continue
                names=','.join('['+c[0]+']'for c in columns(definition))
                cursor.execute('SELECT '+names+' FROM [app].['+table+'] ORDER BY id')
                expected_rows=source.execute('SELECT '+names+' FROM ['+table+'] ORDER BY id')
                count,digest=hash_rows(cursor,expected_rows)
                expected=generated['tables'][system][table]
                result['tables'][key]={'rows':count,'canonical_sha256':digest,
                    'expected':expected,'matches':count==expected['rows']and digest==expected['canonical_sha256']}
                path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
                if not result['tables'][key]['matches']:raise ValueError('Native source hash mismatch: '+key)
    result['all_matched']=len(result['tables'])==len(CLINICAL)+len(BILLING)and all(t['matches']for t in result['tables'].values())
    path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--directory',required=True);p.add_argument('--azure-python',required=True)
    a=p.parse_args()
    r=reconcile(a.directory,a.azure_python)
    print(json.dumps({'all_matched':r['all_matched'],'tables':len(r['tables'])}))
