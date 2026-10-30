-- HealthNet only. Run against hn_dw after the initial pipeline copy.

CREATE TABLE dbo.load_watermark(source_system VARCHAR(20),table_name VARCHAR(100),watermark_utc DATETIME2(6),watermark_id BIGINT);

CREATE TABLE dbo.load_audit(run_id VARCHAR(100),pipeline_name VARCHAR(100),table_name VARCHAR(100),started_utc DATETIME2(6),ended_utc DATETIME2(6),status VARCHAR(30),rows_read BIGINT,rows_written BIGINT,watermark_utc DATETIME2(6));

CREATE TABLE dbo.[core_facility] AS SELECT * FROM [hn_raw].[dbo].[raw_clinical_facility];

CREATE OR ALTER PROCEDURE dbo.[sp_core_facility] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[core_facility]; INSERT INTO dbo.[core_facility] SELECT * FROM [hn_raw].[dbo].[raw_clinical_facility]; COMMIT; END;
GO

CREATE TABLE dbo.[core_department] AS SELECT * FROM [hn_raw].[dbo].[raw_clinical_department];

CREATE OR ALTER PROCEDURE dbo.[sp_core_department] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[core_department]; INSERT INTO dbo.[core_department] SELECT * FROM [hn_raw].[dbo].[raw_clinical_department]; COMMIT; END;
GO

CREATE TABLE dbo.[core_provider] AS SELECT * FROM [hn_raw].[dbo].[raw_clinical_provider];

CREATE OR ALTER PROCEDURE dbo.[sp_core_provider] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[core_provider]; INSERT INTO dbo.[core_provider] SELECT * FROM [hn_raw].[dbo].[raw_clinical_provider]; COMMIT; END;
GO

CREATE TABLE dbo.[core_provider_department_history] AS SELECT * FROM [hn_raw].[dbo].[raw_clinical_provider_assignment];

CREATE OR ALTER PROCEDURE dbo.[sp_core_provider_department_history] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[core_provider_department_history]; INSERT INTO dbo.[core_provider_department_history] SELECT * FROM [hn_raw].[dbo].[raw_clinical_provider_assignment]; COMMIT; END;
GO

CREATE TABLE dbo.[core_payer] AS SELECT * FROM [hn_raw].[dbo].[raw_billing_payer];

CREATE OR ALTER PROCEDURE dbo.[sp_core_payer] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[core_payer]; INSERT INTO dbo.[core_payer] SELECT * FROM [hn_raw].[dbo].[raw_billing_payer]; COMMIT; END;
GO

CREATE TABLE dbo.[core_payer_plan_history] AS SELECT * FROM [hn_raw].[dbo].[raw_billing_payer_plan_history];

CREATE OR ALTER PROCEDURE dbo.[sp_core_payer_plan_history] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[core_payer_plan_history]; INSERT INTO dbo.[core_payer_plan_history] SELECT * FROM [hn_raw].[dbo].[raw_billing_payer_plan_history]; COMMIT; END;
GO

CREATE TABLE dbo.[stg_patient] AS SELECT p.*,COALESCE(m.survivor_id,p.id) mpi_patient_id FROM [hn_raw].[dbo].[raw_clinical_patient] p LEFT JOIN [hn_raw].[dbo].[raw_clinical_patient_merge] m ON m.duplicate_id=p.id;

CREATE OR ALTER PROCEDURE dbo.[sp_stg_patient] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[stg_patient]; INSERT INTO dbo.[stg_patient] SELECT p.*,COALESCE(m.survivor_id,p.id) mpi_patient_id FROM [hn_raw].[dbo].[raw_clinical_patient] p LEFT JOIN [hn_raw].[dbo].[raw_clinical_patient_merge] m ON m.duplicate_id=p.id; COMMIT; END;
GO

