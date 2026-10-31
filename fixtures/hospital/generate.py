"""Streaming, seeded HealthNet sources. All people and identifiers fictional.

No network, environment credentials, AI, DIA or non-standard dependencies.
Money is integer cents; UTC instants are ISO strings. Local ED instants keep
their offset, including the repeated autumn hour. SQLite is the local source
artifact, not a claim that any Azure/Fabric resource has been populated.
"""
import bisect
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import heapq
import json
import math
from pathlib import Path
import random
import sqlite3
from zoneinfo import ZoneInfo
from .schema import CLINICAL, BILLING, columns, ddl

UTC=timezone.utc
START=datetime(2025,10,1,tzinfo=UTC)
END=datetime(2026,10,30,tzinfo=UTC)
SERVICES=('ED','Medicine','Cardiology','Orthopedics','Surgery','Obstetrics',
          'Pediatrics','ICU','Radiology','Laboratory','Pharmacy')
LOS={'Medicine':6.3,'Cardiology':5.0,'Orthopedics':3.6,'Surgery':4.7,
     'Obstetrics':2.4,'Pediatrics':2.8,'ICU':8.0}
DENIALS=('missing information','eligibility','authorization','coding',
         'timely filing','medical necessity','duplicate')
ICD=(('I10','Blood pressure condition'),('E11.9','Diabetes without complications'),
     ('J18.9','Pneumonia, unspecified'),('R10.9','Abdominal pain, unspecified'))


@dataclass(frozen=True)
class Settings:
    seed:int=20261030
    patients:int=60000
    encounters:int=250000
    orders:int=1500000

    def __post_init__(self):
        if min(self.patients,self.encounters,self.orders)<20:
            raise ValueError('Use at least20 rows per primary population')
        if self.orders<self.encounters:
            raise ValueError('At least one order per encounter is required')


def iso(value):
    return value.isoformat(timespec='seconds') if value is not None else None


class Store:
    def __init__(self,path,system):
        self.db=sqlite3.connect(path)
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.execute('PRAGMA journal_mode=DELETE')
        self.db.executescript(ddl(system))
        self.tables=CLINICAL if system=='clinical'else BILLING
        self.ids=defaultdict(int)
        self.names={t:[c[0]for c in columns(d)]for t,d in self.tables.items()}
        self.statements={t:'INSERT INTO ['+t+']('+','.join('['+n+']'for n in ns)+') VALUES('+','.join('?'for _ in ns)+')'for t,ns in self.names.items()}

    def add(self,table,**row):
        self.ids[table]+=1
        row={'id':self.ids[table],**row}
        business=next((row[k]for k in ('ordered_utc','arrival_utc','submitted_at',
                                     'post_date','opened_at')if row.get(k)),iso(START))
        audit=iso(min(datetime.fromisoformat(business).replace(tzinfo=UTC),END))
        row={'created_at':audit,'updated_at':audit,'updated_by':'HEALTHNET-SYNTHETIC',
             'is_deleted':0,**row}
        names=self.names[table]
        if set(row)!=set(names):raise ValueError((table,set(row)^set(names)))
        # Immediate parent-first insertion preserves every intra-database FK.
        self.db.execute(self.statements[table],[row[n]for n in names])
        return row['id']

    def finish(self):
        bad=self.db.execute('PRAGMA foreign_key_check').fetchall()
        if bad:raise ValueError(('FOREIGN_KEYS',bad[:5]))
        self.db.commit()


def canonical_hash(db,table):
    h=hashlib.sha256()
    for row in db.execute('SELECT * FROM ['+table+'] ORDER BY id'):
        h.update(json.dumps(row,ensure_ascii=True,separators=(',',':')).encode()+b'\n')
    return h.hexdigest()


