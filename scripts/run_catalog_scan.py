"""Run at most one queued metadata scan using an operator-configured connection."""
import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile

from investigator.onboarding import ModelStore
from investigator.scans import ScanQueue
from metadata_config import load_config, ROOT


def connection(config_path):
    config=load_config(config_path)
    return config,hashlib.sha256(Path(config_path).read_bytes()).hexdigest()


def collector(config_path, inventory, expected_profile=None):
    # An isolated receipt binds completion to this process, never latest scan.
    # The collector's existing read-only connector policy remains in force.
    def collect():
        raw=Path(config_path).read_bytes()
        if expected_profile is not None and hashlib.sha256(raw).hexdigest()!=expected_profile:
            from investigator.onboarding import Conflict
            raise Conflict('Connection profile changed')
        with tempfile.TemporaryDirectory(prefix='catalog-scan-') as folder:
            summary=Path(folder)/'receipt.json'
            frozen_config=Path(folder)/'config.json'
            frozen_config.write_bytes(raw)
            completed=subprocess.run([sys.executable,str(ROOT/'scripts/metadata_inventory.py'),
                '--config',str(frozen_config),'--database',str(inventory),'--summary',str(summary)],
                stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=900)
            receipt=json.loads(summary.read_text())
        with closing(sqlite3.connect(Path(inventory).resolve().as_uri()+'?mode=ro',uri=True)) as db:
            row=db.execute('SELECT id,status FROM scans WHERE id=?',(receipt['scan_id'],)).fetchone()
            if not row or row[1]!=receipt['status']:raise ValueError('Collector receipt differs')
            observations=db.execute("SELECT capability,status FROM observations WHERE scan_id=? AND asset_id='scan'",(row[0],)).fetchall()
        return {'scan_id':row[0],'status':row[1], 'connections':dict(observations),'collector_exit':completed.returncode}
    return collect


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True)
    parser.add_argument('--database',type=Path,required=True)
    parser.add_argument('--environment',required=True)
    args=parser.parse_args()
    config,profile=connection(args.config)
    store=ModelStore(args.database,config['storage']['database'],args.environment)
    queue=ScanQueue(store,config['fabric']['workspace_id'],profile)
    print(json.dumps(queue.run_one(collector(args.config,store.inventory,profile))))
