"""Evaluator-owned fixture states; retained context IDs remain evidence identities."""
import copy,json,re
from pathlib import Path
from uuid import UUID
from .onboarding import ModelStore,Conflict,digest


def validate_case_pin(case):
    pin=case.get('context_pin')
    if not isinstance(pin,dict) or set(pin)!={'context_id','hash'}:raise ValueError('Context provenance pin required')
    UUID(pin['context_id'])
    if not isinstance(pin['hash'],str) or not re.fullmatch('[0-9a-f]{64}',pin['hash']):raise ValueError('Invalid immutable context hash')
    return pin


def state_definition(fixture,name):
    rows=[r for r in fixture.get('fixture_states',[]) if r.get('id')==name]
    if len(rows)!=1:raise Conflict('Unknown or ambiguous fixture state: '+str(name))
    return rows[0]


def validate_case_state(case):
    name=case.get('fixture_state')
    if not isinstance(name,str) or not re.fullmatch('[a-z][a-z0-9-]{0,99}',name):raise ValueError('Fixture state required')
    return name


def load_case(path):
    case=json.loads(Path(path).read_text(encoding='utf-8-sig'));validate_case_state(case);return case


def require_state(case,established,fixture):
    name=validate_case_state(case);definition=state_definition(fixture,name)
    if established.get('name')!=name:
        raise Conflict('Fixture state mismatch: expected '+name+', observed '+str(established.get('name')))
    if established.get('definition_hash')!=digest(definition):raise Conflict('Fixture state definition differs: '+name)


def approve_state_context(store,fixture,name,model_id,pin,*,approval_reference):
    """Explicit operator state approval, never inference from a context ID.

    Discovery approval/enablement/denies still govern execution. This records
    which fixture was established with that retained context. It neither
    recollects nor approves a new discovery policy.
    """
    validate_case_pin({'context_pin':pin});definition=state_definition(fixture,name)
    if not isinstance(approval_reference,str) or not approval_reference.strip():raise ValueError('State approval evidence required')
    selected=ModelStore(store.database,store.inventory,store.environment,context_pins={model_id:pin})
    if not selected.get(model_id)['enabled']:raise Conflict('Fixture context model disabled')
    with store.connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS acceptance_fixture_contexts (name TEXT, definition_hash TEXT, model_id TEXT, context_id TEXT, context_hash TEXT, approval_reference TEXT, approved_at TEXT DEFAULT CURRENT_TIMESTAMP)')
        db.execute('INSERT INTO acceptance_fixture_contexts(name,definition_hash,model_id,context_id,context_hash,approval_reference) VALUES(?,?,?,?,?,?)',
                   (name,digest(definition),model_id,pin['context_id'],pin['hash'],approval_reference))


def select_store(case_path,store,model_id,*,fixture,invoked_state=None,invoked_context=None):
    """Select latest explicitly approved context for a state, never a hand pin."""
    case=load_case(case_path);name=case['fixture_state'];definition=state_definition(fixture,name)
    if case.get('model_id')!=model_id:raise Conflict('Acceptance model differs from fixture ticket')
    if invoked_state is not None:require_state(case,invoked_state,fixture)
    with store.connect() as db:
        exists=db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='acceptance_fixture_contexts'").fetchone()
        rows=db.execute('SELECT * FROM acceptance_fixture_contexts WHERE name=? AND definition_hash=? AND model_id=? ORDER BY approved_at DESC,rowid DESC',
                        (name,digest(definition),model_id)).fetchall() if exists else []
        other_names=[r[0] for r in db.execute('SELECT DISTINCT name FROM acceptance_fixture_contexts WHERE model_id=? AND context_id=? AND context_hash=? ORDER BY name',
            (model_id,invoked_context.get('context_id'),invoked_context.get('hash'))).fetchall()] if exists and invoked_context is not None else []
    if invoked_context is not None:
        rows=[r for r in rows if r['context_id']==invoked_context.get('context_id') and r['context_hash']==invoked_context.get('hash')]
        if not rows and other_names:raise Conflict('Fixture state mismatch: expected '+name+', observed '+', '.join(other_names))
    if not rows:raise Conflict('No approved context for fixture state '+name)
    row=rows[0];pin={'context_id':row['context_id'],'hash':row['context_hash']}
    selected=ModelStore(store.database,store.inventory,store.environment,context_pins={model_id:pin});selected.get(model_id)
    selected.acceptance_fixture_state={'name':name,'definition_hash':digest(definition),'context':pin,'approval_reference':row['approval_reference']}
    return selected


