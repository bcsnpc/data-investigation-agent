"""Read-only ledger export for the one-time PostgreSQL cutover.

Stop admissions and drain workers first. Never use exported files as replacement
live ledgers. Output includes original rows and approved policies; keep it local.
"""
import argparse
from contextlib import closing
import json
from pathlib import Path
import sqlite3
from investigator.shared_state import sha
from investigator.shared_usage import export_usage,usage_totals


def export_spend(db,*,margin_microdollars,account='model-microdollars'):
    ceiling=db.execute('SELECT ceiling FROM spend_policy WHERE id=1').fetchone()[0]
    cursor=db.execute('SELECT id,created,reserved,charged,status,input_tokens,output_tokens FROM model_spend ORDER BY id')
    columns=[d[0] for d in cursor.description];rows=[list(r) for r in cursor]
    if any(r[4]=='RESERVED' for r in rows):raise ValueError('SPEND_IMPORT_REQUIRES_DRAINED_WORKERS')
    if type(ceiling)is not int or type(margin_microdollars)is not int or not 0<=margin_microdollars<ceiling:
        raise ValueError('EXACT_APPROVED_SPEND_POLICY_REQUIRED')
    if any(type(r[3])is not int or r[3]<0 for r in rows):raise ValueError('EXACT_SPEND_CHARGES_REQUIRED')
    models=[list(r) for r in db.execute('SELECT id,model FROM model_spend_deployments ORDER BY id')]
    return {'version':'shared-account-import-v1','accounts':[{'identity':account,'unit':'MICRODOLLARS',
            'ceiling':ceiling,'protected':margin_microdollars,'opening':sum(r[3] for r in rows),
            'violated':any(r[4]=='VIOLATION' for r in rows)}],
            'original_tables':{'model_spend':{'columns':columns,'rows':rows},'model_spend_deployments':models}}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog',required=True)
    parser.add_argument('--spend-db',required=True)
    parser.add_argument('--policy',required=True,help='Local JSON with policy and round_policy objects')
    parser.add_argument('--margin-microdollars',type=int,required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args(argv)
    policy=json.loads(Path(args.policy).read_text(encoding='utf-8-sig'))
    # Acquire both SQLite read snapshots before copying. In rollback-journal mode
    # concurrent writers cannot commit during the extraction. In WAL mode each
    # snapshot is still consistent; drained admissions are the required cutover.
    with closing(sqlite3.connect(Path(args.catalog).resolve().as_uri()+'?mode=ro',uri=True)) as catalog, closing(sqlite3.connect(Path(args.spend_db).resolve().as_uri()+'?mode=ro',uri=True)) as spend:
        catalog.execute('BEGIN');spend.execute('BEGIN')
        usage=export_usage(catalog,policy['policy']['environment'],policy['policy'],policy['round_policy'])
        money=export_spend(spend,margin_microdollars=args.margin_microdollars)
    output=Path(args.output);output.mkdir(parents=True,exist_ok=True)
    for name,source in [('usage',usage),('spend',money)]:
        target=output/(name+'.json')
        if target.exists():raise ValueError('EXPORT_ALREADY_EXISTS: use a new capture directory')
        target.write_text(json.dumps(source,indent=2)+'\n',encoding='utf8')
    proof={'usage_sha256':sha(usage),'spend_sha256':sha(money),'usage_totals':usage_totals(usage),
           'spend_accounts':money['accounts'],'legacy_sources_unchanged':True}
    (output/'before.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf8')
    print(json.dumps(proof,indent=2))


if __name__=='__main__':main()
