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
        # Approval-time typed profiles are bounded witnesses about a binding,
        # not ticket-cell equivalence. Explicit inference authorization permits
        # provisional reuse by exact context, object, column and current code hash.
        # Legacy declared samples keep their original cell-specific semantics.
        from ..report_cell import validate as validate_cell
        cells=scope.get('resolved_cells') or []
        cell=cells[0] if len(cells)==1 else None
        if cell is not None:validate_cell(cell,scope['measure_id'])
        precision=scope.get('reported_precision')
        result=qualify(path,estate=self.manifest,declared=approval['declared_verifications'],
            inferred=rows,current_hashes=hashes,addresses=addresses,
            context=adapter.model['context_id'],cell=cell,precision=precision)
        result.setdefault('evidence',{})['code_source_receipts']=receipts
        return result
