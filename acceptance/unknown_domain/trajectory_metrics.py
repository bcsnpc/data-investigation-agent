"""Post-hoc metrics only. Never imported by runtime or admission."""
import json


def metrics(state):
    seen=[];overlap=0
    for observation in state.get('observations',[]):
        fingerprint=observation.get('read_fingerprint')
        if observation.get('tool') in ('native','native_records','source','source_records'):
            fingerprint=observation.get('candidate_id')
        if (not fingerprint or observation.get('status')!='COMPLETED'
                or observation.get('completeness') not in ('COMPLETE_RESPONSE','SOURCE_AGGREGATE')):
            continue
        result=json.dumps(observation.get('values'),sort_keys=True,separators=(',',':'))
        if any(previous!=fingerprint and value==result for previous,value in seen):overlap+=1
        seen.append((fingerprint,result))
    sql_proposals=sum((d.get('decision',{}).get('query') or {}).get('tool')=='bounded_sql'
                      for d in state.get('decisions',[]))
    sql_rejections=sum(o.get('status')=='REJECTED' and o.get('metadata',{}).get('proposed_tool')=='bounded_sql'
                       for o in state.get('observations',[]))
    return {'result_equality_overlap_reads':overlap,
            'schema_prefetch_repairs':sum(e.get('kind')=='PROPOSAL_REPAIRED' and
                e.get('detail',{}).get('repair_kind')=='schema_prefetch' for e in state.get('events',[])),
            'sql_query_proposals':sql_proposals,'sql_query_rejections':sql_rejections,
            'sql_rejection_rate':sql_rejections/sql_proposals if sql_proposals else None}
