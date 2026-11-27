"""Deterministic owner-side SQL/semantic fixtures and separate scoring truth.

No network, credentials, engine imports or investigation tickets. The build plan
contains native definitions; the scoring manifest is written to a disjoint root.
Publication receipts must establish which planned objects actually exist.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf8')


def quoted(name):
    if not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*', name):
        raise ValueError('Unsafe generated identifier')
    return '['+name+']'


def qualified(name):
    parts=name.split('.')
    if len(parts)!=2:raise ValueError('Schema-qualified object required')
    return '.'.join(map(quoted,parts))


class Plan:
    def __init__(self, spec):
        self.spec=spec
        self.objects=[];self.edges=[];self.batches=[];self.traps=[]

    def table(self, name, columns, layer='source', rows=None):
        cols=[dict(name=n,data_type=t,nullable=nullable) for n,t,nullable in columns]
        obj=dict(address=name,kind='table',columns=cols,layer=layer,
                 source_of_truth='unknown' if layer!='source' else 'candidate',
                 rows=self.spec['rows'] if rows is None else rows)
        self.objects.append(obj)
        self.batches.append('CREATE TABLE '+qualified(name)+'('+','.join(
            quoted(c['name'])+' '+c['data_type']+(' NULL' if c['nullable'] else ' NOT NULL')for c in cols)+');')
        if obj['rows']:
            # No server-side recursive CTE or sys-table cardinality assumptions.
            values=[]
            for i in range(1,obj['rows']+1):
                row=[]
                for c in cols:
                    t=c['data_type'].lower();n=c['name']
                    if c['nullable'] and i%7==0:v='NULL'
                    elif 'date' in t or t.startswith('time'):v="'2026-11-%02d'"%(1+(i%25)) if not t.startswith('time') else "'12:00:00'"
                    elif any(x in t for x in ('char','text')):
                        value=('202611%02d'%(1+i%25)if n=='ERDAT'else 'USD'if n in('WAERK','WAERS')else 'X'+str(i%9)if 'status'in n.lower()else 'synthetic-'+str(i))
                        length=re.search(r'\(\s*(\d+)\s*\)',t)
                        if length:value=value[:int(length[1])]
                        v="'"+value+"'"
                    elif t.startswith('bit'):v=str(i%2)
                    elif 'geography' in t:v='geography::Point(0,0,4326)'
                    elif 'geometry' in t:v="geometry::STGeomFromText('POINT (0 0)',0)"
                    elif 'binary' in t:v='0x01'
                    elif 'uniqueidentifier' in t:v="'00000000-0000-0000-0000-%012d'"%i
                    elif any(x in t for x in ('decimal','float','numeric')):v=str(i*1.25)
                    else:v=str(i)
                    row.append(v)
                values.append('('+','.join(row)+')')
            for start in range(0,len(values),500):
                self.batches.append('INSERT INTO '+qualified(name)+' VALUES '+','.join(values[start:start+500])+';')
        return obj

    def view(self,name,source,columns=None,layer='mart',expression=None):
        parent=next(o for o in self.objects if o['address']==source)
        columns=columns or [c['name']for c in parent['columns']]
        chosen=[dict(c)for c in parent['columns']if c['name']in columns]
        sql='CREATE VIEW '+qualified(name)+' AS SELECT '+','.join(map(quoted,columns))+' FROM '+qualified(source)+';'
        if expression:sql='CREATE VIEW '+qualified(name)+' AS '+expression+';'
        self.batches.append(sql)
        self.objects.append(dict(address=name,kind='view',columns=chosen,layer=layer,source_of_truth='derived',definition=sql))
        self.edges.append(dict(source=name,target=source,knowledge='parsed',relation='READS'))
        for c in chosen:self.edges.append(dict(source=name+'.'+c['name'],target=source+'.'+c['name'],knowledge='parsed',relation='DERIVED_FROM'))

    def copy(self,name,source,layer='copy'):
        origin=next(o for o in self.objects if o['address']==source)
        self.table(name,[(c['name'],c['data_type'],c['nullable'])for c in origin['columns']],layer,rows=0)
        self.batches.append('INSERT INTO '+qualified(name)+' SELECT * FROM '+qualified(source)+';')
        # Build-time copy is intentionally not a retained native lineage fact.
        self.edges.append(dict(source=name,target=source,knowledge='inferable_only',relation='COPY_OF'))
        self.traps.append(dict(id=name,kind='copy',expected=['AMBIGUOUS','COPY_NOT_AUTHORITATIVE'],
            reason='No retained native producer; equal schemas and names do not establish authority.'))

    def procedure(self,name,sql,source,target,dynamic=False):
        definition='CREATE PROCEDURE '+qualified(name)+' AS BEGIN SET NOCOUNT ON; '+sql+' END;'
        self.batches.append(definition)
        self.objects.append(dict(address=name,kind='procedure',columns=[],layer='load',definition=definition))
        self.edges.extend([dict(source=name,target=t,knowledge='inferable_only'if dynamic else'parsed',relation=r)
                           for t,r in[(source,'READS'),(target,'WRITES')]])
        if dynamic:self.traps.append(dict(id=name,kind='dynamic_sql',expected=['UNRESOLVED','DYNAMIC_SQL_LIMIT'],reason='Do not claim complete static lineage for runtime SQL.'))


def upstream_wwi(directory):
    """Retain the sample's native columns in a small synthetic SQL adaptation.

    Constraints, generated temporal periods, indexes and sample load simulation
    are not copied. Their omission is explicit, never claimed as original WWI.
    """
    root=Path(directory);result=[]
    for path in sorted(root.glob('*.sql')):
        raw=path.read_text(encoding='utf-8-sig')
        table=re.search(r'CREATE TABLE\s+\[?([A-Za-z_][A-Za-z_0-9]*)\]?\.\[?([A-Za-z_][A-Za-z_0-9]*)\]?',raw,re.I)
        if not table:raise ValueError('Unrecognized upstream table: '+path.name)
        columns=[]
        for line in raw.splitlines()[1:]:
            line=re.sub(r'\[sys\]\.\[(geography|geometry)\]',r'\1',line,flags=re.I)
            match=re.match(r'\s*,?\s*\[?([A-Za-z_][A-Za-z_0-9]*)\]?\s+(AS|BIGINT|INT|SMALLINT|TINYINT|NVARCHAR|VARCHAR|NCHAR|CHAR|VARBINARY|BINARY|DECIMAL|NUMERIC|FLOAT|REAL|BIT|DATE|DATETIME2|DATETIMEOFFSET|DATETIME|TIME|GEOGRAPHY|GEOMETRY|UNIQUEIDENTIFIER)\b(\s*\(\s*(?:MAX|\d+)(?:\s*,\s*\d+)?\s*\))?',line,re.I)
            if not match:continue
            name,kind,size=match.groups()
            if kind.upper()=='AS':
                # Materialized string representation in this adaptation; source
                # expression stays in the source pin, not invented as lineage.
                kind='nvarchar';size='(400)'
            if kind.lower()in('geography','geometry'):size=''
            columns.append((name,kind+(size or ''),'NOT NULL'not in line.upper()))
        if not columns:raise ValueError('Empty upstream table: '+path.name)
        result.append((table[1]+'.'+table[2],columns))
    if len(result)!=37:raise ValueError('Expected all 37 pinned non-archive source tables')
    return result


def domain_plan(spec, wwi_source=None):
    p=Plan(spec);n=spec['id']
    integer=lambda name:(name,'int',False)
    text=lambda name:(name,'nvarchar(100)',False)
    amount=lambda name:(name,'decimal(18,2)',False)
    if n=='A':
        if wwi_source is None:raise ValueError('Pinned MIT WideWorldImporters source schema required')
        for name,columns in upstream_wwi(wwi_source):
            p.table(name,columns,rows=spec['rows'] if name=='Sales.OrderLines' else 180 if name=='Sales.Orders' else 20)
        lines=next(o for o in p.objects if o['address']=='Sales.OrderLines')
        p.batches.append('ALTER TABLE [Sales].[OrderLines] ADD StatusCode nvarchar(30) NULL;')
        lines['columns'].append(dict(name='StatusCode',data_type='nvarchar(30)',nullable=True))
        p.copy('Sales.OrderLines_Snapshot','Sales.OrderLines');p.copy('Sales.Orders_Backup','Sales.Orders')
        p.batches.extend(['ALTER TABLE [Sales].[OrderLines] ADD [ExternalChannel] nvarchar(30) NULL;',
                          "UPDATE [Sales].[OrderLines] SET ExternalChannel='web' WHERE OrderLineID>700;"])
        lines['columns'].append(dict(name='ExternalChannel',data_type='nvarchar(30)',nullable=True))
        p.traps.extend([dict(id='Sales.OrderLines.ExternalChannel',kind='schema_drift',expected=['NULL_HISTORY'],reason='Added after snapshots; historical NULL is not missing metadata.'),
                        dict(id='Sales.OrderLines.StatusCode',kind='unknown_status',expected=['UNKNOWN_MEANING'],reason='No native lookup or business-code declaration.')])
        p.view('dw.FactOrderLine','Sales.OrderLines',layer='warehouse')
        p.table('dw.LoadedOrderLine',[(c['name'],c['data_type'],c['nullable'])for c in lines['columns']],layer='warehouse',rows=0)
        p.procedure('etl.LoadOrderLine','DELETE FROM [dw].[LoadedOrderLine]; INSERT INTO [dw].[LoadedOrderLine] SELECT * FROM [Sales].[OrderLines];','Sales.OrderLines','dw.LoadedOrderLine')
        p.batches.append('EXEC [etl].[LoadOrderLine];')
        p.scope='All 37 pinned non-archive WWI source table column shapes; synthetic small rows. Adapted: no original defaults, indexes, FKs, temporal system periods or simulation; computed columns materialized. SQL ETL prototype, Fabric warehouse publication still requires native proof.'
    elif n=='B':
        for name,cols,count in [
            ('src.TBL_CUST',[integer('CUST_ID'),text('CUST_NM')],100),
            ('src.TBL_AGT',[integer('AGT_ID'),text('AGT_NM')],20),
            ('src.TBL_PLCY',[integer('PLCY_ID'),integer('CUST_ID'),integer('AGT_ID'),text('LOB_CD')],200),
            ('src.TBL_PLCY_VER',[integer('PLCY_VER_ID'),integer('PLCY_ID'),integer('VER_NO'),text('ENDRSMNT_CD'),('EFF_DT','date',False)],300),
            ('src.TBL_CVRG',[integer('CVRG_ID'),integer('PLCY_VER_ID'),text('CVRG_CD'),amount('LMT_AMT')],400),
            ('src.TBL_PRM_TRN',[integer('PRM_TRN_ID'),integer('PLCY_VER_ID'),amount('WRITTEN_PRM'),('POST_DT','date',False)],spec['rows']),
            ('src.TBL_CLM',[integer('CLM_ID'),integer('PLCY_ID'),('LOSS_DT','date',False),text('ST_CD')],150),
            ('src.TBL_CLM_RSV',[integer('RSV_ID'),integer('CLM_ID'),amount('RSV_AMT'),('ASOF_DT','date',False)],300),
            ('src.TBL_CLM_PMT',[integer('PMT_ID'),integer('CLM_ID'),amount('PMT_AMT'),('PMT_DT','date',False)],250)]:p.table(name,cols,rows=count)
        source='src.TBL_PRM_TRN'
        for name in ['stg.V_PRM_X1','stg.V_PRM_X2','ods.V_PRM_X3','mart.V_PRM_X4']:
            p.view(name,source,layer='mart'if name.startswith('mart.')else'staging');source=name
        p.view('stg.V_CLM_RSV_X1','src.TBL_CLM_RSV',layer='staging')
        p.view('ods.V_CLM_RSV_X2','stg.V_CLM_RSV_X1',layer='ods')
        p.copy('src.TBL_PRM_TRN_BKP','src.TBL_PRM_TRN');p.copy('src.TBL_PLCY_VER_OLD','src.TBL_PLCY_VER')
        p.table('mart.TBL_PRM_SUM',[integer('PLCY_VER_ID'),amount('WRITTEN_PRM')],layer='summary',rows=0)
        p.procedure('etl.SP_LD_PRM','DELETE FROM [mart].[TBL_PRM_SUM]; INSERT INTO [mart].[TBL_PRM_SUM] SELECT PLCY_VER_ID,SUM(WRITTEN_PRM) FROM [src].[TBL_PRM_TRN] GROUP BY PLCY_VER_ID;','src.TBL_PRM_TRN','mart.TBL_PRM_SUM')
        p.batches.append('EXEC [etl].[SP_LD_PRM];')
        p.table('mart.TBL_RSV_CUR',[integer('RSV_ID'),integer('CLM_ID'),amount('RSV_AMT'),('ASOF_DT','date',False)],layer='mart',rows=0)
        p.procedure('etl.SP_LD_RSV',"DECLARE @q nvarchar(max)=N'DELETE FROM [mart].[TBL_RSV_CUR]; INSERT INTO [mart].[TBL_RSV_CUR] SELECT * FROM [src].[TBL_CLM_RSV]'; EXEC sp_executesql @q;",'src.TBL_CLM_RSV','mart.TBL_RSV_CUR',dynamic=True)
        p.batches.append('EXEC [etl].[SP_LD_RSV];')
        p.traps.append(dict(id='mart.TBL_PRM_SUM',kind='summary_grain',expected=['DISTINCT_GRAIN','UNKNOWN_GRAIN'],reason='Do not equate policy-version summary and premium transactions.'))
        p.scope='Independent synthetic property-and-casualty insurance; no downloaded data'
    elif n=='C':
        for name,cols,count in [
            ('sap.KNA1',[text('KUNNR'),text('NAME1')],50),('sap.MARA',[text('MATNR'),text('MEINS')],60),
            ('sap.VBAK',[text('VBELN'),text('KUNNR'),text('ERDAT'),text('WAERK')],200),
            ('sap.VBAP',[text('VBELN'),integer('POSNR'),text('MATNR'),amount('NETWR'),text('WAERK')],spec['rows']),
            ('sap.BKPF',[text('BELNR'),text('BUKRS'),text('WAERS')],100),
            ('sap.BSEG',[text('BELNR'),integer('BUZEI'),amount('WRBTR'),text('WAERS')],300)]:p.table(name,cols,rows=count)
        p.view('extract.SalesItems','sap.VBAP',layer='extract');p.view('stg.SalesItems','extract.SalesItems',layer='staging');p.view('mart.SalesItems','stg.SalesItems')
        p.batches.append('UPDATE [sap].[BSEG] SET WRBTR=WRBTR+1 WHERE BUZEI<=3;')
        p.traps.extend([dict(id='sap.VBAK.ERDAT',kind='string_date',expected=['STRING_DATE','UNKNOWN_SEMANTICS'],reason='Actual SQL type is text; never claim native DATE.'),
                        dict(id='sap.VBAP.NETWR',kind='currency_pair',expected=['CURRENCY_REQUIRED','UNKNOWN_CURRENCY_SEMANTICS'],reason='Keep WAERK beside amount; do not invent currency conversion.'),
                        dict(id='sap.BSEG',kind='overwrite',expected=['HISTORY_UNAVAILABLE'],reason='No change history configured; current schema is not a before/after proof.')])
        p.scope='Independent SAP-style synthetic schema, no SALT data'
    elif n=='D':
        for name,cols,count in [
            ('landing.Students',[integer('StudentId'),text('Name'),integer('DepartmentId')],100),
            ('landing.Courses',[integer('CourseId'),integer('DepartmentId'),text('Title')],30),
            ('landing.Enrolments',[integer('EnrollmentId'),integer('StudentId'),integer('CourseId')],spec['rows']),
            ('landing.Grades',[integer('EnrollmentId'),amount('Grade')],spec['rows']),
            ('private.Staff',[integer('StaffId'),integer('DepartmentId'),amount('Salary')],25),
            ('landing.UnmappedLegacy',[integer('Key'),text('Value')],10)]:p.table(name,cols,rows=count)
        p.view('ods.Enrolments','landing.Enrolments',layer='ods');p.view('mart.Enrolments','ods.Enrolments')
        p.traps.extend([dict(id='private',kind='permission',expected=['PERMISSION_GAP'],missing_grant='VIEW DEFINITION and SELECT on schema private; intentionally withheld'),
                        dict(id='model',kind='rls',expected=['PERMISSION_GAP'],missing_grant='Membership in the model Investigator role group; intentionally withheld'),
                        dict(id='pipeline/history',kind='history_denied',expected=['PERMISSION_GAP'],missing_grant='Read job history on the education pipeline; intentionally withheld'),
                        dict(id='landing.UnmappedLegacy',kind='orphan',expected=['MISSING_PRODUCER','UNRESOLVED'],reason='No native producer, not an inferred link to another same-key table.')])
        p.scope='Independent synthetic education source'
    else:raise ValueError('Unknown factory estate')
    return p


def build(spec, artifacts, scoring, wwi_source=None):
    artifacts=Path(artifacts).resolve();scoring=Path(scoring).resolve()
    if artifacts==scoring or artifacts in scoring.parents or scoring in artifacts.parents:
        raise ValueError('Scoring root must be disjoint from discovery/build inputs')
    if not re.fullmatch('sb_[a-z]+',spec['database']):raise ValueError('New benchmark database required')
    if not 1<=spec['rows']<=2000:raise ValueError('Small synthetic population required')
    p=domain_plan(spec,wwi_source)
    schemas=sorted({o['address'].split('.')[0]for o in p.objects})
    sql=["CREATE SCHEMA "+quoted(s)+";"for s in schemas if s!='dbo']+p.batches
    native=dict(version=1,estate=spec['id'],database=spec['database'],workspace=spec['workspace'],
        source_scope=p.scope,batches=sql,objects=[dict(address=o['address'],kind=o['kind'])for o in p.objects],
        deployment_status='PLANNED_NOT_OBSERVED',permissions=spec['permissions'])
    for declaration,obj in zip(native['objects'],p.objects):declaration['columns']=obj['columns']
    path=artifacts/spec['id']/'build.json';write(path,native)
    truth=dict(version=1,estate=spec['id'],status='PLANNED_NOT_OBSERVED',
        artifact_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),objects=p.objects,
        edges=p.edges,traps=p.traps,rls_ols=({'rls':'department','ols':['private.Staff.Salary']}if spec['id']=='D'else {}),
        expected_permission_gaps=[t for t in p.traps if t['kind']in('permission','rls','history_denied')])
    write(scoring/(spec['id']+'-manifest.json'),truth)
    return dict(estate=spec['id'],objects=len(p.objects),columns=sum(len(o['columns'])for o in p.objects),
        edges=len(p.edges),traps=len(p.traps),rows=sum(o.get('rows',0)for o in p.objects),status='PLANNED_NOT_OBSERVED')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--spec',type=Path,default=Path(__file__).with_name('specs.json'))
    ap.add_argument('--artifacts',type=Path,required=True);ap.add_argument('--scoring',type=Path,required=True)
    ap.add_argument('--wwi-source',type=Path,required=True)
    args=ap.parse_args()
    print(json.dumps([build(s,args.artifacts,args.scoring,args.wwi_source)for s in json.loads(args.spec.read_text())['estates']],indent=2))


if __name__=='__main__':main()
