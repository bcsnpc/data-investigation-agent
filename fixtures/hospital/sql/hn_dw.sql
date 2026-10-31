-- HealthNet only. Owner bootstrap; no role assignments.

CREATE TABLE dbo.load_watermark(source_system VARCHAR(20),table_name VARCHAR(100),watermark_utc DATETIME2(6),watermark_id BIGINT);

CREATE TABLE dbo.load_audit(run_id VARCHAR(100),pipeline_name VARCHAR(100),table_name VARCHAR(100),started_utc DATETIME2(6),ended_utc DATETIME2(6),status VARCHAR(30),rows_read BIGINT,rows_written BIGINT,watermark_utc DATETIME2(6));

CREATE TABLE dbo.security_mapping(id BIGINT,upn VARCHAR(240),role VARCHAR(40),facility_id BIGINT,department_id BIGINT,provider_id BIGINT); INSERT INTO dbo.security_mapping VALUES(1,'admin@skynwhy.com','Executive',0,0,0),(2,'admin@skynwhy.com','HospitalManager',1,0,0),(3,'admin@skynwhy.com','DepartmentHead',1,2,0),(4,'admin@skynwhy.com','Doctor',1,2,1);

CREATE TABLE dbo.core_date(id BIGINT,calendar_date VARCHAR(10),year_month VARCHAR(7),weekday_number BIGINT,local_midnight_utc DATETIME2(6));

