"""Owner-build relational transformations and independent local baselines.

No DIA engine or expectations. Source audit fields survive transformations.
The warehouse SQL artifact is generated from the same explicit projections.
"""
import json
from pathlib import Path
import sqlite3
from datetime import timedelta
from zoneinfo import ZoneInfo
from .generate import START,END
from .generate import canonical_hash
from .schema import CLINICAL,BILLING,columns

# Every business link is explicit, never inferred from similar display names.
PROJECTIONS={
 'core_facility':('clinical','SELECT * FROM {c}facility'),
 'core_department':('clinical','SELECT * FROM {c}department'),
 'core_provider':('clinical','SELECT * FROM {c}provider'),
 'core_provider_department_history':('clinical','SELECT * FROM ref_department_mapping'),
 'core_payer':('billing','SELECT * FROM {b}payer'),
 'core_payer_plan_history':('billing','SELECT * FROM ref_payer_group_history'),
 'stg_patient':('clinical','SELECT * FROM {mpi}'),
 'mart_encounter':('clinical',"""SELECT e.*,p.mpi_patient_id,
   'SYN-***-'||substr(p.mrn,-4) masked_mrn,substr(p.given_name,1,1)||'***' masked_given_name,substr(p.family_name,1,1)||'***' masked_family_name,
   d.service_line,pa.department_id service_provider_department_id
   FROM {c}encounter e JOIN stg_patient p ON p.id=e.patient_id
   JOIN {c}department d ON d.id=e.department_id
   LEFT JOIN core_provider_department_history pa ON pa.provider_id=e.attending_provider_id
   AND e.service_day>=pa.valid_from AND e.service_day<pa.valid_to
   WHERE e.is_deleted=0 AND p.is_deleted=0"""),
 'mart_ed_visit':('clinical',"SELECT v.*,SUBSTRING(v.arrival_local,12,2) arrival_hour,e.facility_id,e.department_id,e.attending_provider_id,e.service_day FROM {c}ed_visit_detail v JOIN {c}encounter e ON e.id=v.encounter_id WHERE e.is_deleted=0"),
 'mart_order':('clinical',"""SELECT l.*,h.encounter_id,h.provider_id,h.order_type,e.facility_id,e.department_id,e.service_day
   FROM {c}order_line l JOIN {c}order_header h ON h.id=l.order_header_id
   JOIN {c}encounter e ON e.id=h.encounter_id WHERE l.is_deleted=0 AND e.is_deleted=0"""),
 'mart_charge':('billing',"""SELECT c.*,a.encounter_number,a.facility_id,e.department_id,a.payer_plan_id,h.payer_id
   FROM {b}charge c JOIN {b}account a ON a.id=c.account_id LEFT JOIN {c}encounter e ON e.encounter_number=a.encounter_number
   JOIN core_payer_plan_history h ON h.payer_plan_id=a.payer_plan_id
   AND c.service_date>=h.valid_from AND c.service_date<h.valid_to
   WHERE c.is_deleted=0 AND a.is_deleted=0"""),
 'mart_claim':('billing',"SELECT c.*,SUBSTRING(c.submitted_at,1,10) submitted_date,a.facility_id,e.department_id,a.payer_plan_id,ph.payer_id FROM {b}claim c JOIN {b}account a ON a.id=c.account_id LEFT JOIN {c}encounter e ON e.encounter_number=a.encounter_number JOIN core_payer_plan_history ph ON ph.payer_plan_id=a.payer_plan_id AND SUBSTRING(c.submitted_at,1,10)>=ph.valid_from AND SUBSTRING(c.submitted_at,1,10)<ph.valid_to WHERE c.is_deleted=0 AND a.is_deleted=0"),
 'mart_remittance':('billing',"""SELECT l.*,r.claim_id,r.received_at,SUBSTRING(r.received_at,1,10) received_date,c.account_id,c.is_original,c.is_final,a.facility_id,e.department_id,a.payer_plan_id,ph.payer_id
   FROM {b}remittance_line l JOIN {b}remittance r ON r.id=l.remittance_id
   JOIN {b}claim c ON c.id=r.claim_id JOIN {b}account a ON a.id=c.account_id LEFT JOIN {c}encounter e ON e.encounter_number=a.encounter_number
   JOIN core_payer_plan_history ph ON ph.payer_plan_id=a.payer_plan_id AND SUBSTRING(r.received_at,1,10)>=ph.valid_from AND SUBSTRING(r.received_at,1,10)<ph.valid_to
   WHERE l.is_deleted=0 AND r.is_deleted=0 AND c.is_deleted=0 AND a.is_deleted=0"""),
 'mart_payment':('billing',"SELECT p.*,a.facility_id,e.department_id,a.payer_plan_id,ph.payer_id FROM {b}payment p JOIN {b}account a ON a.id=p.account_id LEFT JOIN {c}encounter e ON e.encounter_number=a.encounter_number JOIN core_payer_plan_history ph ON ph.payer_plan_id=a.payer_plan_id AND p.payment_date>=ph.valid_from AND p.payment_date<ph.valid_to WHERE p.is_deleted=0 AND a.is_deleted=0"),
 'mart_adjustment':('billing',"SELECT p.*,a.facility_id,e.department_id,a.payer_plan_id,ph.payer_id FROM {b}adjustment p JOIN {b}account a ON a.id=p.account_id LEFT JOIN {c}encounter e ON e.encounter_number=a.encounter_number JOIN core_payer_plan_history ph ON ph.payer_plan_id=a.payer_plan_id AND p.adjustment_date>=ph.valid_from AND p.adjustment_date<ph.valid_to WHERE p.is_deleted=0 AND a.is_deleted=0"),
 'mart_ar_aging':('billing','SELECT * FROM {b}ar_snapshot_daily WHERE is_deleted=0'),
 'mart_procedure':('clinical',"""SELECT p.*,e.facility_id,e.department_id,e.service_day FROM {c}procedure p
   JOIN {c}encounter e ON e.id=p.encounter_id WHERE p.is_deleted=0 AND e.is_deleted=0"""),
 'mart_census_daily':('clinical',"""SELECT d.id*10+f.id id,d.calendar_date,f.id facility_id,
   COUNT(b.id) midnight_census,f.licensed_beds,
   1.0*COUNT(b.id)/f.licensed_beds occupancy_fraction
   FROM core_date d CROSS JOIN {c}facility f
   LEFT JOIN {c}bed bed ON bed.facility_id=f.id
   LEFT JOIN {c}bed_assignment b ON b.bed_id=bed.id
     AND b.start_utc<=d.local_midnight_utc AND (b.end_utc>d.local_midnight_utc OR b.end_utc IS NULL)
   GROUP BY d.id,d.calendar_date,f.id,f.licensed_beds"""),
 'mart_provider_productivity_daily':('clinical',"""SELECT
   ROW_NUMBER()OVER(ORDER BY e.service_day,e.attending_provider_id,e.facility_id,pa.department_id) id,
   e.service_day,e.attending_provider_id provider_id,e.facility_id,pa.department_id,
   COUNT(*) visits,p.fte,
   COALESCE(SUM(pr.workload_units),0) workload_units,
   COALESCE(SUM(pr.procedures),0) procedures,
   COALESCE(SUM(o.orders),0) orders,
   CAST(ROUND(COALESCE(SUM(pr.workload_units),0)*5000,0) AS BIGINT) synthetic_cost_cents,
   CAST(ROUND(COALESCE(SUM(pr.workload_units),0)*2000,0) AS BIGINT) synthetic_margin_cents
   FROM {c}encounter e JOIN {c}provider p ON p.id=e.attending_provider_id
   JOIN core_provider_department_history pa ON pa.provider_id=p.id AND e.service_day>=pa.valid_from AND e.service_day<pa.valid_to
   LEFT JOIN(SELECT encounter_id,COUNT(*) procedures,SUM(workload_units) workload_units FROM {c}procedure WHERE is_deleted=0 GROUP BY encounter_id)pr ON pr.encounter_id=e.id
   LEFT JOIN(SELECT encounter_id,COUNT(*) orders FROM {c}order_header WHERE is_deleted=0 GROUP BY encounter_id)o ON o.encounter_id=e.id
   WHERE e.is_deleted=0
   GROUP BY e.service_day,e.attending_provider_id,e.facility_id,pa.department_id,p.fte"""),
}


