# Deployment prepends environment parameters and the shared gold_models.py source.
import json
from datetime import datetime, timezone
from uuid import uuid4
from pyspark.sql import functions as F
from delta.tables import DeltaTable

spark.conf.set("spark.sql.session.timeZone", "UTC")
spark.conf.set("spark.sql.ansi.enabled", "true")
run_id = str(uuid4())
started = datetime.now(timezone.utc).isoformat()
silver = f"abfss://{WORKSPACE}@onelake.dfs.fabric.microsoft.com/{SILVER_ID}"
gold = f"abfss://{WORKSPACE}@onelake.dfs.fabric.microsoft.com/{GOLD_ID}"
assert SILVER_BINDING['status']=='BOUND_SILVER'
source_report = SILVER_BINDING['report']
assert source_report['status'] == 'READY', 'Silver is not READY'
silver_run_id = source_report['run_id']
input_keys = {
 'dim_customer':['customer_id'], 'dim_product':['product_id'],
 'fact_order':['order_id'], 'fact_order_line':['order_line_id'],
 'fact_payment':['payment_id'], 'fact_refund':['refund_id'],
 'fact_refund_line':['refund_id','order_line_id']
}
versions, frames, checks = {}, {}, {}
def check(name, condition):
    checks[name] = bool(condition)
    assert condition, name

for name, keys in input_keys.items():
    source = source_report['outputs'][name]
    path = source['path']
    assert path == f"{silver}/Tables/{name}"
    check(f'{name}:identity', DeltaTable.forPath(spark,path).detail().select('id').first()[0] == source['delta_table_id'])
    versions[name] = source['delta_version']
    df = spark.read.format('delta').option('versionAsOf',versions[name]).load(path).cache()
    n = df.count()
    check(f'{name}:schema', df.schema.jsonValue() == source['schema'])
    check(f'{name}:count', n == source_report['silver_counts'][name])
    check(f'{name}:keys', df.select(*keys).distinct().count() == n and not df.where(' OR '.join(f'`{k}` IS NULL' for k in keys)).limit(1).count())
    observed = [r[0] for r in df.select('_silver_run_id').distinct().collect()]
    check(f'{name}:run', observed == [silver_run_id])
    for column, value in {'_source_snapshot_id':source_report['bronze_binding']['source_snapshot_id'],
                          '_source_manifest_sha256':source_report['bronze_binding']['source_manifest_sha256'],
                          '_bronze_proof_sha256':source_report['bronze_binding']['bronze_proof_sha256']}.items():
        check(f'{name}:{column}', [r[0] for r in df.select(column).distinct().collect()] == [value])
    df.createOrReplaceTempView('s_'+name)
    frames[name] = df

outputs, counts = {}, {}
for name, query in QUERIES.items():
    df = spark.sql(query).cache()
    n = df.count()
    check(f'{name}:keys', df.select(*KEYS[name]).distinct().count() == n and not df.where(' OR '.join(f'`{k}` IS NULL' for k in KEYS[name])).limit(1).count())
    df.createOrReplaceTempView('g_'+name)
    outputs[name], counts[name] = df, n

check('order grain', counts['order_summary'] == source_report['silver_counts']['fact_order'])
check('line grain', counts['order_line_summary'] == source_report['silver_counts']['fact_order_line'])
check('refund grain', counts['refund_summary'] == source_report['silver_counts']['fact_refund'])

def no_rows(name, query):
    failures = spark.sql(query).limit(3).collect()
    if failures:
        diagnostic = json.dumps({'status':'FAILED','run_id':run_id,'failed_check':name,
          'examples':[r.asDict() for r in failures]},default=str,indent=2)
        notebookutils.fs.put(f'{gold}/Files/validation/{run_id}-failure.json',diagnostic,True)
        notebookutils.fs.put(f'{gold}/Files/validation/last-failure.json',diagnostic,True)
        print(diagnostic)
    check(name, not failures)

