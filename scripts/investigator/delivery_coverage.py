"""Coverage checks over admitted scope and cited reads; no semantic guesses."""
from .primary_verification import no_comparison, query_references


def conditional_definition(args, case, resolution):
    """Explain measured alternatives without selecting one on the user's behalf."""
    intake = case['intake']
    issue = intake.get('classified_issue_type') or intake.get('issue_type')
    if (issue != 'HOW_IS_THIS_CALCULATED' or intake.get('reported_figure')
            or not no_comparison(intake) or args.get('selected_target') is not None
            or args.get('verdict_class') != 'AS DESIGNED'
            or args.get('verdict') not in ('as designed', 'definition explained')
            or not args.get('undecided')):
        return False
    inventory = case['context'].get('candidate_inventory', {})
    from .intake_candidates import select_unique
    exact_definition=False
    if not inventory.get('exhaustive'):
        from .delivery_references import calculation_measure
        measure=calculation_measure(case['context'],args)
        node=next((n for n in case['context'].get('path',{}).get('nodes',[])
                   if n['id']==measure and n['kind']=='MEASURE'),{})
        asset=node.get('properties',{}).get('asset_id')
        references=query_references(case,args['evidence_ids'])
        exact_definition=bool(asset and any(q['id'] in references and q.get('status')=='SUCCEEDED'
            and asset in q.get('asset_ids',[]) for q in case['queries']) and any(
                case['evidence'].get(i,{}).get('kind')=='RETAINED_DEFINITION_REFERENCE'
                and case['evidence'][i].get('asset_id')==asset for i in args['evidence_ids']))
        if not exact_definition:return False
    # Pure definition of an exact admitted measure does not assert that the
    # bounded inventory covers every visual. Keep its incompleteness recorded.
    checked = select_unique({**inventory,'exhaustive':bool(inventory.get('exhaustive') or exact_definition)}, resolution.get('observations', []), None)
    if not checked['exhaustive'] or checked['selected'] is not None:
        return False
    references = query_references(case, args['evidence_ids'])
    queries = {q['id']: q for q in case['queries']}
    return all(o['evidence_id'] in references
               and queries.get(o['evidence_id'], {}).get('status') == 'SUCCEEDED'
               for o in checked['observations'])


def canonical_selected_target(args,case):
    """Fill an omitted field only from the code's unique cited value match."""
    if args.get('selected_target') is not None:return args,None
    checks=[r['result']for r in case['evidence'].values()if r.get('tool')=='check_target_candidates']
    if not checks:return args,None
    resolution=checks[-1];selected=resolution.get('selected')
    if (not selected or not resolution.get('exhaustive')
            or resolution.get('reason')!='UNIQUE_VALUE_MATCH'
            or resolution.get('matches')!=[selected]):return args,None
    references=query_references(case,args['evidence_ids'])
    observed=[o for o in resolution.get('observations',[])if o['candidate']==selected]
    if len(observed)!=1 or observed[0].get('evidence_id')not in references:return args,None
    return {**args,'selected_target':selected},{'basis':'UNIQUE_CITED_NATIVE_VALUE_MATCH','selected':selected,
        'query_id':observed[0]['evidence_id']}


def candidate_resolution(args, case):
    if not case['context'].get('candidate_inventory'):
        return None
    checks = [r['result'] for r in case['evidence'].values()
              if r.get('tool') == 'check_target_candidates']
    if not checks:
        if (args.get('selected_target') is None and args.get('verdict_class')=='UNRESOLVED'
                and args.get('verdict')=='not found' and args.get('undecided')):
            refs=query_references(case,args['evidence_ids'])
            if any(q['id']in refs and q.get('status')=='SUCCEEDED' for q in case['queries']):
                return {'selected':None,'matches':[],'exhaustive':False,'observations':[],
                        'reason':'UNMEASURED_TARGET_EXPLICIT_HANDOFF'}
        raise ValueError('CHECK_TARGET_CANDIDATES_BEFORE_CONCLUSION')
    resolution = checks[-1]
    if args['selected_target'] != resolution.get('selected'):
        raise ValueError('TARGET_NOT_A_UNIQUE_OBSERVED_MATCH')
    unresolved = (args.get('verdict_class') == 'UNRESOLVED'
                  if case['context'].get('conclusion_contract') == 'question-first-v1'
                  else args.get('verdict') == 'not found')
    if (resolution.get('selected') is None and not unresolved
            and not conditional_definition(args, case, resolution)):
        raise ValueError('UNSELECTED_TARGET_REQUIRES_SIDE_BY_SIDE_FINDINGS_AND_EXACT_UNDECIDED_DISTINCTION')
    return resolution


def source_comparison_required(intake):
    # Authoritative comparison fields, not incidental words such as "source
    # rows" in a calculation explanation or "application load" in a job name.
    return any((intake.get(field) or {}).get('kind') == 'SOURCE_SYSTEM'
               for field in ('compared_with', 'comparison_context'))


def source_comparison(args, case):
    if not source_comparison_required(case['intake']):
        return
    # Native addresses distinguish application SQL from Fabric SQL endpoints.
    # A missing optional SOR declaration does not erase an admitted source route.
    layers = case['context'].get('layers', {})
    source = {key: {o['id'] for o in layer.get('objects', [])
                    if o.get('id', '').startswith('sql://')}
              for key, layer in layers.items()}
    source = {key: ids for key, ids in source.items() if ids}
    declaration = case['context'].get('system_of_record', {})
    if declaration.get('layer') in layers and declaration.get('asset_id'):
        source.setdefault(declaration['layer'], set()).add(declaration['asset_id'])
    requested = (case['intake'].get('compared_with') or {}).get('source')
    if requested:
        # When intake names an exact source object, another source won't do.
        node = next((n for n in case['context'].get('path', {}).get('nodes', [])
                     if n['id'] == requested), {})
        asset = node.get('properties', {}).get('asset_id')
        if asset is None and requested.startswith('sql://'):
            asset=requested
        if asset is None and declaration.get('declared') is True:
            asset=declaration.get('asset_id')
        # Older admitted contexts omit the source node but bind a single
        # application route. Reuse that native route, never a name match.
        if asset is None and len(source)==1:
            pass  # Single admitted database route, possibly multiple tables.
        elif asset is None:
            source={}
        else:
            source = {key: {identity for identity in ids
                            if identity == asset or identity.startswith(asset.rstrip('/') + '/object/')}
                      for key, ids in source.items()}
        source = {key: ids for key, ids in source.items() if ids}
    references = query_references(case, args['evidence_ids'])
    reads = [q for q in case['queries'] if q['id'] in references
             and q.get('purpose') in ('compare', 'recreate', 'record', 'history', 'lookup')
             and set(q.get('asset_ids', [])) & source.get(q['layer'], set())
             and not __import__('re').search(r'\b(?:sys\.|INFORMATION_SCHEMA\.|DESCRIBE\b|SHOW\b)', q.get('text', ''), __import__('re').I)]
    if args.get('verdict_class') == 'UNRESOLVED' and args.get('undecided'):
        return  # An honest missing-source handoff is not a source conclusion.
    if not any(q.get('status') == 'SUCCEEDED' and not q.get('result', {}).get('truncated') for q in reads):
        raise ValueError('SOURCE_COMPARISON_REQUIRES_CITED_SOURCE_READ: compare the requested application/source using its admitted native data route before concluding; metadata or warehouse reads alone do not establish the source value. If unavailable, retain checked findings and the precise missing source fact in an UNRESOLVED handoff.')
