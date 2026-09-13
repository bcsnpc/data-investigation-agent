# Deployment prepends WORKSPACE, BRONZE_ID, SNAPSHOT_ID, MANIFEST_SHA256, VERIFY_ONLY.
import hashlib
import json
from pathlib import Path
import tempfile
from datetime import datetime, timezone
from uuid import UUID, uuid4
from pyspark.sql import functions as F, types as T
from delta.tables import DeltaTable

spark.conf.set('spark.sql.session.timeZone','UTC')
spark.conf.set('spark.sql.ansi.enabled','true')
assert str(UUID(SNAPSHOT_ID))==SNAPSHOT_ID
root=f'abfss://{WORKSPACE}@onelake.dfs.fabric.microsoft.com/{BRONZE_ID}'
source=f'{root}/Files/source_snapshots/{SNAPSHOT_ID}'
schema='snapshot_'+SNAPSHOT_ID.replace('-','')
receipt_path=f'{source}/publication.json'

def download(name):
    path=Path(tempfile.gettempdir())/(str(uuid4())+'-'+name)
    notebookutils.fs.cp(source+'/'+name,'file:'+str(path))
    return path

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1048576),b''):h.update(chunk)
    return h.hexdigest()

manifest_file=download('manifest.json')
assert sha(manifest_file)==MANIFEST_SHA256,'Manifest hash mismatch'
manifest=json.loads(manifest_file.read_text());manifest_file.unlink()
assert manifest['status']=='READY' and manifest['isolation']=='SNAPSHOT' and manifest['transaction_completed'] is True
assert manifest['snapshot_id']==SNAPSHOT_ID
expected={'customers','products','orders','order_lines','payments','shipments','shipment_lines','refunds','refund_lines','audit_log'}
assert len(manifest['tables'])==10 and {t['name'] for t in manifest['tables']}==expected
existing=json.loads(notebookutils.fs.head(receipt_path,1048576)) if notebookutils.fs.exists(receipt_path) else None
if VERIFY_ONLY:assert existing and existing['status']=='COMPLETE'
if existing:assert existing['source_manifest_sha256']==MANIFEST_SHA256

def spark_type(column):
    kind=column['sql_type']
    if kind in ('char','nvarchar','varchar','nchar'):return 'string'
    if kind=='int':return 'int'
    if kind=='bit':return 'boolean'
    if kind=='datetime2':return 'timestamp'
    if kind=='decimal':return f"decimal({int(column['precision'])},{int(column['scale'])})"
    raise ValueError('Unsupported SQL type: '+kind)

frames={}
for table in manifest['tables']:
    name=table['name'];assert table['file']==name+'.jsonl'
    local=download(table['file'])
    assert sha(local)==table['sha256'],'Uploaded source hash differs'
    # Materialize the exact driver-verified bytes, rather than rereading a mutable remote path.
    with local.open(encoding='utf-8') as stream:
        text=spark.createDataFrame(((line.rstrip('\n'),) for line in stream),'value string')
    local.unlink()
    raw=text.select(F.from_json('value',T.ArrayType(T.StringType())).alias('r')).cache()
    assert not raw.where(F.col('r').isNull() | (F.size('r')!=len(table['columns']))).limit(1).count()
    expressions=[];invalid=F.lit(False)
    for i,column in enumerate(table['columns']):
        original=F.col('r')[i];kind=spark_type(column);typed=original.cast(kind)
        if kind=='timestamp':back=F.concat(F.date_format(typed,"yyyy-MM-dd'T'HH:mm:ss.SSSSSS"),F.lit('0'))
        elif kind=='boolean':back=typed.cast('string')
        else:back=typed.cast('string')
        expected_value=F.lower(original) if kind=='boolean' else original
        invalid=invalid | (original.isNotNull() & (typed.isNull() | (back!=expected_value)))
        if column['nullable']=='False':invalid=invalid | original.isNull()
        expressions.append(typed.alias(column['name']))
    assert not raw.where(invalid).limit(1).count(),'Lossy type conversion or nullability violation: '+name
    frame=raw.select(*expressions).cache()
    assert frame.count()==table['rows']
    frames[name]=frame
    raw.unpersist()

if not VERIFY_ONLY and not existing:
    # Fail before writing any output if any planned destination already exists.
    assert all(not notebookutils.fs.exists(f'{root}/Tables/{schema}/{t["name"]}') for t in manifest['tables'])
    spark.sql(f'CREATE SCHEMA IF NOT EXISTS {schema}')

records=[]
for table in manifest['tables']:
    name=table['name'];destination=f'{root}/Tables/{schema}/{name}'
    if not VERIFY_ONLY and not existing:
        frames[name].write.format('delta').mode('errorifexists').save(destination)
    delta=DeltaTable.forPath(spark,destination)
    identity=delta.detail().select('id').first()[0]
    version=int(delta.history(1).select('version').first()[0])
    if existing:
        record=next(t for t in existing['tables'] if t['source_table']==name)
        assert identity==record['delta_table_id'] and version==record['delta_version'],'Published Delta identity/version changed'
        version=record['delta_version']
    actual=spark.read.format('delta').option('versionAsOf',version).load(destination)
    assert [(f.name,f.dataType.simpleString()) for f in actual.schema.fields]==[(f.name,f.dataType.simpleString()) for f in frames[name].schema.fields]
    assert actual.count()==table['rows']
    assert not actual.exceptAll(frames[name]).limit(1).count(),'Extra/different rows'
    assert not frames[name].exceptAll(actual).limit(1).count(),'Missing/different rows'
    assert delta.detail().select('id').first()[0]==identity and int(delta.history(1).select('version').first()[0])==version
    records.append({'source_table':name,'destination':destination,'source_sha256':table['sha256'],
                    'source_schema_sha256':table['schema_sha256'],'rows':table['rows'],
                    'delta_table_id':identity,'delta_version':version,'content_reconciled':True,
                    'delta_schema':actual.schema.jsonValue()})
    print('Verified '+name+': '+str(table['rows']),flush=True)
    frames[name].unpersist()

receipt={'format_version':1,'status':'COMPLETE','source_snapshot_id':SNAPSHOT_ID,
         'mode':'VERIFY_ONLY' if VERIFY_ONLY else 'PUBLISH',
         'source_manifest_sha256':MANIFEST_SHA256,'tables':records,
         'verified_at':datetime.now(timezone.utc).isoformat(),'verification_id':str(uuid4())}
if VERIFY_ONLY:
    notebookutils.fs.put(source+'/verification-'+receipt['verification_id']+'.json',json.dumps(receipt,indent=2),False)
elif not existing:
    notebookutils.fs.put(receipt_path,json.dumps(receipt,indent=2),False)
print(json.dumps({'status':'COMPLETE','verify_only':VERIFY_ONLY,'snapshot_id':SNAPSHOT_ID,'verification_id':receipt['verification_id'],'tables':10,'rows':sum(t['rows'] for t in records)}))
