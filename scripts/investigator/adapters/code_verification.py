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


def resolve_objects(process,context,schemas):
    """Exact physical locations, then each container's declared SQL endpoint.

    Metadata lookup is metered by the existing process adapter. No display-name
    match, guessed endpoint, or global search can manufacture a resolved object.
    """
    from .declared_chain import TYPES
    assets=[a for a in context.get('assets',[]) if a.get('availability')=='CURRENT']
    endpoints={};objects={};unavailable=[]
    for location,columns in schemas.items():
        matches=[a for a in assets if a.get('kind')=='LakehouseTable' and a.get('metadata',{}).get('location')==location]
        if len(matches)!=1:
            unavailable.append({'location':location,'reason':'Exact table location is absent or ambiguous in the approved context'});continue
        asset=matches[0];parent=asset['parent_id'];parts=parent.removeprefix('fabric://').split('/')
        if len(parts)!=2 or parts[0]!=process.config['fabric']['workspace_id']:
            unavailable.append({'location':location,'reason':'Declared container leaves approved workspace'});continue
        if parent not in endpoints:
            if process.read_endpoint is None:raise ValueError('Declared endpoint metadata reader unavailable')
            endpoints[parent]=process.read_endpoint({'workspace':parts[0],'lakehouse':parts[1]})
        declaration=endpoints[parent];properties=declaration.get('properties',{}).get('sqlEndpointProperties',{})
        endpoint_id=parent.rsplit('/',1)[0]+'/'+str(properties.get('id'))
        matches=[a for a in assets if a.get('kind')=='SQLEndpoint' and a['id']==endpoint_id]
        server=process.config['fabric']['sql_reader']['server']
        if declaration.get('id')!=parts[1] or properties.get('connectionString')!=server or len(matches)!=1:
            unavailable.append({'location':location,'reason':'Endpoint declaration does not establish the approved server and discovered object'});continue
        name=asset['name'];schema,table=name.split('.',1) if '.' in name else ('dbo',name)
        objects[location]={'asset_id':asset['id'],'connection':server,'database':matches[0]['name'],
            'endpoint_evidence':{'container':parent,'endpoint_id':endpoint_id,'server':server},
            'catalog':{'id':asset['id'],'provenance':'DECLARED_BY_DEFINITION','metadata':{
                'schema_name':schema,'name':table,'type_desc':'USER_TABLE','columns':[
                    {'name':c,'data_type':TYPES.get(t,t if t in ('smallint','tinyint') else 'sql_variant')} for c,t in columns.items()]}}}
    return objects,unavailable


class VerificationRoute:
    def __init__(self,process,*,objects,context,measure_id,quantity_column,restrictions):
        self.process=process;self.objects=copy.deepcopy(objects)
        self.context=context;self.measure_id=measure_id;self.quantity_column=quantity_column
        self.restrictions=copy.deepcopy(restrictions)

    def compile(self,proposal,side,context,cell,precision):
        proposal=validate(proposal);validate_cell(cell,self.measure_id)
        if context!=self.context:raise ValueError('Verification retained context differs')
        if self.restrictions or cell['mode']!='UNGROUPED':
            raise NotImplementedError('Filtered or grouped lower comparison is not supported; no verification read')
        if side not in ('TARGET','SOURCE'):raise ValueError('Unknown verification side')
        table=proposal['target']['table'];column=proposal['target']['column']
        if column!=self.quantity_column:
            raise NotImplementedError('This proposal is not the quantity established by the selected cell; no substitute measure is invented')
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
        layer={'id':resolved[0]['asset_id'],'binding':{'provenance':'INFERRED_FROM_CODE'},
            'endpoint_evidence':copy.deepcopy(resolved[0].get('endpoint_evidence'))}
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
        else:
            try:
                if isinstance(value,bool):raise ValueError('Boolean is not an additive quantity')
                number=Decimal(str(value))
                if not number.is_finite():raise ValueError('Nonfinite quantity')
            except (ValueError,TypeError,ArithmeticError):
                result.update(status='FAILED',reason='Probe did not return an additive scalar quantity')
            else:result['quantity']={'state':'NUMBER','value':str(value)}
        return result
