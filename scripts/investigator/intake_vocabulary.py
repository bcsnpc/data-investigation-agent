"""Estate-declared measure/column synonyms, never rewritten ticket evidence."""
import copy
from .onboarding import digest


def apply(models, configuration):
    declarations=configuration['vocabulary_aliases']
    result=copy.deepcopy(models)
    for model in result:
        for key in ('measures','columns'):
            for member in model.get(key,[]):
                declared=[d for d in declarations if d['canonical']==member['name']]
                if not declared:continue
                member['aliases']=sorted(set(member.get('aliases',[]))|{d['alias'] for d in declared})
                member['estate_vocabulary']={'provenance':'DECLARED_BY_CONFIGURATION',
                    'declarations':copy.deepcopy(declared),'declaration_hash':digest(declared)}
    return result
