"""Explicit address of a quantity read; absence is never a baseline."""
import copy


def baseline(restrictions):
    return {'kind':'BASELINE','restrictions':copy.deepcopy(restrictions)}


def cell(address):
    return {'kind':'CELL','cell':copy.deepcopy(address)}


def validate(address,measure_id=None):
    if not isinstance(address,dict):raise ValueError('Quantity read requires an explicit address kind')
    if address.get('kind')=='CELL' and set(address)=={'kind','cell'}:
        from .report_cell import validate as validate_cell
        validate_cell(address['cell'],measure_id or address['cell'].get('measure_id'))
    elif address.get('kind')=='RECORD_PRESENCE':
        from .record_presence import validate_address
        validate_address(address)
    elif address.get('kind')=='BINDING_SAMPLE':
        from .binding_sample import validate_address
        validate_address(address)
    elif address.get('kind')=='BASELINE' and set(address)=={'kind','restrictions'}:
        from .onboarding import encoded
        if (not isinstance(address['restrictions'],list)
                or any(not isinstance(r,dict) or not r for r in address['restrictions'])
                or len(encoded(address['restrictions']))>64000):
            raise ValueError('Baseline address requires its bounded evaluated restriction set')
        # The query compiler validates predicate grammar. This contract records
        # it without interpreting one adapter's predicate language as another's.
    else:raise ValueError('Quantity read requires an explicit address kind')
    return address
