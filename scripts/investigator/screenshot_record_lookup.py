"""Case-scoped screenshot lookup. No image or personal values in shared logs.

Vision and query-planning ports are installed model calls. The query planner
writes all lookup SQL/DAX; native results establish keys, not model guesses.
"""
from hashlib import sha256
from copy import deepcopy


class ScreenshotLookup:
    def __init__(self,*,catalog,queries,extract,plan,audit):
        self.catalog,self.queries=catalog,queries
        self.extract,self.plan,self.audit=extract,plan,audit

    def resolve(self,image,intake):
        if not isinstance(image,bytes) or not 1<=len(image)<=1024*1024:
            raise ValueError('SCREENSHOT_BYTES_BOUND')
        checksum=sha256(image).hexdigest()
        extracted=self.extract(image)
        if (not isinstance(extracted,dict) or set(extracted)!={'titles','visible_fields'}
                or not isinstance(extracted['titles'],dict) or not isinstance(extracted['visible_fields'],dict)
                or not extracted['visible_fields']):raise ValueError('SCREENSHOT_EXTRACTION_SHAPE')
        self.audit({'event':'SCREENSHOT_LOOKUP','sha256':checksum,
                    'field_names':sorted(extracted['visible_fields'])})
        # The selected form report is authoritative. Vision may identify a
        # missing page/visual within it, never replace a picked visual.
        report=intake['report'];pages=self.catalog.pages(report)
        if intake.get('page'):pages=[p for p in pages if p['id']==intake['page']]
        title=extracted['titles'].get('page')
        if title and not intake.get('page'):pages=[p for p in pages if p['name'].casefold()==title.casefold()]
        candidates=[]
        for page in pages:
            for visual in self.catalog.visuals(report,page['id']):
                if intake.get('visual') and visual['id']!=intake['visual']:continue
                title=extracted['titles'].get('visual')
                if title and not intake.get('visual') and visual['name'].casefold()!=title.casefold():continue
                candidates.append({'report':report,'page':page['id'],'visual':visual['id'],'name':visual['name']})
        if len(candidates)!=1:
            return {'status':'TARGET_CHOICES','sha256':checksum,'candidates':candidates}
        target=candidates[0]
        plans=self.plan(deepcopy(target),deepcopy(extracted['visible_fields']))
        if not isinstance(plans,list) or not 1<=len(plans)<=5:raise ValueError('LOOKUP_PLAN_BOUND')
        reads=[];successful=0
        for plan in plans:
            fields={'layer','query','kind','key_field','display_fields'}
            if not fields<=set(plan)<=fields|{'match_columns'}:raise ValueError('LOOKUP_PLAN_SHAPE')
            record=self.queries.run(plan['layer'],plan['query'],kind=plan['kind'],purpose='lookup')
            if 'record' in record:record=record['record']
            reads.append({'layer':plan['layer'],'query_id':record.get('id'),'status':record.get('status')})
            if record.get('status')!='SUCCEEDED':continue
            successful+=1
            if record.get('truncated'):
                return {'status':'LOOKUP_TRUNCATED','target':target,'reads':reads,'sha256':checksum,
                        'reason':'Narrow the visible-value lookup; uniqueness is not established.'}
            rows=record['result']['rows']
            if any(not isinstance(r,dict) or plan['key_field'] not in r for r in rows):
                raise ValueError('LOOKUP_MISSING_NATIVE_KEY')
            bindings=plan.get('match_columns',{field:field for field in extracted['visible_fields']})
            if set(bindings)!=set(extracted['visible_fields']):raise ValueError('LOOKUP_VISIBLE_BINDINGS_REQUIRED')
            if any(any(column not in row for column in bindings.values()) for row in rows):
                raise ValueError('LOOKUP_QUERY_MUST_RETURN_VISIBLE_MATCH_COLUMNS')
            rows=[row for row in rows if all(str(row[column])==str(extracted['visible_fields'][field])
                                           for field,column in bindings.items())]
            if any(row[plan['key_field']] is None for row in rows):raise ValueError('LOOKUP_NATIVE_KEY_IS_BLANK')
            keys={str(r[plan['key_field']]) for r in rows}
            if len(keys)==1:
                return {'status':'KEY_RESOLVED','key':next(iter(keys)),'target':target,'reads':reads,'sha256':checksum}
            if keys:
                choices=[]
                for i,row in enumerate(rows):
                    display={k:row[k] for k in plan['display_fields'] if k in row and k!=plan['key_field']}
                    choices.append({'choice':i+1,'display':display})
                return {'status':'KEY_CHOICES','target':target,'choices':choices,
                        'private_keys':[str(r[plan['key_field']]) for r in rows],'reads':reads,'sha256':checksum}
        if not successful:
            return {'status':'LOOKUP_UNAVAILABLE','target':target,'reads':reads,'sha256':checksum}
        return {'status':'NO_MATCH','target':target,'reads':reads,'sha256':checksum,
                'finding':'The visible values were not matched on the checked layers.'}
