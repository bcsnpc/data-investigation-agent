"""Acceptance-file-owned immutable context selection, before any transport."""
import json,re
from pathlib import Path
from uuid import UUID
from .onboarding import ModelStore,Conflict


def validate_case_pin(case):
    pin=case.get('context_pin')
    if not isinstance(pin,dict) or set(pin)!={'context_id','hash'}:raise ValueError('Acceptance context pin is required')
    UUID(pin['context_id'])
    if not isinstance(pin['hash'],str) or not re.fullmatch('[0-9a-f]{64}',pin['hash']):raise ValueError('Invalid immutable context hash')
    return pin


def load_case(path):
    case=json.loads(Path(path).read_text(encoding='utf-8-sig'));validate_case_pin(case);return case


def require_context(case,established):
    expected=validate_case_pin(case)
    if established!=expected:
        raise Conflict('Acceptance context mismatch: expected '+expected['context_id']+' ('+expected['hash']+
                       '), observed '+str(established.get('context_id'))+' ('+str(established.get('hash'))+')')


def select_store(case_path,store,model_id,*,invoked_context=None):
    """The caller may not choose a successor. Current approval/denies still apply."""
    case=load_case(case_path);pin=case['context_pin']
    if invoked_context is not None:require_context(case,invoked_context)
    selected=ModelStore(store.database,store.inventory,store.environment,context_pins={model_id:pin})
    model=selected.get(model_id)
    from .onboarding import digest
    require_context(case,{'context_id':model['context_id'],'hash':digest(model['context'])})
    return selected
