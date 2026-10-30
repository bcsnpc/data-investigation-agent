"""Parameterized Import and Direct Lake model definitions for HealthNet."""
import json
from contextlib import closing
from pathlib import Path
import sqlite3
from .artifacts import write

MEASURES={
 'Gross Charges':('mart_charge','SUM(mart_charge[amount_cents])/100','Signed gross charges by service date, including corrections; not collections.'),
 'Net Revenue':('mart_charge','[Gross Charges]+SUM(mart_adjustment[amount_cents])/100','Service-date gross charges plus signed adjustments in their adjustment-date window; not cash. Payer remapping uses each event date.'),
 'Collections':('mart_payment','SUM(mart_payment[amount_cents])/100','Signed posted insurance and patient cash, including reversals, moves and refunds.'),
 'Gross Charges by Post Date':('mart_charge','CALCULATE([Gross Charges],USERELATIONSHIP(mart_charge[post_date],core_date[calendar_date]))','Same signed charges, grouped by post date rather than service date.'),
 'Denied Dollars':('mart_remittance','CALCULATE(SUM(mart_remittance[denied_cents]),mart_remittance[is_original]=1)/100','Original adjudicated denied dollars by synthetic denial category.'),
 'Initial Denial Rate (count)':('mart_claim','DIVIDE(CALCULATE(COUNTROWS(mart_claim),mart_claim[is_original]=1,mart_claim[status]="DENIED"),CALCULATE(COUNTROWS(mart_claim),mart_claim[is_original]=1,mart_claim[status]<>"SUBMITTED"))','Original adjudicated claim count; pending claims excluded.'),
 'Denial Rate ($)':('mart_remittance','DIVIDE(CALCULATE(SUM(mart_remittance[denied_cents]),mart_remittance[is_original]=1),CALCULATE(SUMX(mart_remittance,mart_remittance[paid_cents]+mart_remittance[adjusted_cents]+mart_remittance[denied_cents]),mart_remittance[is_original]=1))','Denied dollars over original adjudicated remittance dollars; differs from count rate.'),
 'Final Denial Rate':('mart_claim','DIVIDE(CALCULATE(COUNTROWS(mart_claim),mart_claim[is_final]=1,mart_claim[status]="DENIED"),CALCULATE(COUNTROWS(mart_claim),mart_claim[is_final]=1,mart_claim[status]<>"SUBMITTED"))','Latest version of each adjudicated claim group; differs from original claim rate.'),
 'ALOS':('mart_encounter','AVERAGEX(FILTER(mart_encounter,NOT ISBLANK(mart_encounter[admit_utc])&&NOT ISBLANK(mart_encounter[discharge_utc])),DIVIDE(DATEDIFF(mart_encounter[admit_utc],mart_encounter[discharge_utc],SECOND),86400))','Completed inpatient admission-to-discharge days, excludes active admissions.'),
 'Midnight Census':('mart_census_daily','SUM(mart_census_daily[midnight_census])','Occupied beds at America/Chicago local midnight. Across several days this is occupied bed-days, not distinct patients.'),
 'Bed Occupancy %':('mart_census_daily','DIVIDE(SUM(mart_census_daily[midnight_census]),SUM(mart_census_daily[licensed_beds]))','Occupied bed-days divided by licensed available bed-days; capacity-weighted, not an average of facility percentages.'),
 'ED Door-to-Provider (median)':('mart_ed_visit','MEDIAN(mart_ed_visit[door_to_provider_minutes])','Minutes from ED arrival to provider; blank for LWBS, median over nonblank observations.'),
 'LWBS %':('mart_ed_visit','DIVIDE(SUM(mart_ed_visit[lwbs]),COUNTROWS(mart_ed_visit))','Left without being seen among all retained ED visits.'),
 'ED Visits':('mart_ed_visit','COUNTROWS(mart_ed_visit)','Retained ED visits, not all encounter types.'),
 '30-day Readmission %':('mart_encounter','DIVIDE(COUNTROWS(FILTER(mart_encounter,NOT ISBLANK(mart_encounter[readmission_of]))),COUNTROWS(FILTER(mart_encounter,NOT ISBLANK(mart_encounter[admit_utc]))))','Explicit same-person unplanned synthetic readmission links within30days; not risk adjusted.'),
 'Visits':('mart_encounter','COUNTROWS(mart_encounter)','Non-soft-deleted encounters of non-soft-deleted source patients; a transfer can contribute two visits.'),
 'Unique Patients':('mart_encounter','DISTINCTCOUNT(mart_encounter[mpi_patient_id])','Distinct MPI survivors among retained encounters, differs from distinct MRNs.'),
 'Order Count':('mart_order','COUNTROWS(mart_order)','Retained order lines including cancelled and voided statuses; select status to narrow.'),
 'Completed Orders':('mart_order','CALCULATE(COUNTROWS(mart_order),mart_order[status]="RESULTED")','Final resulted status only; excludes withdrawn void/reentry predecessors.'),
 'RVU-style Workload per FTE':('mart_provider_productivity_daily','DIVIDE(SUM(mart_provider_productivity_daily[workload_units]),SUMX(VALUES(core_provider[id]),CALCULATE(MAX(core_provider[fte]))))','Fictional workload units divided by unique provider FTE, never represented as licensed RVUs.'),
 'Procedures':('mart_procedure','COUNTROWS(mart_procedure)','Retained procedure rows, not encounters or order lines.'),
 'Writeoffs':('mart_adjustment','-CALCULATE(SUM(mart_adjustment[amount_cents]),mart_adjustment[adjustment_type]="BAD_DEBT")/100','Positive display of signed bad-debt adjustments; excludes contractual and charity.'),
 'A/R Balance':('mart_ar_aging','CALCULATE(SUM(mart_ar_aging[balance_cents]),mart_ar_aging[snapshot_date]=MAX(mart_ar_aging[snapshot_date]))/100','Posted account balance at the latest snapshot in the selected context; never sums multiple snapshots.'),
}

