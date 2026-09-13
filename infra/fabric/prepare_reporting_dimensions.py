"""Build reporting dimensions from one validated Gold snapshot. Parameters injected."""
import json
from datetime import datetime, timezone
from delta.tables import DeltaTable
from pyspark.sql import functions as F

spark.conf.set('spark.sql.session.timeZone','UTC')
root=f'abfss://{WORKSPACE}@onelake.dfs.fabric.microsoft.com/{GOLD_ID}'
report=json.loads(notebookutils.fs.head(f'{root}/Files/validation/latest.json',1048576))
assert report['status']=='READY' and all(report['checks'].values())
run=report['run_id']
frames,versions={},{}
for name in ['order_summary','order_line_summary','refund_summary']:
    path=f'{root}/Tables/{name}'
    versions[name]=DeltaTable.forPath(spark,path).history(1).first()['version']
    df=spark.read.format('delta').option('versionAsOf',versions[name]).load(path).cache()
    assert df.count()==report['counts'][name]
    assert [r[0] for r in df.select('_gold_run_id').distinct().collect()]==[run]
    frames[name]=df
orders,lines,refunds=[frames[n] for n in ['order_summary','order_line_summary','refund_summary']]
customers=orders.select('customer_id','customer_name','customer_segment','state_code','country_code').distinct()
products=lines.select('product_id','product_name','category','subcategory').distinct()
days=orders.select(F.col('order_day').alias('date')).union(refunds.select(F.col('refund_day').alias('date')))
bounds=days.agg(F.min('date').alias('first'),F.max('date').alias('last')).first()
dates=spark.sql(f"SELECT explode(sequence(DATE '{bounds['first']}',DATE '{bounds['last']}',INTERVAL 1 DAY)) date")
dates=(dates.withColumn('year',F.year('date')).withColumn('month_number',F.month('date'))
 .withColumn('month',F.date_format('date','MMM')).withColumn('year_month',F.date_format('date','yyyy-MM'))
 .withColumn('quarter',F.concat(F.lit('Q'),F.quarter('date'))))
outputs={'dim_date':(dates,'date'),'dim_customer':(customers,'customer_id'),'dim_product':(products,'product_id')}
evidence={'status':'RUNNING','gold_run_id':run,'gold_versions':versions,'counts':{},'schemas':{}}
notebookutils.fs.put(f'{root}/Files/reporting/latest.json',json.dumps(evidence),True)
try:
    for name,(df,key) in outputs.items():
        n=df.count()
        assert n==df.select(key).distinct().count() and not df.where(F.col(key).isNull()).count(),name
        df=df.withColumn('_gold_run_id',F.lit(run))
        path=f'{root}/Tables/{name}'
        df.write.format('delta').mode('overwrite').option('overwriteSchema','true').save(path)
        actual=spark.read.format('delta').load(path)
        assert actual.count()==n and not df.exceptAll(actual).limit(1).count(),name
        evidence['counts'][name]=n
        evidence['schemas'][name]=actual.schema.jsonValue()
    for name,df in frames.items():
        evidence['schemas'][name]=df.schema.jsonValue()
        assert DeltaTable.forPath(spark,f'{root}/Tables/{name}').history(1).first()['version']==versions[name]
    latest=json.loads(notebookutils.fs.head(f'{root}/Files/validation/latest.json',1048576))
    assert latest['status']=='READY' and latest['run_id']==run
    evidence['status']='READY'
except Exception as exc:
    evidence['status']='FAILED'
    evidence['error']=str(exc)[:2000]
    raise
finally:
    evidence['finished_utc']=datetime.now(timezone.utc).isoformat()
    notebookutils.fs.put(f'{root}/Files/reporting/latest.json',json.dumps(evidence,default=str,indent=2),True)
    for df in frames.values(): df.unpersist()