CREATE TABLE dbo.[mart_encounter] AS SELECT e.*,COALESCE(m.survivor_id,e.patient_id) mpi_patient_id,
   p.mrn masked_mrn,p.given_name masked_given_name,p.family_name masked_family_name,
   d.service_line,pa.department_id service_provider_department_id
   FROM [hn_raw].[dbo].[raw_clinical_encounter] e JOIN [hn_raw].[dbo].[raw_clinical_patient] p ON p.id=e.patient_id
   JOIN [hn_raw].[dbo].[raw_clinical_department] d ON d.id=e.department_id
   LEFT JOIN [hn_raw].[dbo].[raw_clinical_patient_merge] m ON m.duplicate_id=e.patient_id
   LEFT JOIN [hn_raw].[dbo].[raw_clinical_provider_assignment] pa ON pa.provider_id=e.attending_provider_id
   AND e.service_day>=pa.valid_from AND e.service_day<pa.valid_to
   WHERE e.is_deleted=0 AND p.is_deleted=0;

CREATE OR ALTER PROCEDURE dbo.[sp_mart_encounter] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[mart_encounter]; INSERT INTO dbo.[mart_encounter] SELECT e.*,COALESCE(m.survivor_id,e.patient_id) mpi_patient_id,
   p.mrn masked_mrn,p.given_name masked_given_name,p.family_name masked_family_name,
   d.service_line,pa.department_id service_provider_department_id
   FROM [hn_raw].[dbo].[raw_clinical_encounter] e JOIN [hn_raw].[dbo].[raw_clinical_patient] p ON p.id=e.patient_id
   JOIN [hn_raw].[dbo].[raw_clinical_department] d ON d.id=e.department_id
   LEFT JOIN [hn_raw].[dbo].[raw_clinical_patient_merge] m ON m.duplicate_id=e.patient_id
   LEFT JOIN [hn_raw].[dbo].[raw_clinical_provider_assignment] pa ON pa.provider_id=e.attending_provider_id
   AND e.service_day>=pa.valid_from AND e.service_day<pa.valid_to
   WHERE e.is_deleted=0 AND p.is_deleted=0; COMMIT; END;
GO

CREATE TABLE dbo.[mart_ed_visit] AS SELECT v.*,e.facility_id,e.department_id,e.attending_provider_id,e.service_day FROM [hn_raw].[dbo].[raw_clinical_ed_visit_detail] v JOIN [hn_raw].[dbo].[raw_clinical_encounter] e ON e.id=v.encounter_id WHERE e.is_deleted=0;

CREATE OR ALTER PROCEDURE dbo.[sp_mart_ed_visit] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[mart_ed_visit]; INSERT INTO dbo.[mart_ed_visit] SELECT v.*,e.facility_id,e.department_id,e.attending_provider_id,e.service_day FROM [hn_raw].[dbo].[raw_clinical_ed_visit_detail] v JOIN [hn_raw].[dbo].[raw_clinical_encounter] e ON e.id=v.encounter_id WHERE e.is_deleted=0; COMMIT; END;
GO

CREATE TABLE dbo.[mart_order] AS SELECT l.*,h.encounter_id,h.provider_id,h.order_type,e.facility_id,e.department_id,e.service_day
   FROM [hn_raw].[dbo].[raw_clinical_order_line] l JOIN [hn_raw].[dbo].[raw_clinical_order_header] h ON h.id=l.order_header_id
   JOIN [hn_raw].[dbo].[raw_clinical_encounter] e ON e.id=h.encounter_id WHERE l.is_deleted=0 AND e.is_deleted=0;

CREATE OR ALTER PROCEDURE dbo.[sp_mart_order] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[mart_order]; INSERT INTO dbo.[mart_order] SELECT l.*,h.encounter_id,h.provider_id,h.order_type,e.facility_id,e.department_id,e.service_day
   FROM [hn_raw].[dbo].[raw_clinical_order_line] l JOIN [hn_raw].[dbo].[raw_clinical_order_header] h ON h.id=l.order_header_id
   JOIN [hn_raw].[dbo].[raw_clinical_encounter] e ON e.id=h.encounter_id WHERE l.is_deleted=0 AND e.is_deleted=0; COMMIT; END;
