IF SCHEMA_ID(N'app') IS NULL EXEC(N'CREATE SCHEMA app');

CREATE TABLE [app].[facility] ([id] BIGINT PRIMARY KEY,
[name] NVARCHAR(240) NOT NULL,
[region] NVARCHAR(240) NOT NULL,
[licensed_beds] BIGINT NOT NULL,
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_facility_watermark] ON [app].[facility]([updated_at],[id]);

CREATE TABLE [app].[department] ([id] BIGINT PRIMARY KEY,
[facility_id] BIGINT NOT NULL REFERENCES [app].[facility]([id]),
[name] NVARCHAR(240) NOT NULL,
[service_line] NVARCHAR(240) NOT NULL,
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_department_watermark] ON [app].[department]([updated_at],[id]);

CREATE INDEX [ix_department_facility_id] ON [app].[department]([facility_id]);

CREATE TABLE [app].[unit] ([id] BIGINT PRIMARY KEY,
[department_id] BIGINT NOT NULL REFERENCES [app].[department]([id]),
[name] NVARCHAR(240) NOT NULL,
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_unit_watermark] ON [app].[unit]([updated_at],[id]);

CREATE INDEX [ix_unit_department_id] ON [app].[unit]([department_id]);

CREATE TABLE [app].[bed] ([id] BIGINT PRIMARY KEY,
[unit_id] BIGINT NOT NULL REFERENCES [app].[unit]([id]),
[facility_id] BIGINT NOT NULL REFERENCES [app].[facility]([id]),
[name] NVARCHAR(240) NOT NULL,
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_bed_watermark] ON [app].[bed]([updated_at],[id]);

CREATE INDEX [ix_bed_unit_id] ON [app].[bed]([unit_id]);

CREATE INDEX [ix_bed_facility_id] ON [app].[bed]([facility_id]);

CREATE TABLE [app].[provider] ([id] BIGINT PRIMARY KEY,
[synthetic_npi] NVARCHAR(240) NOT NULL,
[name] NVARCHAR(240) NOT NULL,
[specialty] NVARCHAR(240) NOT NULL,
[fte] FLOAT NOT NULL,
[provider_type] NVARCHAR(240) NOT NULL,
[current_department_id] BIGINT NOT NULL REFERENCES [app].[department]([id]),
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_provider_watermark] ON [app].[provider]([updated_at],[id]);

CREATE INDEX [ix_provider_current_department_id] ON [app].[provider]([current_department_id]);

CREATE TABLE [app].[provider_assignment] ([id] BIGINT PRIMARY KEY,
[provider_id] BIGINT NOT NULL REFERENCES [app].[provider]([id]),
[department_id] BIGINT NOT NULL REFERENCES [app].[department]([id]),
[valid_from] NVARCHAR(240) NOT NULL,
[valid_to] NVARCHAR(240) NOT NULL,
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_provider_assignment_watermark] ON [app].[provider_assignment]([updated_at],[id]);

CREATE INDEX [ix_provider_assignment_provider_id] ON [app].[provider_assignment]([provider_id]);

CREATE INDEX [ix_provider_assignment_department_id] ON [app].[provider_assignment]([department_id]);

CREATE TABLE [app].[payer_plan] ([id] BIGINT PRIMARY KEY,
[plan_code] NVARCHAR(240) NOT NULL,
[payer_group] NVARCHAR(240) NOT NULL,
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_payer_plan_watermark] ON [app].[payer_plan]([updated_at],[id]);

CREATE TABLE [app].[patient] ([id] BIGINT PRIMARY KEY,
[person_key] NVARCHAR(240) NOT NULL,
[mrn] NVARCHAR(240) NOT NULL,
[given_name] NVARCHAR(240) NOT NULL,
[family_name] NVARCHAR(240) NOT NULL,
[birth_date] NVARCHAR(240) NOT NULL,
[sex] NVARCHAR(240) NOT NULL,
[fictional_address] NVARCHAR(240) NOT NULL,
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_patient_watermark] ON [app].[patient]([updated_at],[id]);

