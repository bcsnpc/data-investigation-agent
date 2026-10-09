"""Handoff content comes from saved, validated findings, never a caller label."""
import copy
from .onboarding import Conflict, digest
from .process_outcomes import validate as validate_outcome

TECHNICAL={'REFRESH_LATENCY','LOAD_LATENCY','INGESTION_GAP','DEFECT','TRANSFORMATION_LOGIC'}
CONSISTENT={'CONSISTENT_TO_SOURCE','CONSISTENT_TO_BOUNDARY'}


def from_state(state):
    synthesis=state.get('synthesis') or {}
    if synthesis.get('status')!='COMPLETED' or not synthesis.get('outputs'):
        raise Conflict('Findings require completed, validated synthesis')
    assessment=synthesis.get('assessment')
    if not isinstance(assessment,dict):raise Conflict('Saved synthesis has no assessment')
    observations={o['id']:o for o in state['observations']}
    if len(observations)!=len(state['observations']):raise Conflict('Duplicate observation identity')
    # Revalidate against original observations, not a narrative projection.
    validate_outcome(assessment,observations)
    evidence=assessment['evidence_ids']
    if any(identity not in observations for identity in evidence):raise Conflict('Finding cites missing evidence')
    return {'session_id':state['id'],'classification':assessment['classification'],
        'assessment':copy.deepcopy(assessment),'outputs':copy.deepcopy(synthesis['outputs']),
        'evidence_ids':list(evidence),'observations':copy.deepcopy(state['observations']),
        'source_hash':synthesis.get('source_hash'),'record_hash':digest(synthesis),
        'question':'Does this answer your question?'}


def package(findings, kind, owner):
    if kind not in ('BUSINESS_VALIDATION','TECH_HANDOFF'):raise ValueError('Unknown handoff kind')
    if not isinstance(owner,str) or not owner:raise Conflict('Handoff requires a named configured owner')
    classification=findings['classification']
    if kind=='BUSINESS_VALIDATION' and classification not in CONSISTENT|{'BUSINESS_QUESTION'}:
        raise Conflict('A technical finding cannot establish consistent business validation')
    return {'kind':kind,'owner':owner,'delivery':'RECORDED_NOT_SENT',
        'session_id':findings['session_id'],'classification':classification,
        'assessment':copy.deepcopy(findings['assessment']),
        'outputs':copy.deepcopy(findings['outputs']),
        'evidence_ids':copy.deepcopy(findings['evidence_ids']),
        'observations':copy.deepcopy(findings['observations']),
        'findings_hash':digest(findings)}