no_rows('order reconciliation', """SELECT g.*,o.captured_amount source_captured,o.refunded_amount source_refunded,o.net_amount source_net,o.total_amount source_total,o.tax_amount source_tax,o.discount_amount source_discount,o.subtotal source_gross FROM s_fact_order o JOIN g_order_summary g ON g.order_id=o.order_id
 WHERE g.captured_amount<>o.captured_amount OR g.refund_amount<>o.refunded_amount
 OR g.net_cash_amount<>o.net_amount OR g.captured_amount<>g.sales_amount+g.tax_amount
 OR g.net_cash_amount<>g.net_sales_amount+g.net_tax_amount
 OR g.sales_amount<>g.gross_sales_amount-g.discount_amount
 OR (o.captured_amount>0 AND (g.captured_amount<>o.total_amount OR g.tax_amount<>o.tax_amount OR g.discount_amount<>o.discount_amount OR g.gross_sales_amount<>o.subtotal))
 OR (o.status='PENDING_PAYMENT' AND g.captured_amount<>0)""")
no_rows('refund reconciliation', "SELECT refund_id FROM g_refund_summary WHERE refund_amount<>refunded_sales_amount+refunded_tax_amount")
no_rows('nonnegative line measures', 'SELECT order_line_id FROM g_order_line_summary WHERE ' + ' OR '.join(f'{c}<0 OR {c} IS NULL' for c in ADDITIVE))
no_rows('cancelled orders fully reversed', "SELECT order_id FROM g_order_summary WHERE status='CANCELLED' AND (net_sales_amount<>0 OR net_tax_amount<>0 OR net_cash_amount<>0 OR net_units<>0 OR captured_amount<>refund_amount)")

def totals(df, columns):
    return {r['currency']:{c:r[c] for c in columns} for r in df.groupBy('currency').agg(*[F.sum(c).alias(c) for c in columns]).collect()}

reference = totals(outputs['order_summary'], ADDITIVE)
for name in ('order_line_summary','sales_daily','sales_by_customer','sales_by_product'):
    check(f'{name}:money and units', totals(outputs[name], ADDITIVE) == reference)
refund_totals = totals(outputs['refund_summary'], ('refund_amount','refunded_sales_amount','refunded_tax_amount','units_returned'))
for currency, measures in reference.items():
    for metric in ('refund_amount','refunded_sales_amount','refunded_tax_amount','units_returned'):
        check(f'refund:{currency}:{metric}', refund_totals.get(currency,{}).get(metric,0) == measures[metric])
check('daily order counts', outputs['sales_daily'].agg(F.sum('order_count')).first()[0] == counts['order_summary'])
check('customer order counts', outputs['sales_by_customer'].agg(F.sum('order_count')).first()[0] == counts['order_summary'])

# Independent captured-payment/header-refund check, grouped by currency.
independent = spark.sql("""SELECT o.currency,SUM(p.amount) captured_amount FROM s_fact_payment p
 JOIN s_fact_order o ON o.order_id=p.order_id WHERE p.payment_status='CAPTURED' GROUP BY o.currency""")
for row in independent.collect():
    check(f'captured payments:{row.currency}', row.captured_amount == reference[row.currency]['captured_amount'])

for name, version in versions.items():
    check(f'{name}:identity stable', DeltaTable.forPath(spark,f'{silver}/Tables/{name}').detail().select('id').first()[0] == source_report['outputs'][name]['delta_table_id'])

# Publish reporting dimensions in the same run as the six reporting aggregates.
customers=outputs['order_summary'].select('customer_id','customer_name','customer_segment','state_code','country_code').distinct()
products=outputs['order_line_summary'].select('product_id','product_name','category','subcategory').distinct()
days=outputs['order_summary'].select(F.col('order_day').alias('date')).union(outputs['refund_summary'].select(F.col('refund_day').alias('date')))
bounds=days.agg(F.min('date').alias('first'),F.max('date').alias('last')).first()
dates=spark.sql(f"SELECT explode(sequence(DATE '{bounds['first']}',DATE '{bounds['last']}',INTERVAL 1 DAY)) date")
dates=(dates.withColumn('year',F.year('date')).withColumn('month_number',F.month('date'))
 .withColumn('month',F.date_format('date','MMM')).withColumn('year_month',F.date_format('date','yyyy-MM'))
 .withColumn('quarter',F.concat(F.lit('Q'),F.quarter('date'))))