INSERT INTO dbo.core_date VALUES
(20251001,'2025-10-01','2025-10',2,'2025-10-01T05:00:00'),
(20251002,'2025-10-02','2025-10',3,'2025-10-02T05:00:00'),
(20251003,'2025-10-03','2025-10',4,'2025-10-03T05:00:00'),
(20251004,'2025-10-04','2025-10',5,'2025-10-04T05:00:00'),
(20251005,'2025-10-05','2025-10',6,'2025-10-05T05:00:00'),
(20251006,'2025-10-06','2025-10',0,'2025-10-06T05:00:00'),
(20251007,'2025-10-07','2025-10',1,'2025-10-07T05:00:00'),
(20251008,'2025-10-08','2025-10',2,'2025-10-08T05:00:00'),
(20251009,'2025-10-09','2025-10',3,'2025-10-09T05:00:00'),
(20251010,'2025-10-10','2025-10',4,'2025-10-10T05:00:00'),
(20251011,'2025-10-11','2025-10',5,'2025-10-11T05:00:00'),
(20251012,'2025-10-12','2025-10',6,'2025-10-12T05:00:00'),
(20251013,'2025-10-13','2025-10',0,'2025-10-13T05:00:00'),
(20251014,'2025-10-14','2025-10',1,'2025-10-14T05:00:00'),
(20251015,'2025-10-15','2025-10',2,'2025-10-15T05:00:00'),
(20251016,'2025-10-16','2025-10',3,'2025-10-16T05:00:00'),
(20251017,'2025-10-17','2025-10',4,'2025-10-17T05:00:00'),
(20251018,'2025-10-18','2025-10',5,'2025-10-18T05:00:00'),
(20251019,'2025-10-19','2025-10',6,'2025-10-19T05:00:00'),
(20251020,'2025-10-20','2025-10',0,'2025-10-20T05:00:00'),
(20251021,'2025-10-21','2025-10',1,'2025-10-21T05:00:00'),
(20251022,'2025-10-22','2025-10',2,'2025-10-22T05:00:00'),
(20251023,'2025-10-23','2025-10',3,'2025-10-23T05:00:00'),
(20251024,'2025-10-24','2025-10',4,'2025-10-24T05:00:00'),
(20251025,'2025-10-25','2025-10',5,'2025-10-25T05:00:00'),
(20251026,'2025-10-26','2025-10',6,'2025-10-26T05:00:00'),
(20251027,'2025-10-27','2025-10',0,'2025-10-27T05:00:00'),
(20251028,'2025-10-28','2025-10',1,'2025-10-28T05:00:00'),
(20251029,'2025-10-29','2025-10',2,'2025-10-29T05:00:00'),
(20251030,'2025-10-30','2025-10',3,'2025-10-30T05:00:00'),
(20251031,'2025-10-31','2025-10',4,'2025-10-31T05:00:00'),
(20251101,'2025-11-01','2025-11',5,'2025-11-01T05:00:00'),
(20251102,'2025-11-02','2025-11',6,'2025-11-02T05:00:00'),
(20251103,'2025-11-03','2025-11',0,'2025-11-03T06:00:00'),
(20251104,'2025-11-04','2025-11',1,'2025-11-04T06:00:00'),
(20251105,'2025-11-05','2025-11',2,'2025-11-05T06:00:00'),
(20251106,'2025-11-06','2025-11',3,'2025-11-06T06:00:00'),
(20251107,'2025-11-07','2025-11',4,'2025-11-07T06:00:00'),
(20251108,'2025-11-08','2025-11',5,'2025-11-08T06:00:00'),
(20251109,'2025-11-09','2025-11',6,'2025-11-09T06:00:00'),
(20251110,'2025-11-10','2025-11',0,'2025-11-10T06:00:00'),
(20251111,'2025-11-11','2025-11',1,'2025-11-11T06:00:00'),
(20251112,'2025-11-12','2025-11',2,'2025-11-12T06:00:00'),
(20251113,'2025-11-13','2025-11',3,'2025-11-13T06:00:00'),
(20251114,'2025-11-14','2025-11',4,'2025-11-14T06:00:00'),
(20251115,'2025-11-15','2025-11',5,'2025-11-15T06:00:00'),
(20251116,'2025-11-16','2025-11',6,'2025-11-16T06:00:00'),
(20251117,'2025-11-17','2025-11',0,'2025-11-17T06:00:00'),
(20251118,'2025-11-18','2025-11',1,'2025-11-18T06:00:00'),
(20251119,'2025-11-19','2025-11',2,'2025-11-19T06:00:00'),
(20251120,'2025-11-20','2025-11',3,'2025-11-20T06:00:00'),
(20251121,'2025-11-21','2025-11',4,'2025-11-21T06:00:00'),
(20251122,'2025-11-22','2025-11',5,'2025-11-22T06:00:00'),
(20251123,'2025-11-23','2025-11',6,'2025-11-23T06:00:00'),
(20251124,'2025-11-24','2025-11',0,'2025-11-24T06:00:00'),
(20251125,'2025-11-25','2025-11',1,'2025-11-25T06:00:00'),
(20251126,'2025-11-26','2025-11',2,'2025-11-26T06:00:00'),
(20251127,'2025-11-27','2025-11',3,'2025-11-27T06:00:00'),
(20251128,'2025-11-28','2025-11',4,'2025-11-28T06:00:00'),
(20251129,'2025-11-29','2025-11',5,'2025-11-29T06:00:00'),
(20251130,'2025-11-30','2025-11',6,'2025-11-30T06:00:00'),
(20251201,'2025-12-01','2025-12',0,'2025-12-01T06:00:00'),
(20251202,'2025-12-02','2025-12',1,'2025-12-02T06:00:00'),
(20251203,'2025-12-03','2025-12',2,'2025-12-03T06:00:00'),
(20251204,'2025-12-04','2025-12',3,'2025-12-04T06:00:00'),
(20251205,'2025-12-05','2025-12',4,'2025-12-05T06:00:00'),
(20251206,'2025-12-06','2025-12',5,'2025-12-06T06:00:00'),
(20251207,'2025-12-07','2025-12',6,'2025-12-07T06:00:00'),
(20251208,'2025-12-08','2025-12',0,'2025-12-08T06:00:00'),
(20251209,'2025-12-09','2025-12',1,'2025-12-09T06:00:00'),
(20251210,'2025-12-10','2025-12',2,'2025-12-10T06:00:00'),
(20251211,'2025-12-11','2025-12',3,'2025-12-11T06:00:00'),
(20251212,'2025-12-12','2025-12',4,'2025-12-12T06:00:00'),
(20251213,'2025-12-13','2025-12',5,'2025-12-13T06:00:00'),
(20251214,'2025-12-14','2025-12',6,'2025-12-14T06:00:00'),
(20251215,'2025-12-15','2025-12',0,'2025-12-15T06:00:00'),
(20251216,'2025-12-16','2025-12',1,'2025-12-16T06:00:00'),
(20251217,'2025-12-17','2025-12',2,'2025-12-17T06:00:00'),
(20251218,'2025-12-18','2025-12',3,'2025-12-18T06:00:00'),
(20251219,'2025-12-19','2025-12',4,'2025-12-19T06:00:00'),
(20251220,'2025-12-20','2025-12',5,'2025-12-20T06:00:00'),
(20251221,'2025-12-21','2025-12',6,'2025-12-21T06:00:00'),
(20251222,'2025-12-22','2025-12',0,'2025-12-22T06:00:00'),
(20251223,'2025-12-23','2025-12',1,'2025-12-23T06:00:00'),
(20251224,'2025-12-24','2025-12',2,'2025-12-24T06:00:00'),
(20251225,'2025-12-25','2025-12',3,'2025-12-25T06:00:00'),
(20251226,'2025-12-26','2025-12',4,'2025-12-26T06:00:00'),
(20251227,'2025-12-27','2025-12',5,'2025-12-27T06:00:00'),
(20251228,'2025-12-28','2025-12',6,'2025-12-28T06:00:00'),
(20251229,'2025-12-29','2025-12',0,'2025-12-29T06:00:00'),
(20251230,'2025-12-30','2025-12',1,'2025-12-30T06:00:00'),
(20251231,'2025-12-31','2025-12',2,'2025-12-31T06:00:00'),
(20260101,'2026-01-01','2026-01',3,'2026-01-01T06:00:00'),
(20260102,'2026-01-02','2026-01',4,'2026-01-02T06:00:00'),
(20260103,'2026-01-03','2026-01',5,'2026-01-03T06:00:00'),
(20260104,'2026-01-04','2026-01',6,'2026-01-04T06:00:00'),
(20260105,'2026-01-05','2026-01',0,'2026-01-05T06:00:00'),
(20260106,'2026-01-06','2026-01',1,'2026-01-06T06:00:00'),
(20260107,'2026-01-07','2026-01',2,'2026-01-07T06:00:00'),
(20260108,'2026-01-08','2026-01',3,'2026-01-08T06:00:00'),
(20260109,'2026-01-09','2026-01',4,'2026-01-09T06:00:00'),
(20260110,'2026-01-10','2026-01',5,'2026-01-10T06:00:00'),
(20260111,'2026-01-11','2026-01',6,'2026-01-11T06:00:00'),
(20260112,'2026-01-12','2026-01',0,'2026-01-12T06:00:00'),
(20260113,'2026-01-13','2026-01',1,'2026-01-13T06:00:00'),
(20260114,'2026-01-14','2026-01',2,'2026-01-14T06:00:00'),
(20260115,'2026-01-15','2026-01',3,'2026-01-15T06:00:00'),
(20260116,'2026-01-16','2026-01',4,'2026-01-16T06:00:00'),
(20260117,'2026-01-17','2026-01',5,'2026-01-17T06:00:00'),
(20260118,'2026-01-18','2026-01',6,'2026-01-18T06:00:00'),
(20260119,'2026-01-19','2026-01',0,'2026-01-19T06:00:00'),
(20260120,'2026-01-20','2026-01',1,'2026-01-20T06:00:00'),
(20260121,'2026-01-21','2026-01',2,'2026-01-21T06:00:00'),
(20260122,'2026-01-22','2026-01',3,'2026-01-22T06:00:00'),
(20260123,'2026-01-23','2026-01',4,'2026-01-23T06:00:00'),
(20260124,'2026-01-24','2026-01',5,'2026-01-24T06:00:00'),
(20260125,'2026-01-25','2026-01',6,'2026-01-25T06:00:00'),
(20260126,'2026-01-26','2026-01',0,'2026-01-26T06:00:00'),
(20260127,'2026-01-27','2026-01',1,'2026-01-27T06:00:00'),
(20260128,'2026-01-28','2026-01',2,'2026-01-28T06:00:00'),
(20260129,'2026-01-29','2026-01',3,'2026-01-29T06:00:00'),
(20260130,'2026-01-30','2026-01',4,'2026-01-30T06:00:00'),
(20260131,'2026-01-31','2026-01',5,'2026-01-31T06:00:00'),
(20260201,'2026-02-01','2026-02',6,'2026-02-01T06:00:00'),
(20260202,'2026-02-02','2026-02',0,'2026-02-02T06:00:00'),
(20260203,'2026-02-03','2026-02',1,'2026-02-03T06:00:00'),
(20260204,'2026-02-04','2026-02',2,'2026-02-04T06:00:00'),
(20260205,'2026-02-05','2026-02',3,'2026-02-05T06:00:00'),
(20260206,'2026-02-06','2026-02',4,'2026-02-06T06:00:00'),
(20260207,'2026-02-07','2026-02',5,'2026-02-07T06:00:00'),
(20260208,'2026-02-08','2026-02',6,'2026-02-08T06:00:00'),
(20260209,'2026-02-09','2026-02',0,'2026-02-09T06:00:00'),
(20260210,'2026-02-10','2026-02',1,'2026-02-10T06:00:00'),
(20260211,'2026-02-11','2026-02',2,'2026-02-11T06:00:00'),
(20260212,'2026-02-12','2026-02',3,'2026-02-12T06:00:00'),
(20260213,'2026-02-13','2026-02',4,'2026-02-13T06:00:00'),
(20260214,'2026-02-14','2026-02',5,'2026-02-14T06:00:00'),
(20260215,'2026-02-15','2026-02',6,'2026-02-15T06:00:00'),
(20260216,'2026-02-16','2026-02',0,'2026-02-16T06:00:00'),
(20260217,'2026-02-17','2026-02',1,'2026-02-17T06:00:00'),
(20260218,'2026-02-18','2026-02',2,'2026-02-18T06:00:00'),
(20260219,'2026-02-19','2026-02',3,'2026-02-19T06:00:00'),
(20260220,'2026-02-20','2026-02',4,'2026-02-20T06:00:00'),
(20260221,'2026-02-21','2026-02',5,'2026-02-21T06:00:00'),
(20260222,'2026-02-22','2026-02',6,'2026-02-22T06:00:00'),
(20260223,'2026-02-23','2026-02',0,'2026-02-23T06:00:00'),
(20260224,'2026-02-24','2026-02',1,'2026-02-24T06:00:00'),
(20260225,'2026-02-25','2026-02',2,'2026-02-25T06:00:00'),
(20260226,'2026-02-26','2026-02',3,'2026-02-26T06:00:00'),
(20260227,'2026-02-27','2026-02',4,'2026-02-27T06:00:00'),
(20260228,'2026-02-28','2026-02',5,'2026-02-28T06:00:00'),
(20260301,'2026-03-01','2026-03',6,'2026-03-01T06:00:00'),
(20260302,'2026-03-02','2026-03',0,'2026-03-02T06:00:00'),
(20260303,'2026-03-03','2026-03',1,'2026-03-03T06:00:00'),
(20260304,'2026-03-04','2026-03',2,'2026-03-04T06:00:00'),
(20260305,'2026-03-05','2026-03',3,'2026-03-05T06:00:00'),
(20260306,'2026-03-06','2026-03',4,'2026-03-06T06:00:00'),
(20260307,'2026-03-07','2026-03',5,'2026-03-07T06:00:00'),
(20260308,'2026-03-08','2026-03',6,'2026-03-08T06:00:00'),
(20260309,'2026-03-09','2026-03',0,'2026-03-09T05:00:00'),
(20260310,'2026-03-10','2026-03',1,'2026-03-10T05:00:00'),
(20260311,'2026-03-11','2026-03',2,'2026-03-11T05:00:00'),
(20260312,'2026-03-12','2026-03',3,'2026-03-12T05:00:00'),
(20260313,'2026-03-13','2026-03',4,'2026-03-13T05:00:00'),
(20260314,'2026-03-14','2026-03',5,'2026-03-14T05:00:00'),
(20260315,'2026-03-15','2026-03',6,'2026-03-15T05:00:00'),
(20260316,'2026-03-16','2026-03',0,'2026-03-16T05:00:00'),
(20260317,'2026-03-17','2026-03',1,'2026-03-17T05:00:00'),
(20260318,'2026-03-18','2026-03',2,'2026-03-18T05:00:00'),
(20260319,'2026-03-19','2026-03',3,'2026-03-19T05:00:00'),
(20260320,'2026-03-20','2026-03',4,'2026-03-20T05:00:00'),
(20260321,'2026-03-21','2026-03',5,'2026-03-21T05:00:00'),
(20260322,'2026-03-22','2026-03',6,'2026-03-22T05:00:00'),
(20260323,'2026-03-23','2026-03',0,'2026-03-23T05:00:00'),
(20260324,'2026-03-24','2026-03',1,'2026-03-24T05:00:00'),
(20260325,'2026-03-25','2026-03',2,'2026-03-25T05:00:00'),
(20260326,'2026-03-26','2026-03',3,'2026-03-26T05:00:00'),
(20260327,'2026-03-27','2026-03',4,'2026-03-27T05:00:00'),
(20260328,'2026-03-28','2026-03',5,'2026-03-28T05:00:00'),
(20260329,'2026-03-29','2026-03',6,'2026-03-29T05:00:00'),
(20260330,'2026-03-30','2026-03',0,'2026-03-30T05:00:00'),
(20260331,'2026-03-31','2026-03',1,'2026-03-31T05:00:00'),
(20260401,'2026-04-01','2026-04',2,'2026-04-01T05:00:00'),
(20260402,'2026-04-02','2026-04',3,'2026-04-02T05:00:00'),
(20260403,'2026-04-03','2026-04',4,'2026-04-03T05:00:00'),
(20260404,'2026-04-04','2026-04',5,'2026-04-04T05:00:00'),
(20260405,'2026-04-05','2026-04',6,'2026-04-05T05:00:00'),
(20260406,'2026-04-06','2026-04',0,'2026-04-06T05:00:00'),
(20260407,'2026-04-07','2026-04',1,'2026-04-07T05:00:00'),
(20260408,'2026-04-08','2026-04',2,'2026-04-08T05:00:00'),
(20260409,'2026-04-09','2026-04',3,'2026-04-09T05:00:00'),
(20260410,'2026-04-10','2026-04',4,'2026-04-10T05:00:00'),
(20260411,'2026-04-11','2026-04',5,'2026-04-11T05:00:00'),
(20260412,'2026-04-12','2026-04',6,'2026-04-12T05:00:00'),
(20260413,'2026-04-13','2026-04',0,'2026-04-13T05:00:00'),
(20260414,'2026-04-14','2026-04',1,'2026-04-14T05:00:00'),
(20260415,'2026-04-15','2026-04',2,'2026-04-15T05:00:00'),
(20260416,'2026-04-16','2026-04',3,'2026-04-16T05:00:00'),
(20260417,'2026-04-17','2026-04',4,'2026-04-17T05:00:00'),
(20260418,'2026-04-18','2026-04',5,'2026-04-18T05:00:00'),
(20260419,'2026-04-19','2026-04',6,'2026-04-19T05:00:00'),
(20260420,'2026-04-20','2026-04',0,'2026-04-20T05:00:00'),
(20260421,'2026-04-21','2026-04',1,'2026-04-21T05:00:00'),
(20260422,'2026-04-22','2026-04',2,'2026-04-22T05:00:00'),
(20260423,'2026-04-23','2026-04',3,'2026-04-23T05:00:00'),
(20260424,'2026-04-24','2026-04',4,'2026-04-24T05:00:00'),
(20260425,'2026-04-25','2026-04',5,'2026-04-25T05:00:00'),
(20260426,'2026-04-26','2026-04',6,'2026-04-26T05:00:00'),
(20260427,'2026-04-27','2026-04',0,'2026-04-27T05:00:00'),
(20260428,'2026-04-28','2026-04',1,'2026-04-28T05:00:00'),
(20260429,'2026-04-29','2026-04',2,'2026-04-29T05:00:00'),
(20260430,'2026-04-30','2026-04',3,'2026-04-30T05:00:00'),
(20260501,'2026-05-01','2026-05',4,'2026-05-01T05:00:00'),
(20260502,'2026-05-02','2026-05',5,'2026-05-02T05:00:00'),
(20260503,'2026-05-03','2026-05',6,'2026-05-03T05:00:00'),
(20260504,'2026-05-04','2026-05',0,'2026-05-04T05:00:00'),
(20260505,'2026-05-05','2026-05',1,'2026-05-05T05:00:00'),
(20260506,'2026-05-06','2026-05',2,'2026-05-06T05:00:00'),
(20260507,'2026-05-07','2026-05',3,'2026-05-07T05:00:00'),
(20260508,'2026-05-08','2026-05',4,'2026-05-08T05:00:00'),
(20260509,'2026-05-09','2026-05',5,'2026-05-09T05:00:00'),
(20260510,'2026-05-10','2026-05',6,'2026-05-10T05:00:00'),
(20260511,'2026-05-11','2026-05',0,'2026-05-11T05:00:00'),
(20260512,'2026-05-12','2026-05',1,'2026-05-12T05:00:00'),
(20260513,'2026-05-13','2026-05',2,'2026-05-13T05:00:00'),
(20260514,'2026-05-14','2026-05',3,'2026-05-14T05:00:00'),
(20260515,'2026-05-15','2026-05',4,'2026-05-15T05:00:00'),
(20260516,'2026-05-16','2026-05',5,'2026-05-16T05:00:00'),
(20260517,'2026-05-17','2026-05',6,'2026-05-17T05:00:00'),
(20260518,'2026-05-18','2026-05',0,'2026-05-18T05:00:00'),
(20260519,'2026-05-19','2026-05',1,'2026-05-19T05:00:00'),
(20260520,'2026-05-20','2026-05',2,'2026-05-20T05:00:00'),
(20260521,'2026-05-21','2026-05',3,'2026-05-21T05:00:00'),
(20260522,'2026-05-22','2026-05',4,'2026-05-22T05:00:00'),
(20260523,'2026-05-23','2026-05',5,'2026-05-23T05:00:00'),
(20260524,'2026-05-24','2026-05',6,'2026-05-24T05:00:00'),
(20260525,'2026-05-25','2026-05',0,'2026-05-25T05:00:00'),
(20260526,'2026-05-26','2026-05',1,'2026-05-26T05:00:00'),
(20260527,'2026-05-27','2026-05',2,'2026-05-27T05:00:00'),
(20260528,'2026-05-28','2026-05',3,'2026-05-28T05:00:00'),
(20260529,'2026-05-29','2026-05',4,'2026-05-29T05:00:00'),
(20260530,'2026-05-30','2026-05',5,'2026-05-30T05:00:00'),
(20260531,'2026-05-31','2026-05',6,'2026-05-31T05:00:00'),
(20260601,'2026-06-01','2026-06',0,'2026-06-01T05:00:00'),
(20260602,'2026-06-02','2026-06',1,'2026-06-02T05:00:00'),
(20260603,'2026-06-03','2026-06',2,'2026-06-03T05:00:00'),
(20260604,'2026-06-04','2026-06',3,'2026-06-04T05:00:00'),
(20260605,'2026-06-05','2026-06',4,'2026-06-05T05:00:00'),
(20260606,'2026-06-06','2026-06',5,'2026-06-06T05:00:00'),
(20260607,'2026-06-07','2026-06',6,'2026-06-07T05:00:00'),
(20260608,'2026-06-08','2026-06',0,'2026-06-08T05:00:00'),
(20260609,'2026-06-09','2026-06',1,'2026-06-09T05:00:00'),
(20260610,'2026-06-10','2026-06',2,'2026-06-10T05:00:00'),
(20260611,'2026-06-11','2026-06',3,'2026-06-11T05:00:00'),
(20260612,'2026-06-12','2026-06',4,'2026-06-12T05:00:00'),
(20260613,'2026-06-13','2026-06',5,'2026-06-13T05:00:00'),
(20260614,'2026-06-14','2026-06',6,'2026-06-14T05:00:00'),
(20260615,'2026-06-15','2026-06',0,'2026-06-15T05:00:00'),
(20260616,'2026-06-16','2026-06',1,'2026-06-16T05:00:00'),
(20260617,'2026-06-17','2026-06',2,'2026-06-17T05:00:00'),
(20260618,'2026-06-18','2026-06',3,'2026-06-18T05:00:00'),
(20260619,'2026-06-19','2026-06',4,'2026-06-19T05:00:00'),
(20260620,'2026-06-20','2026-06',5,'2026-06-20T05:00:00'),
(20260621,'2026-06-21','2026-06',6,'2026-06-21T05:00:00'),
(20260622,'2026-06-22','2026-06',0,'2026-06-22T05:00:00'),
(20260623,'2026-06-23','2026-06',1,'2026-06-23T05:00:00'),
(20260624,'2026-06-24','2026-06',2,'2026-06-24T05:00:00'),
(20260625,'2026-06-25','2026-06',3,'2026-06-25T05:00:00'),
(20260626,'2026-06-26','2026-06',4,'2026-06-26T05:00:00'),
(20260627,'2026-06-27','2026-06',5,'2026-06-27T05:00:00'),
(20260628,'2026-06-28','2026-06',6,'2026-06-28T05:00:00'),
(20260629,'2026-06-29','2026-06',0,'2026-06-29T05:00:00'),
(20260630,'2026-06-30','2026-06',1,'2026-06-30T05:00:00'),
(20260701,'2026-07-01','2026-07',2,'2026-07-01T05:00:00'),
(20260702,'2026-07-02','2026-07',3,'2026-07-02T05:00:00'),
(20260703,'2026-07-03','2026-07',4,'2026-07-03T05:00:00'),
(20260704,'2026-07-04','2026-07',5,'2026-07-04T05:00:00'),
(20260705,'2026-07-05','2026-07',6,'2026-07-05T05:00:00'),
(20260706,'2026-07-06','2026-07',0,'2026-07-06T05:00:00'),
(20260707,'2026-07-07','2026-07',1,'2026-07-07T05:00:00'),
(20260708,'2026-07-08','2026-07',2,'2026-07-08T05:00:00'),
(20260709,'2026-07-09','2026-07',3,'2026-07-09T05:00:00'),
(20260710,'2026-07-10','2026-07',4,'2026-07-10T05:00:00'),
(20260711,'2026-07-11','2026-07',5,'2026-07-11T05:00:00'),
(20260712,'2026-07-12','2026-07',6,'2026-07-12T05:00:00'),
(20260713,'2026-07-13','2026-07',0,'2026-07-13T05:00:00'),
(20260714,'2026-07-14','2026-07',1,'2026-07-14T05:00:00'),
(20260715,'2026-07-15','2026-07',2,'2026-07-15T05:00:00'),
(20260716,'2026-07-16','2026-07',3,'2026-07-16T05:00:00'),
(20260717,'2026-07-17','2026-07',4,'2026-07-17T05:00:00'),
(20260718,'2026-07-18','2026-07',5,'2026-07-18T05:00:00'),
(20260719,'2026-07-19','2026-07',6,'2026-07-19T05:00:00'),
(20260720,'2026-07-20','2026-07',0,'2026-07-20T05:00:00'),
(20260721,'2026-07-21','2026-07',1,'2026-07-21T05:00:00'),
(20260722,'2026-07-22','2026-07',2,'2026-07-22T05:00:00'),
(20260723,'2026-07-23','2026-07',3,'2026-07-23T05:00:00'),
(20260724,'2026-07-24','2026-07',4,'2026-07-24T05:00:00'),
(20260725,'2026-07-25','2026-07',5,'2026-07-25T05:00:00'),
(20260726,'2026-07-26','2026-07',6,'2026-07-26T05:00:00'),
(20260727,'2026-07-27','2026-07',0,'2026-07-27T05:00:00'),
(20260728,'2026-07-28','2026-07',1,'2026-07-28T05:00:00'),
(20260729,'2026-07-29','2026-07',2,'2026-07-29T05:00:00'),
(20260730,'2026-07-30','2026-07',3,'2026-07-30T05:00:00'),
(20260731,'2026-07-31','2026-07',4,'2026-07-31T05:00:00'),
(20260801,'2026-08-01','2026-08',5,'2026-08-01T05:00:00'),
(20260802,'2026-08-02','2026-08',6,'2026-08-02T05:00:00'),
(20260803,'2026-08-03','2026-08',0,'2026-08-03T05:00:00'),
(20260804,'2026-08-04','2026-08',1,'2026-08-04T05:00:00'),
(20260805,'2026-08-05','2026-08',2,'2026-08-05T05:00:00'),
(20260806,'2026-08-06','2026-08',3,'2026-08-06T05:00:00'),
(20260807,'2026-08-07','2026-08',4,'2026-08-07T05:00:00'),
(20260808,'2026-08-08','2026-08',5,'2026-08-08T05:00:00'),
(20260809,'2026-08-09','2026-08',6,'2026-08-09T05:00:00'),
(20260810,'2026-08-10','2026-08',0,'2026-08-10T05:00:00'),
(20260811,'2026-08-11','2026-08',1,'2026-08-11T05:00:00'),
(20260812,'2026-08-12','2026-08',2,'2026-08-12T05:00:00'),
(20260813,'2026-08-13','2026-08',3,'2026-08-13T05:00:00'),
(20260814,'2026-08-14','2026-08',4,'2026-08-14T05:00:00'),
(20260815,'2026-08-15','2026-08',5,'2026-08-15T05:00:00'),
(20260816,'2026-08-16','2026-08',6,'2026-08-16T05:00:00'),
(20260817,'2026-08-17','2026-08',0,'2026-08-17T05:00:00'),
(20260818,'2026-08-18','2026-08',1,'2026-08-18T05:00:00'),
(20260819,'2026-08-19','2026-08',2,'2026-08-19T05:00:00'),
(20260820,'2026-08-20','2026-08',3,'2026-08-20T05:00:00'),
(20260821,'2026-08-21','2026-08',4,'2026-08-21T05:00:00'),
(20260822,'2026-08-22','2026-08',5,'2026-08-22T05:00:00'),
(20260823,'2026-08-23','2026-08',6,'2026-08-23T05:00:00'),
(20260824,'2026-08-24','2026-08',0,'2026-08-24T05:00:00'),
(20260825,'2026-08-25','2026-08',1,'2026-08-25T05:00:00'),
(20260826,'2026-08-26','2026-08',2,'2026-08-26T05:00:00'),
(20260827,'2026-08-27','2026-08',3,'2026-08-27T05:00:00'),
(20260828,'2026-08-28','2026-08',4,'2026-08-28T05:00:00'),
(20260829,'2026-08-29','2026-08',5,'2026-08-29T05:00:00'),
(20260830,'2026-08-30','2026-08',6,'2026-08-30T05:00:00'),
(20260831,'2026-08-31','2026-08',0,'2026-08-31T05:00:00'),
(20260901,'2026-09-01','2026-09',1,'2026-09-01T05:00:00'),
(20260902,'2026-09-02','2026-09',2,'2026-09-02T05:00:00'),
(20260903,'2026-09-03','2026-09',3,'2026-09-03T05:00:00'),
(20260904,'2026-09-04','2026-09',4,'2026-09-04T05:00:00'),
(20260905,'2026-09-05','2026-09',5,'2026-09-05T05:00:00'),
(20260906,'2026-09-06','2026-09',6,'2026-09-06T05:00:00'),
(20260907,'2026-09-07','2026-09',0,'2026-09-07T05:00:00'),
(20260908,'2026-09-08','2026-09',1,'2026-09-08T05:00:00'),
(20260909,'2026-09-09','2026-09',2,'2026-09-09T05:00:00'),
(20260910,'2026-09-10','2026-09',3,'2026-09-10T05:00:00'),
(20260911,'2026-09-11','2026-09',4,'2026-09-11T05:00:00'),
(20260912,'2026-09-12','2026-09',5,'2026-09-12T05:00:00'),
(20260913,'2026-09-13','2026-09',6,'2026-09-13T05:00:00'),
(20260914,'2026-09-14','2026-09',0,'2026-09-14T05:00:00'),
(20260915,'2026-09-15','2026-09',1,'2026-09-15T05:00:00'),
(20260916,'2026-09-16','2026-09',2,'2026-09-16T05:00:00'),
(20260917,'2026-09-17','2026-09',3,'2026-09-17T05:00:00'),
(20260918,'2026-09-18','2026-09',4,'2026-09-18T05:00:00'),
(20260919,'2026-09-19','2026-09',5,'2026-09-19T05:00:00'),
(20260920,'2026-09-20','2026-09',6,'2026-09-20T05:00:00'),
(20260921,'2026-09-21','2026-09',0,'2026-09-21T05:00:00'),
(20260922,'2026-09-22','2026-09',1,'2026-09-22T05:00:00'),
(20260923,'2026-09-23','2026-09',2,'2026-09-23T05:00:00'),
(20260924,'2026-09-24','2026-09',3,'2026-09-24T05:00:00'),
(20260925,'2026-09-25','2026-09',4,'2026-09-25T05:00:00'),
(20260926,'2026-09-26','2026-09',5,'2026-09-26T05:00:00'),
(20260927,'2026-09-27','2026-09',6,'2026-09-27T05:00:00'),
(20260928,'2026-09-28','2026-09',0,'2026-09-28T05:00:00'),
(20260929,'2026-09-29','2026-09',1,'2026-09-29T05:00:00'),
(20260930,'2026-09-30','2026-09',2,'2026-09-30T05:00:00'),
(20261001,'2026-10-01','2026-10',3,'2026-10-01T05:00:00'),
(20261002,'2026-10-02','2026-10',4,'2026-10-02T05:00:00'),
(20261003,'2026-10-03','2026-10',5,'2026-10-03T05:00:00'),
(20261004,'2026-10-04','2026-10',6,'2026-10-04T05:00:00'),
(20261005,'2026-10-05','2026-10',0,'2026-10-05T05:00:00'),
(20261006,'2026-10-06','2026-10',1,'2026-10-06T05:00:00'),
(20261007,'2026-10-07','2026-10',2,'2026-10-07T05:00:00'),
(20261008,'2026-10-08','2026-10',3,'2026-10-08T05:00:00'),
(20261009,'2026-10-09','2026-10',4,'2026-10-09T05:00:00'),
(20261010,'2026-10-10','2026-10',5,'2026-10-10T05:00:00'),
(20261011,'2026-10-11','2026-10',6,'2026-10-11T05:00:00'),
(20261012,'2026-10-12','2026-10',0,'2026-10-12T05:00:00'),
(20261013,'2026-10-13','2026-10',1,'2026-10-13T05:00:00'),
(20261014,'2026-10-14','2026-10',2,'2026-10-14T05:00:00'),
(20261015,'2026-10-15','2026-10',3,'2026-10-15T05:00:00'),
(20261016,'2026-10-16','2026-10',4,'2026-10-16T05:00:00'),
(20261017,'2026-10-17','2026-10',5,'2026-10-17T05:00:00'),
(20261018,'2026-10-18','2026-10',6,'2026-10-18T05:00:00'),
(20261019,'2026-10-19','2026-10',0,'2026-10-19T05:00:00'),
(20261020,'2026-10-20','2026-10',1,'2026-10-20T05:00:00'),
(20261021,'2026-10-21','2026-10',2,'2026-10-21T05:00:00'),
(20261022,'2026-10-22','2026-10',3,'2026-10-22T05:00:00'),
(20261023,'2026-10-23','2026-10',4,'2026-10-23T05:00:00'),
(20261024,'2026-10-24','2026-10',5,'2026-10-24T05:00:00'),
(20261025,'2026-10-25','2026-10',6,'2026-10-25T05:00:00'),
(20261026,'2026-10-26','2026-10',0,'2026-10-26T05:00:00'),
(20261027,'2026-10-27','2026-10',1,'2026-10-27T05:00:00'),
(20261028,'2026-10-28','2026-10',2,'2026-10-28T05:00:00'),
(20261029,'2026-10-29','2026-10',3,'2026-10-29T05:00:00');

