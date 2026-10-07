"""An explanatory sentence may be superseded; structured evidence may not."""
import copy
from .onboarding import encoded
from .path_narrative import validate_mechanism,validate_declared_layer_tokens
from .evidence_prose import schema
from .proposal_limits import ASSESSMENT_CLAIM
from jsonschema import Draft202012Validator

REASON='synthesis rules tightened per human review, #420'


def unchanged_structure(before,after):
    left=copy.deepcopy(before);right=copy.deepcopy(after)
    left['technical_output']['text']=right['technical_output']['text']=''
    if encoded(left)!=encoded(right):raise ValueError('MECHANISM_REVISION_CHANGED_STRUCTURED_FIELDS')


def revise(attempt,text):
    Draft202012Validator(schema(ASSESSMENT_CLAIM)).validate(text)
    validate_declared_layer_tokens(text,attempt['payload']['layer_tokens'])
    validate_mechanism(text)
    changed=copy.deepcopy(attempt['response'])
    changed['technical_output']['text']=text
    unchanged_structure(attempt['response'],changed)
    return changed


def effective_records(records,revisions):
    """Separate supersessions preserve the original response and human grades.

    Match both immutable source identities. Never transfer a sentence to a
    different tape merely because it belongs to the same ticket family.
    """
    changed=copy.deepcopy(records);used=set()
    if revisions.get('reason')!=REASON or revisions.get('version')!=1:
        raise ValueError('MECHANISM_REVISION_REASON_OR_VERSION')
    for row in changed:
        matches=[r for r in revisions['revisions'] if r['source_tape_sha256']==row['tape_sha256']]
        if not matches:continue
        if len(matches)!=1 or not row['attempts']:raise ValueError('MECHANISM_REVISION_AMBIGUOUS')
        revision=matches[0];original=row['attempts'][-1]
        if (revision['case_id']!=row['case_id'] or revision['source_provider_event_sha256']!=original['provider_event_sha256']
                or revision['superseded_text']!=original['response']['technical_output']['text']):
            raise ValueError('MECHANISM_REVISION_SOURCE_DIFFERS')
        updated=revise(original,revision['response']['technical_output']['text'])
        unchanged_structure(original['response'],revision['response'])
        if updated!=revision['response']:raise ValueError('MECHANISM_REVISION_RESPONSE_DIFFERS')
        original['response']=updated;used.add(revision['source_tape_sha256'])
    if used!={r['source_tape_sha256'] for r in revisions['revisions']} or len(used)!=len(revisions['revisions']):
        raise ValueError('MECHANISM_REVISION_SOURCE_MISSING_OR_DUPLICATE')
    return changed


def require_unused_retry(row):
    if (row['status']=='ACCEPTED' or len(row['attempts'])!=1
            or row['attempts'][0]['number']!=1 or row['attempts'][0]['response'] is None):
        raise ValueError('No unused composition retry is established')