TABLE_SETS={
 'HealthNet Operations':['core_facility','core_department','core_date','mart_encounter','mart_ed_visit','mart_order','mart_census_daily'],
 'HealthNet Revenue':['core_facility','core_department','core_payer','core_date','mart_charge','mart_claim','mart_remittance','mart_payment','mart_adjustment','mart_ar_aging'],
 'HealthNet Productivity':['core_facility','core_department','core_provider','core_date','mart_encounter','mart_order','mart_procedure','mart_provider_productivity_daily'],
}


def model(name,db,server,database,owner_upn='admin@skynwhy.com'):
    mode='directLake'if name.endswith('Operations')else'import'
    expressions=[{'name':key,'kind':'m','expression':json.dumps(value)+' meta [IsParameterQuery=true,Type="Text",IsParameterQueryRequired=true]'}for key,value in [('ServerName',server),('DatabaseName',database)]]
    expressions.append({'name':'DatabaseQuery','kind':'m','expression':'Sql.Database(ServerName,DatabaseName,[CreateNavigationProperties=false])'})
    tables=[];relationships=[]
    for table in [*TABLE_SETS[name],'security_mapping']:
        info=db.execute('PRAGMA table_info(['+table+'])').fetchall();cols=[]
        for _,column,typ,_,_,_ in info:
            example=db.execute('SELECT ['+column+']FROM ['+table+'] WHERE ['+column+'] IS NOT NULL LIMIT 1').fetchone()
            v=example[0]if example else None
            dtype='int64'if isinstance(v,int)else'double'if isinstance(v,float)else'string'
            if column.endswith('_utc')or column in('created_at','updated_at','received_at','submitted_at','opened_at','performed_utc'):dtype='dateTime'
            cols.append({'name':column,'dataType':dtype,'sourceColumn':column,'summarizeBy':'none'})
        if mode=='import':
            source={'type':'m','expression':f'let Source=Sql.Database(ServerName,DatabaseName), Rows=Source{{[Schema="dbo",Item="{table}"]}}[Data] in Rows'}
        else:source={'type':'entity','entityName':table,'schemaName':'dbo','expressionSource':'DatabaseQuery'}
        definition={'name':table,'isHidden':table=='security_mapping','columns':cols,'partitions':[{'name':table,'mode':mode,'source':source}],
                    'measures':[{'name':n,'expression':dax,'description':description,'formatString':'0.00%'if '%'in n or'Rate'in n else'#,0.00'}for n,(t,dax,description)in MEASURES.items()if t==table and not(name.endswith('Operations')and n=='Net Revenue')]}
        # OLS-hidden cost/margin columns are on the daily productivity mart.
        tables.append(definition)
        fields={c['name']for c in cols}
        if table.startswith('mart_'):
            for field,dimension,target in [('facility_id','core_facility','id'),('department_id','core_department','id'),('attending_provider_id','core_provider','id'),('provider_id','core_provider','id'),('payer_id','core_payer','id')]:
                if field in fields and dimension in TABLE_SETS[name]:
                    relationships.append({'name':table+'_'+field,'fromTable':table,'fromColumn':field,'toTable':dimension,'toColumn':target,'fromCardinality':'many','toCardinality':'one','crossFilteringBehavior':'oneDirection'})
            date_fields={'mart_charge':'service_date','mart_claim':'submitted_date','mart_remittance':'received_date','mart_payment':'payment_date','mart_adjustment':'adjustment_date','mart_ar_aging':'snapshot_date','mart_census_daily':'calendar_date'}
            date_field=date_fields.get(table,'service_day')
            if date_field in fields:
                relationships.append({'name':table+'_calendar','fromTable':table,'fromColumn':date_field,'toTable':'core_date','toColumn':'calendar_date','fromCardinality':'many','toCardinality':'one','crossFilteringBehavior':'oneDirection'})
            if table=='mart_charge':relationships.append({'name':'charge_post_date','isActive':False,'fromTable':table,'fromColumn':'post_date','toTable':'core_date','toColumn':'calendar_date','fromCardinality':'many','toCardinality':'one','crossFilteringBehavior':'oneDirection'})
    # security_mapping is a native warehouse table, including for Direct Lake.
    roles=[]
    for role in('Executive','HospitalManager','DepartmentHead','Doctor'):
        permissions=[]
        allowed=f'FILTER(security_mapping,security_mapping[upn]=USERPRINCIPALNAME()&&security_mapping[role]="{role}")'
        for t,key in [('core_facility','facility_id'),('core_department','department_id'),('core_provider','provider_id')]:
            if t not in TABLE_SETS[name]:continue
            restricted=(role=='HospitalManager'and t=='core_facility')or(role=='DepartmentHead'and t=='core_department')or(role=='Doctor'and t=='core_provider')
            rule=f'{t}[id] IN SELECTCOLUMNS({allowed},"allowed_id",security_mapping[{key}])'if restricted else f'COUNTROWS({allowed})>0'
            permissions.append({'name':t,'filterExpression':rule})
        if role=='Doctor':
            if not name.endswith('Productivity'):
                # No Doctor access to Revenue or Operations, even when tested.
                permissions=[{'name':'core_facility','filterExpression':'FALSE()'}]
            else:permissions.append({'name':'mart_provider_productivity_daily','columnPermissions':[{'name':c,'metadataPermission':'none'}for c in('synthetic_cost_cents','synthetic_margin_cents')]})
        if role=='DepartmentHead':
            # A facility-only aggregate cannot be safely narrowed by department.
            # Never expose it merely because a department dimension is filtered.
            for definition in tables:
                if definition['name'].startswith('mart_')and not any(c['name']=='department_id'for c in definition['columns']):
                    permissions.append({'name':definition['name'],'filterExpression':'FALSE()'})
            if 'core_department'not in TABLE_SETS[name]:
                permissions=[{'name':'core_facility','filterExpression':'FALSE()'}]
        roles.append({'name':role,'modelPermission':'read','tablePermissions':permissions})
    return {'name':name,'compatibilityLevel':1604,'model':{'culture':'en-US','defaultPowerBIDataSourceVersion':'powerBI_V3','expressions':expressions,'tables':tables,'relationships':relationships,'roles':roles,'annotations':[{'name':'HealthNetNativeValidation','value':'PENDING; definition generation is not live verification'}]}}


def build(directory,root,server,database):
    with closing(sqlite3.connect(Path(directory)/'hn_dw.sqlite'))as db:
        for name in TABLE_SETS:
            folder=Path(root)/(name+'.SemanticModel')
            write(folder/'model.bim',model(name,db,server,database))
            write(folder/'definition.pbism',{'version':'1.0','settings':{}})