CREATE TABLE dbo.[ref_department_mapping]([id] BIGINT NOT NULL,[provider_id] BIGINT NOT NULL,[department_id] BIGINT NOT NULL,[valid_from] VARCHAR(240) NOT NULL,[valid_to] VARCHAR(240) NOT NULL,[created_at] DATETIME2(6) NOT NULL,[updated_at] DATETIME2(6) NOT NULL,[updated_by] VARCHAR(240) NOT NULL,[is_deleted] BIGINT NOT NULL);

CREATE TABLE dbo.[ref_payer_group_history]([id] BIGINT NOT NULL,[payer_plan_id] BIGINT NOT NULL,[payer_id] BIGINT NOT NULL,[valid_from] VARCHAR(240) NOT NULL,[valid_to] VARCHAR(240) NOT NULL,[created_at] DATETIME2(6) NOT NULL,[updated_at] DATETIME2(6) NOT NULL,[updated_by] VARCHAR(240) NOT NULL,[is_deleted] BIGINT NOT NULL);


CREATE TABLE dbo.[core_facility] AS SELECT src.[id],src.[name],src.[region],src.[licensed_beds],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted] FROM (SELECT * FROM [hn_raw].[dbo].[raw_clinical_facility]) src;
GO

CREATE OR ALTER PROCEDURE dbo.[sp_core_facility] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[core_facility]; INSERT INTO dbo.[core_facility] SELECT src.[id],src.[name],src.[region],src.[licensed_beds],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted] FROM (SELECT * FROM [hn_raw].[dbo].[raw_clinical_facility]) src; COMMIT; END;
GO

