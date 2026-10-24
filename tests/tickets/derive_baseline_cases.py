"""Fixture-authored expectations by literal arithmetic, never engine queries."""
import hashlib,json,sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from fixture.seed import load

def records(table):return [dict(zip([c[0]for c in table['columns']],row))for row in table['rows']]
def derive():
 seed=load();tables={t['name']:records(t)for t in seed['tables']}
 movements=tables['stock_movements_e1b8e1'];rates=tables['product_rates_e1b8e1'];matches=Counter(r['product_id']for r in rates);groups=defaultdict(int)
 for row in movements:groups[row['product_id']]+=row['units']
 source=sum(r['units']for r in movements);serving=sum(r['units']*max(1,matches[r['product_id']])for r in movements)
 path=ROOT/'fixture-code/billing/source-seed.json';billing=json.loads(path.read_bytes());b={t['name']:records(t)for t in billing['tables']};history=Counter(row['account_id']for row in b['account_plan_history'])
 invoice_source=sum(r['amount']for r in b['invoices']);invoice_serving=sum(r['amount']*max(1,history[r['account_id']])for r in b['invoices'])
 return {'provenance':'Independent literal arithmetic, no engine or compiled/provider query executed','fixture':{'seed_notebook_sha256':seed['source_sha256'],'source_rows':len(movements),'source_quantity':source,'serving_quantity':serving,'join_excess':serving-source,'per_product':[{'product_id':k,'source_units':v,'rate_matches':matches[k],'left_join_contribution':v*max(1,matches[k])}for k,v in sorted(groups.items())]},'billing':{'seed_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_invoice_amount':invoice_source,'serving_invoice_amount':invoice_serving,'join_excess':invoice_serving-invoice_source,'per_invoice':[{'invoice_id':r['invoice_id'],'status':r['status'],'source_amount':r['amount'],'history_matches':history[r['account_id']],'left_join_contribution':r['amount']*max(1,history[r['account_id']])}for r in b['invoices']],'limitation':'All invoice statuses included to reproduce SUM(Billing[amount]); no judgment whether VOID should count.'},'not_current_value_verification':True}
if __name__=='__main__':print(json.dumps(derive(),indent=2))
