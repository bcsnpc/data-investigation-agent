"""Describe a recorded trajectory without claiming business-answer correctness.

Reads evaluator output only. Never loads expected answers or modifies runtime.
"""
import argparse
from collections import Counter
import json
from pathlib import Path


def score(record):
    state=record.get('session',{})
    observations=state.get('observations',[])
    completed=[o for o in observations if o.get('status')=='COMPLETED']
    lookups=[o for o in completed if o.get('tool')=='context' and o.get('lookup')]
    keys=[json.dumps(o['lookup'],sort_keys=True) for o in lookups]
    reads=[o for o in completed if o.get('tool') in ('bounded_sql','bounded_dax','native','source')]
    rejected=[o for o in observations if o.get('status')=='REJECTED']
    recovered=any(o.get('status')=='COMPLETED' and o.get('tool') in ('bounded_sql','bounded_dax')
                  for i,o in enumerate(observations)
                  if any(p.get('status')=='REJECTED' for p in observations[:i]))
    return {'session_id':state.get('id'),'trial_kind':record.get('trial_kind'),
            'deployment':record.get('planner_deployment'),'status':state.get('status'),
            'classification':state.get('outcome',{}).get('classification'),
            'stop_reason':state.get('stop_reason'),'planner_calls':state.get('planner_calls',0),
            'cloud_calls':state.get('cloud_calls',0),'completed_reads':len(reads),
            'read_tools':dict(Counter(o['tool'] for o in reads)),
            'rejected_actions':len(rejected),'read_after_rejection':recovered,
            'redundant_reads_blocked':sum(o.get('metadata',{}).get('reason_code')=='READ_ALREADY_OBSERVED' for o in rejected),
            'completed_lookups':len(lookups),'distinct_lookup_requests':len(set(keys)),
            'repeated_lookup_requests':len(keys)-len(set(keys)),
            'partial_observations':sum(o.get('completeness')=='PARTIAL' for o in observations),
            'business_correctness':'NOT_GRADED',
            'limitation':'Recovery means a later read succeeded, not that it answered the ticket. Repeated lookups may deliberately reload compacted context. Human or independent domain grading remains required.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('record',type=Path)
    args=parser.parse_args()
    print(json.dumps(score(json.loads(args.record.read_text(encoding='utf-8'))),indent=2))


if __name__=='__main__':main()
