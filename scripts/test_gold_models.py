"""Execute the same reporting SQL against small, independently calculated cases."""
import importlib.util
import unittest
from decimal import Decimal
from pathlib import Path
import duckdb

spec = importlib.util.spec_from_file_location('gold_models',Path(__file__).resolve().parents[1]/'infra/fabric/gold_models.py')
models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(models)

class GoldModelsTest(unittest.TestCase):
    def setUp(self):
        self.db=duckdb.connect()
        self.db.execute("""
        CREATE TABLE s_dim_customer(customer_id VARCHAR,customer_name VARCHAR,customer_segment VARCHAR,state_code VARCHAR,country_code VARCHAR);
        INSERT INTO s_dim_customer VALUES ('C','Example','business','CA','US');
        CREATE TABLE s_dim_product(product_id VARCHAR,product_name VARCHAR,category VARCHAR,subcategory VARCHAR);
        INSERT INTO s_dim_product VALUES ('P','Product P','Office','Accessories'),('Q','Product Q','Office','Accessories');
        CREATE TABLE s_fact_order(order_id VARCHAR,customer_id VARCHAR,order_date TIMESTAMP,currency VARCHAR,status VARCHAR,total_amount DECIMAL(19,4),captured_amount DECIMAL(19,4),refunded_amount DECIMAL(19,4),coupon_code VARCHAR,dataset_id VARCHAR);
        INSERT INTO s_fact_order VALUES
        ('A','C','2026-01-01','USD','PARTIALLY_RETURNED',198,198,99,'PROMO','test'),
        ('B','C','2026-01-01','USD','PAID',55,55,0,NULL,'test'),
        ('CANCEL','C','2026-01-01','USD','CANCELLED',110,0,0,NULL,'test'),
        ('PENDING','C','2026-01-01','USD','PENDING_PAYMENT',110,0,0,NULL,'test'),
        ('EURO','C','2026-01-02','EUR','PAID',12,12,0,NULL,'test');
        CREATE TABLE s_fact_order_line(order_line_id VARCHAR,order_id VARCHAR,product_id VARCHAR,quantity INTEGER,unit_price DECIMAL(19,4),discount_amount DECIMAL(19,4),order_discount_amount DECIMAL(19,4),line_total DECIMAL(19,4),tax_amount DECIMAL(19,4));
        INSERT INTO s_fact_order_line VALUES
        ('A1','A','P',2,60,20,10,90,9),('A2','A','P',1,110,10,10,90,9),
        ('B1','B','Q',2,25,0,0,50,5),('C1','CANCEL','P',1,100,0,0,100,10),
        ('D1','PENDING','P',1,100,0,0,100,10),('E1','EURO','P',1,10,0,0,10,2);
        CREATE TABLE s_fact_refund_line(refund_id VARCHAR,order_line_id VARCHAR,quantity INTEGER,merchandise_amount DECIMAL(19,4),tax_amount DECIMAL(19,4));
        INSERT INTO s_fact_refund_line VALUES ('R1','A1',1,45,4.5),('R2','A1',1,45,4.5);
        CREATE TABLE s_fact_refund(refund_id VARCHAR,order_id VARCHAR,payment_id VARCHAR,refund_date TIMESTAMP,refund_reason VARCHAR,refund_amount DECIMAL(19,4));
        INSERT INTO s_fact_refund VALUES ('R1','A','PAY-A','2026-01-10','Return',49.5),('R2','A','PAY-A','2026-01-11','Return',49.5);
        """)
        for name,query in models.QUERIES.items():
            self.db.execute(f'CREATE VIEW g_{name} AS {query}')

    def tearDown(self):
        self.db.close()

    def row(self,query):
        cursor=self.db.execute(query)
        return dict(zip([d[0] for d in cursor.description],cursor.fetchone()))

    def test_multiple_refunds_and_duplicate_product_lines_do_not_multiply_orders(self):
        row=self.row("SELECT * FROM g_order_summary WHERE order_id='A'")
        self.assertEqual(row['line_count'],2)
        self.assertEqual(row['captured_amount'],Decimal('198'))
        self.assertEqual(row['refund_amount'],Decimal('99'))
        self.assertEqual(row['net_cash_amount'],Decimal('99'))
        self.assertEqual(row['units_returned'],2)
        self.assertEqual(row['net_units'],1)
        row=self.row("SELECT * FROM g_sales_by_product WHERE product_id='P' AND currency='USD'")
        self.assertEqual(row['funded_order_count'],1)
        self.assertEqual(row['order_count'],3)
        self.assertEqual(row['captured_amount'],Decimal('198'))

    def test_both_discounts_are_applied_once_and_tax_is_separate(self):
        row=self.row("SELECT * FROM g_order_line_summary WHERE order_line_id='A1'")
        self.assertEqual(row['gross_sales_amount'],Decimal('120'))
        self.assertEqual(row['discount_amount'],Decimal('30'))
        self.assertEqual(row['sales_amount'],Decimal('90'))
        self.assertEqual(row['tax_amount'],Decimal('9'))
        self.assertEqual(row['net_sales_amount'],Decimal('0'))

    def test_cancelled_and_unpaid_orders_have_zero_sales_but_keep_order_counts(self):
        for order in ('CANCEL','PENDING'):
            row=self.row(f"SELECT * FROM g_order_summary WHERE order_id='{order}'")
            for col in models.MONEY:
                self.assertEqual(row[col],0,col)
            self.assertEqual(row['units_ordered'],1)
            self.assertEqual(row['units_sold'],0)
        row=self.row("SELECT * FROM g_sales_daily WHERE currency='USD'")
        self.assertEqual(row['order_count'],4)
        self.assertEqual(row['funded_order_count'],2)
        self.assertEqual(row['cancelled_order_count'],1)

    def test_all_aggregates_reconcile_and_currencies_remain_separate(self):
        for table in ('sales_daily','sales_by_customer','sales_by_product','order_summary','order_line_summary'):
            row=self.row(f"SELECT SUM(captured_amount) captured,SUM(net_sales_amount) sales,SUM(net_tax_amount) tax,SUM(net_cash_amount) cash FROM g_{table} WHERE currency='USD'")
            self.assertEqual(row,{'captured':Decimal('253'),'sales':Decimal('140'),'tax':Decimal('14'),'cash':Decimal('154')})
        row=self.row("SELECT captured_amount FROM g_sales_daily WHERE currency='EUR'")
        self.assertEqual(row['captured_amount'],Decimal('12'))

    def test_refund_calendar_and_sales_cohort_are_explicit(self):
        row=self.row("SELECT order_day,refund_day,refund_amount FROM g_refund_summary WHERE refund_id='R2'")
        self.assertEqual(str(row['order_day']),'2026-01-01')
        self.assertEqual(str(row['refund_day']),'2026-01-11')
        self.assertEqual(row['refund_amount'],Decimal('49.5'))
        row=self.row("SELECT order_day,refund_amount FROM g_sales_daily WHERE currency='USD'")
        self.assertEqual(str(row['order_day']),'2026-01-01')
        self.assertEqual(row['refund_amount'],Decimal('99'))

    def test_paid_cancellation_preserves_capture_and_full_refund(self):
        self.db.execute("""
        INSERT INTO s_fact_order VALUES ('PAID-CANCEL','C','2026-01-01','USD','CANCELLED',110,110,110,NULL,'test');
        INSERT INTO s_fact_order_line VALUES ('PC1','PAID-CANCEL','Q',2,50,0,0,100,10);
        INSERT INTO s_fact_refund_line VALUES ('RPC','PC1',2,100,10);
        INSERT INTO s_fact_refund VALUES ('RPC','PAID-CANCEL','PAY-PC','2026-01-01','Cancelled before shipment',110);
        """)
        row=self.row("SELECT * FROM g_order_summary WHERE order_id='PAID-CANCEL'")
        self.assertEqual(row['captured_amount'],Decimal('110'))
        self.assertEqual(row['refund_amount'],Decimal('110'))
        for metric in ('net_sales_amount','net_tax_amount','net_cash_amount','net_units'):
            self.assertEqual(row[metric],0,metric)
        self.assertEqual(row['units_sold'],2)
        self.assertEqual(row['units_returned'],2)
        self.assertEqual(row['is_cancelled'],1)
        row=self.row("SELECT * FROM g_sales_daily WHERE currency='USD'")
        self.assertEqual(row['captured_amount'],Decimal('363'))
        self.assertEqual(row['refund_amount'],Decimal('209'))
        self.assertEqual(row['net_cash_amount'],Decimal('154'))

if __name__=='__main__':
    unittest.main()
