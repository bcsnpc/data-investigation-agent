"""Bind a planned Bronze publication to an exact verified source manifest."""
import json
from pathlib import Path
from uuid import UUID
from source_snapshot import verify, TABLES


def plan(folder, manifest_sha256, workspace, lakehouse):
    source = verify(folder, manifest_sha256)
    workspace, lakehouse = str(UUID(workspace)), str(UUID(lakehouse))
    manifest = json.loads((Path(folder)/'manifest.json').read_text(encoding='utf-8'))
    schema = 'snapshot_'+source['snapshot_id'].replace('-', '')
    return {'format_version':1, 'status':'PLANNED', 'source_snapshot_id':source['snapshot_id'],
            'source_manifest_sha256':source['manifest_sha256'],
            'tables':[{'source_table':t['name'], 'source_file':t['file'], 'source_sha256':t['sha256'],
                       'source_schema_sha256':t['schema_sha256'], 'expected_rows':t['rows'],
                       'destination':f"abfss://{workspace}@onelake.dfs.fabric.microsoft.com/{lakehouse}/Tables/{schema}/{t['name']}"}
                      for t in manifest['tables']],
            'requirements':['Verify source hashes before reading', 'Create isolated tables; never overwrite an existing snapshot',
                            'Record Delta table UUID, version, schema and content reconciliation',
                            'Publish COMPLETE receipt only after every table passes',
                            'Downstream reads must pin the recorded versions and verify table UUIDs']}


def validate_receipt(publication_plan, receipt):
    """Validate receipt structure, not remote Delta existence or content."""
    if publication_plan['status'] != 'PLANNED' or receipt.get('status') != 'COMPLETE':
        raise ValueError('Complete publication receipt required')
    for key in ('source_snapshot_id','source_manifest_sha256'):
        if receipt.get(key) != publication_plan[key]:
            raise ValueError('Source reference changed')
    expected = {t['source_table']:t for t in publication_plan['tables']}
    rows = receipt.get('tables', [])
    if set(expected) != TABLES or len(rows) != len(TABLES) or {r['source_table'] for r in rows} != TABLES:
        raise ValueError('Incomplete or duplicate publication mapping')
    identities = set()
    for row in rows:
        source = expected[row['source_table']]
        for key in ('destination','source_sha256','source_schema_sha256'):
            if row.get(key) != source[key]:
                raise ValueError('Publication mapping differs from plan')
        if type(row.get('rows')) is not int or row['rows'] != source['expected_rows']:
            raise ValueError('Publication count differs from extraction')
        identity = str(UUID(row['delta_table_id']))
        if identity in identities:
            raise ValueError('Reused table identity')
        identities.add(identity)
        if type(row.get('delta_version')) is not int or row['delta_version'] < 0:
            raise ValueError('Pinned nonnegative Delta version required')
        if row.get('content_reconciled') is not True:
            raise ValueError('Content reconciliation missing')
    return {'status':'STRUCTURALLY_VALID', 'snapshot_proof':False,
            'remaining':'Trusted publication execution and independent pinned Delta reads required'}
