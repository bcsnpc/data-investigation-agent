"""Plan-only fixture rebuild. No platform client or mutation path is imported.

Apply deliberately does not exist in this round. New tenant identities, explicit
connections and actual returned item IDs must be approved before an executor is
built; a plan cannot manufacture discovery approval or diagnostic permissions.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
import sys
if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fixture.seed import load as seed, summary, insert_plan, NOTEBOOK, ROOT
from investigator.estate_manifest import load as manifest_load

TEMPLATES = Path(__file__).with_name('templates')
TEMPLATE_NAMES = ('original-model', 'application-model', 'predicate-report', 'copy-job', 'audit-pipeline')
AUDIT_COLUMNS = ('run_id', 'pipeline_name', 'status', 'rows_read', 'rows_written',
                 'accounting_state', 'start_time_utc', 'end_time_utc', 'high_watermark')


def templates():
    result = {}
    for name in TEMPLATE_NAMES:
        path = TEMPLATES / (name + '.json')
        raw = path.read_bytes()
        document = json.loads(raw)
        if document.get('source') != 'RETAINED_COLLECTED_DEFINITION':
            raise ValueError('Rebuild template lacks recorded provenance: ' + name)
        if name == 'copy-job':
            if document['definition']['properties']['source']['type'] != 'AzureSqlTable':
                raise ValueError('Copy Job source binding changed')
        elif name == 'audit-pipeline':
            activities = document['definition']['properties']['activities']
            if [activity['type'] for activity in activities] != ['InvokeCopyJob', 'Script']:
                raise ValueError('Audit pipeline operation changed')
            text = activities[1]['typeProperties']['scripts'][0]['text']
            if 'output.rowsRead' not in text or 'output.rowsCopied' not in text or 'COUNT(' in text.upper():
                raise ValueError('Audit template must use copy output, never recount')
        else:
            parts = document['parts']
            if not parts or len({part['path'] for part in parts}) != len(parts):
                raise ValueError('Recorded definition parts are missing or repeated')
            for part in parts:
                if not re.fullmatch('[0-9a-f]{64}', part['source_sha256']):
                    raise ValueError('Recorded part lacks its source hash')
                if part['path'].endswith(('.json', '.bim', '.pbism', '.pbir', '.platform')):
                    json.loads(part['content'])
        result[name] = {'path': str(path.relative_to(TEMPLATES.parent.parent.parent)),
                        'sha256': hashlib.sha256(raw).hexdigest(), 'definition': document}
    return result


def plan(manifest):
    recorded = templates()
    literal = seed()
    steps = []
    def step(name, identity, operation, **details):
        steps.append({'order': len(steps)+1, 'name': name, 'identity': identity,
                      'operation': operation, 'apply_authorized': False, **details})
    step('validate-new-target', 'human estate owner', 'REQUIRE_NEW_ISOLATED_WORKSPACE_AND_DATABASE',
         refusal='Never overwrite current fixture; no permissions are implied by this plan.')
    for table in literal['tables']:
        step('seed-' + table['name'], 'application control writer', 'CREATE_ONLY_PARAMETERIZED_SQL',
             definition=insert_plan(table))
    step('application-source', 'application control writer', 'CREATE_NEW_COPY_SOURCE',
         base='Committed stock movement literals, 360 rows; no investigation arithmetic substituted.',
         required_parameters=['new table name', 'explicit source_modified_at_utc seed timestamp'],
         additional_columns={'source_modified_at_utc': 'datetime2(7)', 'source_row_version': 'bigint'},
         version_recipe='Ordinal 1..360 in committed seed order; no platform rowversion assumed.')
    step('original-containers', 'fixture publisher', 'CREATE_LAKEHOUSES', count=3,
         required_parameters=['new workspace', 'distinct Bronze, Silver and Gold names'])
    step('original-notebook', 'fixture publisher', 'PUBLISH_THEN_EXECUTE_COMMITTED_NOTEBOOK',
         template=str(NOTEBOOK.relative_to(ROOT)), source_sha256=literal['source_sha256'],
         substitutions='Only the three declared container paths; seed and transformations unchanged.')
    step('application-landing', 'fixture publisher', 'CREATE_SEPARATE_LAKEHOUSE',
         refusal='Application copy path cannot reuse the notebook-seeded original Bronze as source evidence.')
    step('application-connection', 'human connection owner', 'DECLARE_EXISTING_AUTHORIZED_AZURE_SQL_CONNECTION',
         required_parameters=['new application database', 'source connection ID'],
         refusal='No embedded connection string, credential creation, or guessed binding.')
    step('copy-job', 'fixture publisher', 'PUBLISH_RECORDED_COPY_JOB', template=recorded['copy-job'])
    step('audit-warehouse', 'warehouse control writer', 'CREATE_WAREHOUSE_AND_CREATE_ONLY_AUDIT_TABLE',
         table='dbo.load_run_audit', columns=list(AUDIT_COLUMNS),
         refusal='Audit must not live behind lakehouse SQL synchronization.')
    step('audit-pipeline', 'fixture publisher', 'PUBLISH_RECORDED_AUDIT_PIPELINE', template=recorded['audit-pipeline'],
         required_parameters=['Copy Job ID', 'invocation connection', 'Warehouse endpoint and item ID'])
    step('initial-copy-and-attestation', 'publisher for run; diagnostic readers for verification',
         'RUN_PIPELINE_ONCE_AND_COMPARE_OWN_ACTIVITY_OUTPUT_WITH_READER_AUDIT_ROW',
         refusal='Missing copy counters remain unavailable; never recount or estimate.')
    for name in ('original-model', 'application-model'):
        step(name, 'fixture publisher', 'PUBLISH_RECORDED_MODEL', template=recorded[name])
    step('predicate-report', 'fixture publisher', 'PUBLISH_RECORDED_REPORT', template=recorded['predicate-report'],
         retained='Pages, visuals, active slicer defaults, page/visual predicates, control page and conditional bookmark.')
    step('reader-grants', 'human estate owner then authorized control identity', 'SEPARATE_EXPLICIT_SCOPE_DECISIONS',
         grants=['SELECT on new application table only', 'SELECT on new audit table only',
                 'Read + Build on the two new models only'],
         refusal='Plan does not execute grants; before/after listings required.')
    step('fixture-states', 'local artifact writer', 'GENERATE_FRESH_STATE_DECLARATIONS',
         states=[{'id': state['id'], 'description': state['description']} for state in manifest.get('fixture_states',[])],
         refusal='State descriptions are not evidence that a mutation or restoration occurred.')
    step('new-manifest', 'local artifact writer', 'WRITE_NEW_ESTATE_MANIFEST_FROM_ACTUAL_RETURNED_IDS',
         required_parameters='All template ${ITEM_n} slots and endpoint slots; no original IDs reused.',
         template_class='PLAN_ONLY; cannot be loaded as an approved executable estate.')
    step('recollect-and-approve', 'authorized discovery operator', 'COLLECT_NEW_CONTEXT_THEN_EXPLICITLY_APPROVE',
         refusal='Old context approvals, snapshots and recorded runs remain historical and are never relabelled.')
    return {'mode':'PLAN_ONLY', 'platform_requests':0, 'mutations':0,
            'apply_implemented':False, 'seed':summary(literal), 'steps':steps}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--plan', required=True, action='store_true')
    args = parser.parse_args(argv)
    print(json.dumps(plan(manifest_load(args.manifest)), indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__': raise SystemExit(main())
