"""Publisher/evaluator tooling, excluded from investigator inputs and imports.

Creates new isolated assets only. Never updates existing application tables.
Run only after challenge_freeze verification and the pre-publication scan.
"""
import argparse
import base64
import json
from pathlib import Path
import random
import subprocess
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from publish_import_fixture import Publisher, Journal, transport
from challenge_freeze import verify


def write(path, body):
    path.write_text(json.dumps(body, indent=2), encoding='utf-8')


def generate(folder):
    rng = random.Random(int.from_bytes(__import__('secrets').token_bytes(8)))
    suffix = uuid4().hex[:6]
    def table(name, columns, rows):
        return {'name': name + '_' + suffix, 'columns': columns, 'rows': rows}
    warehouses = [[1, 'North'], [2, 'Central'], [3, 'Coastal']]
    products = [[i, 'Component ' + str(i)] for i in range(1, 9)]
    rates = [[i, 1, rng.randint(2, 9)] for i in range(1, 9)]
    duplicate = rng.randint(1, 8)
    rates.append([duplicate, 2, rng.randint(10, 15)])
    movements = [[i, rng.randint(1, 3), rng.randint(1, 8), rng.randint(2, 40),
                  '2026-09-' + str(rng.randint(10, 18)), 'RECEIPT' if i % 4 else 'ISSUE'] for i in range(1, 361)]
    orders = [[i, rng.randint(1, 3), rng.randint(1, 8), rng.randint(30, 100), rng.choice(['OPEN', 'RECEIVED'])] for i in range(1, 61)]
    adjustments = [[i, rng.randint(1, 360), rng.randint(-4, 4), rng.choice(['COUNT', 'DAMAGE', 'Z83'])] for i in range(1, 31)]
    tables = [table('warehouse_locations', [['warehouse_id','int'],['warehouse_name','string']], warehouses),
              table('inventory_products', [['product_id','int'],['product_name','string']], products),
              table('product_rates', [['product_id','int'],['rate_version','int'],['unit_cost','int']], rates),
              table('stock_movements', [['movement_id','int'],['warehouse_id','int'],['product_id','int'],['units','int'],['event_day','string'],['movement_type','string']], movements),
              table('purchase_orders', [['purchase_order_id','int'],['warehouse_id','int'],['product_id','int'],['ordered_units','int'],['status','string']], orders),
              table('inventory_adjustments', [['adjustment_id','int'],['movement_id','int'],['units','int'],['reason_code','string']], adjustments)]
    by_name={t['name'].rsplit('_',1)[0]:t for t in tables}
    for t in tables:
        t['primary_key']=[t['columns'][0][0]]
        t['foreign_keys']=[]
    by_name['product_rates']['primary_key']=['product_id','rate_version']
    for source,column,target in [('product_rates','product_id','inventory_products'),
                                 ('stock_movements','product_id','inventory_products'),
                                 ('stock_movements','warehouse_id','warehouse_locations'),
                                 ('purchase_orders','product_id','inventory_products'),
                                 ('purchase_orders','warehouse_id','warehouse_locations'),
                                 ('inventory_adjustments','movement_id','stock_movements')]:
        by_name[source]['foreign_keys'].append({'column':column,'table':by_name[target]['name'],'target_column':column})
    write(folder / 'publisher-input.json', {'suffix':suffix, 'tables':tables})
    # Never exposed to discovery, planner, model descriptions or runtime config.
    write(folder / 'evaluator-private.json', {'duplicate_product':duplicate,
          'source_units':sum(r[3] for r in movements), 'source_rows':len(movements),
          'gold_rows':len(movements)+sum(r[2]==duplicate for r in movements),
          'gold_units':sum(r[3]*(2 if r[2]==duplicate else 1) for r in movements)})


