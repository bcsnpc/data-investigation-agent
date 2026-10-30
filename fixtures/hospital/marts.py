"""Owner-build relational transformations and independent local baselines.

No DIA engine or expectations. Source audit fields survive transformations.
The warehouse SQL artifact is generated from the same explicit projections.
"""
import json
from pathlib import Path
import sqlite3
from .generate import canonical_hash

# Every business link is explicit, never inferred from similar display names.
PROJECTIONS={
 'core_facility':('clinical','SELECT * FROM {c}facility'),
 'core_department':('clinical','SELECT * FROM {c}department'),
 'core_provider':('clinical','SELECT * FROM {c}provider'),
 'core_provider_department_history':('clinical','SELECT * FROM {c}provider_assignment'),
 'core_payer':('billing','SELECT * FROM {b}payer'),
 'core_payer_plan_history':('billing','SELECT * FROM {b}payer_plan_history'),
 'stg_patient':('clinical',"SELECT p.*,COALESCE(m.survivor_id,p.id) mpi_patient_id FROM {c}patient p LEFT JOIN {c}patient_merge m ON m.duplicate_id=p.id"),
 'mart_encounter':('clinical',"""SELECT e.*,COALESCE(m.survivor_id,e.patient_id) mpi_patient_id,
   p.mrn masked_mrn,p.given_name masked_given_name,p.family_name masked_family_name,
   d.service_line,pa.department_id service_provider_department_id
   FROM {c}encounter e JOIN {c}patient p ON p.id=e.patient_id
   JOIN {c}department d ON d.id=e.department_id
   LEFT JOIN {c}patient_merge m ON m.duplicate_id=e.patient_id
   LEFT JOIN {c}provider_assignment pa ON pa.provider_id=e.attending_provider_id
   AND e.service_day>=pa.valid_from AND e.service_day<pa.valid_to
   WHERE e.is_deleted=0 AND p.is_deleted=0"""),
 'mart_ed_visit':('clinical',"SELECT v.*,e.facility_id,e.department_id,e.attending_provider_id,e.service_day FROM {c}ed_visit_detail v JOIN {c}encounter e ON e.id=v.encounter_id WHERE e.is_deleted=0"),
 'mart_order':('clinical',"""SELECT l.*,h.encounter_id,h.provider_id,h.order_type,e.facility_id,e.department_id,e.service_day
   FROM {c}order_line l JOIN {c}order_header h ON h.id=l.order_header_id
   JOIN {c}encounter e ON e.id=h.encounter_id WHERE l.is_deleted=0 AND e.is_deleted=0"""),
 'mart_charge':('billing',"""SELECT c.*,a.encounter_number,a.facility_id,a.payer_plan_id,h.payer_id
   FROM {b}charge c JOIN {b}account a ON a.id=c.account_id
   JOIN {b}payer_plan_history h ON h.payer_plan_id=a.payer_plan_id
   AND c.service_date>=h.valid_from AND c.service_date<h.valid_to
   WHERE c.is_deleted=0 AND a.is_deleted=0"""),
 'mart_claim':('billing',"SELECT c.*,a.facility_id,a.payer_plan_id FROM {b}claim c JOIN {b}account a ON a.id=c.account_id WHERE c.is_deleted=0 AND a.is_deleted=0"),
 'mart_remittance':('billing',"""SELECT l.*,r.claim_id,r.received_at,c.account_id,c.is_original,c.is_final,a.facility_id,a.payer_plan_id
   FROM {b}remittance_line l JOIN {b}remittance r ON r.id=l.remittance_id
   JOIN {b}claim c ON c.id=r.claim_id JOIN {b}account a ON a.id=c.account_id
   WHERE l.is_deleted=0 AND r.is_deleted=0 AND c.is_deleted=0 AND a.is_deleted=0"""),
 'mart_payment':('billing',"SELECT p.*,a.facility_id,a.payer_plan_id FROM {b}payment p JOIN {b}account a ON a.id=p.account_id WHERE p.is_deleted=0 AND a.is_deleted=0"),
 'mart_adjustment':('billing',"SELECT p.*,a.facility_id,a.payer_plan_id FROM {b}adjustment p JOIN {b}account a ON a.id=p.account_id WHERE p.is_deleted=0 AND a.is_deleted=0"),
 'mart_ar_aging':('billing','SELECT * FROM {b}ar_snapshot_daily WHERE is_deleted=0'),
 'mart_procedure':('clinical',"""SELECT p.*,e.facility_id,e.department_id,e.service_day FROM {c}procedure p
   JOIN {c}encounter e ON e.id=p.encounter_id WHERE p.is_deleted=0 AND e.is_deleted=0"""),
}


