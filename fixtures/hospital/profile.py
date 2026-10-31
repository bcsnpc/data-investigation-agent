"""Measured population profile, separate from benchmark assumptions."""
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import statistics


def profile(directory,marts_directory=None):
    directory=Path(directory)
    with closing(sqlite3.connect(directory/'hn_clinical.sqlite'))as db:
        db.execute('ATTACH DATABASE ? AS billing',(str(directory/'hn_billing.sqlite'),))
        def scalar(sql):return db.execute(sql).fetchone()[0]
        def rows(sql):return db.execute(sql).fetchall()
        def median(sql):
            values=[r[0]for r in rows(sql)if r[0]is not None]
            return statistics.median(values)if values else None
        result={
            'source':'full seeded local sources; not native report values',
            'ed_door_provider_median_minutes':median('SELECT door_to_provider_minutes FROM ed_visit_detail'),
            'nonadmitted_ed_los_median_minutes':median('SELECT ed_los_minutes FROM ed_visit_detail WHERE admitted=0'),
            'alos_days_by_service':rows('SELECT d.service_line,AVG(julianday(e.discharge_utc)-julianday(e.admit_utc))FROM encounter e JOIN department d ON d.id=e.department_id WHERE e.admit_utc IS NOT NULL AND e.discharge_utc IS NOT NULL GROUP BY d.service_line ORDER BY 1'),
            'original_payer_mix_encounters':rows('SELECT p.payer_group,COUNT(*),1.0*COUNT(*)/(SELECT COUNT(*)FROM encounter)FROM encounter e JOIN payer_plan p ON p.id=e.payer_plan_id GROUP BY p.payer_group ORDER BY 1'),
            'provider_counts_and_fte':rows('SELECT provider_type,COUNT(*),SUM(fte)FROM provider GROUP BY provider_type ORDER BY 1'),
            'order_type_mix':rows('SELECT h.order_type,COUNT(*),1.0*COUNT(*)/(SELECT COUNT(*)FROM order_line)FROM order_line l JOIN order_header h ON h.id=l.order_header_id GROUP BY h.order_type ORDER BY 1'),
            'order_status_counts':rows('SELECT status,COUNT(*)FROM order_line GROUP BY status ORDER BY 1'),
            'stat_fraction_by_encounter_type':rows("SELECT e.encounter_type,AVG(l.priority='STAT')FROM order_line l JOIN order_header h ON h.id=l.order_header_id JOIN encounter e ON e.id=h.encounter_id GROUP BY 1 ORDER BY 1"),
            'posting_delay_days':rows('SELECT CAST(julianday(post_date)-julianday(service_date) AS INTEGER),COUNT(*)FROM billing.charge GROUP BY 1 ORDER BY 1'),
            'days_to_original_bill_mean':scalar('SELECT AVG(julianday(c.submitted_at)-julianday(a.opened_at))FROM billing.claim c JOIN billing.account a ON a.id=c.account_id WHERE c.is_original=1'),
            'days_original_bill_to_cash_mean':scalar("SELECT AVG(julianday(p.payment_date)-julianday(c.submitted_at))FROM billing.payment p JOIN billing.claim c ON c.account_id=p.account_id AND c.is_original=1 WHERE p.payment_type IN('PATIENT','INSURANCE')"),
            'initial_denial_categories':rows("SELECT r.denial_category,COUNT(*),SUM(r.denied_cents)FROM billing.remittance_line r JOIN billing.remittance m ON m.id=r.remittance_id JOIN billing.claim c ON c.id=m.claim_id WHERE c.is_original=1 AND r.denied_cents>0 GROUP BY 1 ORDER BY 1"),
            'current_ar_by_age_cents':rows("SELECT aging_bucket,SUM(balance_cents)FROM billing.ar_snapshot_daily WHERE snapshot_date='2026-10-29'GROUP BY 1 ORDER BY 1"),
            'adjustments_by_kind_cents':rows('SELECT adjustment_type,COUNT(*),SUM(amount_cents)FROM billing.adjustment GROUP BY 1 ORDER BY 1'),
            'turnaround_median_minutes_by_modality_and_priority':[],
        }
        for modality,priority in rows('SELECT DISTINCT h.order_type,l.priority FROM order_line l JOIN order_header h ON h.id=l.order_header_id ORDER BY 1,2'):
            values=[r[0]for r in db.execute("SELECT (julianday(l.completed_utc)-julianday(l.ordered_utc))*1440 FROM order_line l JOIN order_header h ON h.id=l.order_header_id WHERE l.status='RESULTED'AND l.completed_utc IS NOT NULL AND h.order_type=? AND l.priority=?",(modality,priority))]
            result['turnaround_median_minutes_by_modality_and_priority'].append([modality,priority,statistics.median(values)if values else None])
    if marts_directory:
        with closing(sqlite3.connect(Path(marts_directory)/'hn_dw.sqlite'))as db:
            result['occupancy_fraction_by_facility']=db.execute('SELECT facility_id,1.0*SUM(midnight_census)/SUM(licensed_beds) FROM mart_census_daily GROUP BY 1 ORDER BY 1').fetchall()
            result['provider_daily_visits_and_workload_ranges']=db.execute('SELECT MIN(visits),MAX(visits),AVG(visits),MIN(workload_units),MAX(workload_units)FROM mart_provider_productivity_daily').fetchone()
    return result


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',required=True);p.add_argument('--marts-directory');p.add_argument('--output',required=True)
    a=p.parse_args()
    Path(a.output).write_text(json.dumps(profile(a.directory,a.marts_directory),indent=2)+'\n',encoding='utf8')
