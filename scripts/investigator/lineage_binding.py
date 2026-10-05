"""Consumer-owned proposed lineage, sampled verification and immutable ledger.

A proposal never certifies itself. The verifier observes executable expressions;
it does not replace the original input/output quantity used by an investigation.
"""
import copy
import hashlib
import json
from decimal import Decimal,localcontext
from pathlib import Path
from jsonschema import Draft202012Validator
from .code_sources import obj
from .reported_figure import PRECISION_SCHEMA

MAX_TEXT=500
MAX_COLUMNS=128
MAX_SOURCES=16
MAX_DEPTH=32
MAX_NODES=4096
TEXT={'type':'string','minLength':1,'maxLength':MAX_TEXT}
COLUMN={'type':'string','minLength':1,'maxLength':MAX_COLUMNS}
HASH={'type':'string','pattern':'^[0-9a-f]{64}$'}
NODE={'$ref':'#/$defs/node'}
RELATION={'$ref':'#/$defs/relation'}
def variant(kind,fields):return obj({'kind':{'const':kind},**fields})
def array(item,minimum=1,maximum=MAX_COLUMNS):return {'type':'array','items':item,'minItems':minimum,'maxItems':maximum}

DEFS={
 'node':{'anyOf':[
    variant('COLUMN',{'name':COLUMN}),
    variant('LITERAL',{'value':{'type':['string','number','boolean','null'],'maxLength':MAX_TEXT}}),
    variant('DECIMAL',{'value':{'type':'string','pattern':r'^[+-]?[0-9]+(?:\.[0-9]+)?$','maxLength':MAX_COLUMNS}}),
    *[variant(op,{'left':NODE,'right':NODE}) for op in ('ADD','SUBTRACT','MULTIPLY','DIVIDE','EQ','NE','GT','GE','LT','LE','AND','OR')],
    *[variant(op,{'operand':NODE}) for op in ('SUM','COUNT','MIN','MAX','AVG','NOT')]]},
 'relation':{'anyOf':[
    variant('SCAN',{'table':TEXT,'columns':array(COLUMN)}),
    variant('PROJECT',{'input':RELATION,'columns':array(obj({'name':COLUMN,'expression':NODE}))}),
    variant('FILTER',{'input':RELATION,'predicate':NODE}),
    variant('DEDUPE',{'input':RELATION,'keys':array(COLUMN)}),
    variant('JOIN',{'left':RELATION,'right':RELATION,'how':{'enum':['LEFT','INNER']},'keys':array(COLUMN)}),
    variant('AGGREGATE',{'input':RELATION,'groups':array(COLUMN,0),'columns':array(obj({'name':COLUMN,'expression':NODE}))})]}}
COMMON={
 'boundary':obj({'from_layer':TEXT,'to_layer':TEXT}),
 'sources':array(obj({'table':TEXT,'columns':array(COLUMN)}),1,MAX_SOURCES),
 'target':obj({'table':TEXT,'column':COLUMN}),
 'expression':obj({'relation':RELATION,'column':COLUMN}),
 'location':obj({'item':TEXT,'path':TEXT,'cell':TEXT,'line_start':{'type':'integer','minimum':1},
    'line_end':{'type':'integer','minimum':1},'content_hash':HASH})}
PROPOSED_BINDING_SCHEMA={'anyOf':[
 obj({**COMMON,'extractor':{'const':'STATIC'}}),
 obj({**COMMON,'extractor':{'const':'MODEL'},'confidence':{'type':'number','minimum':0,'maximum':1}})],'$defs':DEFS}

def validate(proposal):
    # Bound the entire tree before recursive schema validation, including scalar
    # subexpressions. A relation-only bound leaves hostile scalar nesting open.
    pending=[(proposal,0)];count=0
    while pending:
        value,depth=pending.pop();count+=1
        if depth>MAX_DEPTH or count>MAX_NODES:
            raise ValueError('ProposedBinding.expression: structural bound exceeded')
        if isinstance(value,dict):pending.extend((v,depth+1) for v in value.values())
        elif isinstance(value,list):pending.extend((v,depth+1) for v in value)
    errors=list(Draft202012Validator(PROPOSED_BINDING_SCHEMA).iter_errors(proposal))
    if errors:raise ValueError('ProposedBinding: '+errors[0].message)
    if proposal['location']['line_end']<proposal['location']['line_start']:
        raise ValueError('ProposedBinding.location: reversed line range')
    def sources(relation,depth=0):
        if depth>MAX_DEPTH:raise ValueError('ProposedBinding.expression: depth bound exceeded')
        kind=relation['kind']
        if kind=='SCAN':return [(relation['table'],relation['columns'])]
        if kind=='JOIN':return sources(relation['left'],depth+1)+sources(relation['right'],depth+1)
        return sources(relation['input'],depth+1)
    actual=sources(proposal['expression']['relation'])
    declared=[(s['table'],s['columns']) for s in proposal['sources']]
    if actual!=declared:raise ValueError('ProposedBinding.sources: differs from expression scan inventory')
    if proposal['target']['column']!=proposal['expression']['column']:
        raise ValueError('ProposedBinding.target: expression output column differs')
    return copy.deepcopy(proposal)

COMPARISON_RULE=("Compile both expressions before either read. Both observations must be completed, "
 "bound to the same retained context, cell address and explicitly declared precision. "
 "Compare their numeric quantities at that precision, or BLANK with BLANK. Equal is "
 "VERIFIED only for that sampled quantity and scope; unequal is FALSIFIED. A compilation, "
 "read, identity or context failure is UNVERIFIED, never evidence of equality. No inferred tolerance.")

