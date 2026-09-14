"""Verify one supported build defect against current local business data and receipt."""
from contextlib import closing
import json
import duckdb
from defect_lab import evidence,fingerprints,query,filter_query


def verify_filter(path,payload,result):
    def blocked(reason):return {'verified':False,'reason':reason}
    if result['comparison_status']!='MISMATCH':return blocked('No discrepancy to explain')
    with closing(duckdb.connect(str(path),read_only=True)) as db:
        db.execute('BEGIN TRANSACTION')
        if not db.execute("SELECT 1 FROM information_schema.tables WHERE table_name='gold_build_receipt'").fetchone():
            return blocked('No captured transformation build evidence')
        receipts=db.execute('SELECT query_text,fingerprints FROM gold_build_receipt').fetchall()
        if len(receipts)!=1:return blocked('Ambiguous build evidence')
        sql,recorded=receipts[0]
        if sql!=filter_query():return blocked('Unsupported transformation; captured SQL is never executed')
        if json.loads(recorded)!=fingerprints(db):return blocked('Source/output changed after build')
        if evidence(path,connection=db)!=payload:return blocked('Investigation observations are stale')
        # Execute only the repository-owned queries, not receipt text.
        predicted=db.execute(filter_query()+' ORDER BY ALL').fetchall()
        actual=db.execute('SELECT * FROM g_order_line_summary ORDER BY ALL').fetchall()
        if predicted!=actual:return blocked('Filtered replay does not reproduce output')
        baseline=db.execute('SELECT order_id,currency,SUM(net_cash_amount) FROM ('+query()+') q GROUP BY order_id,currency').fetchall()
        expected={(r[0],r[1]):r[2] for r in baseline}
        observed={(r['order_id'],r['currency']):r['silver_net_cash'] for r in payload['rows'] if r['silver_present']}
        if expected!=observed:return blocked('Unfiltered contract does not reconcile with Silver')
        return {'verified':True,'cause':'Gold build excludes PARTIALLY_RETURNED records',
                'scope':'This local Silver-to-Gold build only','query_text':sql,'build_fingerprints':json.loads(recorded),
                'filtered_replay_matches':True,'unfiltered_replay_reconciles':True,
                'references':['/request/cause_evidence','/request/lab_evidence/rows']}


def verify(path,payload,result):
    finding=verify_filter(path,payload,result)
    if finding['verified']:return finding
    from lab_freshness import verify as verify_freshness
    freshness=verify_freshness(path,payload,result)
    if freshness['verified']:return freshness
    from lab_refund_arithmetic import verify as verify_arithmetic
    arithmetic=verify_arithmetic(path,payload,result)
    return arithmetic if arithmetic['verified'] else {'verified':False,'filter_reason':finding['reason'],'freshness_reason':freshness['reason'],'arithmetic_reason':arithmetic['reason']}
