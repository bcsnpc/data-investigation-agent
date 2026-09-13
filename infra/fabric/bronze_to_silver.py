# Fabric PySpark notebook source. The deployment helper inserts PARAMETERS.
import json
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4
from pyspark.sql import functions as F
from delta.tables import DeltaTable

spark.conf.set("spark.sql.session.timeZone", "UTC")
run_id = str(uuid4())
started = datetime.now(timezone.utc).isoformat()
bronze = f"abfss://{WORKSPACE}@onelake.dfs.fabric.microsoft.com/{BRONZE_ID}"
silver = f"abfss://{WORKSPACE}@onelake.dfs.fabric.microsoft.com/{SILVER_ID}"
expected = {"customers":20000,"products":150,"orders":100000,"order_lines":286652,
 "payments":105047,"shipments":95545,"shipment_lines":273805,"refunds":7270,
 "refund_lines":12680,"audit_log":509550}
keys = {"customers":["customer_id"],"products":["product_id"],"orders":["order_id"],
 "order_lines":["order_line_id"],"payments":["payment_id"],"shipments":["shipment_id"],
 "shipment_lines":["shipment_id","order_line_id"],"refunds":["refund_id"],
 "refund_lines":["refund_id","order_line_id"],"audit_log":["event_id"]}
frames = read_pinned_bronze(spark, DeltaTable, BRONZE_BINDING)
versions = {r['source_table']:r['delta_version'] for r in BRONZE_BINDING['tables']}
counts, checks = {}, {}
for name in expected:
    df = frames[name]
    df.createOrReplaceTempView("b_"+name)
    counts[name] = df.count()
    # This first release deliberately accepts only the verified initial baseline.
    assert counts[name] == expected[name], f"Baseline count changed: {name}"
    assert df.select(*keys[name]).distinct().count() == counts[name], f"Duplicate key: {name}"
    null_key = " OR ".join(f"`{key}` IS NULL" for key in keys[name])
    assert not df.where(null_key).limit(1).count(), f"Null key: {name}"

queries = {
 "order_customer": "SELECT o.order_id FROM b_orders o LEFT ANTI JOIN b_customers c ON c.customer_id=o.customer_id",
 "line_order": "SELECT l.order_line_id FROM b_order_lines l LEFT ANTI JOIN b_orders o ON o.order_id=l.order_id",
 "line_product": "SELECT l.order_line_id FROM b_order_lines l LEFT ANTI JOIN b_products p ON p.product_id=l.product_id",
 "order_total": "SELECT o.order_id FROM b_orders o JOIN (SELECT order_id,SUM(line_total+tax_amount) amount FROM b_order_lines GROUP BY order_id) l ON l.order_id=o.order_id WHERE l.amount<>o.total_amount",
 "payment_total": "SELECT o.order_id FROM b_orders o LEFT JOIN (SELECT order_id,SUM(amount) amount FROM b_payments WHERE payment_status='CAPTURED' GROUP BY order_id) p ON p.order_id=o.order_id WHERE (o.status NOT IN ('CANCELLED','PENDING_PAYMENT') AND COALESCE(p.amount,0)<>o.total_amount) OR COALESCE(p.amount,0)>o.total_amount",
 "shipment_line": "SELECT sl.order_line_id FROM b_shipment_lines sl LEFT JOIN b_shipments s ON s.shipment_id=sl.shipment_id LEFT JOIN b_order_lines l ON l.order_line_id=sl.order_line_id WHERE s.shipment_id IS NULL OR l.order_line_id IS NULL OR s.order_id<>l.order_id OR sl.quantity<>l.quantity",
 "refund_payment": "SELECT r.refund_id FROM b_refunds r LEFT JOIN b_payments p ON p.payment_id=r.payment_id WHERE p.payment_id IS NULL OR p.order_id<>r.order_id OR p.payment_status<>'CAPTURED'",
 "refund_line": "SELECT rl.refund_id FROM b_refund_lines rl LEFT JOIN b_refunds r ON r.refund_id=rl.refund_id LEFT JOIN b_order_lines l ON l.order_line_id=rl.order_line_id WHERE r.refund_id IS NULL OR l.order_line_id IS NULL OR r.order_id<>l.order_id OR rl.quantity<>l.quantity OR rl.merchandise_amount<>l.line_total OR rl.tax_amount<>l.tax_amount",
 "refund_total": "SELECT r.refund_id FROM b_refunds r LEFT JOIN (SELECT refund_id,SUM(merchandise_amount+tax_amount) amount FROM b_refund_lines GROUP BY refund_id) l ON l.refund_id=r.refund_id WHERE l.refund_id IS NULL OR l.amount<>r.refund_amount",
 "return_limit": "SELECT l.order_line_id FROM b_order_lines l JOIN (SELECT order_line_id,SUM(quantity) quantity FROM b_refund_lines GROUP BY order_line_id) r ON r.order_line_id=l.order_line_id WHERE r.quantity>l.quantity",
 "order_status": "SELECT order_id FROM b_orders WHERE status NOT IN ('PAID','SHIPPED','DELIVERED','PARTIALLY_RETURNED','RETURNED','CANCELLED','PENDING_PAYMENT') OR status IS NULL"
}
for name, query in queries.items():
    checks[name] = spark.sql(query).count()
