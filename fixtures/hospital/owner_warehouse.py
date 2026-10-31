"""Bootstrap the approved HealthNet warehouse with the existing owner only.

Tokens remain in memory. An existing nonempty warehouse is inspected rather
than overwritten after a failed or uncertain attempt.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
from contextlib import contextmanager
from .marts import bootstrap_sql


def routed_address(host,instance):
    """Separate a server-supplied TDS instance from its DNS/TLS hostname."""
    if '\\'not in host:return host,instance
    hostname,separator,native_instance=host.partition('\\')
    if not hostname.lower().endswith('.pbidedicated.windows.net')or not native_instance or '\\'in native_instance:
        raise ValueError('Unexpected named-instance routing address')
    return hostname,native_instance


@contextmanager
def named_instance_routing(driver):
    # python-tds parses instances on the initial server, but passes ENVCHANGE
    # redirect server strings straight to DNS. Keep the native instance and
    # native port for login; certificate checks still validate the real host.
    original=driver._connect
    def connect(*args,**kwargs):
        kwargs['host'],kwargs['instance']=routed_address(kwargs['host'],kwargs['instance'])
        return original(*args,**kwargs)
    driver._connect=connect
    try:yield
    finally:driver._connect=original


def bootstrap(requirements, receipt, azure_python, azure_profile):
    import certifi
    import pytds
    settings=json.loads(Path(requirements).read_text())
    if settings['warehouse_id']!='ef705467-9870-481c-b977-aad877b83c30':
        raise ValueError('Only the approved HealthNet warehouse is allowed')
    env=dict(os.environ,AZURE_CONFIG_DIR=str(azure_profile))
    def token():
        return json.loads(subprocess.check_output([str(azure_python),'-m','azure.cli',
            'account','get-access-token','--resource','https://database.windows.net/',
            '--tenant','dff91047-ebc2-4657-8dbe-5af328d57780','-o','json'],env=env))['accessToken']
    result={'database_id':settings['warehouse_id'],'server':settings['warehouse_server'],
            'identity':'existing Fabric owner via isolated Azure profile',
            'operation':'HealthNet bootstrap only; no grants'}
    try:
        with named_instance_routing(pytds),pytds.connect(server=settings['warehouse_server'],database=settings['warehouse_id'],
                          access_token_callable=token,cafile=certifi.where(),
                          timeout=180,login_timeout=60,appname='HealthNet-owner-build')as connection:
            cursor=connection.cursor()
            cursor.execute('SELECT SUSER_SNAME(),CURRENT_USER')
            result['served_identity']=list(cursor.fetchone())
            cursor.execute('SELECT name FROM sys.tables ORDER BY name')
            result['tables_before']=[r[0]for r in cursor.fetchall()]
            if result['tables_before']:
                result['status']='EXISTING_TABLES_INSPECT_BEFORE_RESUME'
            else:
                cursor.execute(bootstrap_sql())
                connection.commit()
                cursor.execute('SELECT name FROM sys.tables ORDER BY name')
                result['tables_after']=[r[0]for r in cursor.fetchall()]
                cursor.execute('SELECT (SELECT COUNT(*)FROM dbo.core_date),(SELECT COUNT(*)FROM dbo.security_mapping)')
                result['calendar_rows'],result['security_rows']=cursor.fetchone()
                result['status']='SUCCEEDED'
    except Exception as error:
        result.update(status='FAILED',error_type=type(error).__name__,error=str(error))
    Path(receipt).write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--requirements',required=True)
    p.add_argument('--receipt',required=True)
    p.add_argument('--azure-python',required=True)
    p.add_argument('--azure-profile',required=True)
    a=p.parse_args()
    result=bootstrap(a.requirements,a.receipt,a.azure_python,a.azure_profile)
    print(json.dumps(result,indent=2))
    if result['status']!='SUCCEEDED':raise SystemExit(1)
