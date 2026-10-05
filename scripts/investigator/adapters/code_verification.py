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
        application=[a for a in assets if a.get('kind')=='SqlObject' and a['id']==location]
        if application:
            source=process.config.get('sql',{});a=application[0];meta=a['metadata']
            declared='sql://'+source.get('server','')+'/'+source.get('database','')
            if (len(application)!=1 or a['parent_id']!=declared or meta.get('schema_name')!=source.get('visibility_schema')
                    or meta.get('type_desc')!='USER_TABLE' or not source.get('auth',{}).get('account')):
                unavailable.append({'location':location,'reason':'Application object leaves the isolated declared connection or schema'});continue
            objects[location]={'asset_id':a['id'],'surface':'APPLICATION_SQL','connection':source['server'],
                'database':source['database'],'catalog':copy.deepcopy(a)}
            continue
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
        if context!=self.context or context!=self.process.model['context_id']:
            raise ValueError('Verification retained context differs from the actual probe context')
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
        endpoints={(o.get('surface','FABRIC_SQL'),o['connection'],o['database']) for o in resolved}
        if len(endpoints)!=1:raise NotImplementedError('Expression spans distinct declared connections; no cross-connection query')
        surface,connection,database=next(iter(endpoints))
        configured=(self.process.config.get('sql',{}).get('server') if surface=='APPLICATION_SQL' else
            ((self.process.config.get('fabric') or {}).get('sql_reader') or {}).get('server'))
        if connection!=configured:raise ValueError('Declared endpoint differs from isolated SQL reader connection')
        catalog={name:o['catalog'] for name,o in zip(names,resolved)}
        query=compile_quantity(relation,column,catalog)
        layer={'id':resolved[0]['asset_id'],'binding':{'provenance':'INFERRED_FROM_CODE'},
            'endpoint_evidence':copy.deepcopy(resolved[0].get('endpoint_evidence'))}
        return {'layer':layer,'compiled':{'catalog':list(catalog.values()),'query':query,
            'database':database,'source_column':column,'read_address':cell_address(cell)},
            'surface':surface,'context':context,'cell':copy.deepcopy(cell),'precision':copy.deepcopy(precision)}

    def execute(self,side,plan):
        probe=attest(self._application(plan) if plan['surface']=='APPLICATION_SQL' else
            self.process._evaluate_lower(plan['layer'],self.measure_id,plan['compiled']))
        result={k:copy.deepcopy(plan[k]) for k in ('context','cell','precision')}
        result.update(status='COMPLETED' if probe.status=='OBSERVED' else 'FAILED',
            evidence=copy.deepcopy(probe.evidence),reason=probe.reason,failure=copy.deepcopy(probe.failure))
        if probe.status!='OBSERVED':return result
        result['evidence']['execution_surface']=copy.deepcopy(probe.execution_surface)
        if probe.evidence.get('context_id')!=plan['context'] or probe.evidence.get('read_address')!=cell_address(plan['cell']):
            result.update(status='FAILED',reason='Original probe receipt context or cell address differs')
            return result
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


    def _application(self,plan):
        """Use the existing guarded application SQL route and retained receipt."""
        from ..flexible_tools import run
        from ..process_debugging import Probe
        from ..process_quantity import quantity
        from application_sql_surface import read,ENGINE
        from .microsoft_process import SQL_TYPES
        model=self.process.model;compiled=plan['compiled'];source=self.process.config['sql']
        request={'model_id':model['id'],'revision':model['revision'],'context_id':model['context_id'],
            'query':compiled['query'],'max_rows':20,'read_address':compiled['read_address']}
        execute=lambda:run(self.process.store,request,self.process.config,'bounded_sql',
            lambda statement:read(self.process.config,statement))
        result=self.process.meter_read('bounded_sql',execute) if self.process.meter_read else execute()
        surface={'engine':ENGINE,'connection':'sql://'+source['server'],
            'object':source['database'],'identity':source['auth']['account']}
        body=result.get('result') or {}
        if result['status']!='COMPLETED':
            return Probe('UNAVAILABLE',plan['layer']['id'],execution_surface=surface,
                reason='Application verification did not complete; original receipt retained.',
                failure={'interface':'APPLICATION_SQL','receipt_id':result['id'],'read_status':result['status'],
                    'error_type':body.get('error_type'),'codes':[],'specificity':'SPECIFIC'})
        return Probe('OBSERVED',plan['layer']['id'],execution_surface=surface,query=compiled['query'],
            value=quantity(body['rows']),evidence={'id':result['id'],'tool':'bounded_sql',
                'values':body['rows'],'completeness':body['completeness'],'request_hash':result['request_hash'],
                'context_id':request['context_id'],'read_address':request['read_address'],
                'measure_id':self.measure_id,'test_purpose':'VERIFY_LINEAGE_BINDING'},
            surface_report=body.get('surface_report'),surface_reportable=('identity','engine','object'),
            surface_report_types=SQL_TYPES,surface_report_binding=body.get('surface_report_binding'))
