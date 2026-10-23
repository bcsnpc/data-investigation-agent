"""Owner-only temporal-history plans for the existing synthetic practice source.

No credential, executor or investigator write capability is installed here.
The publisher must journal dispatch and verify the returned native metadata.
History stays available until every dependent scored case has finished.
"""
import re
from datetime import datetime
from .source_history import SourceHistoryScenario,TABLE,number,row,FIELDS

HISTORY='[app].[stock_movements_round22_history]'
START='r22_valid_from'
END='r22_valid_to'
DEFAULT_START='DF_round22_source_valid_from'
DEFAULT_END='DF_round22_source_valid_to'


class TemporalSourceScenario:
    def __init__(self,baseline,inspection):
        self.source=SourceHistoryScenario(baseline)
        if (inspection.get('read_only')is not True or inspection.get('exit_code')!=0
                or inspection.get('body',{}).get('status')!='COMPLETED'):
            raise ValueError('TEMPORAL_NATIVE_INSPECTION_REQUIRED')
        sets=inspection['body']['sets']
        if len(sets)!=4 or len(sets[0])!=1:raise ValueError('TEMPORAL_INSPECTION_SHAPE')
        native=sets[0][0]
        if (number(native['temporal_type'])!=0 or number(native['primary_keys'])!=1
                or number(native['triggers'])!=0 or str(native['is_memory_optimized']).lower()!='false'
                or native.get('history_table_id')not in (None,'0',0) or native.get('proposed_history_id')is not None):
            raise ValueError('TEMPORAL_PREEXISTING_FEATURE_OR_HISTORY')
        keys=[r for r in sets[1]if str(r['is_primary_key']).lower()=='true']
        if len(keys)!=1 or keys[0]['column_name']!='movement_id':raise ValueError('TEMPORAL_PRIMARY_KEY_DIFFERS')
        columns=sets[2]
        if ([r['name']for r in columns]!=[*FIELDS,'source_modified_at_utc','source_row_version']
                or any(number(r['generated_always_type'])!=0 or str(r['is_hidden']).lower()!='false' for r in columns)):
            raise ValueError('TEMPORAL_SOURCE_COLUMNS_DIFFER')
        totals=sets[3]
        if len(totals)!=1 or (number(totals[0]['row_count']),number(totals[0]['units'],-9223372036854775808,9223372036854775807),number(totals[0]['newest_version'],0,9223372036854775807))!=(self.source.count,self.source.total,self.source.version):
            raise ValueError('TEMPORAL_SOURCE_PREIMAGE_DIFFERS')
        self.object_id=number(native['object_id'],1)

    @staticmethod
    def metadata():
        return ('SELECT t.object_id,t.temporal_type,t.history_table_id,'
                'OBJECT_SCHEMA_NAME(t.history_table_id) AS history_schema,OBJECT_NAME(t.history_table_id) AS history_name '
                'FROM sys.tables t WHERE t.object_id=OBJECT_ID(N\'app.stock_movements_round_two_20261003\');\n'
                'SELECT c.name,c.generated_always_type,c.is_hidden FROM sys.columns c '
                'WHERE c.object_id=OBJECT_ID(N\'app.stock_movements_round_two_20261003\') ORDER BY c.column_id;\n')

    def enable(self,*,rollback_probe=False):
        if type(rollback_probe)is not bool:raise ValueError('TEMPORAL_PROBE_BOOLEAN')
        # One atomic DDL transaction: any compatibility failure rolls back.
        prefix='SET NOCOUNT ON; SET XACT_ABORT ON; SET LOCK_TIMEOUT 5000; BEGIN TRY BEGIN TRANSACTION;\n'
        guard=(self.source.guard()+"IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE object_id="+str(self.object_id)+
               " AND temporal_type=0 AND history_table_id IS NULL) OR OBJECT_ID(N'app.stock_movements_round22_history') IS NOT NULL "
               "THROW 51022, 'Temporal preimage or proposed history changed', 1;\n")
        ddl=('ALTER TABLE '+TABLE+' ADD ['+START+'] datetime2(7) GENERATED ALWAYS AS ROW START HIDDEN NOT NULL '
             'CONSTRAINT ['+DEFAULT_START+'] DEFAULT SYSUTCDATETIME(), ['+END+'] datetime2(7) GENERATED ALWAYS AS ROW END HIDDEN NOT NULL '
             'CONSTRAINT ['+DEFAULT_END+"] DEFAULT CONVERT(datetime2(7),'9999-12-31 23:59:59.9999999'), "
             'PERIOD FOR SYSTEM_TIME (['+START+'],['+END+']);\n'
             'ALTER TABLE '+TABLE+' SET (SYSTEM_VERSIONING=ON (HISTORY_TABLE='+HISTORY+',DATA_CONSISTENCY_CHECK=ON));\n')
        # Adding period columns must not rewrite the original values/versions.
        check=self.source.guard()+self.metadata()
        finish='ROLLBACK TRANSACTION;\n'if rollback_probe else'COMMIT TRANSACTION;\n'
        return prefix+guard+ddl+check+finish+'END TRY BEGIN CATCH IF @@TRANCOUNT>0 ROLLBACK TRANSACTION; THROW; END CATCH;\n'+self.metadata()

    @staticmethod
    def observation(values):
        if not isinstance(values,list)or not 1<=len(values)<=3:raise ValueError('SOURCE_CASE_ROW_BOUND')
        values=[row(r)for r in values];ids=[r['movement_id']for r in values]
        if len(set(ids))!=len(ids):raise ValueError('SOURCE_CASE_DUPLICATE_ID')
        parameters=[{'name':'@case_id_'+str(i),'value':identity}for i,identity in enumerate(ids)]
        fields=[*FIELDS,'source_modified_at_utc','CONVERT(bigint,source_row_version) AS source_row_version',
                'CONVERT(varchar(33),['+START+'],126) AS '+START,
                'CONVERT(varchar(33),['+END+'],126) AS '+END]
        return {'query':'SELECT TOP (101) '+','.join(fields)+' FROM '+TABLE+' FOR SYSTEM_TIME ALL WHERE movement_id IN ('+
                ','.join(p['name']for p in parameters)+') ORDER BY movement_id,'+START,
                'parameters':parameters,'read_only_objects':[TABLE],'max_rows':101,
                'result_columns':[*FIELDS,'source_modified_at_utc','source_row_version',START,END]}

    @staticmethod
    def history_digest():
        # Native digest binds cleanup to exactly the history that was retained.
        fields=[*FIELDS,'source_modified_at_utc','CONVERT(bigint,source_row_version) AS source_row_version',START,END]
        rows='SELECT '+','.join(fields)+' FROM '+HISTORY+' ORDER BY movement_id,'+START+','+END+' FOR JSON PATH,INCLUDE_NULL_VALUES'
        return "CONVERT(varchar(64),HASHBYTES('SHA2_256',CONVERT(nvarchar(max),COALESCE(("+rows+"),N'[]'))),2)"

    @classmethod
    def comparison(cls,values,*,before,after):
        """Native point-in-time quantities; absence stays NULL plus count zero.

        This is a bounded fixture observation, not ticket admission or a model
        authored query. Both times must fall within the retained history epoch.
        The scored harness must verify that epoch before admitting the case.
        """
        def instant(value):
            if not isinstance(value,str):raise ValueError('TEMPORAL_EXACT_UTC_REQUIRED')
            match=re.fullmatch(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d{1,7}))?Z',value)
            if not match:raise ValueError('TEMPORAL_EXACT_UTC_REQUIRED')
            datetime.fromisoformat(value.replace('Z','+00:00'))
            return match[1],(match[2]or'').ljust(7,'0')
        if instant(before)>=instant(after):raise ValueError('TEMPORAL_COMPARISON_ORDER')
        request=cls.observation(values)
        fields=['movement_id','CONVERT(varchar(33),(SELECT MIN(['+START+']) FROM '+TABLE+'),126) AS history_coverage_from']
        for label in ('before','after'):
            at='CONVERT(datetime2(7),@as_of_'+label+',127)'
            condition='['+START+']<='+at+' AND ['+END+']>'+at
            fields.extend(['COUNT(CASE WHEN '+condition+' THEN 1 END) AS '+label+'_rows',
                           'SUM(CASE WHEN '+condition+' THEN CONVERT(bigint,units) END) AS '+label+'_quantity'])
        request['query']='SELECT TOP ('+str(len(values)+1)+') '+','.join(fields)+' FROM '+TABLE+' FOR SYSTEM_TIME ALL WHERE movement_id IN ('+','.join(p['name']for p in request['parameters'])+') GROUP BY movement_id ORDER BY movement_id'
        request['parameters'] += [{'name':'@as_of_before','value':before},{'name':'@as_of_after','value':after}]
        request['max_rows']=len(values)+1
        request['result_columns']=['movement_id','history_coverage_from','before_rows','before_quantity','after_rows','after_quantity']
        return request

    def disable(self,*,history_object_id,history_rows,history_sha256):
        history_object_id=number(history_object_id,1);history_rows=number(history_rows,0,10000)
        if not isinstance(history_sha256,str)or not re.fullmatch('[A-Fa-f0-9]{64}',history_sha256):raise ValueError('TEMPORAL_NATIVE_HISTORY_DIGEST_REQUIRED')
        # Called only after all dependent scored cases and native history reads
        # are sealed. Never silently drop somebody else's history table.
        return ('SET NOCOUNT ON; SET XACT_ABORT ON; SET LOCK_TIMEOUT 5000; BEGIN TRY BEGIN TRANSACTION;\n'+self.source.guard()+
            'IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE object_id='+str(self.object_id)+' AND temporal_type=2 AND history_table_id='+str(history_object_id)+
            ") OR COALESCE(OBJECT_ID(N'app.stock_movements_round22_history'),-1)<>"+str(history_object_id)+
            " THROW 51022, 'Owned temporal relationship changed', 1;\nIF (SELECT COUNT_BIG(*) FROM "+HISTORY+')<>'+str(history_rows)+
            ' OR COALESCE('+self.history_digest()+",'')<>UPPER('"+history_sha256+"') THROW 51022, 'Native history changed since capture', 1;\n"+
            'ALTER TABLE '+TABLE+' SET (SYSTEM_VERSIONING=OFF);\nALTER TABLE '+TABLE+' DROP PERIOD FOR SYSTEM_TIME;\n'+
            'ALTER TABLE '+TABLE+' DROP CONSTRAINT ['+DEFAULT_START+'],['+DEFAULT_END+'];\n'+
            'ALTER TABLE '+TABLE+' DROP COLUMN ['+START+'],['+END+'];\nDROP TABLE '+HISTORY+';\n'+self.source.guard()+
            'COMMIT TRANSACTION; END TRY BEGIN CATCH IF @@TRANCOUNT>0 ROLLBACK TRANSACTION; THROW; END CATCH;\n'+self.metadata())
