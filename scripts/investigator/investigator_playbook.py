"""Read-only tools exposed by the code-owned investigation phase."""
DETAILS = frozenset({'get_evidence', 'get_evidence_part'})
TOOLS = {
    'recreate': DETAILS | {'visual_context', 'filters_on', 'path_to_source'},
    'quick_facts': DETAILS | {'node_facts', 'last_run', 'last_refresh', 'freshness', 'refresh_facts'},
    'investigate': DETAILS | {'node_facts', 'last_run', 'last_refresh', 'freshness', 'definition_of', 'definition_diff', 'compare_layers',
                              'check_explanation', 'path_to_source', 'visual_context', 'filters_on',
                              'table_columns', 'as_of'},
    'deliver': DETAILS,
}


def allowed(step):
    if step not in TOOLS:
        raise ValueError('UNKNOWN_PLAYBOOK_STEP')
    return frozenset(TOOLS[step])


def require(step, tool):
    if tool not in allowed(step):
        raise ValueError('TOOL_NOT_PERMITTED_FOR_CODE_STEP:' + step + ':' + tool)