CREATE TABLE [app].[patient_alias] ([id] BIGINT PRIMARY KEY,
[patient_id] BIGINT NOT NULL REFERENCES [app].[patient]([id]),
[alias_patient_id] BIGINT NOT NULL REFERENCES [app].[patient]([id]),
[alias_type] NVARCHAR(240) NOT NULL,
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_patient_alias_watermark] ON [app].[patient_alias]([updated_at],[id]);

CREATE INDEX [ix_patient_alias_patient_id] ON [app].[patient_alias]([patient_id]);

CREATE INDEX [ix_patient_alias_alias_patient_id] ON [app].[patient_alias]([alias_patient_id]);

CREATE TABLE [app].[patient_merge] ([id] BIGINT PRIMARY KEY,
[survivor_id] BIGINT NOT NULL REFERENCES [app].[patient]([id]),
[duplicate_id] BIGINT NOT NULL REFERENCES [app].[patient]([id]),
[merged_at] NVARCHAR(240) NOT NULL,
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_patient_merge_watermark] ON [app].[patient_merge]([updated_at],[id]);

CREATE INDEX [ix_patient_merge_survivor_id] ON [app].[patient_merge]([survivor_id]);

CREATE INDEX [ix_patient_merge_duplicate_id] ON [app].[patient_merge]([duplicate_id]);

CREATE TABLE [app].[encounter] ([id] BIGINT PRIMARY KEY,
[encounter_number] NVARCHAR(240) NOT NULL,
[patient_id] BIGINT NOT NULL REFERENCES [app].[patient]([id]),
[facility_id] BIGINT NOT NULL REFERENCES [app].[facility]([id]),
[department_id] BIGINT NOT NULL REFERENCES [app].[department]([id]),
[attending_provider_id] BIGINT REFERENCES [app].[provider]([id]),
[payer_plan_id] BIGINT NOT NULL REFERENCES [app].[payer_plan]([id]),
[encounter_type] NVARCHAR(240) NOT NULL,
[initial_status] NVARCHAR(240) NOT NULL,
[status] NVARCHAR(240) NOT NULL,
[arrival_utc] DATETIME2(6) NOT NULL,
[admit_utc] DATETIME2(6),
[discharge_utc] DATETIME2(6),
[service_day] NVARCHAR(240) NOT NULL,
[readmission_of] BIGINT REFERENCES [app].[encounter]([id]),
[transfer_from] BIGINT REFERENCES [app].[encounter]([id]),
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_encounter_watermark] ON [app].[encounter]([updated_at],[id]);

CREATE INDEX [ix_encounter_patient_id] ON [app].[encounter]([patient_id]);

CREATE INDEX [ix_encounter_facility_id] ON [app].[encounter]([facility_id]);

CREATE INDEX [ix_encounter_department_id] ON [app].[encounter]([department_id]);

CREATE INDEX [ix_encounter_attending_provider_id] ON [app].[encounter]([attending_provider_id]);

CREATE INDEX [ix_encounter_payer_plan_id] ON [app].[encounter]([payer_plan_id]);

CREATE INDEX [ix_encounter_readmission_of] ON [app].[encounter]([readmission_of]);

CREATE INDEX [ix_encounter_transfer_from] ON [app].[encounter]([transfer_from]);

CREATE TABLE [app].[adt_event] ([id] BIGINT PRIMARY KEY,
[encounter_id] BIGINT NOT NULL REFERENCES [app].[encounter]([id]),
[event_type] NVARCHAR(240) NOT NULL,
[event_utc] DATETIME2(6) NOT NULL,
[from_facility_id] BIGINT REFERENCES [app].[facility]([id]),
[to_facility_id] BIGINT REFERENCES [app].[facility]([id]),
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_adt_event_watermark] ON [app].[adt_event]([updated_at],[id]);

CREATE INDEX [ix_adt_event_encounter_id] ON [app].[adt_event]([encounter_id]);

CREATE INDEX [ix_adt_event_from_facility_id] ON [app].[adt_event]([from_facility_id]);

