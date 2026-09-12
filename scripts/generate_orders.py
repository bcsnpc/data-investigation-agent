"""Deterministic, linked retail histories. No network or third-party packages.

All calculations use integer cents and explicit half-up rounding. TSV artifacts
are loaded with SqlBulkCopy after SQLite reconciliation succeeds.
"""
import argparse
import csv
import hashlib
import json
import random
import sqlite3
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

START = datetime(2025, 9, 12)
AS_OF = datetime(2026, 9, 12)
HEADERS = {
 'customers': 'customer_id customer_name customer_segment state country created_at purchase_profile',
 'products': 'product_id product_name category subcategory unit_price active_flag available_from compatibility_family',
 'orders': 'order_id customer_id order_date status subtotal discount_amount tax_amount total_amount created_at updated_at currency coupon_code tax_rate dataset_id',
 'order_lines': 'order_line_id order_id product_id quantity unit_price discount_amount line_total order_discount_amount tax_amount promotion_code',
 'payments': 'payment_id order_id payment_type amount payment_status payment_date',
 'shipments': 'shipment_id order_id carrier tracking_number shipped_at delivered_at',
 'shipment_lines': 'shipment_id order_line_id quantity',
 'refunds': 'refund_id order_id refund_amount refund_reason refund_date payment_id',
 'refund_lines': 'refund_id order_line_id quantity merchandise_amount tax_amount',
 'audit_log': 'event_id entity_type entity_id operation field old_value new_value user_id timestamp',
}
CATEGORIES = [
 ('Keyboard', 4500, 5), ('Mouse', 2200, 7), ('Monitor', 18000, 3),
 ('Dock', 8500, 3), ('Webcam', 4000, 3), ('Headset', 3500, 4),
 ('Cable', 900, 12), ('Stand', 2500, 3), ('Charger', 3000, 5), ('Hub', 3500, 4),
]

def money(cents):
 return f'{cents // 100}.{cents % 100:02d}'

def rounded_ratio(value, numerator, denominator):
 return (value * numerator * 2 + denominator) // (2 * denominator)

