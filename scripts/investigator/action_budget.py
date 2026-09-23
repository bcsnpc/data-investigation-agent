"""Allocate existing planner turns; never enlarge usage or reader authority."""
TEST_TURN_RESERVE = 2


class RetrievalBudgetExceeded(ValueError):
    pass


READ_TOOLS = {'native','source','native_records','source_records','bounded_sql','bounded_dax'}


def summary(state):
    decisions=[d['decision'] for d in state.get('decisions',[])]
    retrievals=sum(d.get('action')=='LOOKUP' for d in decisions)
    tests=sum(d.get('action') in ('RUN','QUERY') for d in decisions)
    reads=sum(o.get('tool') in READ_TOOLS and o.get('status')=='COMPLETED'
              for o in state.get('observations',[]))
    return {'reads_per_run':reads,'retrieval_calls':retrievals,'test_calls':tests,
            'retrieval_test_ratio':retrievals/tests if tests else None}


def allocation(state):
    total=state['envelope']['limits']['planner_calls']
    used=state['planner_calls'];counts=summary(state)
    reserve=min(TEST_TURN_RESERVE,total)
    remaining=max(0,total-used)
    protected=max(0,reserve-counts['test_calls'])
    retrieval_limit=max(0,total-reserve)
    return {'version':1,'planner_limit':total,'planner_remaining':remaining,
            'retrieval_limit':retrieval_limit,'retrieval_used':counts['retrieval_calls'],
            'retrieval_remaining':max(0,min(retrieval_limit-counts['retrieval_calls'],remaining-protected)),
            'test_turns_reserved':reserve,'test_turns_still_protected':min(protected,remaining),
            'test_proposals_used':counts['test_calls'],
            'read_calls_remaining':max(0,state['envelope']['limits']['cloud_calls']-state['cloud_calls']),
            'limitation':'Reserves planning opportunities, not successful reads. Deadlines, total tokens, policy, ambiguity and permission holds still apply.'}
