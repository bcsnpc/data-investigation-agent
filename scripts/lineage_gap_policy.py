"""Fail-closed lineage eligibility for investigation conclusions."""


def classify(graph, gap):
    reason=gap['reason']
    category=('CONDITIONAL_DATAFLOW' if reason=='Conditional dataflow requires runtime evidence' else
              'UNRESOLVED_WRITE_TARGET' if 'write' in reason.lower() else
              'UNSUPPORTED_CODE' if 'Unsupported' in reason or 'parsing' in reason else
              'UNRESOLVED_DEPENDENCY')
    owner=graph.assets.get(gap['asset'])
    targets={target for source,target,kind in graph.edges if source==gap['asset'] and kind=='produces'}
    # An unresolved notebook branch can write elsewhere even if another branch has a known output.
    unscoped=owner is None or (owner['kind']=='Notebook' and
             (not targets or category in ('CONDITIONAL_DATAFLOW','UNRESOLVED_WRITE_TARGET')))
    return {**gap,'category':category,'resolution':'UNRESOLVED',
            'scope':'UNSCOPED' if unscoped else 'ASSET_AND_DEPENDENTS',
            'affected_roots':sorted({gap['asset']}|targets),
            'required_evidence':'Verified execution-specific dependency scope or reviewed parser support'}


def eligibility(graph, downstream):
    trace=graph.traverse(downstream)
    path={a['id'] for a in trace['assets']}
    classified=[classify(graph,g) for g in graph.gaps]
    blockers=[g for g in classified if g['scope']=='UNSCOPED' or path.intersection(g['affected_roots'])]
    return {'status':'INSUFFICIENT_EVIDENCE' if blockers else 'LINEAGE_SUPPORTED',
            'lineage_conclusions_allowed':not blockers,
            'automatic_defect_routing_allowed':False,
            'blocking_gaps':blockers,'unrelated_gap_count':len(classified)-len(blockers),
            'resolved_parser_gap_count':len(graph.resolved_gaps),
            'limitation':'Lineage eligibility alone does not establish snapshot compatibility or a technical defect'}