def notebook(snapshot, workspace, lakes):
    # Source rows are the SQL readback, not separately generated Fabric data.
    source = 'import json\nfrom pyspark.sql import functions as F\n'
    source += 'source_rows = json.loads(' + repr(json.dumps(snapshot['tables'])) + ')\n'
    paths = {k: f'abfss://{workspace}@onelake.dfs.fabric.microsoft.com/{v}/Tables/' for k,v in lakes.items()}
    source += 'paths = ' + repr(paths) + '\n'
    source += '''for table in source_rows:
    schema = ', '.join(name+' '+('long' if kind=='int' else 'string') for name,kind in table['columns'])
    data = spark.createDataFrame(table['rows'], schema)
    data.write.format('delta').mode('errorifexists').save(paths['bronze']+table['name'])
    spark.read.format('delta').load(paths['bronze']+table['name']).dropDuplicates().write.format('delta').mode('errorifexists').save(paths['silver']+table['name'])
'''
    names = {t['name'].rsplit('_',1)[0]:t['name'] for t in snapshot['tables']}
    source += "movements = spark.read.format('delta').load(paths['silver']+"+repr(names['stock_movements'])+")\n"
    source += "rates = spark.read.format('delta').load(paths['silver']+"+repr(names['product_rates'])+")\n"
    source += "valued = movements.join(rates, ['product_id'], 'left').withColumn('movement_value', F.col('units')*F.col('unit_cost'))\n"
    source += "valued.write.format('delta').mode('errorifexists').save(paths['gold']+'movement_values')\n"
    for key in ('warehouse_locations','inventory_products','purchase_orders','inventory_adjustments'):
        source += "spark.read.format('delta').load(paths['silver']+"+repr(names[key])+").write.format('delta').mode('errorifexists').save(paths['gold']+"+repr(key)+")\n"
    return {'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'name':'synapse_pyspark','display_name':'Synapse PySpark'},
        'language_info':{'name':'python'},'dependencies':{'lakehouse':{'default_lakehouse':lakes['gold'], 'default_lakehouse_workspace_id':workspace}}},
        'cells':[{'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],'source':source.splitlines(keepends=True)}]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['generate','sql','fabric','run','status'])
    parser.add_argument('--folder',type=Path,required=True)
    args=parser.parse_args();folder=args.folder
    verify(json.loads((folder/'freeze.json').read_text()))
    if args.action=='generate':
        if (folder/'publisher-input.json').exists():raise ValueError('Variant already generated')
        generate(folder);return
    if args.action=='sql':
        result=subprocess.run(['powershell','-NoProfile','-File',str(Path(__file__).with_name('publish_sql.ps1')),
                               '-Folder',str(folder.resolve())],capture_output=True,text=True,timeout=150)
        if result.returncode:raise RuntimeError('SQL publication failed; inspect publisher-sql-status.json before retry')
        print('SQL publication/readback completed');return
    config=json.loads((folder/'config.json').read_text());workspace=config['fabric']['workspace_id']
    publisher=Publisher(Journal(folder/'publisher.sqlite'),transport)
    if args.action=='fabric':
        snapshot=json.loads((folder/'sql-readback.json').read_text(encoding='utf-8-sig'))
        suffix=snapshot['suffix'];lakes={}
        for layer in ('bronze','silver','gold'):
            item=publisher.item(publisher.post(layer,f'workspaces/{workspace}/lakehouses',{'displayName':'warehouse_'+layer+'_'+suffix}))
            lakes[layer]=item['id'];write(folder/'lakehouses.json',lakes)
        nb=notebook(snapshot,workspace,lakes)
        definition={'format':'ipynb','parts':[{'path':'notebook-content.ipynb','payloadType':'InlineBase64','payload':base64.b64encode(json.dumps(nb).encode()).decode()}]}
        item=publisher.item(publisher.post('notebook',f'workspaces/{workspace}/notebooks',{'displayName':'Warehouse valuation '+suffix,'definition':definition}))
        write(folder/'notebook.json',item);print('Created lakehouses and notebook');return
    item=json.loads((folder/'notebook.json').read_text())
    if args.action=='run':
        result=publisher.post('notebook-run',f"workspaces/{workspace}/items/{item['id']}/jobs/instances?jobType=RunNotebook",{})
        write(folder/'notebook-job.json',result);print('Notebook job submitted');return
    response=json.loads((folder/'notebook-job.json').read_text());headers={k.lower():v for k,v in response['headers'].items()}
    from urllib.parse import urlparse
    location=urlparse(headers['location']);prefix='/v1/workspaces/'+workspace+'/items/'+item['id']+'/jobs/instances/'
    if location.hostname!='api.fabric.microsoft.com' or not location.path.startswith(prefix):raise ValueError('Unexpected job location')
    result=publisher.call(location.path.removeprefix('/v1/'))
    write(folder/'notebook-status.json',result);print(json.dumps(result['text']))


if __name__=='__main__':main()
