"""Owner-declared string equality. Unknown declarations never imply defaults."""
import copy
import hashlib
import json
from jsonschema import Draft202012Validator

SCHEMA = {'type': 'object', 'additionalProperties': False,
          'properties': {'collation': {'type': 'string', 'minLength': 1, 'maxLength': 128},
                         'case_fold': {'type': 'boolean'}, 'trim': {'type': 'boolean'},
                         'accent_fold': {'type': 'boolean'},
                         'kana': {'type': 'boolean'}, 'width': {'type': 'boolean'},
                         'resolution': {'enum': ['DECLARED', 'DECLARED_DEFAULT', 'OBSERVED']},
                         'observation': {'type': 'object'}},
          'required': ['collation', 'case_fold', 'trim', 'accent_fold']}


def validate(value):
    Draft202012Validator(SCHEMA).validate(value)
    if value['collation'] == 'BINARY' and any(value.get(k,False) for k in FLAGS):
        raise ValueError('BINARY declares exact strings, without folding or trimming')
    if value.get('resolution') == 'OBSERVED':
        observed=observation(value['observation'])
        if any(value.get(k) != observed[k] for k in FLAGS) or value['collation'] != observed['collation']:
            raise ValueError('Observed semantics differ from original query-bound result')
    elif 'observation' in value:
        raise ValueError('Only OBSERVED semantics carry an observation')
    return copy.deepcopy(value)


def binary(value):
    """Adapter renderers must opt into a faithful supported declaration."""
    value = validate(value)
    if value['collation'] != 'BINARY' or any(value.get(k,False) for k in FLAGS):
        raise NotImplementedError('STRING_SEMANTICS_RENDERING_UNSUPPORTED: ' + value['collation'])
    return value


def normalization(value):
    value=validate(value)
    if any(value.get(k,False) for k in ('accent_fold','kana','width')):
        raise NotImplementedError('STRING_SEMANTICS_RENDERING_UNSUPPORTED: accent/kana/width folding')
    return {'case_fold':value['case_fold'],'trailing_space_trim':value['trim'],
            'representation':'LENGTH_PREFIXED_UTF16_BINARY'}


FLAGS=('case_fold','accent_fold','trim','kana','width')
OBSERVATION_SCHEMA={'type':'object','additionalProperties':False,
    'properties':{'row':{'type':'object','maxProperties':24},'query':{'type':'string','minLength':1,'maxLength':16000},
        'receipt_id':{'type':'string','minLength':1,'maxLength':128},
        'surface':{'type':'object','additionalProperties':False,
            'properties':{k:{'type':'string','minLength':1} for k in ('engine','version','object','identity')},
            'required':['engine','version','object','identity']},
        'surface_report_binding':{'const':'VALUE_QUERY'}},
    'required':['row','query','receipt_id','surface','surface_report_binding']}
SCHEMA['properties']['observation']=OBSERVATION_SCHEMA
SCHEMA['allOf']=[{'if':{'properties':{'resolution':{'const':'OBSERVED'}},'required':['resolution']},
                 'then':{'required':['kana','width','observation']}}]


def observation(record):
    """Five witnessed comparisons, not an inferred complete linguistic collation.

    A DAX probe may not expose a collation name. OBSERVED_COMPARISON_PROBE
    explicitly names that absence; renderers must still opt into faithful support.
    """
    Draft202012Validator(OBSERVATION_SCHEMA).validate(record)
    row=record['row']
    if any(k not in row or type(row[k]) not in (bool,int) or row[k] not in (0,1) for k in FLAGS):
        raise ValueError('Complete five-comparison row required')
    if any(row.get('surface_'+k)!=record['surface'][k] for k in record['surface']):
        raise ValueError('Semantics surface differs from original same-query self-report')
    collation=row.get('collation')
    if collation is not None and (not isinstance(collation,str) or not collation):
        raise ValueError('Invalid observed collation')
    # No broad default follows from five literals. In particular, all-false does
    # not prove an engine uses binary comparison for every Unicode string.
    return {'collation':collation or 'OBSERVED_COMPARISON_PROBE',
            **{k:bool(row[k]) for k in FLAGS},'resolution':'OBSERVED',
            'observation':copy.deepcopy(record)}


def resolve(declared,record):
    observed=observation(record)
    if declared is not None:
        declared=validate(declared)
        mismatches=[k for k in FLAGS if k in declared and declared[k]!=observed[k]]
        actual=record['row'].get('collation')
        if actual and declared['collation'] != actual:
            mismatches.append('collation')
        if mismatches:
            raise ValueError('STRING_SEMANTICS_DECLARATION_CONTRADICTED: '+json.dumps(
                {'fields':mismatches,'declared':declared,'observed':observed},sort_keys=True))
    return observed


def memo_key(record):
    """The calling estate selects the exact surface; never memoize by engine alone."""
    observation(record)
    return hashlib.sha256(json.dumps(record['surface'],sort_keys=True,separators=(',',':')).encode()).hexdigest()


class Observations:
    def __init__(self):self.records={}

    def remember(self,declared,record):
        resolved=resolve(declared,record)
        self.records[memo_key(record)]=copy.deepcopy(record)
        return resolved

    def lookup(self,surface,declared=None):
        key=hashlib.sha256(json.dumps(surface,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        record=self.records.get(key)
        return resolve(declared,record) if record else None


def resolve_layers(manifest,records):
    """Approval projection; disagreement refuses before any manifest is returned."""
    result=copy.deepcopy(manifest)
    ids={l['id'] for l in result['layers']}
    if set(records)-ids:raise ValueError('Observation names an undeclared layer')
    for layer in result['layers']:
        if layer['id'] in records:
            layer['string_semantics']=resolve(layer.get('string_semantics'),records[layer['id']])
    return result