assert not any(checks.values()), f"Bronze integrity failures: {checks}"

sample = {}
for name in ("orders","order_lines","payments","shipments","refunds"):
    sample[name] = [r.asDict() for r in frames[name].where("order_id='ORD-000002'").collect()]
sample['shipment_lines'] = [r.asDict() for r in spark.sql("SELECT sl.* FROM b_shipment_lines sl JOIN b_shipments s ON s.shipment_id=sl.shipment_id WHERE s.order_id='ORD-000002'").collect()]
sample['refund_lines'] = [r.asDict() for r in spark.sql("SELECT rl.* FROM b_refund_lines rl JOIN b_refunds r ON r.refund_id=rl.refund_id WHERE r.order_id='ORD-000002'").collect()]
sample['audit_log'] = [r.asDict() for r in spark.sql("""SELECT * FROM b_audit_log WHERE (entity_type='order' AND entity_id='ORD-000002')
 OR (entity_type='payment' AND entity_id IN (SELECT payment_id FROM b_payments WHERE order_id='ORD-000002'))
 OR (entity_type='shipment' AND entity_id IN (SELECT shipment_id FROM b_shipments WHERE order_id='ORD-000002'))
 OR (entity_type='refund' AND entity_id IN (SELECT refund_id FROM b_refunds WHERE order_id='ORD-000002'))""").collect()]
assert sample['orders'][0]['total_amount'] == Decimal('1682.6400')
assert sum(r['refund_amount'] for r in sample['refunds']) == Decimal('153.0000')
assert len(sample['order_lines']) == 2

# Keep source grains and keys. Never multiply order totals by joining raw child rows.
transforms = {
 "dim_customer": "SELECT *,UPPER(TRIM(state)) state_code,UPPER(TRIM(country)) country_code FROM b_customers",
 "dim_product": "SELECT * FROM b_products",
 "fact_order_line": "SELECT l.*,p.category,p.subcategory,(l.discount_amount+l.order_discount_amount) total_discount_amount,(l.line_total+l.tax_amount) payable_amount FROM b_order_lines l JOIN b_products p ON p.product_id=l.product_id",
 "fact_payment": "SELECT *,CASE WHEN payment_status='CAPTURED' THEN amount ELSE CAST(0 AS DECIMAL(19,4)) END captured_amount FROM b_payments",
 "fact_refund": "SELECT * FROM b_refunds",
 "fact_shipment": "SELECT * FROM b_shipments",
 "fact_shipment_line": "SELECT * FROM b_shipment_lines",
 "fact_refund_line": "SELECT * FROM b_refund_lines",
 "fact_audit_event": "SELECT * FROM b_audit_log",
 "fact_order": """SELECT o.*,CAST(o.order_date AS DATE) order_day,
   COALESCE(p.captured_amount,CAST(0 AS DECIMAL(19,4))) captured_amount,
   COALESCE(r.refund_amount,CAST(0 AS DECIMAL(19,4))) refunded_amount,
   COALESCE(p.captured_amount,0)-COALESCE(r.refund_amount,0) net_amount,
   o.total_amount-o.tax_amount net_merchandise_amount
   FROM b_orders o LEFT JOIN (SELECT order_id,SUM(amount) captured_amount FROM b_payments
    WHERE payment_status='CAPTURED' GROUP BY order_id) p ON p.order_id=o.order_id
   LEFT JOIN (SELECT order_id,SUM(refund_amount) refund_amount FROM b_refunds GROUP BY order_id) r ON r.order_id=o.order_id"""
}
outputs = {}
sources = dict(zip(["dim_customer","dim_product","fact_order","fact_order_line","fact_payment","fact_shipment","fact_shipment_line","fact_refund","fact_refund_line","fact_audit_event"], expected.keys()))
for name, query in transforms.items():
    df = spark.sql(query)
    df = (df.withColumn("_silver_run_id",F.lit(run_id))
          .withColumn("_bronze_pipeline_run_id",F.lit(None).cast('string'))
          .withColumn("_source_snapshot_id",F.lit(BRONZE_BINDING['source_snapshot_id']))
          .withColumn("_source_manifest_sha256",F.lit(BRONZE_BINDING['source_manifest_sha256']))
          .withColumn("_bronze_proof_sha256",F.lit(BRONZE_BINDING['bronze_proof_sha256']))
          .withColumn("_processed_at_utc",F.to_timestamp(F.lit(started)))
          .withColumn("_bronze_versions",F.lit(json.dumps(versions,sort_keys=True))))
    assert df.count() == counts[sources[name]], f"Grain changed: {name}"
    outputs[name] = df