def allocate(total, weights):
 """Largest-remainder allocation preserves every cent deterministically."""
 denominator = sum(weights)
 if not denominator:
  return [0] * len(weights)
 result = [total * w // denominator for w in weights]
 ranking = sorted(range(len(weights)), key=lambda i: (-(total * weights[i] % denominator), i))
 for i in ranking[:total - sum(result)]:
  result[i] += 1
 assert sum(result) == total
 return result

def stamp(value):
 return value.isoformat(timespec='seconds') if value else None

def generate(output, count, seed):
 output.mkdir(parents=True, exist_ok=True)
 db_path = output / 'baseline.sqlite'
 if db_path.exists():
  raise ValueError('Output already contains a baseline; choose a new directory.')
 rng = random.Random(seed)
 dataset_id = f'retail-v1-s{seed}-n{count}-20260912'
 conn = sqlite3.connect(db_path)
 # Local tables store money as formatted decimal text; validation converts to cents.
 for table, header in HEADERS.items():
  conn.execute(f'CREATE TABLE {table} ({", ".join(header.split())})')
 def emit(table, row):
  assert len(row) == len(HEADERS[table].split()), table
  conn.execute(f'INSERT INTO {table} VALUES ({",".join("?" for _ in row)})', row)
 customer_count = max(20, count // 5)
 states = [('CA', 825), ('TX', 800), ('NY', 850), ('IL', 800), ('WA', 900), ('OR', 0)]
 first = ['Avery','Jordan','Morgan','Casey','Taylor','Riley','Alex','Sam','Jamie','Cameron']
 last = ['Brooks','Patel','Chen','Rivera','Kim','Wilson','Reed','Singh','Nguyen','Parker']
 customers = []
 schedules = []
 # 40% one-time, 45% repeat, 15% business; every customer gets at least one order.
 for i in range(customer_count):
  profile = 'one_time' if i < customer_count * .40 else ('repeat' if i < customer_count * .85 else 'business')
  cid = f'CUST-{i+1:06d}'
  state, tax = rng.choice(states)
  name = f'{rng.choice(first)} {rng.choice(last)}' if profile != 'business' else f'{rng.choice(last)} Workspace {i+1:05d}'
  created = START + timedelta(days=rng.randrange(-180, 250), hours=rng.randrange(24))
  family = rng.choice(['USB-C', 'USB-A'])
  customers.append((cid, profile, created, tax, family))
  emit('customers', [cid,name,'Small Business' if profile == 'business' else 'Consumer',state,'US',stamp(created),profile])
  schedules.append(i)
 repeaters = [i for i,c in enumerate(customers) if c[1] != 'one_time']
 weights = [4 if customers[i][1] == 'business' else 1 for i in repeaters]
 schedules.extend(rng.choices(repeaters, weights=weights, k=count-customer_count))
 products = []
 for i in range(150):
  category, base, popularity = CATEGORIES[i % 10]
  tier = i // 10
  family = 'USB-C' if tier % 2 == 0 else 'USB-A'
  available = START + timedelta(days=120 if tier == 14 else -90)
  price = base + tier * max(200, base // 12)
  pid = f'PROD-{i+1:04d}'
  products.append((pid,category,price,popularity,family,available))
  emit('products',[pid,f'{category} {family} Series {tier+1}', 'Office Electronics',category,money(price),1,stamp(available),family])
 # Shared calendar generates promotion/weekend demand, rather than uniform dates.
 calendar = [START + timedelta(days=d) for d in range((AS_OF-START).days)]
 day_weights = [4 if d.month == 11 and 24 <= d.day <= 30 else (2 if d.month == 8 else (0.8 if d.weekday() >= 5 else 1)) for d in calendar]
 events = []
 for ci in schedules:
  created = customers[ci][2]
  valid = [(d,w) for d,w in zip(calendar,day_weights) if d >= max(START,created)]
  day = rng.choices([x[0] for x in valid], weights=[x[1] for x in valid])[0]
  events.append((day + timedelta(hours=rng.randrange(8,22),minutes=rng.randrange(60),seconds=rng.randrange(60)),ci))
 events.sort()
 previous = {}
 status_counts = Counter()
 event_number = 0
 def audit(entity_type, entity_id, operation, field, old, new, at, actor):
  nonlocal event_number
  event_number += 1
  emit('audit_log',[f'EVT-{event_number:09d}',entity_type,entity_id,operation,field,old,new,actor,stamp(at)])
 for oi,(at,ci) in enumerate(events,1):
  oid = f'ORD-{oi:06d}'
  cid,profile,created,tax,family = customers[ci]
  actor = f'customer:{cid}'
  existing = previous.setdefault(cid,set())
  candidates = [p for p in products if p[5] <= at and p[4] == family]
  basket = []
  for _ in range(rng.choices([1,2,3,4,5],[12,25,35,20,8])[0]):
   options = [p for p in candidates if p not in basket]
   pw = [p[3] * (2 if p[1] in ('Cable','Dock','Hub') and 'Monitor' in existing else 1) * (.2 if p[1] in existing and p[1] == 'Monitor' and profile != 'business' else 1) for p in options]
   basket.append(rng.choices(options,weights=pw)[0])
  promo = at.month == 11 and 24 <= at.day <= 30
  coupon = 'WELCOME10' if not existing and rng.random() < .45 else ('OFFICE5' if profile == 'business' and rng.random() < .30 else None)
  gross, item_discounts, quantities, prices = [],[],[],[]
  for p in basket:
   qty = rng.choices([1,2,3],[80,17,3])[0] if profile != 'business' else rng.choices([2,5,8,10,15],[20,35,20,20,5])[0]
   # Catalog list price is stable; promotions are explicit discounts.
   price = p[2]
   g = qty * price
   discount = rounded_ratio(g,15,100) if promo and p[1] in ('Keyboard','Mouse','Headset') else 0
   gross.append(g); item_discounts.append(discount); quantities.append(qty); prices.append(price)
  net_before_coupon = [g-d for g,d in zip(gross,item_discounts)]
  coupon_total = rounded_ratio(sum(net_before_coupon),10 if coupon == 'WELCOME10' else 5,100) if coupon else 0
  allocated = allocate(coupon_total,net_before_coupon)
  nets = [n-d for n,d in zip(net_before_coupon,allocated)]
  taxes = [rounded_ratio(n,tax,10000) for n in nets]
  total = sum(nets)+sum(taxes)
  line_ids = [f'LINE-{oi:06d}-{j+1:02d}' for j in range(len(basket))]
  for j,p in enumerate(basket):
   emit('order_lines',[line_ids[j],oid,p[0],quantities[j],money(prices[j]),money(item_discounts[j]),money(nets[j]),money(allocated[j]),money(taxes[j]),'NOV15' if item_discounts[j] else None])
  history = [(at,'PENDING_PAYMENT')]
  payment_id = f'PAY-{oi:06d}-02'
  failed = rng.random() < .075
  paid_at = at + timedelta(minutes=rng.randrange(5,90) if failed else 1)
  cancel_unpaid = rng.random() < .025
  if failed:
   emit('payments',[f'PAY-{oi:06d}-01',oid,'Card',money(total),'FAILED',stamp(at+timedelta(seconds=20))])
   audit('payment',f'PAY-{oi:06d}-01','CREATE','payment_status',None,'FAILED',at+timedelta(seconds=20),'payment_gateway')
  paid = not cancel_unpaid and paid_at <= AS_OF
  shipment = None
  refund_at = None
  refund_selection = []
  refund_reason = None
  if cancel_unpaid:
   cancelled = at + timedelta(hours=2)
   if cancelled <= AS_OF: history.append((cancelled,'CANCELLED'))
  elif paid:
   emit('payments',[payment_id,oid,'Bank Transfer' if profile == 'business' else 'Card',money(total),'CAPTURED',stamp(paid_at)])
   audit('payment',payment_id,'CREATE','payment_status',None,'CAPTURED',paid_at,'payment_gateway')
   history.append((paid_at,'PAID'))
   cancel_paid = rng.random() < .015
   ship_at = paid_at + timedelta(days=rng.choices([1,2,4,7],[60,30,8,2])[0])
   if cancel_paid:
    cancelled = paid_at + timedelta(hours=3)
    if cancelled <= AS_OF:
     history.append((cancelled,'CANCELLED'))
     refund_at = cancelled
     refund_selection = list(range(len(basket)))
     refund_reason = 'Cancelled before shipment'
   elif ship_at <= AS_OF:
    delivery = ship_at + timedelta(days=rng.choices([2,3,5,9],[35,40,20,5])[0])
    shipment = f'SHIP-{oi:06d}'
    delivered = delivery if delivery <= AS_OF else None
    emit('shipments',[shipment,oid,rng.choice(['DemoParcel','DemoExpress']),f'DEMO{oi:012d}',stamp(ship_at),stamp(delivered)])
    for lid,qty in zip(line_ids,quantities): emit('shipment_lines',[shipment,lid,qty])
    history.append((ship_at,'SHIPPED'))
    if delivered:
     history.append((delivery,'DELIVERED'))
     if rng.random() < .065:
      return_at = delivery + timedelta(days=rng.randrange(2,22))
      if return_at <= AS_OF:
       refund_at = return_at
       refund_selection = list(range(len(basket))) if rng.random() < .25 else [rng.randrange(len(basket))]
       refund_reason = rng.choice(['Changed mind','Defective item','Not suitable'])
       history.append((return_at,'RETURNED' if len(refund_selection) == len(basket) else 'PARTIALLY_RETURNED'))
  if refund_at:
   rid = f'REF-{oi:06d}'
   amount = sum(nets[j]+taxes[j] for j in refund_selection)
   assert 0 < amount <= total
   emit('refunds',[rid,oid,money(amount),refund_reason,stamp(refund_at),payment_id])
   for j in refund_selection:
    emit('refund_lines',[rid,line_ids[j],quantities[j],money(nets[j]),money(taxes[j])])
   audit('refund',rid,'CREATE','refund_amount',None,money(amount),refund_at,'refund_service')
  status = history[-1][1]
  emit('orders',[oid,cid,stamp(at),status,money(sum(gross)),money(sum(item_discounts)+coupon_total),money(sum(taxes)),money(total),stamp(at),stamp(history[-1][0]),'USD',coupon,f'{tax/10000:.4f}',dataset_id])
  old = None
  for when,new in history:
   audit('order',oid,'CREATE' if old is None else 'UPDATE','status',old,new,when,actor if old is None else 'order_service')
   old = new
  if paid: existing.update(p[1] for p in basket)
  status_counts[status] += 1
 conn.commit()
 counts = validate(conn)
 files = {}
 for table,header in HEADERS.items():
  path = output / f'{table}.tsv'
  with path.open('w',encoding='utf-8',newline='') as stream:
   writer = csv.writer(stream,delimiter='\t',lineterminator='\n',quoting=csv.QUOTE_NONE)
   writer.writerow(header.split())
   for row in conn.execute(f'SELECT * FROM {table}'):
    writer.writerow(['\\N' if v is None else v for v in row])
  files[table] = hashlib.sha256(path.read_bytes()).hexdigest()
 manifest = dict(dataset_id=dataset_id,seed=seed,as_of=stamp(AS_OF),orders=count,counts=counts,status_counts=dict(status_counts),files=files,validation='passed')
 (output/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
 conn.close()
 print(json.dumps(manifest,indent=2))

def validate(conn):
 from decimal import Decimal
 conn.create_function('cents',1,lambda v: int(Decimal(str(v))*100))
 checks = {
 'orphan order lines': 'SELECT count(*) FROM order_lines l LEFT JOIN orders o ON o.order_id=l.order_id WHERE o.order_id IS NULL',
 'line tax rounding': 'SELECT count(*) FROM order_lines l JOIN orders o ON o.order_id=l.order_id WHERE cents(l.tax_amount) != CAST((cents(l.line_total)*CAST(round(o.tax_rate*10000) AS INTEGER)*2+10000)/20000 AS INTEGER)',
 'customer chronology': 'SELECT count(*) FROM orders o LEFT JOIN customers c ON c.customer_id=o.customer_id WHERE c.customer_id IS NULL OR o.order_date<c.created_at',
 'product availability': 'SELECT count(*) FROM order_lines l LEFT JOIN products p ON p.product_id=l.product_id JOIN orders o ON o.order_id=l.order_id WHERE p.product_id IS NULL OR o.order_date<p.available_from',
 'line arithmetic': 'SELECT count(*) FROM order_lines WHERE cents(line_total) != quantity*cents(unit_price)-cents(discount_amount)-cents(order_discount_amount) OR cents(line_total)<0',
 'order arithmetic': 'SELECT count(*) FROM orders WHERE cents(total_amount)!=cents(subtotal)-cents(discount_amount)+cents(tax_amount)',
 'line reconciliation': '''SELECT count(*) FROM orders o LEFT JOIN (SELECT order_id, sum(quantity*cents(unit_price)) gross,sum(cents(discount_amount)+cents(order_discount_amount)) discount,sum(cents(tax_amount)) tax,sum(cents(line_total)+cents(tax_amount)) total FROM order_lines GROUP BY order_id) l ON o.order_id=l.order_id WHERE l.order_id IS NULL OR cents(o.subtotal)!=l.gross OR cents(o.discount_amount)!=l.discount OR cents(o.tax_amount)!=l.tax OR cents(o.total_amount)!=l.total''',
 'captured payment reconciliation': '''SELECT count(*) FROM orders o LEFT JOIN (SELECT order_id,sum(cents(amount)) amount FROM payments WHERE payment_status='CAPTURED' GROUP BY order_id) p ON p.order_id=o.order_id WHERE (o.status NOT IN ('CANCELLED','PENDING_PAYMENT') AND coalesce(p.amount,0)!=cents(o.total_amount)) OR coalesce(p.amount,0)>cents(o.total_amount)''',
 'payment chronology': 'SELECT count(*) FROM payments p LEFT JOIN orders o ON o.order_id=p.order_id WHERE o.order_id IS NULL OR p.payment_date<o.order_date',
 'refund payment linkage': "SELECT count(*) FROM refunds r LEFT JOIN payments p ON p.payment_id=r.payment_id WHERE p.payment_id IS NULL OR p.order_id!=r.order_id OR p.payment_status!='CAPTURED' OR r.refund_date<p.payment_date OR cents(r.refund_amount)>cents(p.amount)",
 'refund line reconciliation': '''SELECT count(*) FROM refunds r LEFT JOIN (SELECT refund_id,sum(cents(merchandise_amount)+cents(tax_amount)) amount FROM refund_lines GROUP BY refund_id) l ON l.refund_id=r.refund_id WHERE l.refund_id IS NULL OR l.amount!=cents(r.refund_amount)''',
 'return linkage and limits': '''SELECT count(*) FROM refund_lines r LEFT JOIN order_lines l ON l.order_line_id=r.order_line_id JOIN refunds f ON f.refund_id=r.refund_id WHERE l.order_line_id IS NULL OR l.order_id!=f.order_id OR r.quantity>l.quantity OR cents(r.merchandise_amount)>cents(l.line_total) OR cents(r.tax_amount)>cents(l.tax_amount)''',
 'shipment linkage': '''SELECT count(*) FROM shipment_lines sl LEFT JOIN order_lines l ON l.order_line_id=sl.order_line_id JOIN shipments s ON s.shipment_id=sl.shipment_id WHERE l.order_line_id IS NULL OR l.order_id!=s.order_id OR sl.quantity!=l.quantity''',
 'shipping chronology': '''SELECT count(*) FROM shipments s LEFT JOIN payments p ON p.order_id=s.order_id AND p.payment_status='CAPTURED' WHERE p.payment_id IS NULL OR s.shipped_at<p.payment_date OR (s.delivered_at IS NOT NULL AND s.delivered_at<s.shipped_at)''',
 'return eligibility': "SELECT count(*) FROM refunds r LEFT JOIN shipments s ON s.order_id=r.order_id WHERE r.refund_reason!='Cancelled before shipment' AND (s.delivered_at IS NULL OR r.refund_date<s.delivered_at)",
 'current status': '''SELECT count(*) FROM orders o LEFT JOIN audit_log a ON a.entity_id=o.order_id AND a.entity_type='order' AND a.timestamp=o.updated_at WHERE a.event_id IS NULL OR a.new_value!=o.status''',
 'audit chain': '''SELECT count(*) FROM (SELECT old_value,lag(new_value) OVER(PARTITION BY entity_id ORDER BY timestamp,event_id) prev FROM audit_log WHERE entity_type='order') WHERE old_value IS NOT prev''',
 }
 counts = {t:conn.execute(f'SELECT count(*) FROM {t}').fetchone()[0] for t in HEADERS}
 for t in HEADERS:
  primary = HEADERS[t].split()[0]
  if t in ('shipment_lines','refund_lines'): primary += ',order_line_id'
  duplicates = conn.execute(f'SELECT count(*) FROM (SELECT {primary} FROM {t} GROUP BY {primary} HAVING count(*)>1)').fetchone()[0]
  if duplicates: raise ValueError(f'Duplicate keys: {t}')
 # Index joins so validating the full dataset remains inexpensive.
 for t,col in [('orders','order_id'),('customers','customer_id'),('products','product_id'),('order_lines','order_id'),('order_lines','order_line_id'),('payments','order_id'),('payments','payment_id'),('refunds','refund_id'),('shipments','order_id'),('shipments','shipment_id'),('audit_log','entity_id')]:
  conn.execute(f'CREATE INDEX IF NOT EXISTS ix_{t}_{col} ON {t}({col})')
 for name,query in checks.items():
  failures = conn.execute(query).fetchone()[0]
  if failures: raise ValueError(f'{name}: {failures} violations')
 for table,column in [('orders','updated_at'),('payments','payment_date'),('refunds','refund_date'),('audit_log','timestamp'),('shipments','delivered_at')]:
  if conn.execute(f'SELECT count(*) FROM {table} WHERE {column}>?',(stamp(AS_OF),)).fetchone()[0]:
   raise ValueError(f'Future events in {table}')
 print(f'Validation passed: {len(checks)} relationship checks, unique keys, as-of checks.',flush=True)
 return counts

if __name__ == '__main__':
 parser = argparse.ArgumentParser()
 parser.add_argument('--orders',type=int,default=100000)
 parser.add_argument('--seed',type=int,default=42)
 parser.add_argument('--output',type=Path,required=True)
 args = parser.parse_args()
 if args.orders < 100: parser.error('Use at least 100 orders')
 generate(args.output,args.orders,args.seed)