def bootstrap_sql():
    sql=["-- HealthNet only. Owner bootstrap; no role assignments.",
         "CREATE TABLE dbo.load_watermark(source_system VARCHAR(20),table_name VARCHAR(100),watermark_utc DATETIME2(6),watermark_id BIGINT);",
         "CREATE TABLE dbo.load_audit(run_id VARCHAR(100),pipeline_name VARCHAR(100),table_name VARCHAR(100),started_utc DATETIME2(6),ended_utc DATETIME2(6),status VARCHAR(30),rows_read BIGINT,rows_written BIGINT,watermark_utc DATETIME2(6));"]
    sql.append("CREATE TABLE dbo.security_mapping(id BIGINT,upn VARCHAR(240),role VARCHAR(40),facility_id BIGINT,department_id BIGINT,provider_id BIGINT); INSERT INTO dbo.security_mapping VALUES(1,'admin@skynwhy.com','Executive',0,0,0),(2,'admin@skynwhy.com','HospitalManager',1,0,0),(3,'admin@skynwhy.com','DepartmentHead',1,2,0),(4,'admin@skynwhy.com','Doctor',1,2,1);")
    sql.append('CREATE TABLE dbo.core_date(id BIGINT,calendar_date VARCHAR(10),year_month VARCHAR(7),weekday_number BIGINT,local_midnight_utc DATETIME2(6));')
    sql.append('INSERT INTO dbo.core_date VALUES\n'+',\n'.join('('+','.join(str(v)if isinstance(v,int)else"'"+v.replace('+00:00','')+"'"for v in row)+')'for row in calendar_rows())+';')
    for table,definition in [('ref_department_mapping',CLINICAL['provider_assignment']),('ref_payer_group_history',BILLING['payer_plan_history'])]:
        fields=[]
        for name,kind,nullable,_ in columns(definition):
            dtype={'int':'BIGINT','real':'FLOAT','text':'VARCHAR(240)'}[kind]
            if name.endswith('_utc')or name in('created_at','updated_at'):dtype='DATETIME2(6)'
            fields.append('['+name+'] '+dtype+(' NULL'if nullable else' NOT NULL'))
        sql.append('CREATE TABLE dbo.['+table+']('+','.join(fields)+');')
    return '\n\n'.join(sql)+'\n'


