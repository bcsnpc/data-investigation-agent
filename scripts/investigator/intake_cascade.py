"""One cheap extraction pass, with one configured stronger fallback pass."""
from copy import deepcopy
from .guided_text_resolver import Resolver


class Cascade:
    def __init__(self, *, catalog, first_model, fallback_model, record, resolver_factory=Resolver):
        self.catalog, self.first_model, self.fallback_model = catalog, first_model, fallback_model
        self.record, self.resolver_factory = record, resolver_factory

    def resolve(self, text):
        stages=[]
        def extract(model, stage):
            result=self.resolver_factory(catalog=self.catalog, model=model, record=self.record).resolve(text)
            low=result.get('resolution_confidence') in ('FUZZY','RELATED_WORDS','LOW','UNVERIFIED')
            row={'stage':stage,'model':model.model,'status':result['status'],
                 'code':result.get('code'),'low_confidence':low}
            stages.append(row)
            self.record({'event':'INTAKE_CASCADE_STAGE',**row})
            return result,low
        result,low=extract(self.first_model,'FIRST')
        if result['status']!='READY' or low:
            result,low=extract(self.fallback_model(),'FALLBACK')
        result=deepcopy(result)
        result['intake_cascade']={'stages':stages,'fallback_used':len(stages)==2,
            'resolved_by_model':stages[-1]['model'] if result['status']=='READY' else None}
        return result