CREATE TABLE dbo.[core_department] AS SELECT src.[id],src.[facility_id],src.[name],src.[service_line],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted] FROM (SELECT * FROM [hn_raw].[dbo].[raw_clinical_department]) src;
GO

CREATE OR ALTER PROCEDURE dbo.[sp_core_department] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[core_department]; INSERT INTO dbo.[core_department] SELECT src.[id],src.[facility_id],src.[name],src.[service_line],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted] FROM (SELECT * FROM [hn_raw].[dbo].[raw_clinical_department]) src; COMMIT; END;
GO

CREATE TABLE dbo.[core_provider] AS SELECT src.[id],src.[synthetic_npi],src.[name],src.[specialty],src.[fte],src.[provider_type],src.[current_department_id],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted] FROM (SELECT * FROM [hn_raw].[dbo].[raw_clinical_provider]) src;
GO

CREATE OR ALTER PROCEDURE dbo.[sp_core_provider] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[core_provider]; INSERT INTO dbo.[core_provider] SELECT src.[id],src.[synthetic_npi],src.[name],src.[specialty],src.[fte],src.[provider_type],src.[current_department_id],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted] FROM (SELECT * FROM [hn_raw].[dbo].[raw_clinical_provider]) src; COMMIT; END;
GO

