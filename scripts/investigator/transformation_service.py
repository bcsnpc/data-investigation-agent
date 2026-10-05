"""One fetched unit, static/model proposals, verification, immutable lineage.

Source transport and data execution are supplied by the installed adapter; the
service knows no estate's names, expected figures or required layer order.
"""
import copy
from .code_sources import read
from .transformation_reader import propose
from .lineage_binding import verify,require_declared_approval


def run(*,source,path,meter,root,schemas,boundary,item,target_table,layers,
        context,cell,precision,compiler,execute,ledger,model=None,
        git_fetch=None,item_fetch=None,declared=False):
    unit,receipt=read(source,path,meter=meter,root=root,git_fetch=git_fetch,item_fetch=item_fetch)
    extraction=propose(unit,schemas=schemas,boundary=boundary,item=item,
        target_table=target_table,layers=layers,model=model)
    result={'code_receipt':receipt,'extraction':extraction,'verifications':[]}
    # Retain each attempt as it completes, including failures and refusals.
    # Do not claim a whole boundary is verified because one column agreed.
    for proposal in extraction['proposals']:
        verification=verify(proposal,context=context,cell=cell,precision=precision,
                            compiler=compiler,execute=execute)
        ledger.append(verification);result['verifications'].append(verification)
    if declared:
        if not result['verifications']:raise ValueError('Declared binding produced no verifiable proposal')
        require_declared_approval(result['verifications'])
    return result


def select(*,declared,inferred,current_hashes,boundary,target_column,context,cell,precision):
    """Declared first; a sampled binding cannot be reused for a different cell.

    STALE entries remain in evidence. No missing hash is treated as current, and
    no confidence score changes eligibility. The ledger view supplies freshness.
    """
    from .lineage_binding import validate
    for rows,provenance in ((declared,'DECLARED_BY_CONFIGURATION'),(inferred,'INFERRED_FROM_CODE')):
        candidates=[];excluded=[]
        # A later failed verification supersedes an earlier success for the
        # same proposal and sample. History is retained, not cherry-picked.
        from .lineage_binding import seal
        latest={seal({k:r[k] for k in ('proposal','context','cell','precision')}):r for r in rows}
        for row in latest.values():
            p=validate(row['proposal'])
            if p['boundary']!=boundary or p['target']['column']!=target_column:continue
            location=p['location'];current=current_hashes.get((location['item'],location['path']))
            status=row['status'] if current==location['content_hash'] else 'STALE'
            if status!='VERIFIED' or any(row.get(k)!=v for k,v in
                    (('context',context),('cell',cell),('precision',precision))):
                excluded.append({'location':copy.deepcopy(location),'status':status,'reason':
                    'Code is changed or unavailable.' if status=='STALE' else 'Verification is absent, failed or belongs to a different sample.'})
                continue
            candidates.append(row)
        # Multiple identical verifications are history, not ambiguity. Distinct
        # expressions for the same boundary cannot silently choose a winner.
        unique={seal(c['proposal']):c for c in candidates}
        if len(unique)>1:return {'status':'AMBIGUOUS','reason':'Multiple verified code bindings for the selected quantity','excluded':excluded}
        if unique:return {'status':'RESOLVED','provenance':provenance,
                          'verification':copy.deepcopy(next(iter(unique.values()))),'excluded':excluded}
        if rows is declared and any(validate(r['proposal'])['boundary']==boundary for r in rows):
            return {'status':'UNBOUND','reason':'Declared binding lacks current matching verification','excluded':excluded}
    return {'status':'UNBOUND','reason':'Neither a declared nor a current verified inferred binding matches the selected quantity and scope.'}
