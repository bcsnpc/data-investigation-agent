"""Publisher-only, transaction-guarded plans for reversible source record cases.

No executor or credentials live here. The approved fixture controller must save
the plan before dispatch, meter it, retain native rows, and reconcile uncertain
dispatches before doing anything else. Investigator ports never import this.
"""
import copy,hashlib,re
from datetime import date
from investigator.process_tape import bytes_of

TABLE='[app].[stock_movements_round_two_20261003]'
FIELDS=('movement_id','warehouse_id','product_id','units','event_day','movement_type')

def number(value,low=0,high=2147483647):
    if isinstance(value,bool)or not re.fullmatch(r'-?[0-9]+',str(value)):raise ValueError('SOURCE_CASE_INTEGER_REQUIRED')
    result=int(value)
    if not low<=result<=high:raise ValueError('SOURCE_CASE_INTEGER_BOUND')
    return result

def row(value):
    if not isinstance(value,dict)or set(value)!=set(FIELDS):raise ValueError('SOURCE_CASE_ROW_FIELDS')
    result={k:number(value[k],-2147483648 if k=='units'else 1)for k in FIELDS[:4]}
    day=date.fromisoformat(value['event_day']).isoformat()
    if day!=value['event_day']or value['movement_type']not in ('RECEIPT','ISSUE'):raise ValueError('SOURCE_CASE_LITERAL_REFUSED')
    return {**result,'event_day':day,'movement_type':value['movement_type']}

