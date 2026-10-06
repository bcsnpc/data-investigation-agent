"""Installation approval and a single metered transformation-reader pass.

Adapter factories resolve exact discovered objects and executable sample cells.
The controller never authors figures, substitutes samples, or changes manifests.
"""
import copy
from pathlib import Path
from ..code_sources import read
from ..lineage_binding import Ledger
from ..transformation_approval import approve
from ..transformation_service import run_unit


class Controller:
    def __init__(self,manifest,path,root,*,meter,route_factory,git_fetch=None,item_fetch=None,lineage_proposer=None,proposal_record=None):
        self.manifest=copy.deepcopy(manifest);self.path=Path(path);self.root=Path(root)
        self.meter=meter;self.route_factory=route_factory
        self.git_fetch=git_fetch;self.item_fetch=item_fetch
        self.lineage_proposer=lineage_proposer;self.proposal_record=proposal_record
        self.ledger=Ledger(self.path.with_suffix('.lineage.jsonl'))
        self.destination=self.path.with_suffix('.lineage-approval.json')

    def approve(self,samples):
        from ..lineage_proposer import at_approval
        if self.manifest.get('lineage_proposer',False):
            if self.lineage_proposer is None or self.proposal_record is None:
                raise ValueError('Enabled lineage proposer requires an explicit approval transport and recorder')
            at_approval(self.manifest,self.lineage_proposer,self.proposal_record)
        # Each declaration may resolve to its own physical connection, but all
        # executions go through the same consumer verifier and approval gate.
        routes={}
        from ..lineage_binding import seal,validate
        expected={(b['from_layer'],b['to_layer']) for b in self.manifest['lineage']['bindings']}
        covered=set()
        for sample in samples:
            if set(sample)!={'proposal','context','cell','precision'}:
                raise ValueError('Declared approval sample fields differ from contract')
            p=validate(sample['proposal']);covered.add((p['boundary']['from_layer'],p['boundary']['to_layer']))
        if covered!=expected:raise ValueError('Declared approval samples do not cover exactly the configured bindings')
        for sample in samples:
            key=seal(sample['proposal'])
            if key in routes:raise ValueError('Duplicate declared approval sample')
            routes[key]=self.route_factory(sample)
        def compile_side(proposal,side,context,cell,precision):
            route=routes[seal(proposal)]
            return {'route':seal(proposal),'plan':route.compile(proposal,side,context,cell,precision)}
        def execute(side,compiled):
            return routes[compiled['route']].execute(side,compiled['plan'])
        return approve(self.manifest,samples=samples,compiler=compile_side,execute=execute,
                       ledger=self.ledger,destination=self.destination)

    def infer(self,samples,*,model=None):
        from ..transformation_approval import read_approval
        # A reader pass cannot bypass a failed or missing manifest approval.
        approval=read_approval(self.destination,self.manifest)
        sources={s['id']:s for s in self.manifest['lineage']['code_sources']}
        authorized={(b['from_layer'],b['to_layer']):b for b in self.manifest['lineage']['code_locations']
                    if b['may_infer_from_code']}
        planned=[]
        comparison_sample=self.manifest['lineage'].get('verification_sample')
        supplied=[s.get('binding_sample') for s in samples if 'binding_sample' in s]
        if supplied:
            from ..binding_sample import SAMPLE_SCHEMA
            from jsonschema import Draft202012Validator
            if len(supplied)!=len(samples) or any(s!=supplied[0] for s in supplied):
                raise ValueError('All binding requests must declare the same sample restriction')
            Draft202012Validator(SAMPLE_SCHEMA).validate(supplied[0])
            if comparison_sample is not None and comparison_sample!=supplied[0]:
                raise ValueError('Binding sample differs from manifest declaration')
            comparison_sample=supplied[0]
        for sample in samples:
            expected={'boundary','source','path','target_table','schemas','context','cell','precision'}
            if comparison_sample is not None:expected-={'cell','precision'}
            if supplied:expected.add('binding_sample')
            if set(sample)!=expected:raise ValueError('Code-reader sample fields differ from contract')
            boundary=sample['boundary'];edge=(boundary['from_layer'],boundary['to_layer'])
            if edge not in authorized or {'source':sample['source'],'path':sample['path']} not in authorized[edge]['locations']:
                raise ValueError('Code-reader location is not authorized for this boundary')
            if sample['source'] not in sources:raise ValueError('Code-reader source is undeclared')
            planned.append(copy.deepcopy(sample))
        if {(s['boundary']['from_layer'],s['boundary']['to_layer']) for s in planned}!=set(authorized):
            raise ValueError('Reader pass lacks an executable sample for an authorized boundary')
        fetched={};results=[]
        for sample in planned:
            key=(sample['source'],sample['path'])
            if key not in fetched:
                fetched[key]=read(sources[key[0]],key[1],meter=self.meter,root=self.root,
                                 git_fetch=self.git_fetch,item_fetch=self.item_fetch)
            unit,receipt=fetched[key];route=self.route_factory(sample)
            results.append(run_unit(unit=unit,receipt=receipt,schemas=sample['schemas'],
                boundary=sample['boundary'],item=sample['source'],target_table=sample['target_table'],
                layers=self.manifest['layers'],context=sample['context'],cell=sample.get('cell'),
                precision=sample.get('precision'),compiler=route.compile,execute=route.execute,
                ledger=self.ledger,model=model,comparison_sample=comparison_sample,
                target_profile=route.target_profile if comparison_sample is not None else None))
        return {'approval_hash':approval['manifest_hash'],'boundaries':results,
                'code_receipts':[copy.deepcopy(v[1]) for v in fetched.values()]}
