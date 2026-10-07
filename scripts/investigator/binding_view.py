"""Read-only ledger display; recorded verdict is never current admission."""
import copy


def read(installation):
    if installation is None:return []
    rows=[]
    for entry in installation.ledger.records():
        proposal=entry['proposal']
        values=[]
        for observation in entry.get('observations',[]):
            values.append({'status':observation.get('status'),
                'value':copy.deepcopy(observation.get('quantity',observation.get('quantities'))),
                'receipt_id':(observation.get('evidence') or {}).get('id')})
        rows.append({'location':copy.deepcopy(proposal['location']),
            'boundary':copy.deepcopy(proposal['boundary']), 'target':copy.deepcopy(proposal['target']),
            'recorded_verdict':entry['status'], 'context':entry['context'],
            'values':values,'current_eligibility':'NOT_EVALUATED',
            'reason':entry.get('reason')})
    return rows
