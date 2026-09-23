"""Compiled-candidate reuse within one declared scope and immutable context version."""
import json
from .onboarding import digest


class RedundantRead(ValueError):
    def __init__(self, observation):
        super().__init__('Identical compiled candidate and declared scope already observed in this context version; reuse the attached receipt and result')
        self.observation = observation


def normalized(tool, query):
    if tool == 'bounded_sql':
        import sqlglot
        return [(token.token_type.name, token.text) for token in sqlglot.tokenize(query, read='tsql')]
    if tool == 'bounded_dax':
        from .semantic_graph import tokenize
        tokens, gaps = tokenize(query)
        return None if gaps else tokens
    return None


def key(tool, plan, request, version, scope_hash=None):
    compiled = request.get('compiled_read')
    if compiled is None or version is None:
        return None
    return digest({'tool':tool, 'compiled_read':compiled,
        'resolved_assets':request.get('asset_ids'), 'parameters':request.get('parameters'),
        'context_version':version,
        'declared_scope':{k:v for k,v in plan.items() if k!='query'}, 'run_scope_hash':scope_hash,
        'context_hash':request['context_hash'], 'policy_hash':request['policy_hash']})



def check(store, state, tool, plan, request):
    version = state.get('discovery_version')
    scope_hash = state.get('scope_hash')
    wanted = key(tool, plan, request, version, scope_hash)
    if wanted is None:
        return
    from .receipt_integrity import verify
    with store.connect() as db:
        for observation in state['observations']:
            if (observation.get('tool') != tool or observation.get('status') != 'COMPLETED'
                    or observation.get('completeness') != 'COMPLETE_RESPONSE'
                    or observation.get('read_context_version') != version
                    or observation.get('read_scope_hash') != scope_hash):
                continue
            if verify(db,tool,observation['id'])['state'] != 'SEALED':
                continue
            row = db.execute('SELECT request FROM flexible_diagnostics WHERE id=?',(observation['id'],)).fetchone()
            if row:
                previous = json.loads(row['request'])
                if key(tool,previous['plan'],previous,version,observation.get('read_scope_hash')) == wanted:
                    raise RedundantRead(observation)
