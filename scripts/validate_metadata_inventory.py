"""Validate the latest live inventory against the deployed POC contract."""
import json
import sqlite3
from pathlib import Path
from fabric_api import ROOT


def validate():
    summary = json.loads((ROOT / '.local/metadata/latest.json').read_text())
    assert summary['status'] == 'COMPLETE', summary
    with sqlite3.connect(ROOT / '.local/metadata/inventory.sqlite') as db:
        rows = db.execute('SELECT id,parent_id,kind,name,metadata FROM assets WHERE scan_id=?', (summary['scan_id'],)).fetchall()
        observations = db.execute('SELECT capability,status FROM observations WHERE scan_id=?', (summary['scan_id'],)).fetchall()
    ids = {r[0] for r in rows}
    assert all(parent is None or parent in ids for _,parent,*_ in rows), 'Orphaned metadata child'
    by_kind = {}
    for aid,parent,kind,name,metadata in rows:
        by_kind.setdefault(kind, []).append((aid, parent, name, json.loads(metadata)))
    for kind,count in {'LakehouseTable':29, 'Measure':25, 'SemanticRelationship':5, 'SemanticTable':6, 'ReportPage':4, 'ReportVisual':45}.items():
        assert len(by_kind.get(kind, [])) == count, (kind,len(by_kind.get(kind, [])))
    source_objects = by_kind['SqlObject']
    assert sum(len(x[3]['foreign_keys']) for x in source_objects) == 11
    assert all(x[3]['columns'] for x in source_objects if x[3]['type_desc'] == 'USER_TABLE')
    config = json.loads((ROOT / 'infra/fabric/environment.json').read_text())
    for field,count in [('bronze_lakehouse_id',10),('silver_lakehouse_id',10),('gold_lakehouse_id',9)]:
        assert sum(parent.endswith('/'+config[field]) for _,parent,_,_ in by_kind['LakehouseTable']) == count, field
    expected_model = json.loads((ROOT / 'infra/powerbi/OrderOps.SemanticModel/model.bim').read_text())['model']
    expected = {m['name']:m['expression'] for t in expected_model['tables'] for m in t.get('measures',[])}
    actual = {name:data['expression'] for _,_,name,data in by_kind['Measure']}
    assert actual == expected, 'Live DAX differs from version-controlled deployment'
    assert all(status != 'UNAVAILABLE' for _,status in observations)
    assert any(cap=='refresh_history' and status=='AVAILABLE' for cap,status in observations)
    result = {'scan_id':summary['scan_id'], 'status':'PASS', 'asset_count':len(rows),
              'checks':['parent references','29 lakehouse tables and layer counts','25 deployed DAX expressions',
                        'semantic/report counts','11 source foreign keys','capability availability','refresh history']}
    (ROOT / '.local/metadata/validation.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    validate()