def context_handles(workspace):
    """Discover captured stores, including aliases and newly added consumers.

    Walk the component graph, not a hand-maintained list of three setters.
    Ancestor detection prevents workspace/intake and runtime/governor cycles.
    No dictionaries, callables, transports or retained evidence are traversed.
    """
    result=[]
    links={'agent','runtime','governor','intake','screenshots','workspace'}
    def visit(owner,path,ancestors):
        if owner is None or id(owner) in ancestors:return
        attributes=vars(owner)
        if 'store' in attributes:result.append((path+'.store',owner))
        for name,value in sorted(attributes.items()):
            if name.startswith('_') or callable(value) or not hasattr(value,'__dict__'):continue
            if name in links or 'store' in vars(value):
                visit(value,path+'.'+name,ancestors|{id(owner)})
    visit(workspace,'workspace',set())
    return result


def assert_run_context(workspace):
    """Refuse before intake if any consumer escapes the selected fixture pin."""
    selection=getattr(workspace,'_acceptance_run',None)
    if selection is None:return None
    values={}
    for name,owner in context_handles(workspace):
        store=owner.store
        value={'database':str(Path(store.database).resolve()),
            'inventory':str(Path(store.inventory).resolve()),'environment':store.environment,
            'pins':copy.deepcopy(store.context_pins)}
        try:
            model=store.get(selection['model_id'])
            value.update(context_id=model['context_id'],context_hash=digest(model['context']),
                         revision=model['revision'],enabled=model['enabled'])
        except (ValueError,KeyError) as exc:value['error']=str(exc)
        values[name]=value
    expected=selection['handles']
    if set(values)!=set(expected) or any(values[k]!=expected[k] for k in values if k in expected):
        raise Conflict('Run context handles disagree: '+json.dumps(values,sort_keys=True))
    return copy.deepcopy(values)


def pin_run_context(workspace,case_path,*,fixture,invoked_state=None,invoked_context=None):
    """Only runner entry point: select from an approved fixture state and pin all consumers."""
    case=load_case(case_path);model_id=case['model_id']
    selected=select_store(case_path,workspace.store,model_id,fixture=fixture,
        invoked_state=invoked_state,invoked_context=invoked_context)
    handles=context_handles(workspace)
    if not handles:raise Conflict('Run has no context handles')
    # Pinning may select metadata, never move a consumer to another estate/database.
    storage=(selected.database.resolve(),selected.inventory.resolve(),selected.environment)
    for name,owner in handles:
        s=owner.store
        if (s.database.resolve(),s.inventory.resolve(),s.environment)!=storage:
            raise Conflict('Context handle points at another estate: '+name)
    for _,owner in handles:owner.store=selected
    model=selected.get(model_id)
    value={'database':str(selected.database.resolve()),'inventory':str(selected.inventory.resolve()),
        'environment':selected.environment,'pins':copy.deepcopy(selected.context_pins),
        'context_id':model['context_id'],'context_hash':digest(model['context']),
        'revision':model['revision'],'enabled':model['enabled']}
    workspace._acceptance_run={'model_id':model_id,'fixture_state':copy.deepcopy(selected.acceptance_fixture_state),
                              'handles':{name:copy.deepcopy(value) for name,_ in handles}}
    workspace.agent._acceptance_workspace=workspace
    assert_run_context(workspace)
    return selected


def declared_role_view(payload,fixture):
    """Dated grading view only. Never mutate old receipts, labels or outputs."""
    from .layer_roles import declarations
    roles=declarations([{k:r[k] for k in ('asset_id','role','business_name')} for r in fixture['layers']])
    view=copy.deepcopy(payload)
    labels=view.setdefault('layer_labels',{})
    for identity,role in roles.items():labels.setdefault(identity,{}).update(role)
    return view