CREATE TABLE dbo.[core_provider_department_history] AS SELECT src.[id],src.[provider_id],src.[department_id],src.[valid_from],src.[valid_to],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted] FROM (SELECT * FROM ref_department_mapping) src;
GO

CREATE OR ALTER PROCEDURE dbo.[sp_core_provider_department_history] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[core_provider_department_history]; INSERT INTO dbo.[core_provider_department_history] SELECT src.[id],src.[provider_id],src.[department_id],src.[valid_from],src.[valid_to],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted] FROM (SELECT * FROM ref_department_mapping) src; COMMIT; END;
GO

CREATE TABLE dbo.[core_payer] AS SELECT src.[id],src.[name],src.[payer_group],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted] FROM (SELECT * FROM [hn_raw].[dbo].[raw_billing_payer]) src;
GO

CREATE OR ALTER PROCEDURE dbo.[sp_core_payer] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[core_payer]; INSERT INTO dbo.[core_payer] SELECT src.[id],src.[name],src.[payer_group],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted] FROM (SELECT * FROM [hn_raw].[dbo].[raw_billing_payer]) src; COMMIT; END;
GO

CREATE TABLE dbo.[core_payer_plan_history] AS SELECT src.[id],src.[payer_plan_id],src.[payer_id],src.[valid_from],src.[valid_to],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted] FROM (SELECT * FROM ref_payer_group_history) src;
GO

CREATE OR ALTER PROCEDURE dbo.[sp_core_payer_plan_history] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[core_payer_plan_history]; INSERT INTO dbo.[core_payer_plan_history] SELECT src.[id],src.[payer_plan_id],src.[payer_id],src.[valid_from],src.[valid_to],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted] FROM (SELECT * FROM ref_payer_group_history) src; COMMIT; END;
GO

CREATE TABLE dbo.[stg_patient] AS SELECT src.[id],src.[person_key],src.[mrn],src.[given_name],src.[family_name],src.[birth_date],src.[sex],src.[fictional_address],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted],src.[mpi_patient_id] FROM (SELECT * FROM [hn_raw].[dbo].[stg_patient]) src;
GO

CREATE OR ALTER PROCEDURE dbo.[sp_stg_patient] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[stg_patient]; INSERT INTO dbo.[stg_patient] SELECT src.[id],src.[person_key],src.[mrn],src.[given_name],src.[family_name],src.[birth_date],src.[sex],src.[fictional_address],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted],src.[mpi_patient_id] FROM (SELECT * FROM [hn_raw].[dbo].[stg_patient]) src; COMMIT; END;
GO

CREATE TABLE dbo.[mart_encounter] AS SELECT src.[id],src.[encounter_number],src.[patient_id],src.[facility_id],src.[department_id],src.[attending_provider_id],src.[payer_plan_id],src.[encounter_type],src.[initial_status],src.[status],CONVERT(DATETIME2(6),src.[arrival_utc]) [arrival_utc],CONVERT(DATETIME2(6),src.[admit_utc]) [admit_utc],CONVERT(DATETIME2(6),src.[discharge_utc]) [discharge_utc],src.[service_day],src.[readmission_of],src.[transfer_from],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted],src.[mpi_patient_id],src.[masked_mrn],src.[masked_given_name],src.[masked_family_name],src.[service_line],src.[service_provider_department_id] FROM (SELECT e.*,p.mpi_patient_id,
   CONCAT('SYN-***-',RIGHT(p.mrn,4)) masked_mrn,CONCAT(LEFT(p.given_name,1),'***') masked_given_name,CONCAT(LEFT(p.family_name,1),'***') masked_family_name,
   d.service_line,pa.department_id service_provider_department_id
   FROM [hn_raw].[dbo].[raw_clinical_encounter] e JOIN stg_patient p ON p.id=e.patient_id
   JOIN [hn_raw].[dbo].[raw_clinical_department] d ON d.id=e.department_id
   LEFT JOIN core_provider_department_history pa ON pa.provider_id=e.attending_provider_id
   AND e.service_day>=pa.valid_from AND e.service_day<pa.valid_to
   WHERE e.is_deleted=0 AND p.is_deleted=0) src;
GO