for name,df,key in [('dim_customer',customers,'customer_id'),('dim_product',products,'product_id'),('dim_date',dates,'date')]:
    counts[name]=df.count()
    check(f'{name}:keys',df.select(key).distinct().count()==counts[name] and not df.where(F.col(key).isNull()).limit(1).count())
    outputs[name]=df

report = {'status':'RUNNING','run_id':run_id,'started_utc':started,'silver_run_id':silver_run_id,
 'silver_binding':SILVER_BINDING,'outputs':{},
 'silver_versions':versions,'bronze_pipeline_run_id':source_report['bronze_pipeline_run_id'],
 'checks':checks,'counts':counts,'totals_by_currency':reference,
 'sample_order':[r.asDict() for r in outputs['order_summary'].where("order_id='ORD-000002'").collect()],
 'sample_lines':[r.asDict() for r in outputs['order_line_summary'].where("order_id='ORD-000002'").collect()]}
notebookutils.fs.put(f'{gold}/Files/validation/latest.json',json.dumps(report,default=str,indent=2),True)
try:
    for name, df in outputs.items():
        published = (df.withColumn('_gold_run_id',F.lit(run_id))
         .withColumn('_silver_run_id',F.lit(silver_run_id))
         .withColumn('_source_snapshot_id',F.lit(source_report['bronze_binding']['source_snapshot_id']))
         .withColumn('_source_manifest_sha256',F.lit(source_report['bronze_binding']['source_manifest_sha256']))
         .withColumn('_silver_proof_sha256',F.lit(SILVER_BINDING['silver_proof_sha256']))
         .withColumn('_processed_at_utc',F.to_timestamp(F.lit(started)))
         .withColumn('_silver_versions',F.lit(json.dumps(versions,sort_keys=True))))
        path=f'{gold}/Tables/{name}'
        published.write.format('delta').mode('overwrite').option('overwriteSchema','true').save(path)
        table=DeltaTable.forPath(spark,path)
        identity=table.detail().select('id').first()[0]
        version=table.history(1).select('version').first()[0]
        actual=spark.read.format('delta').option('versionAsOf',version).load(path)
        check(f'{name}:persisted schema',[(f.name,f.dataType.simpleString()) for f in actual.schema.fields]==[(f.name,f.dataType.simpleString()) for f in published.schema.fields])
        check(f'{name}:persisted rows', actual.count()==counts[name] and not published.exceptAll(actual).limit(1).count() and not actual.exceptAll(published).limit(1).count())
        report['outputs'][name]={'path':path,'delta_table_id':identity,'delta_version':version,'rows':counts[name],
                                 'schema':actual.schema.jsonValue(),'content_reconciled':True}
    for name,output in report['outputs'].items():
        table=DeltaTable.forPath(spark,output['path'])
        check(f'{name}:output stable',table.detail().select('id').first()[0]==output['delta_table_id'] and table.history(1).select('version').first()[0]==output['delta_version'])
    report['status']='READY'
except Exception as exc:
    report['status']='FAILED'
    report['failure']=str(exc)[:1000]
    raise
finally:
    report['finished_utc']=datetime.now(timezone.utc).isoformat()
    notebookutils.fs.put(f'{gold}/Files/validation/{run_id}.json',json.dumps(report,default=str,indent=2),True)
    notebookutils.fs.put(f'{gold}/Files/validation/latest.json',json.dumps(report,default=str,indent=2),True)
    for df in list(outputs.values())+list(frames.values()):
        df.unpersist()
print(json.dumps({'status':report['status'],'run_id':run_id,'counts':counts}))
