"""Version-pinned budget journal dispatch; archived producers remain unchanged."""
from . import budget_delta, budget_delta_v2

def implementation(tape):
    if budget_delta_v2.enabled(tape): return budget_delta_v2
    if budget_delta.enabled(tape): return budget_delta
    return None

def enabled(tape): return implementation(tape) is not None

def prepare(tape,database,environment):
    module=implementation(tape)
    if module: module.prepare(tape,database,environment)

def prepare_memory(tape,db,environment):
    module=implementation(tape)
    if module: module.prepare_memory(tape,db,environment)

def checkpoint(tape,db,environment,owned):
    return implementation(tape).checkpoint(tape,db,environment,owned)
