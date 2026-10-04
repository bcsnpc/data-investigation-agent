"""Names resolve within the selected catalog, by declared kind, not guesses."""
import copy
from .reported_figure import span
from .reported_figure import SPAN_SCHEMA
from .definition_target import ID
SCHEMA={'type':'object','additionalProperties':False,'properties':{
    'kind':{'type':'string','enum':['REPORT','MODEL','LAYER']},'asset_id':copy.deepcopy(ID),
    'source':copy.deepcopy(SPAN_SCHEMA)},'required':['kind','asset_id','source']}


def resolve(source,model,ticket=None):
    quote=span(source,ticket)
    groups=(('REPORT',model.get('reports',[])),('MODEL',[model]),('LAYER',model.get('declared_layers',[])))
    for kind,entries in groups:
        found=[e for e in entries if e['name']==quote]
        if len(found)>1:
            if kind=='REPORT':return None # resolve_report retains its closed ambiguity refusal
            raise ValueError('Name ambiguity among '+kind+' candidates: '+', '.join(e['id'] for e in found))
        if found:return {'kind':kind,'asset_id':found[0]['id'],'source':copy.deepcopy(source)}
    return None


def validate(value,model,ticket=None):
    if not isinstance(value,dict) or set(value)!={'kind','asset_id','source'}:
        raise ValueError('Malformed named context')
    if resolve(value['source'],model,ticket)!=value:raise ValueError('Named context differs from declared catalog kind')
    return value
