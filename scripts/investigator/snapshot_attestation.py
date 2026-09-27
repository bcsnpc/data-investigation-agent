"""Optional served-snapshot evidence. Never selects a process outcome."""
import copy

UNVERIFIED='SNAPSHOT_UNVERIFIED'
VERIFIED='SNAPSHOT_VERIFIED'
KEYS=('engine','connection','object')


def bound(report, evidence_id, surface):
    """Only an adapter-produced, query-bound report can attest a served version.

    A metadata watermark, timestamp, or merely equal quantity is not such a report.
    Source identities include a native dataset identity; versions are opaque strings.
    """
    if not isinstance(report,dict):return False
    identity=report.get('identity_provenance',{})
    return (report.get('status')=='AVAILABLE' and report.get('binding')=='QUERY_BOUND'
        and report.get('quantity_receipt_id')==evidence_id
        and isinstance(report.get('evidence_id'),str) and bool(report['evidence_id'])
        and isinstance(identity,dict) and isinstance(identity.get('account'),str) and bool(identity['account'])
        and type(identity.get('execution_reader')) is bool
        and isinstance(surface,dict) and isinstance(surface.get('identity'),str)
        and ((identity['account'].casefold()==surface['identity'].casefold())==identity['execution_reader'])
        and isinstance(report.get('surface'),dict) and isinstance(surface,dict)
        and all(report['surface'].get(k)==surface.get(k) and bool(surface.get(k)) for k in KEYS)
        and isinstance(report.get('dataset_id'),str) and bool(report['dataset_id'])
        and isinstance(report.get('version'),str) and bool(report['version']))


def comparison(observation, upper=None, lower=None):
    reports={'upper':copy.deepcopy(upper),'lower':copy.deepcopy(lower)}
    missing=[side for side in reports if not bound(reports[side],observation.get(side+'_evidence_id'),
                                                   observation.get(side+'_execution_surface'))]
    status=UNVERIFIED
    reason='QUERY_BOUND_VERSION_MISSING' if missing else 'DATASET_OR_VERSION_DIFFERS'
    if not missing and all(upper[k]==lower[k] for k in ('dataset_id','version')):
        status=VERIFIED;reason='SAME_DATASET_AND_SERVED_VERSION'
    return {'version':1,'status':status,'reason':reason,'unverified_sides':missing,
            'upper':reports['upper'],'lower':reports['lower']}


def checked(observation):
    value=observation.get('snapshot_attestation')
    if value is None:return comparison(observation) # historical evidence stays readable, never upgraded
    if not isinstance(value,dict) or value!=comparison(observation,value.get('upper'),value.get('lower')):
        raise ValueError('Snapshot attestation differs from query-bound evidence')
    return value


def limitation(observation, ordinal):
    value=checked(observation)
    if value['status']==VERIFIED:return None
    sides=' and '.join(value['unverified_sides']) or 'aligned'
    basis=('the '+sides+' served data version is not attested to its quantity read' if value['unverified_sides'] else
           'the attested dataset/version pairs do not match')
    claim=('agreement does not establish that either value is current' if observation.get('values_equal') else
           'different update timing was not excluded as a cause of the difference')
    return f'Comparison {ordinal}: SNAPSHOT_UNVERIFIED; {basis}; {claim}.'


def enrich(observations, probes, adapter, available):
    cache={}
    for o in observations:
        if o.get('comparison_status')!='CROSS_SURFACE_VERIFIED':continue
        reports=[]
        for side in ('upper','lower'):
            key=o[side+'_evidence_id'];probe=probes.get(key)
            if key not in cache:
                report=copy.deepcopy((probe.evidence or {}).get('snapshot_identity')) if probe else None
                if report is None and probe and 'snapshot_identity' in available:
                    try:report=adapter.snapshot_identity(probe)
                    except Exception as exc:report={'status':'UNAVAILABLE','reason':'OPTIONAL_METADATA_FAILED','error_type':type(exc).__name__}
                cache[key]=report
            reports.append(cache[key])
        o['snapshot_attestation']=comparison(o,*reports)


def payload_comparisons(payload):
    return [e['result'] for e in payload.get('evidence',[]) if e.get('tool')=='process'
            and e.get('result',{}).get('comparison_status')=='CROSS_SURFACE_VERIFIED']


def business_limit(payload):
    sentences=[]
    for ordinal,o in enumerate(payload_comparisons(payload),1):
        att=o.get('snapshot_attestation') or {'status':UNVERIFIED,'unverified_sides':['upper','lower']}
        if att['status']==VERIFIED:continue
        sides=att.get('unverified_sides',[])
        names={'upper':'the check nearer the report','lower':'the check further back'}
        if sides:
            sentences.append(f"Comparison {ordinal} lacks a verified data version for "+' and '.join(names[s] for s in sides)+'.')
        else:sentences.append(f'Comparison {ordinal} has different attested data versions or datasets; their alignment is unverified.')
        sentences.append('Agreement does not establish that either value is up to date.' if o['values_equal'] else
                         'Different update timing was not excluded as a cause of this difference.')
    return ' '.join(sentences)