CREATE INDEX [ix_adt_event_to_facility_id] ON [app].[adt_event]([to_facility_id]);

CREATE TABLE [app].[bed_assignment] ([id] BIGINT PRIMARY KEY,
[encounter_id] BIGINT NOT NULL REFERENCES [app].[encounter]([id]),
[bed_id] BIGINT NOT NULL REFERENCES [app].[bed]([id]),
[start_utc] DATETIME2(6) NOT NULL,
[end_utc] DATETIME2(6),
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_bed_assignment_watermark] ON [app].[bed_assignment]([updated_at],[id]);

CREATE INDEX [ix_bed_assignment_encounter_id] ON [app].[bed_assignment]([encounter_id]);

CREATE INDEX [ix_bed_assignment_bed_id] ON [app].[bed_assignment]([bed_id]);

CREATE TABLE [app].[ed_visit_detail] ([id] BIGINT PRIMARY KEY,
[encounter_id] BIGINT NOT NULL REFERENCES [app].[encounter]([id]),
[triage_level] BIGINT NOT NULL,
[arrival_local] NVARCHAR(240) NOT NULL,
[utc_offset_minutes] BIGINT NOT NULL,
[door_to_provider_minutes] BIGINT,
[ed_los_minutes] BIGINT NOT NULL,
[lwbs] BIGINT NOT NULL,
[admitted] BIGINT NOT NULL,
[transferred] BIGINT NOT NULL,
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_ed_visit_detail_watermark] ON [app].[ed_visit_detail]([updated_at],[id]);

CREATE INDEX [ix_ed_visit_detail_encounter_id] ON [app].[ed_visit_detail]([encounter_id]);

CREATE TABLE [app].[diagnosis] ([id] BIGINT PRIMARY KEY,
[encounter_id] BIGINT NOT NULL REFERENCES [app].[encounter]([id]),
[code_system] NVARCHAR(240) NOT NULL,
[code] NVARCHAR(240) NOT NULL,
[description] NVARCHAR(240) NOT NULL,
[sequence] BIGINT NOT NULL,
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_diagnosis_watermark] ON [app].[diagnosis]([updated_at],[id]);

CREATE INDEX [ix_diagnosis_encounter_id] ON [app].[diagnosis]([encounter_id]);

CREATE TABLE [app].[procedure] ([id] BIGINT PRIMARY KEY,
[encounter_id] BIGINT NOT NULL REFERENCES [app].[encounter]([id]),
[provider_id] BIGINT NOT NULL REFERENCES [app].[provider]([id]),
[code_system] NVARCHAR(240) NOT NULL,
[code] NVARCHAR(240) NOT NULL,
[description] NVARCHAR(240) NOT NULL,
[performed_utc] DATETIME2(6) NOT NULL,
[workload_units] FLOAT NOT NULL,
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_procedure_watermark] ON [app].[procedure]([updated_at],[id]);

CREATE INDEX [ix_procedure_encounter_id] ON [app].[procedure]([encounter_id]);

CREATE INDEX [ix_procedure_provider_id] ON [app].[procedure]([provider_id]);

CREATE TABLE [app].[order_header] ([id] BIGINT PRIMARY KEY,
[encounter_id] BIGINT NOT NULL REFERENCES [app].[encounter]([id]),
[provider_id] BIGINT REFERENCES [app].[provider]([id]),
[order_type] NVARCHAR(240) NOT NULL,
[ordered_utc] DATETIME2(6) NOT NULL,
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_order_header_watermark] ON [app].[order_header]([updated_at],[id]);

CREATE INDEX [ix_order_header_encounter_id] ON [app].[order_header]([encounter_id]);

CREATE INDEX [ix_order_header_provider_id] ON [app].[order_header]([provider_id]);

