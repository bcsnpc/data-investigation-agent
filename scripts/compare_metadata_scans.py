"""Compare refactored discovery with a retained baseline scan, independent of timestamps."""
import argparse
from contextlib import closing
import json
import sqlite3
from pathlib import Path
from metadata_config import ROOT


def compare(database, baseline, current):
    with closing(sqlite3.connect(database)) as db:
        def assets(scan):
            state = db.execute('SELECT status FROM scans WHERE id=?',(scan,)).fetchone()
            if not state or state[0] != 'COMPLETE':
                raise ValueError('Parity requires two complete scans')
            return {aid:(parent,kind,name,json.loads(data)) for aid,parent,kind,name,data in
                    db.execute('SELECT id,parent_id,kind,name,metadata FROM assets WHERE scan_id=?',(scan,))}
        before, after = assets(baseline), assets(current)
    added, removed = sorted(after.keys()-before.keys()), sorted(before.keys()-after.keys())
    changed=[]
    for aid in before.keys() & after.keys():
        old,new=before[aid],after[aid]
        if old[1]=='SqlDatabase' and new[1]=='SqlDatabase':
            old[3].pop('captured_at',None); new[3].pop('captured_at',None)
        if old != new: changed.append(aid)
    return {'status':'PASS' if not (added or removed or changed) else 'FAIL',
            'baseline':baseline,'current':current,'asset_count':len(after),
            'added':added,'removed':removed,'changed':sorted(changed)}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database',type=Path,default=ROOT/'.local/metadata/inventory.sqlite')
    parser.add_argument('--baseline',required=True)
    parser.add_argument('--current',required=True)
    args=parser.parse_args()
    result=compare(args.database,args.baseline,args.current)
    (args.database.parent/'parity.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['status']=='PASS' else 1)
