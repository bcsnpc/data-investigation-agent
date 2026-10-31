IF SCHEMA_ID(N'app') IS NULL EXEC(N'CREATE SCHEMA app');

CREATE TABLE [app].[payer] ([id] BIGINT PRIMARY KEY,
[name] NVARCHAR(240) NOT NULL,
[payer_group] NVARCHAR(240) NOT NULL,
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_payer_watermark] ON [app].[payer]([updated_at],[id]);

CREATE TABLE [app].[payer_plan] ([id] BIGINT PRIMARY KEY,
[plan_code] NVARCHAR(240) NOT NULL,
[current_payer_id] BIGINT NOT NULL REFERENCES [app].[payer]([id]),
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_payer_plan_watermark] ON [app].[payer_plan]([updated_at],[id]);

CREATE INDEX [ix_payer_plan_current_payer_id] ON [app].[payer_plan]([current_payer_id]);

CREATE TABLE [app].[payer_plan_history] ([id] BIGINT PRIMARY KEY,
[payer_plan_id] BIGINT NOT NULL REFERENCES [app].[payer_plan]([id]),
[payer_id] BIGINT NOT NULL REFERENCES [app].[payer]([id]),
[valid_from] NVARCHAR(240) NOT NULL,
[valid_to] NVARCHAR(240) NOT NULL,
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_payer_plan_history_watermark] ON [app].[payer_plan_history]([updated_at],[id]);

CREATE INDEX [ix_payer_plan_history_payer_plan_id] ON [app].[payer_plan_history]([payer_plan_id]);

CREATE INDEX [ix_payer_plan_history_payer_id] ON [app].[payer_plan_history]([payer_id]);

CREATE TABLE [app].[account] ([id] BIGINT PRIMARY KEY,
[account_number] NVARCHAR(240) NOT NULL,
[encounter_number] NVARCHAR(240) NOT NULL,
[facility_id] BIGINT NOT NULL,
[patient_mrn] NVARCHAR(240) NOT NULL,
[payer_plan_id] BIGINT NOT NULL REFERENCES [app].[payer_plan]([id]),
[opened_at] NVARCHAR(240) NOT NULL,
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_account_watermark] ON [app].[account]([updated_at],[id]);

CREATE INDEX [ix_account_payer_plan_id] ON [app].[account]([payer_plan_id]);

CREATE TABLE [app].[charge] ([id] BIGINT PRIMARY KEY,
[account_id] BIGINT NOT NULL REFERENCES [app].[account]([id]),
[service_date] NVARCHAR(240) NOT NULL,
[post_date] NVARCHAR(240) NOT NULL,
[revenue_centre_code] NVARCHAR(240) NOT NULL,
[procedure_code] NVARCHAR(240) NOT NULL,
[units] BIGINT NOT NULL,
[amount_cents] BIGINT NOT NULL,
[correction_of] BIGINT REFERENCES [app].[charge]([id]),
[correction_reason] NVARCHAR(240) NOT NULL,
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_charge_watermark] ON [app].[charge]([updated_at],[id]);

CREATE INDEX [ix_charge_account_id] ON [app].[charge]([account_id]);

CREATE INDEX [ix_charge_correction_of] ON [app].[charge]([correction_of]);

CREATE TABLE [app].[claim] ([id] BIGINT PRIMARY KEY,
[account_id] BIGINT NOT NULL REFERENCES [app].[account]([id]),
[claim_group] NVARCHAR(240) NOT NULL,
[version] BIGINT NOT NULL,
[submission_type] NVARCHAR(240) NOT NULL,
[is_original] BIGINT NOT NULL,
[is_final] BIGINT NOT NULL,
[bill_type] NVARCHAR(240) NOT NULL,
[ms_drg] NVARCHAR(240) NOT NULL,
[submitted_at] NVARCHAR(240) NOT NULL,
[status] NVARCHAR(240) NOT NULL,
[billed_cents] BIGINT NOT NULL,
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_claim_watermark] ON [app].[claim]([updated_at],[id]);

CREATE INDEX [ix_claim_account_id] ON [app].[claim]([account_id]);

CREATE TABLE [app].[claim_line] ([id] BIGINT PRIMARY KEY,
[claim_id] BIGINT NOT NULL REFERENCES [app].[claim]([id]),
[charge_id] BIGINT NOT NULL REFERENCES [app].[charge]([id]),
[amount_cents] BIGINT NOT NULL,
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_claim_line_watermark] ON [app].[claim_line]([updated_at],[id]);

CREATE INDEX [ix_claim_line_claim_id] ON [app].[claim_line]([claim_id]);

CREATE INDEX [ix_claim_line_charge_id] ON [app].[claim_line]([charge_id]);

CREATE TABLE [app].[remittance] ([id] BIGINT PRIMARY KEY,
[claim_id] BIGINT NOT NULL REFERENCES [app].[claim]([id]),
[received_at] NVARCHAR(240) NOT NULL,
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_remittance_watermark] ON [app].[remittance]([updated_at],[id]);

