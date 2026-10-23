"""One estate per scheduled wake; existing shared SCAN policy remains authority."""
from investigator.shared_state import configured_state, sha
from cloud_facts_collector import execute as collect, validate


def select(configs, state):
    if not isinstance(configs,list) or not 1<=len(configs)<=3:raise ValueError('FACT_DISPATCHER_CONFIGS')
    for config in configs:validate(config)
    estates=[c['estate'] for c in configs]
    if len(set(estates))!=len(estates):raise ValueError('FACT_DISPATCHER_DUPLICATE_ESTATE')
    if any(c['max_requests']>8 or c.get('list_interval_seconds',21600)<21600 or c.get('max_subjects_per_wake',10)>2 for c in configs):
        raise ValueError('FACT_DISPATCHER_APPROVED_ALLOWANCE')
    key=sha(sorted(estates))
    try:cursor=state.get('facts_dispatcher',key)
    except KeyError:cursor=None
    offset=int(cursor['body']['next']) if cursor else 0
    selected=sorted(configs,key=lambda c:c['estate'])[offset%len(configs)]
    return selected,key,cursor,(offset+1)%len(configs)


def execute(configs,*,state=None,collector=collect):
    state=state or configured_state()
    if state is None or state.backend!='postgresql':raise ValueError('FACT_DISPATCHER_SHARED_POSTGRESQL_REQUIRED')
    selected,key,cursor,next_offset=select(configs,state)
    # The collector itself admits every physical request to shared monthly SCAN;
    # dispatch cannot create an account, grant scope, or widen a request bound.
    result=collector(selected)
    state.put('facts_dispatcher',key,{'next':next_offset,'last_estate':selected['estate']},
        revision=cursor['revision'] if cursor else None)
    return {'status':'COLLECTED','selected_estate':selected['estate'],'next_index':next_offset,
        'other_estates_not_read':[c['estate'] for c in configs if c['estate']!=selected['estate']],
        'collection':result,'max_physical_requests_this_wake':8,'purpose':'SCAN'}