def warehouse_sql():
    sql=[bootstrap_sql()]
    for name,(_,query)in PROJECTIONS.items():
        c='[hn_raw].[dbo].[raw_clinical_';b='[hn_raw].[dbo].[raw_billing_'
        # Token replacement is on schema-known table tokens, not SQL names supplied by users.
        import re
        q=re.sub(r'\{c\}([a-z_]+)',lambda m:c+m[1]+']',query)
        q=re.sub(r'\{b\}([a-z_]+)',lambda m:b+m[1]+']',q)
        q=q.replace('{mpi}','[hn_raw].[dbo].[stg_patient]')
        q=q.replace("'SYN-***-'||substr(p.mrn,-4)","CONCAT('SYN-***-',RIGHT(p.mrn,4))").replace("substr(p.given_name,1,1)||'***'","CONCAT(LEFT(p.given_name,1),'***')").replace("substr(p.family_name,1,1)||'***'","CONCAT(LEFT(p.family_name,1),'***')")
        sql.append(f"CREATE TABLE dbo.[{name}] AS {q};\nGO")
        sql.append(f"CREATE OR ALTER PROCEDURE dbo.[sp_{name}] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[{name}]; INSERT INTO dbo.[{name}] {q}; COMMIT; END;\nGO")
    sql.append('CREATE OR ALTER PROCEDURE dbo.sp_run_all AS BEGIN SET NOCOUNT ON;\n'+'\n'.join('EXEC dbo.[sp_'+n+'];'for n in PROJECTIONS)+'\nEND;\nGO')
    return '\n\n'.join(sql)+'\n'


