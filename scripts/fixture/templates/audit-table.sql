CREATE TABLE [dbo].[load_run_audit] (
 [run_id] varchar(36) NOT NULL,
 [pipeline_name] varchar(36) NOT NULL,
 [status] varchar(24) NOT NULL,
 [rows_read] bigint NULL,
 [rows_written] bigint NULL,
 [accounting_state] varchar(32) NOT NULL,
 [start_time_utc] varchar(40) NOT NULL,
 [end_time_utc] varchar(40) NULL,
 [high_watermark] varchar(256) NULL
);