# Validate transformations before publishing any output table.
fact = outputs['fact_order']
assert not fact.where('net_amount<0').limit(1).count()
example = fact.where("order_id='ORD-000002'").first().asDict()
assert example['net_amount'] == Decimal('1529.6400')
assert outputs['fact_order_line'].agg(F.sum('payable_amount')).first()[0] == frames['orders'].agg(F.sum('total_amount')).first()[0]

report = {"status":"VALIDATED","run_id":run_id,"started_utc":started,"bronze_pipeline_run_id":None,
 "bronze_binding":BRONZE_BINDING,"outputs":{},
 "bronze_versions":versions,"bronze_counts":counts,"checks":checks,"sample_order":sample,
 "silver_counts":{},"silver_sample_order":example}
report_path = f"{silver}/Files/validation/{run_id}.json"
# Delta overwrites are atomic per table, not across all tables. Publish READY only after every verification passes.
notebookutils.fs.put(f"{silver}/Files/validation/latest.json",json.dumps({"status":"RUNNING","run_id":run_id}),True)
for name, df in outputs.items():
    path = f"{silver}/Tables/{name}"
    df.write.format('delta').mode('overwrite').option('overwriteSchema','true').save(path)
    table = DeltaTable.forPath(spark,path)
    identity = table.detail().select('id').first()[0]
    version = table.history(1).select('version').first()[0]
    actual = spark.read.format('delta').option('versionAsOf',version).load(path)
    n = actual.count()
    assert n == counts[sources[name]], f"Destination count mismatch: {name}"
    assert actual.select(*keys[sources[name]]).distinct().count() == n
    assert [(f.name,f.dataType.simpleString()) for f in actual.schema.fields] == [(f.name,f.dataType.simpleString()) for f in df.schema.fields], f"Destination schema mismatch: {name}"
    assert not actual.exceptAll(df).limit(1).count(), f"Unexpected output rows: {name}"
    assert not df.exceptAll(actual).limit(1).count(), f"Missing output rows: {name}"
    assert table.detail().select('id').first()[0] == identity
    report['outputs'][name] = {'path':path,'delta_table_id':identity,'delta_version':version,
                               'rows':n,'schema':actual.schema.jsonValue(),'content_reconciled':True}
    report['silver_counts'][name] = n
for name, output in report['outputs'].items():
    table = DeltaTable.forPath(spark,output['path'])
    assert table.detail().select('id').first()[0] == output['delta_table_id']
    assert table.history(1).select('version').first()[0] == output['delta_version'], f"Concurrent Silver write: {name}"
report['status']='READY'
report['finished_utc']=datetime.now(timezone.utc).isoformat()
notebookutils.fs.put(report_path,json.dumps(report,default=str,indent=2),True)
notebookutils.fs.put(f"{silver}/Files/validation/latest.json",json.dumps(report,default=str,indent=2),True)
print(json.dumps({"status":"READY","run_id":run_id,"report_path":report_path,"counts":report['silver_counts']}))