CREATE OR ALTER PROCEDURE dbo.[sp_mart_encounter] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[mart_encounter]; INSERT INTO dbo.[mart_encounter] SELECT src.[id],src.[encounter_number],src.[patient_id],src.[facility_id],src.[department_id],src.[attending_provider_id],src.[payer_plan_id],src.[encounter_type],src.[initial_status],src.[status],CONVERT(DATETIME2(6),src.[arrival_utc]) [arrival_utc],CONVERT(DATETIME2(6),src.[admit_utc]) [admit_utc],CONVERT(DATETIME2(6),src.[discharge_utc]) [discharge_utc],src.[service_day],src.[readmission_of],src.[transfer_from],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted],src.[mpi_patient_id],src.[masked_mrn],src.[masked_given_name],src.[masked_family_name],src.[service_line],src.[service_provider_department_id] FROM (SELECT e.*,p.mpi_patient_id,
   CONCAT('SYN-***-',RIGHT(p.mrn,4)) masked_mrn,CONCAT(LEFT(p.given_name,1),'***') masked_given_name,CONCAT(LEFT(p.family_name,1),'***') masked_family_name,
   d.service_line,pa.department_id service_provider_department_id
   FROM [hn_raw].[dbo].[raw_clinical_encounter] e JOIN stg_patient p ON p.id=e.patient_id
   JOIN [hn_raw].[dbo].[raw_clinical_department] d ON d.id=e.department_id
   LEFT JOIN core_provider_department_history pa ON pa.provider_id=e.attending_provider_id
   AND e.service_day>=pa.valid_from AND e.service_day<pa.valid_to
   WHERE e.is_deleted=0 AND p.is_deleted=0) src; COMMIT; END;
GO

CREATE TABLE dbo.[mart_ed_visit] AS SELECT src.[id],src.[encounter_id],src.[triage_level],src.[arrival_local],src.[utc_offset_minutes],src.[door_to_provider_minutes],src.[ed_los_minutes],src.[lwbs],src.[admitted],src.[transferred],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted],src.[arrival_hour],src.[facility_id],src.[department_id],src.[attending_provider_id],src.[service_day] FROM (SELECT v.*,SUBSTRING(v.arrival_local,12,2) arrival_hour,e.facility_id,e.department_id,e.attending_provider_id,e.service_day FROM [hn_raw].[dbo].[raw_clinical_ed_visit_detail] v JOIN [hn_raw].[dbo].[raw_clinical_encounter] e ON e.id=v.encounter_id WHERE e.is_deleted=0) src;
GO

CREATE OR ALTER PROCEDURE dbo.[sp_mart_ed_visit] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[mart_ed_visit]; INSERT INTO dbo.[mart_ed_visit] SELECT src.[id],src.[encounter_id],src.[triage_level],src.[arrival_local],src.[utc_offset_minutes],src.[door_to_provider_minutes],src.[ed_los_minutes],src.[lwbs],src.[admitted],src.[transferred],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted],src.[arrival_hour],src.[facility_id],src.[department_id],src.[attending_provider_id],src.[service_day] FROM (SELECT v.*,SUBSTRING(v.arrival_local,12,2) arrival_hour,e.facility_id,e.department_id,e.attending_provider_id,e.service_day FROM [hn_raw].[dbo].[raw_clinical_ed_visit_detail] v JOIN [hn_raw].[dbo].[raw_clinical_encounter] e ON e.id=v.encounter_id WHERE e.is_deleted=0) src; COMMIT; END;
GO

CREATE TABLE dbo.[mart_order] AS SELECT src.[id],src.[order_header_id],src.[line_number],src.[item_code],src.[priority],src.[status],CONVERT(DATETIME2(6),src.[ordered_utc]) [ordered_utc],CONVERT(DATETIME2(6),src.[completed_utc]) [completed_utc],src.[replaces_order_line_id],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted],src.[encounter_id],src.[provider_id],src.[order_type],src.[facility_id],src.[department_id],src.[service_day] FROM (SELECT l.*,h.encounter_id,h.provider_id,h.order_type,e.facility_id,e.department_id,e.service_day
   FROM [hn_raw].[dbo].[raw_clinical_order_line] l JOIN [hn_raw].[dbo].[raw_clinical_order_header] h ON h.id=l.order_header_id
   JOIN [hn_raw].[dbo].[raw_clinical_encounter] e ON e.id=h.encounter_id WHERE l.is_deleted=0 AND e.is_deleted=0) src;
GO

CREATE OR ALTER PROCEDURE dbo.[sp_mart_order] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[mart_order]; INSERT INTO dbo.[mart_order] SELECT src.[id],src.[order_header_id],src.[line_number],src.[item_code],src.[priority],src.[status],CONVERT(DATETIME2(6),src.[ordered_utc]) [ordered_utc],CONVERT(DATETIME2(6),src.[completed_utc]) [completed_utc],src.[replaces_order_line_id],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted],src.[encounter_id],src.[provider_id],src.[order_type],src.[facility_id],src.[department_id],src.[service_day] FROM (SELECT l.*,h.encounter_id,h.provider_id,h.order_type,e.facility_id,e.department_id,e.service_day
   FROM [hn_raw].[dbo].[raw_clinical_order_line] l JOIN [hn_raw].[dbo].[raw_clinical_order_header] h ON h.id=l.order_header_id
   JOIN [hn_raw].[dbo].[raw_clinical_encounter] e ON e.id=h.encounter_id WHERE l.is_deleted=0 AND e.is_deleted=0) src; COMMIT; END;
GO

CREATE TABLE dbo.[mart_charge] AS SELECT src.[id],src.[account_id],src.[service_date],src.[post_date],src.[revenue_centre_code],src.[procedure_code],src.[units],src.[amount_cents],src.[correction_of],src.[correction_reason],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted],src.[encounter_number],src.[facility_id],src.[department_id],src.[payer_plan_id],src.[payer_id] FROM (SELECT c.*,a.encounter_number,a.facility_id,e.department_id,a.payer_plan_id,h.payer_id
   FROM [hn_raw].[dbo].[raw_billing_charge] c JOIN [hn_raw].[dbo].[raw_billing_account] a ON a.id=c.account_id LEFT JOIN [hn_raw].[dbo].[raw_clinical_encounter] e ON e.encounter_number=a.encounter_number
   JOIN core_payer_plan_history h ON h.payer_plan_id=a.payer_plan_id
   AND c.service_date>=h.valid_from AND c.service_date<h.valid_to
   WHERE c.is_deleted=0 AND a.is_deleted=0) src;
GO

CREATE OR ALTER PROCEDURE dbo.[sp_mart_charge] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[mart_charge]; INSERT INTO dbo.[mart_charge] SELECT src.[id],src.[account_id],src.[service_date],src.[post_date],src.[revenue_centre_code],src.[procedure_code],src.[units],src.[amount_cents],src.[correction_of],src.[correction_reason],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted],src.[encounter_number],src.[facility_id],src.[department_id],src.[payer_plan_id],src.[payer_id] FROM (SELECT c.*,a.encounter_number,a.facility_id,e.department_id,a.payer_plan_id,h.payer_id
   FROM [hn_raw].[dbo].[raw_billing_charge] c JOIN [hn_raw].[dbo].[raw_billing_account] a ON a.id=c.account_id LEFT JOIN [hn_raw].[dbo].[raw_clinical_encounter] e ON e.encounter_number=a.encounter_number
   JOIN core_payer_plan_history h ON h.payer_plan_id=a.payer_plan_id
   AND c.service_date>=h.valid_from AND c.service_date<h.valid_to
   WHERE c.is_deleted=0 AND a.is_deleted=0) src; COMMIT; END;
GO

CREATE TABLE dbo.[mart_claim] AS SELECT src.[id],src.[account_id],src.[claim_group],src.[version],src.[submission_type],src.[is_original],src.[is_final],src.[bill_type],src.[ms_drg],CONVERT(DATETIME2(6),src.[submitted_at]) [submitted_at],src.[status],src.[billed_cents],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted],src.[submitted_date],src.[facility_id],src.[department_id],src.[payer_plan_id],src.[payer_id] FROM (SELECT c.*,SUBSTRING(c.submitted_at,1,10) submitted_date,a.facility_id,e.department_id,a.payer_plan_id,ph.payer_id FROM [hn_raw].[dbo].[raw_billing_claim] c JOIN [hn_raw].[dbo].[raw_billing_account] a ON a.id=c.account_id LEFT JOIN [hn_raw].[dbo].[raw_clinical_encounter] e ON e.encounter_number=a.encounter_number JOIN core_payer_plan_history ph ON ph.payer_plan_id=a.payer_plan_id AND SUBSTRING(c.submitted_at,1,10)>=ph.valid_from AND SUBSTRING(c.submitted_at,1,10)<ph.valid_to WHERE c.is_deleted=0 AND a.is_deleted=0) src;
GO

