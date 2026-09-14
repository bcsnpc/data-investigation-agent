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