def verify(proposal,*,context,cell,precision,compiler,execute):
    proposal=validate(proposal)
    Draft202012Validator(PRECISION_SCHEMA).validate(precision)
    if not context or not isinstance(cell,dict):raise ValueError('Verification requires context and cell address')
    receipt={'proposal':proposal,'context':context,'cell':copy.deepcopy(cell),'precision':copy.deepcopy(precision),
             'observations':[],'status':'UNVERIFIED','reason':None,
             'limits':['Sampled quantity agreement does not establish row membership, global equivalence, aligned snapshots or business intent.']}
    try:
        # Consumer compilers retain the existing parser, authorization and caps.
        plans=[compiler(proposal,side,context,cell,precision) for side in ('TARGET','SOURCE')]
    except (ValueError,NotImplementedError) as exc:
        receipt['reason']='Cannot compile faithfully: '+str(exc);return receipt
    for side,plan in zip(('TARGET','SOURCE'),plans):
        try:observation=execute(side,plan)
        except (ValueError,OSError,TimeoutError) as exc:
            receipt['observations'].append({'status':'FAILED','error_type':type(exc).__name__,'error':str(exc),'side':side})
            receipt['reason']='The '+side.lower()+' read failed; no equality established.';return receipt
        receipt['observations'].append(copy.deepcopy(observation))
        if not isinstance(observation,dict) or observation.get('status')!='COMPLETED':
            receipt['reason']='The '+side.lower()+' read did not complete.';return receipt
        if any(observation.get(key)!=expected for key,expected in
               (('context',context),('cell',cell),('precision',precision))):
            receipt['reason']='Observed context, cell address or precision differs.';return receipt
        value=observation.get('quantity')
        if not isinstance(value,dict) or value.get('state') not in ('NUMBER','BLANK'):
            receipt['reason']='The read did not establish a scalar quantity or BLANK.';return receipt
        if value['state']=='NUMBER':
            try:
                number=Decimal(value['value'])
                if not number.is_finite():raise ValueError('Nonfinite quantity')
            except (ValueError,KeyError,TypeError,ArithmeticError):
                receipt['reason']='The numeric quantity is invalid.';return receipt
    from .process_debugging import attest_surface
    from .surface_difference import grade,BOUNDARY_GRADES
    for observation in receipt['observations']:
        original=observation.get('evidence')
        if not isinstance(original,dict):
            receipt['reason']='Original quantity-bound surface evidence is missing.';return receipt
        attestation=original.get('surface_attestation') or {}
        if attest_surface(original.get('execution_surface'),original.get('surface_report'),
                          attestation.get('required_fields',()))!=attestation:
            receipt['reason']='Original surface attestation cannot be recomputed.';return receipt
    difference=grade(*(o['evidence'] for o in receipt['observations']))
    receipt['surface_difference']=difference
    if difference['grade'] not in BOUNDARY_GRADES:
        receipt['reason']='No independent quantity-bound surface comparison: '+str(difference['reason']);return receipt
    receipt['snapshot_status']='SNAPSHOT_UNVERIFIED'
    receipt['limits'].append('SNAPSHOT_UNVERIFIED: matching served data versions were not established; timing is not excluded.')
    left,right=[o['quantity'] for o in receipt['observations']]
    if left['state']!=right['state']:equal=False
    elif left['state']=='BLANK':equal=True
    else:
        with localcontext() as ctx:
            ctx.prec=256;values=[Decimal(x['value']) for x in (left,right)]
            if precision['state']=='STATED_PLACE':
                quantum=Decimal(1).scaleb(precision['place'])
                values=[v.quantize(quantum) for v in values]
            equal=values[0]==values[1]
    receipt['status']='VERIFIED' if equal else 'FALSIFIED'
    receipt['reason']='The sampled expressions agree.' if equal else 'The sampled expressions differ.'
    return receipt

def seal(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()

class Ledger:
    def __init__(self,path):self.path=Path(path)
    def append(self,verification):
        if verification['status'] not in ('VERIFIED','FALSIFIED','UNVERIFIED'):
            raise ValueError('Only verifier results enter lineage ledger')
        validate(verification['proposal'])
        row={'event':'VERIFICATION','verification':verification,'sha256':seal(verification)}
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.path.open('a',encoding='utf8') as stream:stream.write(json.dumps(row,separators=(',',':'))+'\n')
    def view(self,current_hashes):
        result=[]
        if not self.path.exists():return result
        for line in self.path.read_text(encoding='utf8').splitlines():
            row=json.loads(line);v=row['verification']
            if set(row)!={'event','verification','sha256'} or row['event']!='VERIFICATION' or seal(v)!=row['sha256']:
                raise ValueError('Lineage ledger integrity differs')
            proposal=validate(v['proposal']);location=proposal['location']
            fresh=current_hashes.get((location['item'],location['path']))==location['content_hash']
            result.append({**copy.deepcopy(v),'status':v['status'] if fresh else 'STALE',
                           'provenance':'INFERRED_FROM_CODE'})
        return result

def require_declared_approval(verifications):
    for v in verifications:
        if v['status']=='FALSIFIED':raise ValueError('Declared binding falsified: '+json.dumps(v['observations'],sort_keys=True))
        if v['status']!='VERIFIED':raise ValueError('Declared binding is not verified: '+str(v['reason']))