CREATE OR ALTER PROCEDURE dbo.[sp_mart_claim] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[mart_claim]; INSERT INTO dbo.[mart_claim] SELECT src.[id],src.[account_id],src.[claim_group],src.[version],src.[submission_type],src.[is_original],src.[is_final],src.[bill_type],src.[ms_drg],CONVERT(DATETIME2(6),src.[submitted_at]) [submitted_at],src.[status],src.[billed_cents],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted],src.[submitted_date],src.[facility_id],src.[department_id],src.[payer_plan_id],src.[payer_id] FROM (SELECT c.*,SUBSTRING(c.submitted_at,1,10) submitted_date,a.facility_id,e.department_id,a.payer_plan_id,ph.payer_id FROM [hn_raw].[dbo].[raw_billing_claim] c JOIN [hn_raw].[dbo].[raw_billing_account] a ON a.id=c.account_id LEFT JOIN [hn_raw].[dbo].[raw_clinical_encounter] e ON e.encounter_number=a.encounter_number JOIN core_payer_plan_history ph ON ph.payer_plan_id=a.payer_plan_id AND SUBSTRING(c.submitted_at,1,10)>=ph.valid_from AND SUBSTRING(c.submitted_at,1,10)<ph.valid_to WHERE c.is_deleted=0 AND a.is_deleted=0) src; COMMIT; END;
GO

CREATE TABLE dbo.[mart_remittance] AS SELECT src.[id],src.[remittance_id],src.[claim_line_id],src.[paid_cents],src.[adjusted_cents],src.[denied_cents],src.[denial_code],src.[denial_category],src.[remark_code],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted],src.[claim_id],CONVERT(DATETIME2(6),src.[received_at]) [received_at],src.[received_date],src.[account_id],src.[is_original],src.[is_final],src.[facility_id],src.[department_id],src.[payer_plan_id],src.[payer_id] FROM (SELECT l.*,r.claim_id,r.received_at,SUBSTRING(r.received_at,1,10) received_date,c.account_id,c.is_original,c.is_final,a.facility_id,e.department_id,a.payer_plan_id,ph.payer_id
   FROM [hn_raw].[dbo].[raw_billing_remittance_line] l JOIN [hn_raw].[dbo].[raw_billing_remittance] r ON r.id=l.remittance_id
   JOIN [hn_raw].[dbo].[raw_billing_claim] c ON c.id=r.claim_id JOIN [hn_raw].[dbo].[raw_billing_account] a ON a.id=c.account_id LEFT JOIN [hn_raw].[dbo].[raw_clinical_encounter] e ON e.encounter_number=a.encounter_number
   JOIN core_payer_plan_history ph ON ph.payer_plan_id=a.payer_plan_id AND SUBSTRING(r.received_at,1,10)>=ph.valid_from AND SUBSTRING(r.received_at,1,10)<ph.valid_to
   WHERE l.is_deleted=0 AND r.is_deleted=0 AND c.is_deleted=0 AND a.is_deleted=0) src;
GO

CREATE OR ALTER PROCEDURE dbo.[sp_mart_remittance] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[mart_remittance]; INSERT INTO dbo.[mart_remittance] SELECT src.[id],src.[remittance_id],src.[claim_line_id],src.[paid_cents],src.[adjusted_cents],src.[denied_cents],src.[denial_code],src.[denial_category],src.[remark_code],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted],src.[claim_id],CONVERT(DATETIME2(6),src.[received_at]) [received_at],src.[received_date],src.[account_id],src.[is_original],src.[is_final],src.[facility_id],src.[department_id],src.[payer_plan_id],src.[payer_id] FROM (SELECT l.*,r.claim_id,r.received_at,SUBSTRING(r.received_at,1,10) received_date,c.account_id,c.is_original,c.is_final,a.facility_id,e.department_id,a.payer_plan_id,ph.payer_id
   FROM [hn_raw].[dbo].[raw_billing_remittance_line] l JOIN [hn_raw].[dbo].[raw_billing_remittance] r ON r.id=l.remittance_id
   JOIN [hn_raw].[dbo].[raw_billing_claim] c ON c.id=r.claim_id JOIN [hn_raw].[dbo].[raw_billing_account] a ON a.id=c.account_id LEFT JOIN [hn_raw].[dbo].[raw_clinical_encounter] e ON e.encounter_number=a.encounter_number
   JOIN core_payer_plan_history ph ON ph.payer_plan_id=a.payer_plan_id AND SUBSTRING(r.received_at,1,10)>=ph.valid_from AND SUBSTRING(r.received_at,1,10)<ph.valid_to
   WHERE l.is_deleted=0 AND r.is_deleted=0 AND c.is_deleted=0 AND a.is_deleted=0) src; COMMIT; END;
GO

CREATE TABLE dbo.[mart_payment] AS SELECT src.[id],src.[account_id],src.[claim_id],src.[payment_date],src.[amount_cents],src.[payment_type],src.[reverses_payment_id],src.[moved_to_account_id],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted],src.[facility_id],src.[department_id],src.[payer_plan_id],src.[payer_id] FROM (SELECT p.*,a.facility_id,e.department_id,a.payer_plan_id,ph.payer_id FROM [hn_raw].[dbo].[raw_billing_payment] p JOIN [hn_raw].[dbo].[raw_billing_account] a ON a.id=p.account_id LEFT JOIN [hn_raw].[dbo].[raw_clinical_encounter] e ON e.encounter_number=a.encounter_number JOIN core_payer_plan_history ph ON ph.payer_plan_id=a.payer_plan_id AND p.payment_date>=ph.valid_from AND p.payment_date<ph.valid_to WHERE p.is_deleted=0 AND a.is_deleted=0) src;
GO

CREATE OR ALTER PROCEDURE dbo.[sp_mart_payment] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[mart_payment]; INSERT INTO dbo.[mart_payment] SELECT src.[id],src.[account_id],src.[claim_id],src.[payment_date],src.[amount_cents],src.[payment_type],src.[reverses_payment_id],src.[moved_to_account_id],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted],src.[facility_id],src.[department_id],src.[payer_plan_id],src.[payer_id] FROM (SELECT p.*,a.facility_id,e.department_id,a.payer_plan_id,ph.payer_id FROM [hn_raw].[dbo].[raw_billing_payment] p JOIN [hn_raw].[dbo].[raw_billing_account] a ON a.id=p.account_id LEFT JOIN [hn_raw].[dbo].[raw_clinical_encounter] e ON e.encounter_number=a.encounter_number JOIN core_payer_plan_history ph ON ph.payer_plan_id=a.payer_plan_id AND p.payment_date>=ph.valid_from AND p.payment_date<ph.valid_to WHERE p.is_deleted=0 AND a.is_deleted=0) src; COMMIT; END;
GO

CREATE TABLE dbo.[mart_adjustment] AS SELECT src.[id],src.[account_id],src.[adjustment_date],src.[amount_cents],src.[adjustment_type],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted],src.[facility_id],src.[department_id],src.[payer_plan_id],src.[payer_id] FROM (SELECT p.*,a.facility_id,e.department_id,a.payer_plan_id,ph.payer_id FROM [hn_raw].[dbo].[raw_billing_adjustment] p JOIN [hn_raw].[dbo].[raw_billing_account] a ON a.id=p.account_id LEFT JOIN [hn_raw].[dbo].[raw_clinical_encounter] e ON e.encounter_number=a.encounter_number JOIN core_payer_plan_history ph ON ph.payer_plan_id=a.payer_plan_id AND p.adjustment_date>=ph.valid_from AND p.adjustment_date<ph.valid_to WHERE p.is_deleted=0 AND a.is_deleted=0) src;
GO

CREATE OR ALTER PROCEDURE dbo.[sp_mart_adjustment] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[mart_adjustment]; INSERT INTO dbo.[mart_adjustment] SELECT src.[id],src.[account_id],src.[adjustment_date],src.[amount_cents],src.[adjustment_type],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted],src.[facility_id],src.[department_id],src.[payer_plan_id],src.[payer_id] FROM (SELECT p.*,a.facility_id,e.department_id,a.payer_plan_id,ph.payer_id FROM [hn_raw].[dbo].[raw_billing_adjustment] p JOIN [hn_raw].[dbo].[raw_billing_account] a ON a.id=p.account_id LEFT JOIN [hn_raw].[dbo].[raw_clinical_encounter] e ON e.encounter_number=a.encounter_number JOIN core_payer_plan_history ph ON ph.payer_plan_id=a.payer_plan_id AND p.adjustment_date>=ph.valid_from AND p.adjustment_date<ph.valid_to WHERE p.is_deleted=0 AND a.is_deleted=0) src; COMMIT; END;
GO

CREATE TABLE dbo.[mart_ar_aging] AS SELECT src.[id],src.[snapshot_date],src.[facility_id],src.[payer_id],src.[aging_bucket],src.[balance_cents],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted] FROM (SELECT * FROM [hn_raw].[dbo].[raw_billing_ar_snapshot_daily] WHERE is_deleted=0) src;
GO

