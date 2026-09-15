"""Current proof readiness from implemented adapters, never operator flags."""
from .onboarding import digest


def readiness(model):
    context=model.get('context') or {}
    reports=context.get('reports') or []
    assets=reports[0]['model_assets'] if reports else []
    modes=sorted({p.get('mode','unknown') for a in assets if a['kind']=='SemanticTable'
                  for p in a['metadata'].get('partitions',[])})
    requirements=[
      ('retained_definition','AVAILABLE' if context else 'MISSING','Immutable catalog context is retained; this is not a remote version lock.'),
      ('upstream_semantic_contract','PARTIAL','Direct SUM/COUNTROWS shapes can be checked; materialization lineage and effective grain/filter/date equivalence are not certified.'),
      ('remote_definition_stability','MISSING','No adapter proves definitions stayed unchanged throughout both captures.'),
      ('shared_input_generation','MISSING','Native/source read receipts are not bound to one proven input generation.'),
      ('complete_native_readback','PARTIAL','Bounded projected key/value groups and multiplicity can be read natively; full fixture contents and generation/publication certification remain unverified.'),
      ('exclusive_remote_write_boundary','MISSING','No connector enforces an exclusive publication boundary across capture; a local lease is insufficient.'),
      ('effective_identity_and_context','MISSING','Runtime identity, RLS, date roles and relationship/filter propagation are not jointly certified.'),
    ]
    body={'version':'proof-requirements-v1','model_id':model['id'],'context_id':model['context_id'],
          'observed_partition_modes':modes,'requirements':[{'id':key,'state':state,'reason':reason} for key,state,reason in requirements],
          'live_acceptance_ready':False,'verification_adapter_registered':False,
          'preflight_available':True,
          'preflight_limitation':'Read-only metadata observations expose gaps; they cannot certify an exclusive remote write boundary.',
          'next_gate':'Run the proof preflight, then establish controlled publication/input generation and effective context before live healthy/defect acceptance.'}
    return dict(body,hash=digest(body))