class SourceHistoryScenario:
    def __init__(self,baseline):
        baseline=copy.deepcopy(baseline);seal=baseline.pop('seal',None)
        if hashlib.sha256(bytes_of(baseline)).hexdigest()!=seal:raise ValueError('SOURCE_BASELINE_SEAL_DIFFERS')
        if baseline.get('status')!='READ_ONLY_BASELINE_COMPLETE'or baseline.get('table')!=TABLE:raise ValueError('SOURCE_BASELINE_REQUIRED')
        sets=baseline['result']['body']['sets'];self.rows=sets[1]
        if len(self.rows)!=number(baseline['row_count'])or hashlib.sha256(bytes_of(self.rows)).hexdigest()!=baseline['rows_sha256']:raise ValueError('SOURCE_BASELINE_ROWS_DIFFER')
        self.count=len(self.rows);self.total=sum(number(r['units'],-2147483648)for r in self.rows)
        if self.total!=number(baseline['source_units'], -9223372036854775808,9223372036854775807):raise ValueError('SOURCE_BASELINE_TOTAL_DIFFERS')
        self.version=max((number(r['source_row_version'],0,9223372036854775807)for r in self.rows),default=0)
        self.ids={number(r['movement_id'],1)for r in self.rows}
        if len(self.ids)!=self.count:raise ValueError('SOURCE_BASELINE_DUPLICATE_ID')

    def guard(self,exclude=''):
        table=TABLE+' WITH (UPDLOCK,HOLDLOCK)'+(' WHERE movement_id NOT IN ('+exclude+')'if exclude else'')
        return ('IF (SELECT COUNT_BIG(*) FROM '+table+')<>'+str(self.count)
                +' OR COALESCE((SELECT SUM(CONVERT(bigint,units)) FROM '+table+'),0)<>'+str(self.total)
                +' OR COALESCE((SELECT MAX(CONVERT(bigint,source_row_version)) FROM '+table+'),0)<>'+str(self.version)
                +" THROW 51022, 'Source preimage changed; control refused', 1;\n")

    def insert(self,values):
        if not isinstance(values,list)or not 1<=len(values)<=3:raise ValueError('SOURCE_CASE_ROW_BOUND')
        values=[row(r)for r in values];ids=[r['movement_id']for r in values]
        if len(set(ids))!=len(ids)or self.ids.intersection(ids):raise ValueError('SOURCE_CASE_ID_NOT_NEW')
        literals=['('+','.join(str(r[k])for k in FIELDS[:4])+",N'"+r['event_day']+"',N'"+r['movement_type']+"',SYSUTCDATETIME())"for r in values]
        sql='SET NOCOUNT ON; SET XACT_ABORT ON; SET TRANSACTION ISOLATION LEVEL SERIALIZABLE; BEGIN TRANSACTION;\n'+self.guard()
        sql+='INSERT INTO '+TABLE+' ('+','.join(FIELDS)+',source_modified_at_utc) VALUES '+','.join(literals)+';\n'
        sql+='SELECT '+','.join(FIELDS)+',source_modified_at_utc,CONVERT(bigint,source_row_version) AS source_row_version FROM '+TABLE+' WHERE movement_id IN ('+','.join(map(str,ids))+') ORDER BY movement_id; COMMIT;'
        return {'rows':values,'query':sql,'restoration':'Delete only these rows after matching their native row versions and the unchanged original preimage. Database-wide rowversion advances are not reversible.'}

    def observation(self,values):
        """Bounded investigator read for the exact independently authored rows.

        This is fixture control input, not a ticket-selected SQL expression.
        The ordinary managed SQL worker still enforces its read-only guards
        and query-bound surface report. A missing row remains observable.
        """
        if not isinstance(values,list)or not 1<=len(values)<=3:raise ValueError('SOURCE_CASE_ROW_BOUND')
        values=[row(r)for r in values];ids=[r['movement_id']for r in values]
        if len(set(ids))!=len(ids)or self.ids.intersection(ids):raise ValueError('SOURCE_CASE_ID_NOT_NEW')
        columns=[*FIELDS,'source_modified_at_utc','source_row_version']
        fields=[*FIELDS[:4],'CONVERT(varchar(10),event_day,23) AS event_day','movement_type',
                'source_modified_at_utc','CONVERT(bigint,source_row_version) AS source_row_version']
        parameters=[{'name':'@case_id_'+str(i),'value':identity}for i,identity in enumerate(ids)]
        return {'query':'SELECT '+','.join(fields)+' FROM '+TABLE+' WHERE movement_id IN ('+
            ','.join(p['name']for p in parameters)+') ORDER BY movement_id',
            'parameters':parameters,'read_only_objects':[TABLE],'max_rows':len(ids)+1,'result_columns':columns}

    def restore(self,planned,observed):
        expected=[row(r)for r in planned]
        if not isinstance(observed,list)or len(observed)!=len(expected)or not observed:raise ValueError('SOURCE_NATIVE_INSERT_RECEIPT_REQUIRED')
        native={number(r['movement_id'],1):r for r in observed}
        if len(native)!=len(expected)or {r['movement_id']for r in expected}!=set(native):raise ValueError('SOURCE_NATIVE_INSERT_IDENTITIES_DIFFER')
        guards=[]
        for r in expected:
            actual=native[r['movement_id']]
            if row({k:actual[k]for k in FIELDS})!=r:raise ValueError('SOURCE_NATIVE_INSERT_VALUES_DIFFER')
            version=number(actual.get('source_row_version'),self.version+1,9223372036854775807)
            guards.append('(movement_id='+str(r['movement_id'])+' AND CONVERT(bigint,source_row_version)='+str(version)+')')
        ids=','.join(str(r['movement_id'])for r in expected)
        return ('SET NOCOUNT ON; SET XACT_ABORT ON; SET TRANSACTION ISOLATION LEVEL SERIALIZABLE; BEGIN TRANSACTION;\n'+self.guard(ids)
                +'IF (SELECT COUNT_BIG(*) FROM '+TABLE+' WITH (UPDLOCK,HOLDLOCK) WHERE '+' OR '.join(guards)+')<>'+str(len(expected))
                +" THROW 51022, 'Inserted rows changed; restoration refused', 1;\nDELETE FROM "+TABLE+' WHERE movement_id IN ('+ids+'); COMMIT;')