CREATE INDEX [ix_remittance_claim_id] ON [app].[remittance]([claim_id]);

CREATE TABLE [app].[remittance_line] ([id] BIGINT PRIMARY KEY,
[remittance_id] BIGINT NOT NULL REFERENCES [app].[remittance]([id]),
[claim_line_id] BIGINT NOT NULL REFERENCES [app].[claim_line]([id]),
[paid_cents] BIGINT NOT NULL,
[adjusted_cents] BIGINT NOT NULL,
[denied_cents] BIGINT NOT NULL,
[denial_code] NVARCHAR(240) NOT NULL,
[denial_category] NVARCHAR(240) NOT NULL,
[remark_code] NVARCHAR(240) NOT NULL,
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_remittance_line_watermark] ON [app].[remittance_line]([updated_at],[id]);

CREATE INDEX [ix_remittance_line_remittance_id] ON [app].[remittance_line]([remittance_id]);

CREATE INDEX [ix_remittance_line_claim_line_id] ON [app].[remittance_line]([claim_line_id]);

CREATE TABLE [app].[payment] ([id] BIGINT PRIMARY KEY,
[account_id] BIGINT NOT NULL REFERENCES [app].[account]([id]),
[claim_id] BIGINT REFERENCES [app].[claim]([id]),
[payment_date] NVARCHAR(240) NOT NULL,
[amount_cents] BIGINT NOT NULL,
[payment_type] NVARCHAR(240) NOT NULL,
[reverses_payment_id] BIGINT REFERENCES [app].[payment]([id]),
[moved_to_account_id] BIGINT REFERENCES [app].[account]([id]),
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_payment_watermark] ON [app].[payment]([updated_at],[id]);

CREATE INDEX [ix_payment_account_id] ON [app].[payment]([account_id]);

CREATE INDEX [ix_payment_claim_id] ON [app].[payment]([claim_id]);

CREATE INDEX [ix_payment_reverses_payment_id] ON [app].[payment]([reverses_payment_id]);

CREATE INDEX [ix_payment_moved_to_account_id] ON [app].[payment]([moved_to_account_id]);

CREATE TABLE [app].[adjustment] ([id] BIGINT PRIMARY KEY,
[account_id] BIGINT NOT NULL REFERENCES [app].[account]([id]),
[adjustment_date] NVARCHAR(240) NOT NULL,
[amount_cents] BIGINT NOT NULL,
[adjustment_type] NVARCHAR(240) NOT NULL,
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_adjustment_watermark] ON [app].[adjustment]([updated_at],[id]);

CREATE INDEX [ix_adjustment_account_id] ON [app].[adjustment]([account_id]);

CREATE TABLE [app].[ar_snapshot_daily] ([id] BIGINT PRIMARY KEY,
[snapshot_date] NVARCHAR(240) NOT NULL,
[facility_id] BIGINT NOT NULL,
[payer_id] BIGINT NOT NULL REFERENCES [app].[payer]([id]),
[aging_bucket] NVARCHAR(240) NOT NULL,
[balance_cents] BIGINT NOT NULL,
[created_at] DATETIME2(6) NOT NULL,
[updated_at] DATETIME2(6) NOT NULL,
[updated_by] NVARCHAR(240) NOT NULL,
[is_deleted] BIGINT NOT NULL);

CREATE INDEX [ix_ar_snapshot_daily_watermark] ON [app].[ar_snapshot_daily]([updated_at],[id]);

CREATE INDEX [ix_ar_snapshot_daily_payer_id] ON [app].[ar_snapshot_daily]([payer_id]);

ALTER TABLE [app].[charge] ADD [valid_from] DATETIME2 GENERATED ALWAYS AS ROW START HIDDEN NOT NULL DEFAULT SYSUTCDATETIME(), [valid_to] DATETIME2 GENERATED ALWAYS AS ROW END HIDDEN NOT NULL DEFAULT CONVERT(DATETIME2,'9999-12-31 23:59:59.9999999'), PERIOD FOR SYSTEM_TIME([valid_from],[valid_to]);
ALTER TABLE [app].[charge] SET (SYSTEM_VERSIONING=ON (HISTORY_TABLE=[app].[charge_history]));

ALTER TABLE [app].[claim] ADD [valid_from] DATETIME2 GENERATED ALWAYS AS ROW START HIDDEN NOT NULL DEFAULT SYSUTCDATETIME(), [valid_to] DATETIME2 GENERATED ALWAYS AS ROW END HIDDEN NOT NULL DEFAULT CONVERT(DATETIME2,'9999-12-31 23:59:59.9999999'), PERIOD FOR SYSTEM_TIME([valid_from],[valid_to]);
ALTER TABLE [app].[claim] SET (SYSTEM_VERSIONING=ON (HISTORY_TABLE=[app].[claim_history]));