CREATE OR ALTER PROCEDURE dbo.[sp_mart_ar_aging] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[mart_ar_aging]; INSERT INTO dbo.[mart_ar_aging] SELECT src.[id],src.[snapshot_date],src.[facility_id],src.[payer_id],src.[aging_bucket],src.[balance_cents],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted] FROM (SELECT * FROM [hn_raw].[dbo].[raw_billing_ar_snapshot_daily] WHERE is_deleted=0) src; COMMIT; END;
GO

CREATE TABLE dbo.[mart_procedure] AS SELECT src.[id],src.[encounter_id],src.[provider_id],src.[code_system],src.[code],src.[description],CONVERT(DATETIME2(6),src.[performed_utc]) [performed_utc],src.[workload_units],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted],src.[facility_id],src.[department_id],src.[service_day] FROM (SELECT p.*,e.facility_id,e.department_id,e.service_day FROM [hn_raw].[dbo].[raw_clinical_procedure] p
   JOIN [hn_raw].[dbo].[raw_clinical_encounter] e ON e.id=p.encounter_id WHERE p.is_deleted=0 AND e.is_deleted=0) src;
GO

CREATE OR ALTER PROCEDURE dbo.[sp_mart_procedure] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[mart_procedure]; INSERT INTO dbo.[mart_procedure] SELECT src.[id],src.[encounter_id],src.[provider_id],src.[code_system],src.[code],src.[description],CONVERT(DATETIME2(6),src.[performed_utc]) [performed_utc],src.[workload_units],CONVERT(DATETIME2(6),src.[created_at]) [created_at],CONVERT(DATETIME2(6),src.[updated_at]) [updated_at],src.[updated_by],src.[is_deleted],src.[facility_id],src.[department_id],src.[service_day] FROM (SELECT p.*,e.facility_id,e.department_id,e.service_day FROM [hn_raw].[dbo].[raw_clinical_procedure] p
   JOIN [hn_raw].[dbo].[raw_clinical_encounter] e ON e.id=p.encounter_id WHERE p.is_deleted=0 AND e.is_deleted=0) src; COMMIT; END;
GO

CREATE TABLE dbo.[mart_census_daily] AS SELECT src.[id],src.[calendar_date],src.[facility_id],src.[midnight_census],src.[licensed_beds],src.[occupancy_fraction] FROM (SELECT d.id*10+f.id id,d.calendar_date,f.id facility_id,
   COUNT(b.id) midnight_census,f.licensed_beds,
   1.0*COUNT(b.id)/f.licensed_beds occupancy_fraction
   FROM core_date d CROSS JOIN [hn_raw].[dbo].[raw_clinical_facility] f
   LEFT JOIN [hn_raw].[dbo].[raw_clinical_bed] bed ON bed.facility_id=f.id
   LEFT JOIN [hn_raw].[dbo].[raw_clinical_bed_assignment] b ON b.bed_id=bed.id
     AND b.start_utc<=d.local_midnight_utc AND (b.end_utc>d.local_midnight_utc OR b.end_utc IS NULL)
   GROUP BY d.id,d.calendar_date,f.id,f.licensed_beds) src;
GO

CREATE OR ALTER PROCEDURE dbo.[sp_mart_census_daily] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[mart_census_daily]; INSERT INTO dbo.[mart_census_daily] SELECT src.[id],src.[calendar_date],src.[facility_id],src.[midnight_census],src.[licensed_beds],src.[occupancy_fraction] FROM (SELECT d.id*10+f.id id,d.calendar_date,f.id facility_id,
   COUNT(b.id) midnight_census,f.licensed_beds,
   1.0*COUNT(b.id)/f.licensed_beds occupancy_fraction
   FROM core_date d CROSS JOIN [hn_raw].[dbo].[raw_clinical_facility] f
   LEFT JOIN [hn_raw].[dbo].[raw_clinical_bed] bed ON bed.facility_id=f.id
   LEFT JOIN [hn_raw].[dbo].[raw_clinical_bed_assignment] b ON b.bed_id=bed.id
     AND b.start_utc<=d.local_midnight_utc AND (b.end_utc>d.local_midnight_utc OR b.end_utc IS NULL)
   GROUP BY d.id,d.calendar_date,f.id,f.licensed_beds) src; COMMIT; END;
GO

CREATE TABLE dbo.[mart_provider_productivity_daily] AS SELECT src.[id],src.[service_day],src.[provider_id],src.[facility_id],src.[department_id],src.[visits],src.[fte],src.[workload_units],src.[procedures],src.[orders],src.[synthetic_cost_cents],src.[synthetic_margin_cents] FROM (SELECT
   ROW_NUMBER()OVER(ORDER BY e.service_day,e.attending_provider_id,e.facility_id,pa.department_id) id,
   e.service_day,e.attending_provider_id provider_id,e.facility_id,pa.department_id,
   COUNT(*) visits,p.fte,
   COALESCE(SUM(pr.workload_units),0) workload_units,
   COALESCE(SUM(pr.procedures),0) procedures,
   COALESCE(SUM(o.orders),0) orders,
   CAST(ROUND(COALESCE(SUM(pr.workload_units),0)*5000,0) AS BIGINT) synthetic_cost_cents,
   CAST(ROUND(COALESCE(SUM(pr.workload_units),0)*2000,0) AS BIGINT) synthetic_margin_cents
   FROM [hn_raw].[dbo].[raw_clinical_encounter] e JOIN [hn_raw].[dbo].[raw_clinical_provider] p ON p.id=e.attending_provider_id
   JOIN core_provider_department_history pa ON pa.provider_id=p.id AND e.service_day>=pa.valid_from AND e.service_day<pa.valid_to
   LEFT JOIN(SELECT encounter_id,COUNT(*) procedures,SUM(workload_units) workload_units FROM [hn_raw].[dbo].[raw_clinical_procedure] WHERE is_deleted=0 GROUP BY encounter_id)pr ON pr.encounter_id=e.id
   LEFT JOIN(SELECT encounter_id,COUNT(*) orders FROM [hn_raw].[dbo].[raw_clinical_order_header] WHERE is_deleted=0 GROUP BY encounter_id)o ON o.encounter_id=e.id
   WHERE e.is_deleted=0
   GROUP BY e.service_day,e.attending_provider_id,e.facility_id,pa.department_id,p.fte) src;
GO

CREATE OR ALTER PROCEDURE dbo.[sp_mart_provider_productivity_daily] AS BEGIN SET NOCOUNT ON; BEGIN TRANSACTION; DELETE FROM dbo.[mart_provider_productivity_daily]; INSERT INTO dbo.[mart_provider_productivity_daily] SELECT src.[id],src.[service_day],src.[provider_id],src.[facility_id],src.[department_id],src.[visits],src.[fte],src.[workload_units],src.[procedures],src.[orders],src.[synthetic_cost_cents],src.[synthetic_margin_cents] FROM (SELECT
   ROW_NUMBER()OVER(ORDER BY e.service_day,e.attending_provider_id,e.facility_id,pa.department_id) id,
   e.service_day,e.attending_provider_id provider_id,e.facility_id,pa.department_id,
   COUNT(*) visits,p.fte,
   COALESCE(SUM(pr.workload_units),0) workload_units,
   COALESCE(SUM(pr.procedures),0) procedures,
   COALESCE(SUM(o.orders),0) orders,
   CAST(ROUND(COALESCE(SUM(pr.workload_units),0)*5000,0) AS BIGINT) synthetic_cost_cents,
   CAST(ROUND(COALESCE(SUM(pr.workload_units),0)*2000,0) AS BIGINT) synthetic_margin_cents
   FROM [hn_raw].[dbo].[raw_clinical_encounter] e JOIN [hn_raw].[dbo].[raw_clinical_provider] p ON p.id=e.attending_provider_id
   JOIN core_provider_department_history pa ON pa.provider_id=p.id AND e.service_day>=pa.valid_from AND e.service_day<pa.valid_to
   LEFT JOIN(SELECT encounter_id,COUNT(*) procedures,SUM(workload_units) workload_units FROM [hn_raw].[dbo].[raw_clinical_procedure] WHERE is_deleted=0 GROUP BY encounter_id)pr ON pr.encounter_id=e.id
   LEFT JOIN(SELECT encounter_id,COUNT(*) orders FROM [hn_raw].[dbo].[raw_clinical_order_header] WHERE is_deleted=0 GROUP BY encounter_id)o ON o.encounter_id=e.id
   WHERE e.is_deleted=0
   GROUP BY e.service_day,e.attending_provider_id,e.facility_id,pa.department_id,p.fte) src; COMMIT; END;
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
EXEC dbo.[sp_mart_census_daily];
EXEC dbo.[sp_mart_provider_productivity_daily];
END;
GO
