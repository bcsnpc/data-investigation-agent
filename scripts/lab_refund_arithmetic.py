"""Verify a supported local double-refund arithmetic build, never arbitrary receipt SQL."""
from contextlib import closing
import json
import duckdb
from defect_lab import evidence,fingerprints,query,double_refund_query


def verify(path,payload,result):
    def blocked(reason):return {'verified':False,'reason':reason}
    if result['comparison_status']!='MISMATCH':return blocked('No discrepancy')
    with closing(duckdb.connect(str(path),read_only=True)) as db:
        db.execute('BEGIN TRANSACTION')
        if not db.execute("SELECT 1 FROM information_schema.tables WHERE table_name='gold_arithmetic_receipt'").fetchone():return blocked('No arithmetic build receipt')
        receipts=db.execute('SELECT query_text,fingerprints FROM gold_arithmetic_receipt').fetchall()
        if len(receipts)!=1:return blocked('Ambiguous arithmetic receipt')
        sql,encoded=receipts[0]
        if sql!=double_refund_query():return blocked('Unsupported arithmetic transformation')
        try:recorded=json.loads(encoded)
        except (ValueError,TypeError):return blocked('Invalid build fingerprint')
        if recorded!=fingerprints(db):return blocked('Source/output changed after build')
        if evidence(path,connection=db)!=payload:return blocked('Stale observation')
        actual=db.execute('SELECT * FROM g_order_line_summary ORDER BY ALL').fetchall()
        if db.execute(double_refund_query()+' ORDER BY ALL').fetchall()!=actual:return blocked('Arithmetic replay does not reproduce output')
        expected={(r[0],r[1]):r[2] for r in db.execute('SELECT order_id,currency,SUM(net_cash_amount) FROM ('+query()+') q GROUP BY 1,2').fetchall()}
        observed={(r['order_id'],r['currency']):r['silver_net_cash'] for r in payload['rows'] if r['silver_present']}
        if expected!=observed:return blocked('Corrected query does not reconcile with Silver')
        return {'verified':True,'classification':'TECHNICAL_DEFECT','cause':'Gold build subtracts refund amount twice',
                'scope':'Supported local Silver-to-Gold arithmetic build only','query_text':sql,
                'build_fingerprints':recorded,'faulty_replay_matches':True,'corrected_replay_reconciles':True,
                'references':['/request/cause_evidence','/request/lab_evidence/rows']}
