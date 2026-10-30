"""One source schema, emitted as SQLite locally and Azure SQL at installation.

Amounts are signed integer cents. Nullable foreign keys are written with ?.
Cross-system encounter numbers intentionally have no cross-database FK.
"""
AUDIT = 'created_at:text updated_at:text updated_by:text is_deleted:int'
CLINICAL = {
 'facility':'id:int name:text region:text licensed_beds:int',
 'department':'id:int facility_id:int>facility name:text service_line:text',
 'unit':'id:int department_id:int>department name:text',
 'bed':'id:int unit_id:int>unit facility_id:int>facility name:text',
 'provider':'id:int synthetic_npi:text name:text specialty:text fte:real provider_type:text current_department_id:int>department',
 'provider_assignment':'id:int provider_id:int>provider department_id:int>department valid_from:text valid_to:text',
 'payer_plan':'id:int plan_code:text payer_group:text',
 'patient':'id:int person_key:text mrn:text given_name:text family_name:text birth_date:text sex:text fictional_address:text',
 'patient_alias':'id:int patient_id:int>patient alias_patient_id:int>patient alias_type:text',
 'patient_merge':'id:int survivor_id:int>patient duplicate_id:int>patient merged_at:text',
 'encounter':'id:int encounter_number:text patient_id:int>patient facility_id:int>facility department_id:int>department attending_provider_id:int?>provider payer_plan_id:int>payer_plan encounter_type:text initial_status:text status:text arrival_utc:text admit_utc:text? discharge_utc:text? service_day:text readmission_of:int?>encounter transfer_from:int?>encounter',
 'adt_event':'id:int encounter_id:int>encounter event_type:text event_utc:text from_facility_id:int?>facility to_facility_id:int?>facility',
 'bed_assignment':'id:int encounter_id:int>encounter bed_id:int>bed start_utc:text end_utc:text?',
 'ed_visit_detail':'id:int encounter_id:int>encounter triage_level:int arrival_local:text utc_offset_minutes:int door_to_provider_minutes:int? ed_los_minutes:int lwbs:int admitted:int transferred:int',
 'diagnosis':'id:int encounter_id:int>encounter code_system:text code:text description:text sequence:int',
 'procedure':'id:int encounter_id:int>encounter provider_id:int>provider code_system:text code:text description:text performed_utc:text workload_units:real',
 'order_header':'id:int encounter_id:int>encounter provider_id:int?>provider order_type:text ordered_utc:text',
 'order_line':'id:int order_header_id:int>order_header line_number:int item_code:text priority:text status:text ordered_utc:text completed_utc:text? replaces_order_line_id:int?>order_line',
 'result':'id:int order_line_id:int>order_line component:text status:text observed_value:real? unit:text reference_low:real? reference_high:real? resulted_utc:text',
 'medication_admin':'id:int order_line_id:int>order_line encounter_id:int>encounter drug_code:text dose:real unit:text administered_utc:text status:text',
}
BILLING = {
 'payer':'id:int name:text payer_group:text',
 'payer_plan':'id:int plan_code:text current_payer_id:int>payer',
 'payer_plan_history':'id:int payer_plan_id:int>payer_plan payer_id:int>payer valid_from:text valid_to:text',
 'account':'id:int account_number:text encounter_number:text facility_id:int patient_mrn:text payer_plan_id:int>payer_plan opened_at:text',
 'charge':'id:int account_id:int>account service_date:text post_date:text revenue_centre_code:text procedure_code:text units:int amount_cents:int correction_of:int?>charge correction_reason:text',
 'claim':'id:int account_id:int>account claim_group:text version:int submission_type:text is_original:int is_final:int bill_type:text ms_drg:text submitted_at:text status:text billed_cents:int',
 'claim_line':'id:int claim_id:int>claim charge_id:int>charge amount_cents:int',
 'remittance':'id:int claim_id:int>claim received_at:text',
 'remittance_line':'id:int remittance_id:int>remittance claim_line_id:int>claim_line paid_cents:int adjusted_cents:int denied_cents:int denial_code:text denial_category:text remark_code:text',
 'payment':'id:int account_id:int>account claim_id:int?>claim payment_date:text amount_cents:int payment_type:text reverses_payment_id:int?>payment moved_to_account_id:int?>account',
 'adjustment':'id:int account_id:int>account adjustment_date:text amount_cents:int adjustment_type:text',
 'ar_snapshot_daily':'id:int snapshot_date:text facility_id:int payer_id:int>payer aging_bucket:text balance_cents:int',
}
TEMPORAL = {'clinical':{'patient':None,'encounter':None,'order_line':30},
            'billing':{'charge':None,'claim':None}}


def columns(definition):
    result=[]
    for token in (definition+' '+AUDIT).split():
        name,kind=token.split(':');kind,_,reference=kind.partition('>')
        result.append((name,kind.rstrip('?'),'?' in kind,reference))
    return result


def ddl(system, dialect='sqlite'):
    tables=CLINICAL if system=='clinical' else BILLING
    statements=[]
    if dialect=='azure':
        statements.append("IF SCHEMA_ID(N'app') IS NULL EXEC(N'CREATE SCHEMA app');")
    for table,definition in tables.items():
        fields=[]
        for name,kind,nullable,reference in columns(definition):
            sqltype={'int':'BIGINT','real':'FLOAT','text':'NVARCHAR(240)'}[kind] if dialect=='azure' else {'int':'INTEGER','real':'REAL','text':'TEXT'}[kind]
            if dialect=='azure' and (name.endswith('_utc') or name in ('created_at','updated_at')):sqltype='DATETIME2(6)'
            field=f'[{name}] {sqltype}'+(' PRIMARY KEY' if name=='id' else '' if nullable else ' NOT NULL')
            if reference:field+=' REFERENCES '+('[app].'if dialect=='azure'else'')+f'[{reference}]([id])'
            fields.append(field)
        prefix='[app].'if dialect=='azure'else''
        statements.append(f'CREATE TABLE {prefix}[{table}] ('+',\n'.join(fields)+');')
        statements.append(f'CREATE INDEX [ix_{table}_watermark] ON {prefix}[{table}]([updated_at],[id]);')
    if dialect=='azure':
        for table,days in TEMPORAL[system].items():
            retention=f', HISTORY_RETENTION_PERIOD = {days} DAYS'if days else''
            statements.append(f"ALTER TABLE [app].[{table}] ADD [valid_from] DATETIME2 GENERATED ALWAYS AS ROW START HIDDEN NOT NULL DEFAULT SYSUTCDATETIME(), [valid_to] DATETIME2 GENERATED ALWAYS AS ROW END HIDDEN NOT NULL DEFAULT CONVERT(DATETIME2,'9999-12-31 23:59:59.9999999'), PERIOD FOR SYSTEM_TIME([valid_from],[valid_to]);\nALTER TABLE [app].[{table}] SET (SYSTEM_VERSIONING=ON (HISTORY_TABLE=[app].[{table}_history]{retention}));")
    return '\n\n'.join(statements)+'\n'
