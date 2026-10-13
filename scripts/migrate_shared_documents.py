"""Export existing catalog/case state read-only and plan/apply its shared migration."""
import argparse
from contextlib import closing
import json
from pathlib import Path
import sqlite3
from uuid import uuid4
from investigator.shared_state import SharedState,configured_state,sha
from investigator.shared_document_migration import export_documents,import_documents,validate_bundle


def rehearsal(source,identity):
    # Exercise the same importer with an in-memory offline repository. Raw ticket
    # text never goes through an extra temporary SQLite disk file during planning.
    uri='file:migration-plan-'+uuid4().hex+'?mode=memory&cache=shared'
    with closing(sqlite3.connect(uri,uri=True)):
        state=SharedState(lambda:sqlite3.connect(uri,uri=True),backend='sqlite',mode='offline');state.migrate()
        return import_documents(state,identity,source)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);commands=p.add_subparsers(dest='command',required=True)
    export=commands.add_parser('export')
    export.add_argument('--catalog',required=True);export.add_argument('--environment',required=True)
    export.add_argument('--readiness',action='append',default=[],help='Retained local certificate JSON, repeat for each certificate')
    export.add_argument('--tape-class',required=True,choices=['EXACT'],help='Projected shared persistence remains unsupported; never silently export as exact')
    export.add_argument('--output',required=True)
    plan=commands.add_parser('migrate')
    plan.add_argument('--source',required=True);plan.add_argument('--expected-sha256',required=True)
    plan.add_argument('--migration-id',required=True);plan.add_argument('--report',required=True)
    plan.add_argument('--apply',action='store_true',help='Default is offline plan only')
    args=p.parse_args(argv)
    destination=Path(args.output if args.command=='export' else args.report)
    if destination.exists():p.error('Output exists; preserve it and choose a new path')
    destination.parent.mkdir(parents=True,exist_ok=True)
    if args.command=='export':
        certificates=[json.loads(Path(path).read_text(encoding='utf-8-sig'))for path in args.readiness]
        with closing(sqlite3.connect(Path(args.catalog).resolve().as_uri()+'?mode=ro',uri=True)) as db:
            db.row_factory=sqlite3.Row;db.execute('BEGIN')
            source=export_documents(db,args.environment,certificates)
        validate_bundle(source)
        destination.write_text(json.dumps(source,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
        print(json.dumps({'status':'EXPORTED','source_sha256':sha(source),'tickets':len(source['components'][1]['rows']),
                          'models':len(source['components'][0]['models']),'certificates':len(certificates),'output':str(destination)}))
        return 0
    source=json.loads(Path(args.source).read_text(encoding='utf-8-sig'))
    if sha(source)!=args.expected_sha256:p.error('Source hash differs from the reviewed bundle')
    proof=rehearsal(source,args.migration_id)
    report={'mode':'APPLY'if args.apply else'PLAN','source_sha256':sha(source),'offline_rehearsal':proof,
            'applied_components':[],'legacy_sources_unchanged':True}
    if args.apply:
        state=configured_state()
        if state is None:p.error('Explicit PostgreSQL managed identity configuration is required')
        def checkpoint(proofs):
            report['applied_components']=proofs;report['status']='PARTIAL'
            destination.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
        try:
            report['verification']=import_documents(state,args.migration_id,source,checkpoint=checkpoint)
        except Exception as exc:
            report['status']='FAILED';report['error_type']=type(exc).__name__
            destination.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
            raise
    report['status']='APPLIED'if args.apply else'PLANNED'
    destination.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':report['status'],'source_sha256':sha(source),'report':str(destination)}))
    return 0


if __name__=='__main__':raise SystemExit(main())