def generate(output,settings=Settings()):
    output=Path(output)
    output.mkdir(parents=True,exist_ok=False)
    rng=random.Random(settings.seed)
    clinical=Store(output/'hn_clinical.sqlite','clinical')
    billing=Store(output/'hn_billing.sqlite','billing')
    c,b=clinical.add,billing.add
    # Scaled profiles keep the same reference estate; only fact volume changes.
    beds=defaultdict(list)
    for facility,(name,size)in enumerate((('North',450),('Central',280),('South',150)),1):
        c('facility',id=facility,name='HealthNet '+name,region='Fictional Northmere',licensed_beds=size)
        for i,service in enumerate(SERVICES):
            dep=(facility-1)*11+i+1
            c('department',id=dep,facility_id=facility,name=name+' '+service,service_line=service)
            c('unit',id=dep,department_id=dep,name=name+' '+service+' Unit')
        for i in range(size):
            unit=(facility-1)*11+2+(i%7)
            ident=c('bed',unit_id=unit,facility_id=facility,name=f'SYN-BED-{facility}-{i+1:03}')
            heapq.heappush(beds[facility],(START,ident))
    cutoff='2026-04-16'
    providers=defaultdict(list)
    for i in range(1,361):
        service=SERVICES[(i-1)%8];facility=(i-1)%3+1
        old=(facility-1)*11+SERVICES.index(service)+1
        new=old if i%10 else (facility-1)*11+((SERVICES.index(service)+1)%8)+1
        c('provider',id=i,synthetic_npi=f'SIM-NPI-{i:07}',name=f'Synth Doctor {i:03}',
          specialty=service,fte=0.5 if i%4==0 else 1.0,
          provider_type='Physician'if i<=300 else'AdvancedPractice',current_department_id=new)
        c('provider_assignment',provider_id=i,department_id=old,valid_from='2025-10-01',valid_to=cutoff if old!=new else'9999-12-31')
        if old!=new:c('provider_assignment',provider_id=i,department_id=new,valid_from=cutoff,valid_to='9999-12-31')
        providers[(facility,service)].append(i)
    groups=('Medicare','Medicaid','Commercial','SelfPay')
    for i,group in enumerate(groups,1):b('payer',id=i,name='Synthetic '+group+' Payer',payer_group=group)
    for i in range(1,13):
        payer=(i-1)%4+1;remapped=i in(3,7)
        c('payer_plan',id=i,plan_code=f'SYN-PLAN-{i:02}',payer_group=groups[payer-1])
        b('payer_plan',id=i,plan_code=f'SYN-PLAN-{i:02}',current_payer_id=2 if remapped else payer)
        b('payer_plan_history',payer_plan_id=i,payer_id=payer,valid_from='2025-10-01',valid_to='2026-05-15'if remapped else'9999-12-31')
        if remapped:b('payer_plan_history',payer_plan_id=i,payer_id=2,valid_from='2026-05-15',valid_to='9999-12-31')
    duplicate_count=max(2,settings.patients//50)
    unique=settings.patients-duplicate_count
    children=[];ob_patients=[];demographics={}
    for i in range(1,settings.patients+1):
        person=i if i<=unique else i-unique
        if person not in demographics:
            demographics[person]=((datetime(2025,1,1)-timedelta(days=rng.randrange(365*90))).date(),rng.choices(('F','M','X'),(.505,.485,.01))[0])
        birth,sex=demographics[person]
        if (START.date()-birth).days<18*365:children.append(i)
        if sex=='F'and 18*365<=(START.date()-birth).days<=45*365:ob_patients.append(i)
        c('patient',id=i,person_key=f'SYN-PERSON-{person:06}',mrn=f'ZZ-HN-{i:07}',
          given_name=f'Synth{person:06}',family_name=f'Fiction{person%977:03}',
          birth_date=birth.isoformat(),
          sex=sex,fictional_address=f'{person} Simulation Lane, Northmere, ZZ',
          is_deleted=int(i%997==0))
        if i>unique:
            c('patient_alias',patient_id=person,alias_patient_id=i,alias_type='MPI_DUPLICATE')
            if i%2==0:c('patient_merge',survivor_id=person,duplicate_id=i,merged_at='2026-03-15T12:00:00+00:00')
    # Local arrivals have explicit hourly, weekend and winter weights.
    days=(END-START).days
    weights=[(1.14 if (START+timedelta(days=d)).month in(11,12,1,2)else 1.0)*
             (0.92 if (START+timedelta(days=d)).weekday()>4 else 1.0)for d in range(days)]
    cumulative=[];total=0
    for w in weights:total+=w;cumulative.append(total)
    arrivals=[]
    hour_weights=[.35]*7+[.8]*3+[1.35]*12+[.7]*2
    for _ in range(settings.encounters):
        day=bisect.bisect_left(cumulative,rng.random()*total)
        hour=rng.choices(range(24),hour_weights)[0]
        arrivals.append(START+timedelta(days=day,hours=hour,minutes=rng.randrange(60)))
    arrivals.sort()
    prior=[];encounters=[];balance_events=defaultdict(list)
    for i,arrival in enumerate(arrivals,1):
        facility=rng.choices((1,2,3),(450,280,150))[0]
        kind=rng.choices(('ED','INPATIENT','OBSERVATION','OUTPATIENT','SURGERY'),(.42,.14,.08,.32,.04))[0]
        inpatient=kind=='INPATIENT'or kind=='ED'and rng.random()<.115
        service=rng.choices(tuple(LOS),(.43,.12,.1,.13,.1,.07,.05))[0]if inpatient else 'ED'if kind=='ED'else rng.choice(SERVICES[1:7])
        dep=(facility-1)*11+SERVICES.index(service)+1
        candidates=providers[(facility,service)]
        provider=rng.choice(candidates)if candidates else rng.randrange(1,361)
        patient=rng.randrange(1,settings.patients+1);readmission=None;transfer=None
        if service=='Pediatrics'and children:patient=rng.choice(children)
        if service=='Obstetrics'and ob_patients:patient=rng.choice(ob_patients)
        # Select a real preceding discharged inpatient, not a flag-only readmission.
        if inpatient and rng.random()<.12:
            eligible=[p for p in prior[-1800:]if p['service']==service and timedelta(0)<arrival-p['discharge']<=timedelta(days=30)]
            if eligible:
                previous=rng.choice(eligible);patient=previous['patient'];readmission=previous['id']
        if kind=='ED'and rng.random()<.024:
            eligible=[p for p in prior[-200:]if p['facility']!=facility and timedelta(0)<=arrival-p['discharge']<timedelta(days=1)]
            if eligible:
                previous=rng.choice(eligible);patient=previous['patient'];transfer=previous['id'];readmission=None
        lwbs=kind=='ED'and not inpatient and rng.random()<.025
        provider=None if lwbs or i%193==0 else provider
        los_minutes=round(min(1500,max(25,rng.lognormvariate(math.log(180),.55))))
        admit=None;bed=None
        if inpatient:
            ready=arrival+timedelta(minutes=los_minutes if kind=='ED'else 45)
            available,bed=heapq.heappop(beds[facility]);admit=max(available,ready)
            duration=timedelta(hours=max(12,min(45*24,rng.gammavariate(2,LOS[service]*12))))
            planned_end=admit+duration;heapq.heappush(beds[facility],(planned_end,bed))
        else:planned_end=arrival+timedelta(minutes=los_minutes if kind=='ED'else rng.randrange(45,480))
        discharge=planned_end if planned_end<END else None
        status='LEFT_WITHOUT_BEING_SEEN'if lwbs else'DISCHARGED'if discharge else'ACTIVE'
        if admit and admit>=END:admit=None;bed=None;status='WAITING'
        payer=rng.choices((1,2,3,4),(.37,.24,.31,.08))[0];plan=payer+4*rng.randrange(3)
        encounter_number=f'HNE-{i:09}'
        initial='OBSERVATION'if inpatient and i%23==0 else'INPATIENT'if inpatient else kind
        c('encounter',id=i,encounter_number=encounter_number,patient_id=patient,
          facility_id=facility,department_id=dep,attending_provider_id=provider,payer_plan_id=plan,
          encounter_type='INPATIENT'if inpatient else kind,initial_status=initial,status=status,
          arrival_utc=iso(arrival),admit_utc=iso(admit),discharge_utc=iso(discharge),
          service_day=arrival.date().isoformat(),readmission_of=readmission,transfer_from=transfer,
          is_deleted=int(i%1237==0))
        if admit:
            c('adt_event',encounter_id=i,event_type='ADMIT',event_utc=iso(admit),from_facility_id=None,to_facility_id=facility)
            c('bed_assignment',encounter_id=i,bed_id=bed,start_utc=iso(admit),end_utc=iso(discharge))
        if transfer:c('adt_event',encounter_id=i,event_type='TRANSFER',event_utc=iso(arrival),from_facility_id=previous['facility'],to_facility_id=facility)
        if discharge:
            c('adt_event',encounter_id=i,event_type='DISCHARGE',event_utc=iso(discharge),from_facility_id=facility,to_facility_id=None)
            if inpatient:prior.append({'id':i,'patient':patient,'discharge':discharge,'facility':facility,'service':service})
        if kind=='ED':
            local=arrival.astimezone(ZoneInfo('America/Chicago'))
            wait=None if lwbs else max(1,round(rng.lognormvariate(math.log(25),.8)))
            ed_end=admit or planned_end
            c('ed_visit_detail',encounter_id=i,triage_level=rng.choices((1,2,3,4,5),(.02,.17,.48,.27,.06))[0],
              arrival_local=local.isoformat(),utc_offset_minutes=int(local.utcoffset().total_seconds()/60),
              door_to_provider_minutes=wait,ed_los_minutes=max(1,int((min(ed_end,END)-arrival).total_seconds()/60)),
              lwbs=int(lwbs),admitted=int(inpatient),transferred=int(transfer is not None))
        code,description=rng.choice(ICD)
        c('diagnosis',encounter_id=i,code_system='ICD-10-CM',code=code,description=description,sequence=1)
        if kind=='SURGERY'or inpatient and service=='Surgery':
            c('procedure',encounter_id=i,provider_id=provider or 1,
              code_system='ICD-10-PCS'if inpatient else'SYNTHETIC-PROCEDURE',
              code='0WQF0ZZ'if inpatient else f'PRC-{10000+i%900}',
              description='Synthetic inpatient repair scenario'if inpatient else'Synthetic outpatient procedure',
              performed_utc=iso(arrival),workload_units=round(rng.uniform(2,12),2))
        encounters.append((i,arrival,facility,patient,provider,plan,inpatient,kind))
        # The two application systems share business numbers, not database FKs.
        if i%503==0:continue
        account=b('account',account_number=f'HNA-{i:09}',encounter_number=encounter_number,
                  facility_id=facility,patient_mrn=f'ZZ-HN-{patient:07}',payer_plan_id=plan,opened_at=iso(arrival))
        base=max(0,round(rng.lognormvariate(math.log(2800000 if inpatient else 180000),.55)))
        if i%101==0:base=0
        charge_ids=[];late=i%20==0
        post=min(arrival+timedelta(days=rng.randrange(4,35)if late else rng.randrange(0,4)),END-timedelta(seconds=1))
        for j,amount in enumerate((base//3,base-base//3)):
            charge_ids.append(b('charge',account_id=account,service_date=arrival.date().isoformat(),post_date=post.date().isoformat(),
                revenue_centre_code='SYN-RC-'+str(10+j),procedure_code=f'PRC-{10200+j}',units=1,
                amount_cents=amount,correction_of=None,correction_reason='bundled'if base==0 else''))
        if i%79==0:
            for amount in(-10000,10000):b('charge',account_id=account,service_date=arrival.date().isoformat(),post_date=post.date().isoformat(),revenue_centre_code='SYN-RC-ADJ',procedure_code='PRC-CORRECTION',units=1,amount_cents=amount,correction_of=charge_ids[0],correction_reason='credit and re-enter')
        billed=min(post+timedelta(days=rng.randrange(1,6)),END-timedelta(seconds=1))
        denied=rng.random()<.12;resolved=denied and rng.random()<.75
        versions=(3 if i%3==0 else 2)if denied else 1;last_claim=None
        for version in range(1,versions+1):
            final=version==versions;claim_denied=denied and not(final and resolved)
            submitted=min(billed+timedelta(days=14*(version-1)),END-timedelta(seconds=1))
            claim=b('claim',account_id=account,claim_group=f'SYN-CG-{i:09}',version=version,submission_type='ORIGINAL'if version==1 else'CORRECTED'if version==2 else'RESUBMISSION',is_original=int(version==1),is_final=int(final),bill_type='SYN-INPATIENT'if inpatient else'SYN-OUTPATIENT',ms_drg='SYN-DRG-01'if inpatient else'',submitted_at=iso(submitted),status='DENIED'if claim_denied else'PAID',billed_cents=base)
            received=submitted+timedelta(days=22)
            remit=b('remittance',claim_id=claim,received_at=iso(received))if received<END else None
            if remit is None:billing.db.execute("UPDATE claim SET status='SUBMITTED' WHERE id=?",(claim,))
            for charge_id,amount in zip(charge_ids,(base//3,base-base//3)):
                line=b('claim_line',claim_id=claim,charge_id=charge_id,amount_cents=amount)
                category=DENIALS[i%len(DENIALS)]if claim_denied else'';adjusted=round(amount*.58)
                if remit is not None:b('remittance_line',remittance_id=remit,claim_line_id=line,paid_cents=0 if claim_denied else amount-adjusted,
                  adjusted_cents=adjusted,denied_cents=amount-adjusted if claim_denied else 0,
                  denial_code=f'DN-SYN-{i%7+1:02}'if claim_denied else'',denial_category=category,remark_code='SYN-RMK-01'if claim_denied else'')
            last_claim=claim
        adjustment=round(base*.58)
        bad_debt=round(base*.1)if i%10==0 and(END-post).days>100 else 0
        b('adjustment',account_id=account,adjustment_date=post.date().isoformat(),amount_cents=-(adjustment-bad_debt),adjustment_type='CONTRACTUAL')
        writeoff=(post+timedelta(days=90)).date()
        if bad_debt:b('adjustment',account_id=account,adjustment_date=writeoff.isoformat(),amount_cents=-bad_debt,adjustment_type='BAD_DEBT')
        net=base-adjustment;age=(END-arrival).days
        paid=net if age>50 else round(net*.35)
        payment_date=min(billed+timedelta(days=rng.randrange(14,40)),END-timedelta(seconds=1)).date().isoformat()
        payment=b('payment',account_id=account,claim_id=last_claim,payment_date=payment_date,amount_cents=paid,
                  payment_type='PATIENT'if payer==4 else'INSURANCE',reverses_payment_id=None,moved_to_account_id=None)
        if i%113==0:
            b('payment',account_id=account,claim_id=last_claim,payment_date=payment_date,amount_cents=-paid,payment_type='REVERSAL',reverses_payment_id=payment,moved_to_account_id=None)
            b('payment',account_id=account,claim_id=last_claim,payment_date=payment_date,amount_cents=paid,payment_type='REPOST',reverses_payment_id=None,moved_to_account_id=account)
        if i%307==0 and account>1:
            wrong=b('payment',account_id=account-1,claim_id=None,payment_date=payment_date,amount_cents=paid,payment_type='MISPOST',reverses_payment_id=None,moved_to_account_id=account)
            b('payment',account_id=account-1,claim_id=None,payment_date=payment_date,amount_cents=-paid,payment_type='MOVE_REVERSAL',reverses_payment_id=wrong,moved_to_account_id=account)
        if i%211==0 and paid:
            refund=min(paid,5000);b('payment',account_id=account,claim_id=last_claim,payment_date=payment_date,amount_cents=-refund,payment_type='REFUND',reverses_payment_id=payment,moved_to_account_id=None)
            b('adjustment',account_id=account,adjustment_date=payment_date,amount_cents=-refund,adjustment_type='CHARITY')
        event_payer=2 if plan in(3,7)and arrival.date().isoformat()>='2026-05-15'else payer
        balance_events[(facility,event_payer)].append((post.date(),payment_date,net+bad_debt,paid,writeoff,bad_debt))
        if i%10000==0:clinical.db.commit();billing.db.commit()
    # Intentionally orphaned business-number links; no fabricated clinical FK.
    for i in range(max(2,settings.encounters//2500)):
        b('account',account_number=f'HNA-ORPHAN-{i:05}',encounter_number=f'HNE-ABSENT-{i:05}',facility_id=1,patient_mrn='ZZ-SYNTHETIC-ORPHAN',payer_plan_id=1,opened_at=iso(START))
    # Exactly the configured order-line count, with correlated order/results.
    for n in range(settings.orders):
        encounter=encounters[n%len(encounters)];eid,arrival,facility,patient,provider,plan,inpatient,kind=encounter
        modality=rng.choices(('LAB','IMAGING','PHARMACY'),(.75,.12,.13))[0]
        ordered=min(arrival+timedelta(minutes=(n//len(encounters))*30),END-timedelta(seconds=1))
        priority='STAT'if rng.random()<(.4 if kind=='ED'else.12)else'ROUTINE'
        status=rng.choices(('RESULTED','CANCELLED','VOIDED','IN_PROGRESS','ORDERED'),(.925,.04,.015,.015,.005))[0]
        header=c('order_header',encounter_id=eid,provider_id=provider,order_type=modality,ordered_utc=iso(ordered))
        tat=max(4,round(rng.lognormvariate(math.log({'LAB':55,'IMAGING':90,'PHARMACY':35}[modality]),.5)))/(2 if priority=='STAT'else 1)
        completed=min(ordered+timedelta(minutes=tat),END-timedelta(seconds=1))if status=='RESULTED'else None
        replaces=n-len(encounters)+1 if n>=len(encounters)and n%251==0 else None
        if replaces:
            previous=clinical.db.execute('SELECT h.order_type,l.completed_utc FROM order_line l JOIN order_header h ON h.id=l.order_header_id WHERE l.id=?',(replaces,)).fetchone()
            # A replacement stays with the same encounter/modality and follows
            # any retained result. It does not refer to the previous patient.
            modality=previous[0]
            if previous[1]:ordered=min(max(ordered,datetime.fromisoformat(previous[1])+timedelta(minutes=1)),END-timedelta(seconds=1))
            clinical.db.execute('UPDATE order_header SET order_type=?,ordered_utc=? WHERE id=?',(modality,iso(ordered),header))
            clinical.db.execute("UPDATE order_line SET status='VOIDED',updated_at=? WHERE id=?",(iso(ordered),replaces))
            clinical.db.execute("UPDATE result SET status='WITHDRAWN',updated_at=? WHERE order_line_id=?",(iso(ordered),replaces))
            clinical.db.execute("UPDATE medication_admin SET status='ENTERED_IN_ERROR',updated_at=? WHERE order_line_id=?",(iso(ordered),replaces))
            completed=min(ordered+timedelta(minutes=tat),END-timedelta(seconds=1))if status=='RESULTED'else None
        line=c('order_line',order_header_id=header,line_number=1,item_code='SYN-'+modality+'-01',priority=priority,status=status,ordered_utc=iso(ordered),completed_utc=iso(completed),replaces_order_line_id=replaces)
        if status=='RESULTED':
            for component in range(2):
                value=round(rng.gauss(100,12),2)if modality=='LAB'else None
                c('result',order_line_id=line,component='SYN-ANALYTE-'+str(component)if modality=='LAB'else'SYN-STATUS-'+str(component),status='PRELIMINARY'if component==0 else'FINAL',observed_value=value,unit='SYN-U'if value is not None else'',reference_low=80 if value is not None else None,reference_high=120 if value is not None else None,resulted_utc=iso(completed))
            if modality=='PHARMACY':c('medication_admin',order_line_id=line,encounter_id=eid,drug_code='SYN-DRUG-001',dose=1,unit='SYN-DOSE',administered_utc=iso(completed),status='GIVEN')
        if n%20000==0:clinical.db.commit()
    # A/R is a daily aggregate by facility, payer, aging bucket; never an
    # independently sampled number. Every account's posted net/payment events
    # determine its balance, keeping this scalable instead of10M account-days.
    aging=('0-30','31-60','61-90','91-120','121+')
    for (facility,payer),events in sorted(balance_events.items()):
        buckets=defaultdict(lambda:defaultdict(int))
        for post,payment_date,net,paid,writeoff,bad_debt in events:
            paid_date=datetime.fromisoformat(payment_date).date()
            for day in range(max(0,(post-START.date()).days),days):
                date=(START+timedelta(days=day)).date();balance=net-(paid if date>=paid_date else 0)-(bad_debt if date>=writeoff else 0)
                if not balance:continue
                age=(date-post).days;bucket=0 if age<=30 else 1 if age<=60 else 2 if age<=90 else 3 if age<=120 else 4
                buckets[date][aging[bucket]]+=balance
        for date,balances in sorted(buckets.items()):
            for bucket,balance in sorted(balances.items()):b('ar_snapshot_daily',snapshot_date=date.isoformat(),facility_id=facility,payer_id=payer,aging_bucket=bucket,balance_cents=balance)
    clinical.finish();billing.finish()
    summary={'version':'healthnet-synthetic/1','seed':settings.seed,'synthetic_only':True,'period_start':iso(START),'period_end_exclusive':iso(END),'tables':{}}
    for system,store in(('clinical',clinical),('billing',billing)):
        summary['tables'][system]={t:{'rows':store.db.execute('SELECT COUNT(*) FROM ['+t+']').fetchone()[0],'canonical_sha256':canonical_hash(store.db,t)}for t in store.tables}
        store.db.close()
        (output/('hn_'+system+'-schema.sql')).write_text(ddl(system,'azure'),encoding='utf8')
    (output/'generation.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8')
    return summary
