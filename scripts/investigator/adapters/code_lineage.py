"""Installed code-source freshness and sampled-lineage path qualification.

Credentials and native retrieval remain adapter-owned. This service never turns
an old retained-definition path into verified inferred lineage on its own.
"""
import copy
from pathlib import Path
from ..code_sources import read
from ..lineage_binding import Ledger,revalidate_verification
from ..lineage_runtime import qualify
from ..transformation_approval import read_approval
from ..onboarding import digest
from ..process_tape import bounded_call


class Installation:
    def __init__(self,manifest,path,root,*,git_fetch=None,item_fetch=None):
        self.manifest=copy.deepcopy(manifest);self.path=Path(path);self.root=Path(root)
        self.ledger=Ledger(self.path.with_suffix('.lineage.jsonl'))
        self.approval_path=self.path.with_suffix('.lineage-approval.json')
        self.git_fetch=git_fetch;self.item_fetch=item_fetch

    def approval(self):
        return read_approval(self.approval_path,self.manifest)

    def __call__(self,adapter,path,scope,meter,model=None):
        from ..context_search import latest
        context=latest(adapter.store) or {}
        active=[b for b in self.manifest['lineage'].get('code_locations',[]) if b['may_infer_from_code']]
        if not active:return path
        # Read the sealed approval and ledger through bounded tape boundaries.
        # Replays never re-open or rewrite the live installation evidence.
        approval=bounded_call('lineage_approval',{'manifest_hash':digest(self.manifest)},self.approval)
        sources={s['id']:s for s in self.manifest['lineage'].get('code_sources',[])}
        hashes={};receipts=[]
        for location in sorted({(x['source'],x['path']) for b in active for x in b['locations']}):
            source_id,file=location
            unit,receipt=read(sources[source_id],file,
                meter=lambda execute:meter('code_source',execute,True),root=self.root,
                git_fetch=self.git_fetch,item_fetch=self.item_fetch)
            item=source_id
            # The source-scoped file locator is the binding identity. Native
            # and logical identifiers are retained as reported evidence, never
            # interchanged or guessed from a folder name.
            hashes[(item,file)]=unit['content_hash'];receipts.append(receipt)
        rows=bounded_call('lineage_ledger',{'manifest_hash':digest(self.manifest)},self.ledger.records)
        assets={a['id']:a for a in context.get('assets',[]) if a.get('availability')=='CURRENT'}
        addresses={k:a.get('metadata',{}).get('location') for k,a in assets.items()}
        # Resolve under an explicitly recorded sampled cell, never invent one or
        # copy the ticket's figure into a verification. The normal walk still
        # compiles and refuses unsupported ticket restrictions independently.
        samples=[v for v in rows+approval['declared_verifications']
                 if v['context']==adapter.model['context_id']]
        cells={digest({k:v[k] for k in ('context','cell','precision')}):v for v in samples}
        if len(cells)!=1:
            reason='No unique recorded verification sample is available for the retained model context.'
            result=copy.deepcopy(path)
            by_asset={l['asset_id']:l['id'] for l in self.manifest['layers']}
            edges={(b['from_layer'],b['to_layer']) for b in active}
            for i,(upper,lower) in enumerate(zip(result['layers'],result['layers'][1:])):
                if (by_asset.get(lower['id']),by_asset.get(upper['id'])) in edges:
                    result.update(layers=result['layers'][:i+1],stopped_by='NO_LINEAGE',
                        missing_comparable_quantity=reason,unresolved_boundary={
                            'upper_layer':upper['id'],'lower_layer':lower['id'],'reason':reason})
                    break
        else:
            sample=next(iter(cells.values()))
            result=qualify(path,estate=self.manifest,declared=approval['declared_verifications'],
                inferred=rows,current_hashes=hashes,addresses=addresses,
                context=sample['context'],cell=sample['cell'],precision=sample['precision'])
        result.setdefault('evidence',{})['code_source_receipts']=receipts
        return result
