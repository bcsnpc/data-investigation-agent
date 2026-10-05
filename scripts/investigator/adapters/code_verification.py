"""Compile neutral code bindings into the existing isolated SQL probe route.

The caller supplies exact discovered locations and endpoint declarations. This
adapter performs no name search and never substitutes the verifier expression
for the untransformed input quantity in the investigation walk.
"""
import copy
from decimal import Decimal
from ..lineage_binding import validate
from ..report_cell import validate as validate_cell
from ..read_address import cell as cell_address
from ..transformation_sql import compile_quantity
from ..process_debugging import attest


class VerificationRoute:
    def __init__(self,process,*,objects,context,measure_id,restrictions):
        self.process=process;self.objects=copy.deepcopy(objects)
        self.context=context;self.measure_id=measure_id
        self.restrictions=copy.deepcopy(restrictions)

    def compile(self,proposal,side,context,cell,precision):
        proposal=validate(proposal);validate_cell(cell,self.measure_id)
        if context!=self.context:raise ValueError('Verification retained context differs')
        if self.restrictions or cell['mode']!='UNGROUPED':
            raise NotImplementedError('Filtered or grouped lower comparison is not supported; no verification read')
        if side not in ('TARGET','SOURCE'):raise ValueError('Unknown verification side')
        table=proposal['target']['table'];column=proposal['target']['column']
        relation=proposal['expression']['relation'] if side=='SOURCE' else {
            'kind':'SCAN','table':table,'columns':[column]}
        names=[s['table'] for s in proposal['sources']] if side=='SOURCE' else [table]
        try:resolved=[self.objects[name] for name in names]
        except KeyError as exc:raise ValueError('Exact code location is absent from approved object inventory: '+str(exc)) from exc
        endpoints={(o['connection'],o['database']) for o in resolved}
        if len(endpoints)!=1:raise NotImplementedError('Expression spans distinct declared connections; no cross-connection query')
        connection,database=next(iter(endpoints))
        configured=((self.process.config.get('fabric') or {}).get('sql_reader') or {}).get('server')
        if connection!=configured:raise ValueError('Declared endpoint differs from isolated SQL reader connection')
        catalog={name:o['catalog'] for name,o in zip(names,resolved)}
        query=compile_quantity(relation,column,catalog)
        layer={'id':resolved[0]['asset_id'],'binding':{'provenance':'INFERRED_FROM_CODE'}}
        return {'layer':layer,'compiled':{'catalog':list(catalog.values()),'query':query,
            'database':database,'source_column':column,'read_address':cell_address(cell)},
            'context':context,'cell':copy.deepcopy(cell),'precision':copy.deepcopy(precision)}

    def execute(self,side,plan):
        probe=attest(self.process._evaluate_lower(plan['layer'],self.measure_id,plan['compiled']))
        result={k:copy.deepcopy(plan[k]) for k in ('context','cell','precision')}
        result.update(status='COMPLETED' if probe.status=='OBSERVED' else 'FAILED',
            evidence=copy.deepcopy(probe.evidence),reason=probe.reason,failure=copy.deepcopy(probe.failure))
        if probe.status!='OBSERVED':return result
        result['evidence']['execution_surface']=copy.deepcopy(probe.execution_surface)
        value=probe.value
        if isinstance(value,dict) and set(value)=={'quantity'}:value=value['quantity']
        if value is None:result['quantity']={'state':'BLANK'}
        elif isinstance(value,(int,float,Decimal)) and not isinstance(value,bool):
            result['quantity']={'state':'NUMBER','value':str(value)}
        else:result.update(status='FAILED',reason='Probe did not return an additive scalar quantity')
        return result
