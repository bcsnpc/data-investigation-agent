"""Verify the supported local prior-refund snapshot, without inferring refresh SLA."""
from contextlib import closing
import json
import duckdb
from defect_lab import evidence,fingerprints,query,stale_query,digest


def verify(path,payload,result):
    def blocked(reason):return {'verified':False,'reason':reason}
    if result['comparison_status']!='MISMATCH':return blocked('No discrepancy')
    with closing(duckdb.connect(str(path),read_only=True)) as db:
        db.execute('BEGIN TRANSACTION')
        if not db.execute("SELECT 1 FROM information_schema.tables WHERE table_name='gold_snapshot_receipt'").fetchone():return blocked('No source-version build receipt')
        rows=db.execute('SELECT contract,query_hash,fingerprints FROM gold_snapshot_receipt').fetchall()
        if len(rows)!=1:return blocked('Ambiguous source-version evidence')
        contract,code_hash,hashes=rows[0]
        if contract!='local-prior-empty-refund-snapshot-v1' or code_hash!=digest(query()):return blocked('Unsupported snapshot or changed transformation')
        if json.loads(hashes)!=fingerprints(db) or evidence(path,connection=db)!=payload:return blocked('Stale receipt or observations')
        if not db.execute('SELECT COUNT(*) FROM s_fact_refund_line').fetchone()[0]:return blocked('No newer refund evidence')
        actual=db.execute('SELECT * FROM g_order_line_summary ORDER BY ALL').fetchall()
        if db.execute(stale_query()+' ORDER BY ALL').fetchall()!=actual:return blocked('Prior snapshot does not reproduce Gold')
        current=db.execute('SELECT order_id,currency,SUM(net_cash_amount) FROM ('+query()+') q GROUP BY order_id,currency').fetchall()
        expected={(r[0],r[1]):r[2] for r in current}
        silver={(r['order_id'],r['currency']):r['silver_net_cash'] for r in payload['rows'] if r['silver_present']}
        if expected!=silver:return blocked('Current replay does not reconcile with Silver')
        return {'verified':True,'classification':'REFRESH_FRESHNESS',
                'cause':'Gold uses the prior empty-refund source snapshot; current refunds are not reflected',
                'scope':'Supported local snapshot fixture only; refresh frequency and scheduler failure are not inferred',
                'snapshot_contract':contract,'query_hash':code_hash,'build_fingerprints':json.loads(hashes),
                'prior_replay_matches':True,'current_replay_reconciles':True,
                'references':['/request/cause_evidence','/request/lab_evidence/rows']}
