"""Explicit synthesis projection of Microsoft process-context receipt contracts."""
import copy
from ..onboarding import Conflict


def ingestion_evidence(observation):
    """Ingestion receipts are not context-search metadata responses.

    Preserve the declared asset and the complete bounded transport report. Missing
    required evidence is an error, never an empty result or an inferred success.
    """
    if 'metadata' in observation or 'lookup' in observation:
        raise Conflict('Ingestion context mixes incompatible receipt shapes')
    if not isinstance(observation.get('asset_id'),str) or not observation['asset_id']:
        raise Conflict('Ingestion context requires its asset identity')
    report=observation.get('delta_commit')
    if not isinstance(report,dict):raise Conflict('Ingestion context requires its commit report')
    required={
        'AVAILABLE':{'status','latest_commit','commit_info'},
        'EMPTY_RESPONSE':{'status','latest_commit'},
        'UNAVAILABLE':{'status','error_type'},
    }
    status=report.get('status')
    if not isinstance(status,str) or status not in required or set(report)!=required[status]:
        raise Conflict('Ingestion commit report does not match its status contract')
    if status=='AVAILABLE' and (not isinstance(report['latest_commit'],str) or not report['latest_commit']
                              or not isinstance(report['commit_info'],dict)):
        raise Conflict('Available ingestion report requires commit identity and information')
    if status=='EMPTY_RESPONSE' and report['latest_commit'] is not None and not isinstance(report['latest_commit'],str):
        raise Conflict('Empty ingestion report has invalid commit identity')
    if status=='UNAVAILABLE' and (not isinstance(report['error_type'],str) or not report['error_type']):
        raise Conflict('Unavailable ingestion report requires its failure category')
    return {'kind':'INGESTION_METADATA','asset_id':observation['asset_id'],
            'delta_commit':copy.deepcopy(report)}
