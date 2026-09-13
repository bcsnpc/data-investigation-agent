"""Supplement a captured graph with verified SQL-snapshot-to-Bronze mappings."""
import argparse
import json
from pathlib import Path
from urllib.parse import quote
from metadata_config import ROOT,load_config
from silver_snapshot_input import build


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--evidence',type=Path,required=True)
    args=parser.parse_args()
    estate=json.loads((ROOT/'infra/fabric/environment.json').read_text())
    config=load_config(ROOT/'infra/metadata/development.json')
    snapshot=estate['snapshot_bronze']
    binding=build(config['storage']['database'],snapshot['source_snapshot_id'],snapshot['verification_id'],
                  estate['workspace_id'],estate['bronze_lakehouse_id'])
    manifest=json.loads((ROOT/'.local/source-snapshots'/binding['source_snapshot_id']/'manifest.json').read_text())
    source=manifest['source']
    evidence=json.loads(args.evidence.read_text())
    evidence['snapshot_mappings']=[{'sql_parent':'sql://'+source['server']+'/'+source['database'],
        'sql_table':source['schema']+'.'+row['source_table'],'destination':row['destination'],
        'source_snapshot_id':binding['source_snapshot_id'],'source_manifest_sha256':binding['source_manifest_sha256'],
        'bronze_verification_id':binding['bronze_verification_id'],'bronze_proof_sha256':binding['bronze_proof_sha256'],
        'delta_table_id':row['delta_table_id'],'delta_version':row['delta_version'],
        'scope':'Verified publication dependency at recorded version; not a claim about arbitrary current contents'} for row in binding['tables']]
    args.evidence.write_text(json.dumps(evidence,indent=2),encoding='utf-8')
    print('Recorded verified snapshot mappings:',len(evidence['snapshot_mappings']))
