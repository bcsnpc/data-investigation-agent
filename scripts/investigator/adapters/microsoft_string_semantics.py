"""Literal comparison controls on the engine that actually executes them.

The SQL analytics endpoint is a T-SQL engine; never label its answer Spark.
No method here acquires an identity, starts compute or grants permission.
"""
from .microsoft_self_report import compose

PAIRS=(('case_fold','a','A'),('accent_fold','a','\u00e1'),('trim','a','a '),
       ('kana','\u30a2','\uff71'),('width','a','\uff41'))


def dax():
    fields=','.join('"'+key+'","'+left+'"="'+right+'"' for key,left,right in PAIRS)
    version='CONCATENATEX(SELECTCOLUMNS(FILTER(INFO.PROPERTIES(),[PropertyName]="DBMSVersion"),"ReportValue",[Value]),[ReportValue],"")'
    return compose('EVALUATE ROW('+fields+',"surface_version",'+version+')')


def sql():
    # Unicode literals are essential: varchar conversions can turn width/kana
    # comparisons into accidental equality before the engine compares them.
    fields=','.join("CASE WHEN N'"+left+"'=N'"+right+"' THEN 1 ELSE 0 END AS ["+key+"]"
                    for key,left,right in PAIRS)
    return ('SELECT '+fields+",CAST(DATABASEPROPERTYEX(DB_NAME(),'Collation') AS nvarchar(128)) AS collation,"
            "CURRENT_USER AS surface_identity,DB_NAME() AS surface_object,"
            "CAST(SERVERPROPERTY('EngineEdition') AS varchar(20)) AS surface_engine,"
            "CAST(SERVERPROPERTY('ProductVersion') AS varchar(128)) AS surface_version")


def spark():
    fields=','.join("('"+left+"'='"+right+"') AS "+key for key,left,right in PAIRS)
    return ('SELECT '+fields+',version() AS surface_engine,version() AS surface_version,'
            'current_database() AS surface_object,current_user() AS surface_identity')
