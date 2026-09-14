"""Bind a native page requirement to the same retained scan as ticket lineage."""
from contextlib import closing
from pathlib import Path
import sqlite3
from report_definition_evidence import bundle
from report_drillthrough_context import assess


def check(database,lineage,report,page,order_id):
    with closing(sqlite3.connect(Path(database).resolve().as_uri()+'?mode=ro',uri=True)) as db:
        row=db.execute('SELECT scan_id FROM lineage_runs WHERE id=?',(lineage,)).fetchone()
    if row is None:raise ValueError('Ticket lineage unavailable')
    return assess(bundle(database,row[0],report),page,order_id)


def pages(database,lineage):
    """Retained page choices; availability is not supported-filter certification."""
    import json
    if lineage is None:return []
    with closing(sqlite3.connect(Path(database).resolve().as_uri()+'?mode=ro',uri=True)) as db:
        if not db.execute("SELECT 1 FROM sqlite_master WHERE name='lineage_runs'").fetchone():return []
        rows=db.execute("SELECT r.id,r.name,p.metadata FROM lineage_runs l JOIN assets p ON p.scan_id=l.scan_id JOIN assets r ON r.scan_id=p.scan_id AND r.id=p.parent_id WHERE l.id=? AND p.kind='ReportPage' AND r.kind='Report' ORDER BY r.name,p.name",(lineage,)).fetchall()
    return [{'report_id':rid,'report_name':name,'path':'definition/pages/'+m['name']+'/page.json','label':m.get('displayName',m['name'])}
            for rid,name,raw in rows for m in [json.loads(raw)] if isinstance(m.get('name'),str)]


def slicers(database,lineage,report,page,selections=None):
    from report_slicer_context import assess as assess_slicers
    with closing(sqlite3.connect(Path(database).resolve().as_uri()+'?mode=ro',uri=True)) as db:
        row=db.execute('SELECT scan_id FROM lineage_runs WHERE id=?',(lineage,)).fetchone()
    if row is None:raise ValueError('Ticket lineage unavailable')
    return assess_slicers(bundle(database,row[0],report),page,selections)