def warehouse_sql():
    sql=["-- HealthNet only. Run against hn_dw after the initial pipeline copy.",
         "CREATE TABLE dbo.load_watermark(source_system VARCHAR(20),table_name VARCHAR(100),watermark_utc DATETIME2(6),watermark_id BIGINT);",
         "CREATE TABLE dbo.load_audit(run_id VARCHAR(100),pipeline_name VARCHAR(100),table_name VARCHAR(100),started_utc DATETIME2(6),ended_utc DATETIME2(6),status VARCHAR(30),rows_read BIGINT,rows_written BIGINT,watermark_utc DATETIME2(6));"]
    for name,(_,query)in PROJECTIONS.items():
        c='[hn_raw].[dbo].[raw_clinical_';b='[hn_raw].[dbo].[raw_billing_'
        # Token replacement is on schema-known table tokens, not SQL names supplied by users.
        import re
        q=re.sub(r'\{c\}([a-z_]+)',lambda m:c+m[1]+']',query)
        q=re.sub(r'\{b\}([a-z_]+)',lambda m:b+m[1]+']',q)
        sql.append(f"CREATE TABLE dbo.[{name}] AS {q};")
        sql.append(f"CREATE OR ALTER PROCEDURE dbo.[sp_{name}] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[{name}]; INSERT INTO dbo.[{name}] {q}; COMMIT; END;\nGO")
    sql.append('CREATE OR ALTER PROCEDURE dbo.sp_run_all AS BEGIN SET NOCOUNT ON;\n'+'\n'.join('EXEC dbo.[sp_'+n+'];'for n in PROJECTIONS)+'\nEND;\nGO')
    return '\n\n'.join(sql)+'\n'