GO

CREATE TABLE dbo.[mart_charge] AS SELECT c.*,a.encounter_number,a.facility_id,a.payer_plan_id,h.payer_id
   FROM [hn_raw].[dbo].[raw_billing_charge] c JOIN [hn_raw].[dbo].[raw_billing_account] a ON a.id=c.account_id
   JOIN [hn_raw].[dbo].[raw_billing_payer_plan_history] h ON h.payer_plan_id=a.payer_plan_id
   AND c.service_date>=h.valid_from AND c.service_date<h.valid_to
   WHERE c.is_deleted=0 AND a.is_deleted=0;

CREATE OR ALTER PROCEDURE dbo.[sp_mart_charge] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[mart_charge]; INSERT INTO dbo.[mart_charge] SELECT c.*,a.encounter_number,a.facility_id,a.payer_plan_id,h.payer_id
   FROM [hn_raw].[dbo].[raw_billing_charge] c JOIN [hn_raw].[dbo].[raw_billing_account] a ON a.id=c.account_id
   JOIN [hn_raw].[dbo].[raw_billing_payer_plan_history] h ON h.payer_plan_id=a.payer_plan_id
   AND c.service_date>=h.valid_from AND c.service_date<h.valid_to
   WHERE c.is_deleted=0 AND a.is_deleted=0; COMMIT; END;
GO

CREATE TABLE dbo.[mart_claim] AS SELECT c.*,a.facility_id,a.payer_plan_id FROM [hn_raw].[dbo].[raw_billing_claim] c JOIN [hn_raw].[dbo].[raw_billing_account] a ON a.id=c.account_id WHERE c.is_deleted=0 AND a.is_deleted=0;

CREATE OR ALTER PROCEDURE dbo.[sp_mart_claim] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[mart_claim]; INSERT INTO dbo.[mart_claim] SELECT c.*,a.facility_id,a.payer_plan_id FROM [hn_raw].[dbo].[raw_billing_claim] c JOIN [hn_raw].[dbo].[raw_billing_account] a ON a.id=c.account_id WHERE c.is_deleted=0 AND a.is_deleted=0; COMMIT; END;
GO

CREATE TABLE dbo.[mart_remittance] AS SELECT l.*,r.claim_id,r.received_at,c.account_id,c.is_original,c.is_final,a.facility_id,a.payer_plan_id
   FROM [hn_raw].[dbo].[raw_billing_remittance_line] l JOIN [hn_raw].[dbo].[raw_billing_remittance] r ON r.id=l.remittance_id
   JOIN [hn_raw].[dbo].[raw_billing_claim] c ON c.id=r.claim_id JOIN [hn_raw].[dbo].[raw_billing_account] a ON a.id=c.account_id
   WHERE l.is_deleted=0 AND r.is_deleted=0 AND c.is_deleted=0 AND a.is_deleted=0;

CREATE OR ALTER PROCEDURE dbo.[sp_mart_remittance] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[mart_remittance]; INSERT INTO dbo.[mart_remittance] SELECT l.*,r.claim_id,r.received_at,c.account_id,c.is_original,c.is_final,a.facility_id,a.payer_plan_id
   FROM [hn_raw].[dbo].[raw_billing_remittance_line] l JOIN [hn_raw].[dbo].[raw_billing_remittance] r ON r.id=l.remittance_id
   JOIN [hn_raw].[dbo].[raw_billing_claim] c ON c.id=r.claim_id JOIN [hn_raw].[dbo].[raw_billing_account] a ON a.id=c.account_id
   WHERE l.is_deleted=0 AND r.is_deleted=0 AND c.is_deleted=0 AND a.is_deleted=0; COMMIT; END;
GO

