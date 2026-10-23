"""Publisher-only, isolated data visibility fixture in the existing billing DB.

Both actors retain their existing db_datareader role. This is identity-dependent
data/query logic, not an installed RLS security policy or a permission change.
"""
import re
from .source_history import number

ROWS='[app].[round22_access_rows]'
READERS='[app].[round22_access_readers]'
EXPORT='[app].[round22_access_export]'
ACTORS=('orderops_investigator','dia-investigator-round19')
DATA=[(case,group,10*case+(5 if group else 0))for case in (1,2,3)for group in (0,1)]
VIEW=('CREATE VIEW '+EXPORT+' AS SELECT r.case_id,'
      'SUM(CASE WHEN m.reader_name IS NOT NULL THEN CONVERT(bigint,r.units) END) AS quantity,'
      'COUNT(m.reader_name) AS visible_rows FROM '+ROWS+' AS r LEFT JOIN '+READERS+
      ' AS m ON m.visibility_group=r.visibility_group AND m.reader_name=CURRENT_USER GROUP BY r.case_id;')


class AccessSourceScenario:
    def __init__(self,inspection):
        if inspection.get('status')!='METADATA_AVAILABLE':raise ValueError('ACCESS_NATIVE_READER_INSPECTION_REQUIRED')
        sets=inspection['attempts'][-1]['body']['sets']
        if len(sets)!=3 or sets[0][0]['database_name']!='billingapp' or not sets[0][0]['app_schema_id']:
            raise ValueError('ACCESS_APPROVED_DATABASE_REQUIRED')
        if {(r['name'],r['role_name'])for r in sets[1]}!={(actor,'db_datareader')for actor in ACTORS} or len(sets[1])!=2:
            raise ValueError('ACCESS_EXISTING_READERS_ONLY')
        if len(sets[2])!=1 or any(v is not None for v in sets[2][0].values()):raise ValueError('ACCESS_OBJECT_ALREADY_EXISTS')

    @staticmethod
    def fingerprint():
        return ("CONVERT(varchar(64),HASHBYTES('SHA2_256',CONVERT(nvarchar(max),"
          "COALESCE((SELECT case_id,visibility_group,units FROM "+ROWS+" ORDER BY case_id,visibility_group FOR JSON PATH),N'[]')+"
          "COALESCE((SELECT reader_name,visibility_group FROM "+READERS+" ORDER BY reader_name,visibility_group FOR JSON PATH),N'[]')+"
          "COALESCE(OBJECT_DEFINITION(OBJECT_ID(N'app.round22_access_export')),N''))),2)")

    @classmethod
    def inventory(cls):
        return ("SELECT OBJECT_ID(N'app.round22_access_rows') AS rows_id,OBJECT_ID(N'app.round22_access_readers') AS readers_id,"
          "OBJECT_ID(N'app.round22_access_export') AS export_id,(SELECT COUNT_BIG(*) FROM "+ROWS+
          ') AS row_count,(SELECT COUNT_BIG(*) FROM '+READERS+') AS reader_mapping_count,'+cls.fingerprint()+' AS fixture_sha256;')

    @classmethod
    def create(cls):
        values=','.join('('+','.join(map(str,row))+')'for row in DATA)
        # All text is constant fixture code; none is supplied by a model.
        quoted=VIEW.replace("'","''")
        return ("SET NOCOUNT ON; SET XACT_ABORT ON; SET LOCK_TIMEOUT 5000; BEGIN TRY BEGIN TRANSACTION;\n"
          "IF DB_NAME()<>N'billingapp' THROW 51022, 'Approved database differs', 1;\n"
          "IF OBJECT_ID(N'app.round22_access_rows') IS NOT NULL OR OBJECT_ID(N'app.round22_access_readers') IS NOT NULL OR OBJECT_ID(N'app.round22_access_export') IS NOT NULL THROW 51022, 'Isolated access fixture already exists', 1;\n"
          'CREATE TABLE '+ROWS+' (case_id int NOT NULL,visibility_group int NOT NULL,units int NOT NULL,PRIMARY KEY(case_id,visibility_group));\n'
          'CREATE TABLE '+READERS+' (reader_name nvarchar(128) NOT NULL,visibility_group int NOT NULL,PRIMARY KEY(reader_name,visibility_group));\n'
          'INSERT INTO '+ROWS+' VALUES '+values+';\n'
          'INSERT INTO '+READERS+" VALUES (N'orderops_investigator',0),(N'dia-investigator-round19',0),(N'dia-investigator-round19',1);\n"
          "EXEC sys.sp_executesql N'"+quoted+"';\n"+cls.inventory()+
          '\nCOMMIT TRANSACTION; END TRY BEGIN CATCH IF @@TRANCOUNT>0 ROLLBACK TRANSACTION; THROW; END CATCH;')

    @staticmethod
    def read():
        return {'query':'SELECT TOP (4) case_id,quantity,visible_rows FROM '+EXPORT+' ORDER BY case_id',
                'read_only_objects':[EXPORT],'parameters':[],'max_rows':4,'result_columns':['case_id','quantity','visible_rows']}

    @classmethod
    def cleanup(cls,receipt):
        expected={'rows_id','readers_id','export_id','row_count','reader_mapping_count','fixture_sha256'}
        if not isinstance(receipt,dict)or set(receipt)!=expected:raise ValueError('ACCESS_NATIVE_OWNERSHIP_RECEIPT_REQUIRED')
        digest=receipt['fixture_sha256']
        if not isinstance(digest,str)or not re.fullmatch('[a-fA-F0-9]{64}',digest):raise ValueError('ACCESS_NATIVE_FIXTURE_DIGEST_REQUIRED')
        if (number(receipt['row_count']),number(receipt['reader_mapping_count']))!=(6,3):raise ValueError('ACCESS_FIXTURE_COUNTS_DIFFER')
        guard=[]
        for name in ('rows','readers','export'):
            guard.append("COALESCE(OBJECT_ID(N'app.round22_access_"+name+"'),-1)<>"+str(number(receipt[name+'_id'],1)))
        return ("SET NOCOUNT ON; SET XACT_ABORT ON; SET LOCK_TIMEOUT 5000; BEGIN TRY BEGIN TRANSACTION;\n"
          "IF DB_NAME()<>N'billingapp' OR "+' OR '.join(guard)+" THROW 51022, 'Owned access objects differ', 1;\n"
          'IF (SELECT COUNT_BIG(*) FROM '+ROWS+')<>6 OR (SELECT COUNT_BIG(*) FROM '+READERS+
          ")<>3 OR COALESCE("+cls.fingerprint()+",'')<>UPPER('"+digest+"') THROW 51022, 'Access fixture changed since capture', 1;\n"
          'DROP VIEW '+EXPORT+'; DROP TABLE '+READERS+'; DROP TABLE '+ROWS+';\n'
          'COMMIT TRANSACTION; END TRY BEGIN CATCH IF @@TRANCOUNT>0 ROLLBACK TRANSACTION; THROW; END CATCH;')