VISUALS=[
 ('operations','Encounters','SELECT COUNT(*) FROM mart_encounter'),
 ('operations','Unique Patients','SELECT COUNT(DISTINCT mpi_patient_id) FROM mart_encounter'),
 ('operations','Admissions','SELECT COUNT(*) FROM mart_encounter WHERE admit_utc IS NOT NULL'),
 ('operations','Discharges','SELECT COUNT(*) FROM mart_encounter WHERE discharge_utc IS NOT NULL'),
 ('operations','ALOS by Service','SELECT service_line,AVG(julianday(discharge_utc)-julianday(admit_utc)) FROM mart_encounter WHERE admit_utc IS NOT NULL AND discharge_utc IS NOT NULL GROUP BY service_line ORDER BY service_line'),
 ('operations','ED Arrivals by Hour',"SELECT substr(arrival_local,12,2),COUNT(*) FROM mart_ed_visit GROUP BY substr(arrival_local,12,2) ORDER BY 1"),
 ('operations','ED Door-to-Provider','SELECT door_to_provider_minutes FROM mart_ed_visit WHERE door_to_provider_minutes IS NOT NULL ORDER BY door_to_provider_minutes'),
 ('operations','LWBS %','SELECT AVG(lwbs) FROM mart_ed_visit'),
 ('operations','Orders by Type and Status','SELECT order_type,status,COUNT(*) FROM mart_order GROUP BY order_type,status ORDER BY 1,2'),
 ('operations','Turnaround by Type','SELECT order_type,AVG((julianday(completed_utc)-julianday(ordered_utc))*1440) FROM mart_order WHERE completed_utc IS NOT NULL AND status=\'RESULTED\' GROUP BY order_type ORDER BY 1'),
 ('operations','Patient Detail','SELECT masked_mrn,masked_given_name,masked_family_name,encounter_number FROM mart_encounter ORDER BY id LIMIT 100'),
 ('revenue','Gross by Service Month',"SELECT substr(service_date,1,7),SUM(amount_cents) FROM mart_charge GROUP BY substr(service_date,1,7) ORDER BY 1"),
 ('revenue','Gross by Post Month',"SELECT substr(post_date,1,7),SUM(amount_cents) FROM mart_charge GROUP BY substr(post_date,1,7) ORDER BY 1"),
 ('revenue','Collections by Month',"SELECT substr(payment_date,1,7),SUM(amount_cents) FROM mart_payment GROUP BY substr(payment_date,1,7) ORDER BY 1"),
 ('revenue','Net Revenue','SELECT (SELECT SUM(amount_cents)FROM mart_charge)+(SELECT SUM(amount_cents)FROM mart_adjustment)'),
 ('revenue','Payer Mix','SELECT payer_id,SUM(amount_cents) FROM mart_charge GROUP BY payer_id ORDER BY 1'),
 ('revenue','Denials by Category',"SELECT denial_category,SUM(denied_cents) FROM mart_remittance WHERE is_original=1 GROUP BY denial_category ORDER BY 1"),
 ('revenue','Initial Denial Rate',"SELECT AVG(status='DENIED') FROM mart_claim WHERE is_original=1 AND status<>'SUBMITTED'"),
 ('revenue','Final Denial Rate',"SELECT AVG(status='DENIED') FROM mart_claim WHERE is_final=1 AND status<>'SUBMITTED'"),
 ('revenue','A/R Aging',"SELECT aging_bucket,SUM(balance_cents)FROM mart_ar_aging WHERE snapshot_date='2026-10-29'GROUP BY aging_bucket ORDER BY 1"),
 ('revenue','Writeoffs',"SELECT adjustment_type,SUM(amount_cents)FROM mart_adjustment GROUP BY adjustment_type ORDER BY 1"),
 ('productivity','Visits per Doctor','SELECT attending_provider_id,COUNT(*) FROM mart_encounter WHERE attending_provider_id IS NOT NULL GROUP BY attending_provider_id ORDER BY 1'),
 ('productivity','Procedure Workload','SELECT provider_id,SUM(workload_units) FROM mart_procedure GROUP BY provider_id ORDER BY 1'),
 ('productivity','Orders per Doctor','SELECT provider_id,COUNT(*)FROM mart_order GROUP BY provider_id ORDER BY 1'),
 ('productivity','Department Leaderboard','SELECT service_provider_department_id,COUNT(*)FROM mart_encounter GROUP BY service_provider_department_id ORDER BY 2 DESC,1'),
]


def build_local(directory):
    directory=Path(directory)
    db=sqlite3.connect(directory/'hn_dw.sqlite')
    if db.execute("SELECT COUNT(*)FROM sqlite_master WHERE type='table'").fetchone()[0]:raise FileExistsError('Local warehouse already populated')
    db.execute('ATTACH DATABASE ? AS clinical',(str(directory/'hn_clinical.sqlite'),))
    db.execute('ATTACH DATABASE ? AS billing',(str(directory/'hn_billing.sqlite'),))
    for name,(_,query)in PROJECTIONS.items():
        db.execute('CREATE TABLE ['+name+'] AS '+query.format(c='clinical.',b='billing.'))
        db.execute('CREATE UNIQUE INDEX ix_'+name+'_id ON ['+name+'](id)')
    # Explicit masking, even though every source identity is fictional.
    db.execute("UPDATE mart_encounter SET masked_mrn='SYN-***-'||substr(masked_mrn,-4),masked_given_name=substr(masked_given_name,1,1)||'***',masked_family_name=substr(masked_family_name,1,1)||'***'")
    db.commit()
    baseline={}
    for estate,title,sql in VISUALS:
        rows=db.execute(sql).fetchall()
        if title=='ED Door-to-Provider':
            import statistics
            rows=[[statistics.median(r[0]for r in rows)if rows else None]]
        baseline[estate+'/'+title]={'sql':sql,'rows':rows,'native_model_checked':False}
    counts={name:{'rows':db.execute('SELECT COUNT(*)FROM ['+name+']').fetchone()[0],'canonical_sha256':canonical_hash(db,name)}for name in PROJECTIONS}
    db.close()
    report={'source':'local independently evaluated SQL','marts':counts,'visuals':baseline,'native_reconciliation':'PENDING'}
    (directory/'baseline.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    (directory/'warehouse.sql').write_text(warehouse_sql(),encoding='utf8')
    return report