CREATE TABLE [app].[order_line] ([id] BIGINT PRIMARY KEY,
[order_header_id] BIGINT NOT NULL REFERENCES [app].[order_header]([id]),
[line_number] BIGINT NOT NULL,
[item_code] NVARCHAR(240) NOT NULL,
[priority] NVARCHAR(240) NOT NULL,
[status] NVARCHAR(240) NOT NULL,
[ordered_utc] DATETIME2(6) NOT NULL,
[completed_utc] DATETIME2(6),
[replaces_order_line_id] BIGINT REFERENCES [app].[order_line]([id]),
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_order_line_watermark] ON [app].[order_line]([updated_at],[id]);

CREATE INDEX [ix_order_line_order_header_id] ON [app].[order_line]([order_header_id]);

CREATE INDEX [ix_order_line_replaces_order_line_id] ON [app].[order_line]([replaces_order_line_id]);

CREATE TABLE [app].[result] ([id] BIGINT PRIMARY KEY,
[order_line_id] BIGINT NOT NULL REFERENCES [app].[order_line]([id]),
[component] NVARCHAR(240) NOT NULL,
[status] NVARCHAR(240) NOT NULL,
[observed_value] FLOAT,
[unit] NVARCHAR(240) NOT NULL,
[reference_low] FLOAT,
[reference_high] FLOAT,
[resulted_utc] DATETIME2(6) NOT NULL,
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_result_watermark] ON [app].[result]([updated_at],[id]);

CREATE INDEX [ix_result_order_line_id] ON [app].[result]([order_line_id]);

CREATE TABLE [app].[medication_admin] ([id] BIGINT PRIMARY KEY,
[order_line_id] BIGINT NOT NULL REFERENCES [app].[order_line]([id]),
[encounter_id] BIGINT NOT NULL REFERENCES [app].[encounter]([id]),
[drug_code] NVARCHAR(240) NOT NULL,
[dose] FLOAT NOT NULL,
[unit] NVARCHAR(240) NOT NULL,
[administered_utc] DATETIME2(6) NOT NULL,
[status] NVARCHAR(240) NOT NULL,
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_medication_admin_watermark] ON [app].[medication_admin]([updated_at],[id]);

CREATE INDEX [ix_medication_admin_order_line_id] ON [app].[medication_admin]([order_line_id]);

CREATE INDEX [ix_medication_admin_encounter_id] ON [app].[medication_admin]([encounter_id]);

ALTER TABLE [app].[patient] ADD [valid_from] DATETIME2 GENERATED ALWAYS AS ROW START HIDDEN NOT NULL DEFAULT SYSUTCDATETIME(), [valid_to] DATETIME2 GENERATED ALWAYS AS ROW END HIDDEN NOT NULL DEFAULT CONVERT(DATETIME2,'9999-12-31 23:59:59.9999999'), PERIOD FOR SYSTEM_TIME([valid_from],[valid_to]);
ALTER TABLE [app].[patient] SET (SYSTEM_VERSIONING=ON (HISTORY_TABLE=[app].[patient_history]));

ALTER TABLE [app].[encounter] ADD [valid_from] DATETIME2 GENERATED ALWAYS AS ROW START HIDDEN NOT NULL DEFAULT SYSUTCDATETIME(), [valid_to] DATETIME2 GENERATED ALWAYS AS ROW END HIDDEN NOT NULL DEFAULT CONVERT(DATETIME2,'9999-12-31 23:59:59.9999999'), PERIOD FOR SYSTEM_TIME([valid_from],[valid_to]);
ALTER TABLE [app].[encounter] SET (SYSTEM_VERSIONING=ON (HISTORY_TABLE=[app].[encounter_history]));

ALTER TABLE [app].[order_line] ADD [valid_from] DATETIME2 GENERATED ALWAYS AS ROW START HIDDEN NOT NULL DEFAULT SYSUTCDATETIME(), [valid_to] DATETIME2 GENERATED ALWAYS AS ROW END HIDDEN NOT NULL DEFAULT CONVERT(DATETIME2,'9999-12-31 23:59:59.9999999'), PERIOD FOR SYSTEM_TIME([valid_from],[valid_to]);
ALTER TABLE [app].[order_line] SET (SYSTEM_VERSIONING=ON (HISTORY_TABLE=[app].[order_line_history], HISTORY_RETENTION_PERIOD = 30 DAYS));