VISUALS=[
 ('operations','Midnight Census','SELECT SUM(midnight_census) FROM mart_census_daily WHERE calendar_date=\'2026-10-29\''),
 ('operations','Bed Occupancy %','SELECT 1.0*SUM(midnight_census)/SUM(licensed_beds) FROM mart_census_daily'),
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
 ('productivity','Workload per FTE','SELECT provider_id,SUM(workload_units)/MAX(fte) FROM mart_provider_productivity_daily GROUP BY provider_id ORDER BY 1'),
]


def build_local(directory,source_directory=None):
    directory=Path(directory)
    source_directory=Path(source_directory)if source_directory else directory
    directory.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(directory/'hn_dw.sqlite')
    if db.execute("SELECT COUNT(*)FROM sqlite_master WHERE type='table'").fetchone()[0]:raise FileExistsError('Local warehouse already populated')
    db.execute('ATTACH DATABASE ? AS clinical',(str(source_directory/'hn_clinical.sqlite'),))
    db.execute('ATTACH DATABASE ? AS billing',(str(source_directory/'hn_billing.sqlite'),))
    # Local counterparts of the separately deployed Dataflow and MPI notebook.
    # Their tables are consumed by the same downstream relational projections.
    db.execute('CREATE TABLE ref_department_mapping AS SELECT * FROM clinical.provider_assignment WHERE is_deleted=0')
    db.execute('CREATE TABLE ref_payer_group_history AS SELECT * FROM billing.payer_plan_history WHERE is_deleted=0')
    db.execute('CREATE TABLE mpi_result AS SELECT p.*,COALESCE(m.survivor_id,p.id) mpi_patient_id FROM clinical.patient p LEFT JOIN clinical.patient_merge m ON m.duplicate_id=p.id AND m.is_deleted=0')
    db.execute('CREATE TABLE security_mapping(id INTEGER PRIMARY KEY,upn TEXT,role TEXT,facility_id INTEGER,department_id INTEGER,provider_id INTEGER)')
    db.executemany('INSERT INTO security_mapping VALUES(?,?,?,?,?,?)',[(1,'admin@skynwhy.com','Executive',0,0,0),(2,'admin@skynwhy.com','HospitalManager',1,0,0),(3,'admin@skynwhy.com','DepartmentHead',1,2,0),(4,'admin@skynwhy.com','Doctor',1,2,1)])
    db.execute('CREATE TABLE core_date(id INTEGER PRIMARY KEY,calendar_date TEXT,year_month TEXT,weekday_number INTEGER,local_midnight_utc TEXT)')
    db.executemany('INSERT INTO core_date VALUES(?,?,?,?,?)',calendar_rows())
    for name,(_,query)in PROJECTIONS.items():
        db.execute('CREATE TABLE ['+name+'] AS '+query.format(c='clinical.',b='billing.',mpi='mpi_result'))
        db.execute('CREATE UNIQUE INDEX ix_'+name+'_id ON ['+name+'](id)')
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


def calendar_rows():
    from datetime import datetime,timezone
    result=[]
    for n in range((END-START).days):
        date=(START+timedelta(days=n)).date()
        midnight=datetime.combine(date,datetime.min.time(),ZoneInfo('America/Chicago')).astimezone(timezone.utc)
        result.append((int(date.strftime('%Y%m%d')),date.isoformat(),date.strftime('%Y-%m'),date.weekday(),midnight.isoformat(timespec='seconds')))
    return result
