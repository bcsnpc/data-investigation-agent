"""A checked citation namespace; business composition stays with the engine."""
import copy
from jsonschema import Draft202012Validator
from . import proposal_limits as limits


REFERENCE_FIELDS=frozenset(('receipt_id','evidence_id','evidence_ids','referenced_evidence_ids','read_receipt_ids','comparison_id'))


def validate_references(payload,originals=None):
    evidence=payload.get('evidence',[])
    visible={e['id'] for e in evidence}
    if len(visible)!=len(evidence):raise ValueError('Synthesis spine repeats an evidence identity')
    original={o['id']:o for o in originals} if originals is not None else None
    def check(identity,path):
        if not isinstance(identity,str) or identity not in visible:
            raise ValueError('Dangling synthesis spine receipt '+str(identity)+' at '+path)
        if original is not None and (identity not in original or original[identity].get('status')!='COMPLETED'):
            raise ValueError('Synthesis spine receipt unavailable in evidence store: '+identity)
    for identity in visible:check(identity,'evidence')
    def walk(value,path):
        if isinstance(value,dict):
            for key,item in value.items():
                if key in REFERENCE_FIELDS or key.endswith(('_receipt_id','_evidence_id')):
                    for identity in item if isinstance(item,list) else [item]:
                        if identity is not None:check(identity,path+'.'+key)
                else:walk(item,path+'.'+key)
        elif isinstance(value,list):
            for i,item in enumerate(value):walk(item,path+'['+str(i)+']')
    walk(payload,'spine')


def prepare(payload):
    validate_references(payload)
    ids=sorted(e['id'] for e in payload['evidence'])
    handles={'r'+str(i):identity for i,identity in enumerate(ids)}
    forward={identity:handle for handle,identity in handles.items()}
    def translate(value):
        if isinstance(value,str):return forward.get(value,value)
        if isinstance(value,dict):return {key:translate(item) for key,item in value.items()}
        if isinstance(value,list):return [translate(item) for item in value]
        return copy.deepcopy(value)
    wire_payload=translate(payload)
    # The model does not copy deterministic business wording back to the engine.
    wire_payload.pop('rendered_business',None)
    statement={'type':'object','additionalProperties':False,'properties':{
        'text':{'type':'string','description':'Mechanism only. Complete sentences, at most '+str(limits.ASSESSMENT_CLAIM)+' characters; no limitations or path-account references.'},
        'evidence_ids':{'type':'array','items':{'type':'string','enum':list(handles)}}},
        'required':['text','evidence_ids']}
    schema={'type':'object','additionalProperties':False,'properties':{'technical_output':statement},'required':['technical_output']}
    from .adapters.structured_output_contract import validate
    validate(schema)
    return wire_payload,schema,handles


def decode(value,payload,schema,handles):
    Draft202012Validator(schema).validate(value)
    technical=copy.deepcopy(value['technical_output'])
    refs=technical['evidence_ids']
    if len(refs)>limits.ASSESSMENT_REFS or (handles and not refs):raise ValueError('Synthesis requires bounded visible citations')
    technical['evidence_ids']=[handles[ref] for ref in refs]
    from .output_contract import business_text
    outcome=payload.get('outcome') or (payload.get('deterministic_process_finding') or {})['classification']
    return {'business_output':{'text':business_text(outcome,payload),'evidence_ids':copy.deepcopy(technical['evidence_ids'])},
            'technical_output':technical}