CREATE TABLE dbo.[mart_payment] AS SELECT p.*,a.facility_id,a.payer_plan_id FROM [hn_raw].[dbo].[raw_billing_payment] p JOIN [hn_raw].[dbo].[raw_billing_account] a ON a.id=p.account_id WHERE p.is_deleted=0 AND a.is_deleted=0;

CREATE OR ALTER PROCEDURE dbo.[sp_mart_payment] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[mart_payment]; INSERT INTO dbo.[mart_payment] SELECT p.*,a.facility_id,a.payer_plan_id FROM [hn_raw].[dbo].[raw_billing_payment] p JOIN [hn_raw].[dbo].[raw_billing_account] a ON a.id=p.account_id WHERE p.is_deleted=0 AND a.is_deleted=0; COMMIT; END;
GO

CREATE TABLE dbo.[mart_adjustment] AS SELECT p.*,a.facility_id,a.payer_plan_id FROM [hn_raw].[dbo].[raw_billing_adjustment] p JOIN [hn_raw].[dbo].[raw_billing_account] a ON a.id=p.account_id WHERE p.is_deleted=0 AND a.is_deleted=0;

CREATE OR ALTER PROCEDURE dbo.[sp_mart_adjustment] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[mart_adjustment]; INSERT INTO dbo.[mart_adjustment] SELECT p.*,a.facility_id,a.payer_plan_id FROM [hn_raw].[dbo].[raw_billing_adjustment] p JOIN [hn_raw].[dbo].[raw_billing_account] a ON a.id=p.account_id WHERE p.is_deleted=0 AND a.is_deleted=0; COMMIT; END;
GO

CREATE TABLE dbo.[mart_ar_aging] AS SELECT * FROM [hn_raw].[dbo].[raw_billing_ar_snapshot_daily] WHERE is_deleted=0;

CREATE OR ALTER PROCEDURE dbo.[sp_mart_ar_aging] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[mart_ar_aging]; INSERT INTO dbo.[mart_ar_aging] SELECT * FROM [hn_raw].[dbo].[raw_billing_ar_snapshot_daily] WHERE is_deleted=0; COMMIT; END;
GO

CREATE TABLE dbo.[mart_procedure] AS SELECT p.*,e.facility_id,e.department_id,e.service_day FROM [hn_raw].[dbo].[raw_clinical_procedure] p
   JOIN [hn_raw].[dbo].[raw_clinical_encounter] e ON e.id=p.encounter_id WHERE p.is_deleted=0 AND e.is_deleted=0;

CREATE OR ALTER PROCEDURE dbo.[sp_mart_procedure] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[mart_procedure]; INSERT INTO dbo.[mart_procedure] SELECT p.*,e.facility_id,e.department_id,e.service_day FROM [hn_raw].[dbo].[raw_clinical_procedure] p
   JOIN [hn_raw].[dbo].[raw_clinical_encounter] e ON e.id=p.encounter_id WHERE p.is_deleted=0 AND e.is_deleted=0; COMMIT; END;
GO

CREATE OR ALTER PROCEDURE dbo.sp_run_all AS BEGIN SET NOCOUNT ON;
EXEC dbo.[sp_core_facility];
EXEC dbo.[sp_core_department];
EXEC dbo.[sp_core_provider];
EXEC dbo.[sp_core_provider_department_history];
EXEC dbo.[sp_core_payer];
EXEC dbo.[sp_core_payer_plan_history];
EXEC dbo.[sp_stg_patient];
EXEC dbo.[sp_mart_encounter];
EXEC dbo.[sp_mart_ed_visit];
EXEC dbo.[sp_mart_order];
EXEC dbo.[sp_mart_charge];
EXEC dbo.[sp_mart_claim];
EXEC dbo.[sp_mart_remittance];
EXEC dbo.[sp_mart_payment];
EXEC dbo.[sp_mart_adjustment];
EXEC dbo.[sp_mart_ar_aging];
EXEC dbo.[sp_mart_procedure];
END;
GO
