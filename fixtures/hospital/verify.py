"""Independent relational and financial checks of generated sources."""
import json
from pathlib import Path
import sqlite3
from .generate import END


def verify(directory):
    directory=Path(directory)
    db=sqlite3.connect(directory/'hn_clinical.sqlite')
    db.execute('ATTACH DATABASE ? AS billing',(str(directory/'hn_billing.sqlite'),))
    checks={}
    def zero(name,sql):
        count=db.execute(sql).fetchone()[0]
        checks[name]={'violations':count,'passed':count==0}
    for schema in('main','billing'):
        checks[schema+'_foreign_keys']={'violations':len(db.execute('PRAGMA '+schema+'.foreign_key_check').fetchall())}
        checks[schema+'_foreign_keys']['passed']=checks[schema+'_foreign_keys']['violations']==0
    zero('bed_intervals_do_not_overlap',"""SELECT COUNT(*) FROM (
      SELECT start_utc,LAG(COALESCE(end_utc,'9999')) OVER(PARTITION BY bed_id ORDER BY start_utc,id) previous_end FROM bed_assignment
    ) WHERE previous_end>start_utc""")
    zero('readmission_same_person_within_30_days',"""SELECT COUNT(*) FROM encounter e JOIN encounter p ON p.id=e.readmission_of
      WHERE e.patient_id<>p.patient_id OR julianday(e.arrival_utc)-julianday(p.discharge_utc) NOT BETWEEN 0 AND 30""")
    zero('replacement_same_encounter',"""SELECT COUNT(*) FROM order_line l JOIN order_header h ON h.id=l.order_header_id
      JOIN order_line p ON p.id=l.replaces_order_line_id JOIN order_header ph ON ph.id=p.order_header_id
      WHERE h.encounter_id<>ph.encounter_id OR h.order_type<>ph.order_type OR p.status<>'VOIDED'""")
    zero('duplicate_demographics_agree',"""SELECT COUNT(*) FROM patient_alias a JOIN patient p ON p.id=a.patient_id JOIN patient q ON q.id=a.alias_patient_id
      WHERE p.person_key<>q.person_key OR p.birth_date<>q.birth_date OR p.sex<>q.sex""")
    zero('claim_one_original_and_final',"""SELECT COUNT(*) FROM(SELECT claim_group FROM billing.claim GROUP BY claim_group HAVING SUM(is_original)<>1 OR SUM(is_final)<>1)""")
    zero('claim_lines_match_claim',"""SELECT COUNT(*) FROM billing.claim c JOIN(SELECT claim_id,SUM(amount_cents) amount FROM billing.claim_line GROUP BY claim_id)l ON l.claim_id=c.id WHERE l.amount<>c.billed_cents""")
    zero('remittance_conservation',"""SELECT COUNT(*) FROM billing.remittance_line r JOIN billing.claim_line l ON l.id=r.claim_line_id
      WHERE r.paid_cents+r.adjusted_cents+r.denied_cents<>l.amount_cents""")
    zero('submitted_claims_have_no_future_remittance',"""SELECT COUNT(*) FROM billing.claim c JOIN billing.remittance r ON r.claim_id=c.id WHERE c.status='SUBMITTED' OR r.received_at>='2026-10-30'""")
    zero('payment_reversals_conserve',"""SELECT COUNT(*) FROM billing.payment r JOIN billing.payment p ON p.id=r.reverses_payment_id
      WHERE r.payment_type IN('REVERSAL','MOVE_REVERSAL') AND (r.amount_cents<>-p.amount_cents OR r.account_id<>p.account_id)""")
    zero('temporal_business_times_ordered',"""SELECT COUNT(*) FROM encounter WHERE discharge_utc<arrival_utc OR admit_utc<arrival_utc OR discharge_utc<admit_utc""")
    finance=db.execute("""SELECT (SELECT COALESCE(SUM(amount_cents),0)FROM billing.charge)
       +(SELECT COALESCE(SUM(amount_cents),0)FROM billing.adjustment)
       -(SELECT COALESCE(SUM(amount_cents),0)FROM billing.payment)""").fetchone()[0]
    snapshots=db.execute("SELECT COALESCE(SUM(balance_cents),0) FROM billing.ar_snapshot_daily WHERE snapshot_date='2026-10-29'").fetchone()[0]
    checks['current_ar_equals_charges_plus_adjustments_minus_payments']={'passed':finance==snapshots,'accounting_balance_cents':finance,'snapshot_balance_cents':snapshots}
    messiness={name:db.execute(sql).fetchone()[0]for name,sql in {
      'duplicate_mrns':'SELECT COUNT(*)FROM patient_alias','merged_mrns':'SELECT COUNT(*)FROM patient_merge',
      'provider_transfers':"SELECT COUNT(*)FROM provider_assignment WHERE valid_from='2026-04-16'",
      'late_charges':'SELECT COUNT(*)FROM billing.charge WHERE post_date>service_date',
      'cross_month_late_charges':"SELECT COUNT(*)FROM billing.charge WHERE substr(post_date,1,7)<>substr(service_date,1,7)",
      'cancelled_orders':"SELECT COUNT(*)FROM order_line WHERE status='CANCELLED'",
      'voided_orders':"SELECT COUNT(*)FROM order_line WHERE status='VOIDED'",
      'reentered_orders':'SELECT COUNT(*)FROM order_line WHERE replaces_order_line_id IS NOT NULL',
      'reversals':"SELECT COUNT(*)FROM billing.payment WHERE payment_type='REVERSAL'",
      'refunds':"SELECT COUNT(*)FROM billing.payment WHERE payment_type='REFUND'",
      'misposts_moved':"SELECT COUNT(*)FROM billing.payment WHERE payment_type='MOVE_REVERSAL'",
      'corrected_claims':"SELECT COUNT(*)FROM billing.claim WHERE submission_type='CORRECTED'",
      'resubmissions':"SELECT COUNT(*)FROM billing.claim WHERE submission_type='RESUBMISSION'",
      'observation_to_ip':"SELECT COUNT(*)FROM encounter WHERE initial_status='OBSERVATION'AND encounter_type='INPATIENT'",
      'interhospital_transfers':'SELECT COUNT(*)FROM encounter WHERE transfer_from IS NOT NULL',
      'soft_deleted_encounters':'SELECT COUNT(*)FROM encounter WHERE is_deleted=1',
      'null_attending':'SELECT COUNT(*)FROM encounter WHERE attending_provider_id IS NULL',
      'zero_charges':'SELECT COUNT(*)FROM billing.charge WHERE amount_cents=0',
      'billing_only_accounts':'SELECT COUNT(*)FROM billing.account a LEFT JOIN encounter e ON e.encounter_number=a.encounter_number WHERE e.id IS NULL',
      'clinical_only_encounters':'SELECT COUNT(*)FROM encounter e LEFT JOIN billing.account a ON e.encounter_number=a.encounter_number WHERE a.id IS NULL',
      'bad_debt_writeoffs':"SELECT COUNT(*)FROM billing.adjustment WHERE adjustment_type='BAD_DEBT'",
    }.items()}
    distributions={}
    for name,sql in {
      'ed_admission_fraction':'SELECT AVG(admitted) FROM ed_visit_detail',
      'ed_lwbs_fraction':'SELECT AVG(lwbs) FROM ed_visit_detail',
      'ed_transfer_fraction':'SELECT AVG(transferred) FROM ed_visit_detail',
      'inpatient_completed_alos_days':"SELECT AVG(julianday(discharge_utc)-julianday(admit_utc))FROM encounter WHERE admit_utc IS NOT NULL AND discharge_utc IS NOT NULL",
      'readmission_fraction_admissions':'SELECT AVG(readmission_of IS NOT NULL)FROM encounter WHERE admit_utc IS NOT NULL',
      'orders_per_encounter':'SELECT 1.0*(SELECT COUNT(*)FROM order_line)/(SELECT COUNT(*)FROM encounter)',
      'stat_fraction':"SELECT AVG(priority='STAT')FROM order_line",
      'cancellation_fraction':"SELECT AVG(status='CANCELLED')FROM order_line",
      'initial_adjudicated_denial_fraction':"SELECT AVG(status='DENIED')FROM billing.claim WHERE is_original=1 AND status<>'SUBMITTED'",
      'final_adjudicated_denial_fraction':"SELECT AVG(status='DENIED')FROM billing.claim WHERE is_final=1 AND status<>'SUBMITTED'",
      'part_time_provider_fraction':'SELECT AVG(fte<1)FROM provider',
    }.items():distributions[name]=db.execute(sql).fetchone()[0]
    db.close()
    report={'checks':checks,'all_passed':all(c['passed']for c in checks.values()),'messiness':messiness,'distributions':distributions,'native_verification':False}
    (directory/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    return report
