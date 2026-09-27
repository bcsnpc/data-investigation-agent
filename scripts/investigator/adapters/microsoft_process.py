"""Microsoft Fabric/Power BI/Azure SQL adapter for the neutral process engine."""
import json
import hashlib
import re
from uuid import uuid4
from .. import context_search
from ..declared_pointer import resolve as resolve_declared
from ..flexible_tools import run as run_query
from ..model_context import assets
from ..process_debugging import Probe


SURFACE_IDENTITY='surface_identity'
# Service errors this surface reports only generically through Execute Queries.
# The same model's XMLA interface can expose the underlying failure.
GENERIC_SERVICE_ERRORS=frozenset(('DatasetExecuteQueriesError',))


def _quantity(rows):
    """One scalar from a one-row, one-column result, normalised so that equal
    numbers from different engines compare equal. Anything else is kept as is."""
    from decimal import Decimal,InvalidOperation
    if not isinstance(rows,list) or len(rows)!=1 or not isinstance(rows[0],dict) or len(rows[0])!=1:return rows
    cell=next(iter(rows[0].values()))
    value=cell.get('value') if isinstance(cell,dict) else cell
    if value is None:return {'quantity':None}
    try:number=Decimal(str(value))
    except (InvalidOperation,ValueError):return {'quantity':str(value)}
    return {'quantity':format(number.normalize(),'f') if number!=0 else '0'}


class MicrosoftProcessAdapter:
    def __init__(self,store,config,model,execute_native,execute_source,judge_definition=None,meter_read=None,
                 read_ingestion=None,lower_surface=None,read_failure_detail=None,execute_lower=None):
        self.store,self.config,self.model=store,config,model
        self.execute_native,self.execute_source=execute_native,execute_source
        self.judge_definition=judge_definition
        self.meter_read=meter_read
        self.read_ingestion=read_ingestion
        # Session state of an independent lower surface, established by the
        # caller before the run. Absent or not READY means undeclared.
        self.lower_surface=lower_surface
        # Another interface to the semantic surface, used only to obtain a more
        # specific failure than Execute Queries reports. Absent means undeclared.
        self.read_failure_detail=read_failure_detail
        # Executes an admitted request on the independent lower surface.
        self.execute_lower=execute_lower
        self._paths={}

    def capabilities(self):
        result={'resolve_measure_path','evaluate_scoped_quantity','presentation_context','job_history'}
        if self.judge_definition is not None:result.add('transformation_definition')
        if self.read_ingestion is not None:result.add('ingestion')
        if (self.lower_surface or {}).get('status')=='READY' and self.execute_lower is not None:
            result.add('independent_lower_surface')
        if self.read_failure_detail is not None:result.add('failure_detail')
        return result

    def capability_gaps(self):
        result={'presentation_freshness':
          'Presentation refresh history is unavailable to the isolated execution reader; it is not elevated for metadata access.'}
        if self.read_ingestion is None:
            result['ingestion']='No isolated metadata transport is configured for ingestion history.'
        if self.judge_definition is None:
            result['transformation_definition']='No governed definition-judgment provider is configured.'
        if self.read_failure_detail is None:
            result['failure_detail']='No second interface to the semantic surface is configured for failure detail.'
        surface=self.lower_surface or {}
        if surface.get('status')=='READY' and self.execute_lower is None:
            result['independent_lower_surface']='The lower-surface session is ready, but no reader transport is configured.'
        elif surface.get('status')!='READY':
            result['independent_lower_surface']=(
                'Sign-in required for '+str(surface.get('account') or 'the configured account')
                +' in profile '+str(surface.get('profile') or 'the configured profile')+'.'
                if surface.get('status')=='SIGN_IN_REQUIRED' else
                'The configured lower-surface profile holds a different account or tenant.'
                if surface.get('status')=='ACCOUNT_MISMATCH' else
                'No independent lower surface is configured.')
        return result

    def resolve_declared_source(self,declaration):
        context=context_search.latest(self.store)
        if not context:return {'status':'SCOPE_NOT_DISCOVERED','candidates':[],
                               'provenance':'DECLARED_BY_DEFINITION'}
        return resolve_declared(context['assets'],declaration)

    def _partition_binding(self,metadata):
        context=context_search.latest(self.store)
        if not context:return {'status':'SCOPE_NOT_DISCOVERED','candidates':[]}
        all_assets=context['assets'];by_id={a['id']:a for a in all_assets}
        coverage=context.get('coverage',{})
        def denied(scope):
            item=coverage.get(scope,{})
            return item.get('status')=='UNAVAILABLE' and item.get('error_type') in (
                'PermissionError','HTTPError','ForbiddenError')
        model_root=next((a['id'] for a in self.model['context'].get('model_assets',[])
                         if a.get('kind')=='SemanticModel'),None)
        definition=next((a for a in all_assets if a.get('parent_id')==model_root and
                         a.get('kind')=='DefinitionPart' and a.get('name')=='model.bim' and
                         a.get('availability')=='CURRENT'),None)
        table=next((a for a in metadata.get('assets',[]) if a.get('kind')=='SemanticTable'),None)
        partitions=(table or {}).get('metadata',{}).get('partitions',[])
        if not definition and model_root and denied(model_root+'/definition'):
            return {'status':'ACCESS_DENIED','scope_ids':[model_root],'candidates':[],
                    'reason':'The declared model definition was denied to the metadata identity.'}
        if not definition:
            complete=coverage.get(model_root+'/definition',{}).get('status')=='COMPLETE'
            return {'status':'NO_DECLARATION' if complete else 'DEFINITION_UNAVAILABLE','candidates':[],
                    'reason':('The complete retained model definition has no model.bim part.' if complete else
                              'Model definition coverage is incomplete; declaration absence is not established.')}
        if not partitions:
            return {'status':'NO_DECLARATION','candidates':[]}
        if len(partitions)!=1:
            return {'status':'UNSUPPORTED_DECLARATION','candidates':[],
                    'reason':'Multiple semantic partitions require an explicit partition-selection rule.'}
        source=partitions[0].get('source',{});expression_name=source.get('expressionSource')
        try:document=json.loads(definition['metadata']['content'])['model']
        except (KeyError,TypeError,ValueError):
            return {'status':'DEFINITION_UNAVAILABLE','candidates':[],
                    'reason':'The retained model definition could not be decoded.'}
        if not expression_name:return {'status':'NO_DECLARATION','candidates':[]}
        expressions={x.get('name'):x.get('expression') for x in document.get('expressions',[])}
        expression=expressions.get(expression_name)
        if expression is None:
            return {'status':'DEFINITION_UNAVAILABLE','candidates':[],
                    'reason':'The partition references an expression absent from the retained definition.'}
        if isinstance(expression,list):expression='\n'.join(expression)
        match=re.search(r'Sql\.Database\(\s*"([^"]+)"\s*,\s*"([^"]+)"',expression or '')
        if not match:
            return {'status':'UNSUPPORTED_DECLARATION','candidates':[],
                    'reason':'The declared partition connection is outside the supported Sql.Database form.'}
        workspace=self.config['fabric']['workspace_id'];endpoint='fabric://'+workspace+'/'+match.group(2)
        if endpoint not in by_id:return {'status':'SCOPE_NOT_DISCOVERED','scope_ids':[endpoint],'candidates':[]}
        relations=[e for e in context.get('graph',{}).get('edges',[]) if e.get('source')==endpoint
                   and e.get('relation')=='NATIVE_CASCADEDELETE' and by_id.get(e.get('target'),{}).get('kind')=='Lakehouse']
        roots=sorted({e['target'] for e in relations})
        if not roots:
            status='ACCESS_DENIED' if denied(model_root+'/relations/upstream') else 'SCOPE_NOT_DISCOVERED'
            return {'status':status,'scope_ids':[endpoint],'candidates':[],
                    'reason':('The native item-relation cross-check was denied to the metadata identity.'
                              if status=='ACCESS_DENIED' else 'No native item relation resolved the declared endpoint scope.')}
        labels=[source.get('schemaName','')+'.'+source.get('entityName',''),source.get('entityName','')]
        labels=[x.lstrip('.') for x in labels if x.strip('.')]
        offset=definition['metadata']['content'].find(str(source.get('entityName','')))
        declaration={'scope_ids':roots,'target_labels':labels,
            'target_kinds':['LakehouseTable'],'definition_asset_id':definition['id'],
            'declared_connection_asset_id':endpoint}
        if offset>=0:declaration['definition_offset']=offset
        resolved=self.resolve_declared_source(declaration)
        # What the definition declares about the source partition and security.
        # A lower-layer quantity is compiled from these declarations only.
        resolved['declared_partition']={'schema_name':source.get('schemaName'),'entity_name':source.get('entityName'),
            'source_type':source.get('type'),'mode':partitions[0].get('mode'),'partition_count':len(partitions)}
        resolved['declared_role_count']=len(document.get('roles') or [])
        resolved['relation_cross_check']={'status':'AGREES' if resolved['status']=='RESOLVED' else 'NO_UNIQUE_AGREEMENT',
            'relations':[{'source':e['source'],'target':e['target'],'relation':e['relation']} for e in relations]}
        return resolved

    def resolve_path(self,measure_id):
        if measure_id in self._paths:return self._paths[measure_id]
        result=context_search.measure_path(self.store,self.model,measure_id)
        metadata=result;measure=metadata['measure']
        gaps=metadata.get('gaps',[])
        binding=self._partition_binding(metadata) if self.store is not None else {'status':'NO_DECLARATION','candidates':[]}
        layers=[{'id':measure['parent_id'],'kind':'presentation','measure':measure}]
        if binding.get('status')=='RESOLVED':
            referenced_columns=[a for a in metadata.get('assets',[]) if a.get('kind')=='SemanticColumn']
            expression=measure.get('metadata',{}).get('expression','')
            if isinstance(expression,list):expression='\n'.join(expression)
            simple=re.fullmatch(r'\s*SUM\s*\(\s*(?:\'((?:\'\'|[^\'])+)\'|([A-Za-z_][\w]*))\s*\[((?:\]\]|[^\]])+)\]\s*\)\s*',expression,re.I)
            if simple:
                table_name=(simple.group(1) or simple.group(2)).replace("''", "'")
                column_name=simple.group(3).replace(']]',']')
                column=next((a for a in referenced_columns if a.get('name')==column_name),None)
                # Column declarations travel on the referenced SemanticColumn
                # assets (name, sourceColumn, dataType), as the definition states them.
                declared=[dict(a.get('metadata',{}),name=a.get('name')) for a in referenced_columns]
                layers.append({'id':binding['asset']['id'],'kind':'declared_source','measure':measure,
                    'semantic_table':table_name,'semantic_column':column_name,
                    'declared_columns':declared,
                    'binding':binding,'definition_asset_id':binding['definition_asset_id']})
                gaps=[g for g in gaps if g.get('reason')!='UNRESOLVED_PARTITION_IDENTITY']
            context=context_search.latest(self.store);edges=(context or {}).get('graph',{}).get('edges',[])
            upstream=[]
            for edge in edges:
                if edge.get('source')!=binding['asset']['id'] or edge.get('relation')!='DERIVED_FROM':continue
                target=next((a for a in (context or {}).get('assets',[]) if a['id']==edge.get('target')),None)
                if not target:continue
                resolved=self.resolve_declared_source({'scope_ids':[target['parent_id']],
                    'target_labels':[target['name']],'target_kinds':[target['kind']]})
                upstream.append({'status':resolved['status'],'asset':resolved.get('asset'),
                    'candidates':resolved['candidates'],'provenance':'DECLARED_BY_DEFINITION',
                    'definition_evidence':edge.get('evidence',[])})
            binding['upstream_declarations']=upstream
            binding['external_source_declaration']={'status':'CAPABILITY_NOT_IMPLEMENTED',
                'reason':'Application-source declaration inspection is not implemented for this path; absence is not established.'}
        partition_gap=next((g for g in gaps if g.get('reason')=='UNRESOLVED_PARTITION_IDENTITY'),None)
        missing=(partition_gap or next(iter(gaps),None) or {}).get('detail')
        if partition_gap:
            table=next((a for a in metadata.get('assets',[]) if a.get('kind')=='SemanticTable'),{})
            partitions=table.get('metadata',{}).get('partitions',[])
            source=partitions[0].get('source',{}) if partitions else {}
            label='.'.join(str(source[k]) for k in ('schemaName','entityName') if source.get(k))
            missing=(f'The partition source label {label!r} for {table.get("name","the semantic table")!r} '
                     'has no stable discovered asset binding, so no lower-layer quantity can be compiled under the declared scope.')
        if binding.get('status')=='AMBIGUOUS':
            missing='The declared source reference is ambiguous within its declared connection scope: '+', '.join(x['id'] for x in binding['candidates'])+'.'
        elif binding.get('status') not in ('RESOLVED','NO_DECLARATION'):
            missing='The definition declares a source connection, but its scope could not be resolved: '+binding['status']+'.'
        path={'layers':layers,
                'boundary':measure['parent_id'],
                'stopped_by':'CAPABILITY_UNAVAILABLE' if gaps else 'REACHED',
                'missing_comparable_quantity':missing,
                'evidence':{'id':'path-'+str(uuid4()),'tool':'context','completeness':'PARTIAL' if gaps else 'COMPLETE_RESPONSE',
                            'metadata':metadata,'declared_source_binding':binding}}
        self._paths[measure_id]=path
        return path

    def evaluate(self,layer,measure_id,scope):
        measure=next(a for a in assets(self.model['context']) if a['id']==measure_id)
        reader=((self.config or {}).get('fabric') or {}).get('native_reader') or {}
        # The declared identity is what we intend to connect as; the surface's
        # own USERPRINCIPALNAME() answer is what establishes it. Power BI does
        # not report which model it served, so the object stays unattested.
        semantic_surface={'engine':'POWER_BI_DAX','connection':self.model['workspace'],
                          'object':self.model['native_id'],'identity':reader.get('account')}
        name=measure['name'].replace(']',']]')
        identity=f',"{SURFACE_IDENTITY}",USERPRINCIPALNAME()'
        query=f'EVALUATE ROW("baseline", [{name}]{identity})'
        if layer.get('kind')=='declared_source':
            if scope.get('filters'):
                return Probe('NOT_COMPARABLE',layer['id'],reason='Declared source comparison does not yet translate filtered scope faithfully.')
            if 'independent_lower_surface' in self.capabilities():
                compiled,refusal=self._lower_quantity(layer,scope)
                if compiled:return self._evaluate_lower(layer,measure_id,compiled)
                layer=dict(layer,lower_refusal=refusal)
            table=layer['semantic_table'].replace("'","''");column=layer['semantic_column'].replace(']',']]')
            query=f'EVALUATE ROW("baseline", SUM(\'{table}\'[{column}]){identity})'
        if scope.get('filters'):
            from ..native_diagnostics import build as build_native
            native_plan={'model_id':self.model['id'],'revision':self.model['revision'],
                'context_id':self.model['context_id'],'measure_ids':[measure_id],
                'filters':scope['filters'],'dimension_id':None,'include_dependencies':False}
            native=build_native(self.model,native_plan)['query'].removeprefix('EVALUATE ')
            query='EVALUATE ADDCOLUMNS('+native+identity+')'
        plan={'model_id':self.model['id'],'revision':self.model['revision'],
              'context_id':self.model['context_id'],'query':query,'max_rows':20,
              'surface_report':{'identity':SURFACE_IDENTITY}}
        execute=lambda:run_query(self.store,plan,self.config,'bounded_dax',self.execute_native)
        result=self.meter_read('bounded_dax',execute) if self.meter_read else execute()
        if result['status']!='COMPLETED':
            body=result.get('result') or {};code=body.get('service_error_code')
            failure={'interface':'EXECUTE_QUERIES','receipt_id':result.get('id'),'read_status':result['status'],
                     'error_type':body.get('error_type'),'http_status':body.get('http_status'),
                     'codes':[code] if isinstance(code,str) else [],
                     'specificity':('GENERIC' if code in GENERIC_SERVICE_ERRORS else
                                    'UNCERTAIN' if result['status']=='INTERRUPTED' else 'SPECIFIC')}
            return Probe('UNAVAILABLE',layer['id'],reason='The presentation reader could not establish a baseline.',
                         query=query,execution_surface=semantic_surface,failure=failure)
        rows=result['result']['rows'];value=_quantity(rows)
        report=result['result'].get('surface_report')
        definition_check=layer.get('kind')=='declared_source'
        return Probe('NOT_COMPARABLE' if definition_check else 'OBSERVED',layer['id'],evidence={'id':result['id'],'tool':'bounded_dax',
            'completeness':result['result']['completeness'],'values':rows,
            'request_hash':result['request_hash'],
            'measure_id':measure_id,'dimension_id':None,
            'test_purpose':'CHECK_DECLARED_SOURCE_DEFINITION' if definition_check else 'ESTABLISH_BASELINE',
            **({'binding_provenance':(layer.get('binding') or {}).get('provenance'),
                'independent_read_refused':layer.get('lower_refusal')} if definition_check else {})},
            value=value,query=query,
            reason='NO_INDEPENDENT_LOWER_READ' if definition_check else None,
            execution_surface=semantic_surface,surface_report=report,surface_reportable=('identity',))

    def _lower_quantity(self,layer,scope):
        """Compile the declared-source quantity for an independent surface, or say why not.

        Faithful equivalence only: the measure is a plain SUM over one semantic
        column (checked when the layer was resolved). The partition is a single
        whole-entity partition. The column declares a source column. The model
        declares no security roles that could filter one side and not the other.
        The SQL endpoint is declared by the binding. Anything else is refused;
        nothing is approximated or matched by name.
        """
        if scope.get('filters'):
            return None,'Declared source comparison does not yet translate filtered scope faithfully.'
        binding=layer.get('binding') or {}
        partition=binding.get('declared_partition') or {}
        if binding.get('status')!='RESOLVED':return None,'The declared source binding is not resolved.'
        if partition.get('partition_count')!=1 or partition.get('source_type') not in (None,'entity'):
            return None,'The source partition is not a single whole-entity partition.'
        if not partition.get('schema_name') or not partition.get('entity_name'):
            return None,'The partition does not declare its source schema and entity.'
        if binding.get('declared_role_count',1)!=0:
            return None,'The model declares security roles that could filter one surface and not the other.'
        column=next((c for c in layer.get('declared_columns',[]) if c.get('name')==layer.get('semantic_column')),None)
        if not column or not column.get('sourceColumn') or column.get('type')=='calculated' or column.get('expression'):
            return None,'The measured column does not declare a physical source column.'
        context=context_search.latest(self.store) or {}
        endpoint=next((a for a in context.get('assets',[]) if a.get('id')==binding.get('declared_connection_asset_id')
                       and a.get('kind')=='SQLEndpoint'),None)
        if not endpoint:return None,'The binding declares no SQL endpoint for the source.'
        from ..source_diagnostics import quote
        types={'int64':'bigint','double':'float','decimal':'decimal','string':'nvarchar','boolean':'bit','dateTime':'datetime2'}
        columns=[{'name':c['sourceColumn'],'data_type':types.get(c.get('dataType'),'sql_variant')}
                 for c in layer.get('declared_columns',[]) if c.get('sourceColumn') and c.get('type')!='calculated']
        catalog=[{'id':layer['id'],'provenance':'DECLARED_BY_DEFINITION',
                  'metadata':{'schema_name':partition['schema_name'],'name':partition['entity_name'],
                              'type_desc':'USER_TABLE','columns':columns}}]
        query=('SELECT SUM('+quote(column['sourceColumn'])+') AS '+quote('quantity')+' FROM '
               +quote(partition['schema_name'])+'.'+quote(partition['entity_name']))
        return {'catalog':catalog,'query':query,'database':endpoint['name'],'source_column':column['sourceColumn']},None

    def _evaluate_lower(self,layer,measure_id,compiled):
        reader=((self.config or {}).get('fabric') or {}).get('sql_reader') or {}
        surface={'engine':'FABRIC_SQL','connection':'sql://'+str(reader.get('server')),'object':compiled['database'],
                 'identity':reader.get('account')}
        plan={'model_id':self.model['id'],'revision':self.model['revision'],'context_id':self.model['context_id'],
              'query':compiled['query'],'max_rows':20}
        execute=lambda:run_query(self.store,plan,self.config,'bounded_fabric_sql',
            lambda request:self.execute_lower(compiled['database'],request),catalog=compiled['catalog'])
        result=self.meter_read('bounded_fabric_sql',execute) if self.meter_read else execute()
        provenance=(layer.get('binding') or {}).get('provenance')
        if result['status']!='COMPLETED':
            body=result.get('result') or {}
            return Probe('UNAVAILABLE',layer['id'],reason='The independent lower-layer read did not complete.',
                query=compiled['query'],execution_surface=surface,
                failure={'interface':'FABRIC_SQL','receipt_id':result.get('id'),'read_status':result['status'],
                         'error_type':body.get('error_type'),'codes':[],
                         'specificity':'UNCERTAIN' if result['status']=='INTERRUPTED' else 'SPECIFIC'})
        rows=result['result']['rows']
        return Probe('OBSERVED',layer['id'],evidence={'id':result['id'],'tool':'bounded_fabric_sql',
            'completeness':result['result']['completeness'],'values':rows,'request_hash':result['request_hash'],
            'measure_id':measure_id,'dimension_id':None,'test_purpose':'COMPARE_DECLARED_SOURCE',
            'binding_provenance':provenance,'lower_quantity':{'source_column':compiled['source_column'],
                'catalog_provenance':'DECLARED_BY_DEFINITION'}},
            value=_quantity(rows),query=compiled['query'],execution_surface=surface,
            surface_report=result['result'].get('surface_report'),surface_reportable=('identity','object'))

    def failure_detail(self,layer,probe):
        """Re-issue the failed query through XMLA to obtain the surface's specific error."""
        context=context_search.latest(self.store) or {}
        workspace=next((a['name'] for a in context.get('assets',[])
                        if a.get('kind')=='Workspace' and a.get('id')=='fabric://'+self.model['workspace']),None)
        if not workspace or not probe.query:
            return {'interface':'XMLA','specificity':'GENERIC','codes':[],'status':'NOT_ADDRESSABLE'}
        request={'workspace_name':workspace,'model_name':self.model['name'],'query':probe.query}
        execute=lambda:self.read_failure_detail(request)
        result=self.meter_read('xmla_failure',execute) if self.meter_read else execute()
        codes=[c for c in (result.get('codes') or []) if isinstance(c,str)]
        return {'interface':'XMLA','status':result.get('status'),'codes':codes,
                'specificity':'SPECIFIC' if codes else 'GENERIC','error_type':result.get('error_type')}

    def presentation_context(self,boundary,scope):
        from report_slicer_context import assess as assess_slicers
        definitions=[];slicer_context=[];drillthrough_pages=[];pages_examined=0
        for report in self.model['context'].get('reports',[]):
            parts=report.get('report_definitions',[])
            evidence={'scan_id':self.model['context']['scan_id'],'report':report['report'],
                'binding_status':report.get('binding_status','UNRESOLVED'),
                'gaps':report.get('gaps',[]),'report_definitions':parts,
                'model_assets':self.model['context'].get('model_assets',[])}
            evidence['bundle_hash']=hashlib.sha256(json.dumps(evidence,sort_keys=True).encode()).hexdigest()
            page_paths=sorted(p['name'] for p in parts if p.get('name','').endswith('/page.json'))
            for page_path in page_paths[:20]:
                try:slicer_context.append(assess_slicers(evidence,page_path))
                except (KeyError,TypeError,ValueError) as exc:
                    slicer_context.append({'page_path':page_path,'status':'UNSUPPORTED',
                        'reason':'Retained page/slicer definition could not be parsed: '+type(exc).__name__})
                pages_examined+=1
            for part in report.get('report_definitions',[]):
                if part.get('name')=='definition/report.json' or part.get('name','').endswith(('/page.json','/visual.json')):
                    try:body=json.loads(part['metadata']['content'])
                    except (KeyError,TypeError,ValueError):body={}
                    if part.get('name','').endswith('/page.json') and body.get('pageBinding',{}).get('type')=='Drillthrough':
                        drillthrough_pages.append({'asset_id':part['id'],'path':part['name'],
                            'definition_hash':part['content_hash'],'status':'NEEDS_RUNTIME_CONTEXT'})
                    definitions.append({'asset_id':part['id'],'path':part['name'],'content_hash':part['content_hash'],
                        'filter_config_present':'filterConfig' in body,
                        'visual_type':body.get('visual',{}).get('visualType')})
        return {'status':'INCONCLUSIVE','explains':None,
          'reason':'Static report definitions cannot establish the active bookmark, selection or RLS context.',
          'evidence':{'id':'presentation-context-'+str(uuid4()),'tool':'context',
            'completeness':'COMPLETE_RESPONSE','definitions':definitions,
            'slicer_context':slicer_context,'drillthrough_pages':drillthrough_pages,
            'pages_examined':pages_examined,'pages_truncated':any(
                sum(p.get('name','').endswith('/page.json') for p in r.get('report_definitions',[]))>20
                for r in self.model['context'].get('reports',[])),
            'limitation':'Static definitions do not establish active bookmarks, selections or RLS.'}}

    def transformation_definition(self,boundary):
        identity=boundary['lower'].get('definition_asset_id')
        if not identity:
            return {'status':'UNAVAILABLE','explains':None,
                    'reason':'No retained definition identity covers this boundary.'}
        names=[]
        for candidate in (boundary['upper'].get('measure',{}).get('name'),
                          boundary['lower'].get('semantic_table'),
                          boundary['lower'].get('semantic_column'),
                          boundary['lower'].get('binding',{}).get('asset',{}).get('name')):
            if isinstance(candidate,str) and candidate and candidate not in names:names.append(candidate)
        searches=[]
        for name in names[:4]:
            result=context_search.find_content(self.store,identity,name)
            searches.append({k:result[k] for k in ('asset_id','context_version','content_hash',
                'total_characters','needle','matches','truncated','next_offset')})
        excerpts=[{'needle':s['needle'],**match} for s in searches for match in s['matches']][:12]
        if searches and not excerpts and any(s['truncated'] for s in searches):
            return {'status':'UNAVAILABLE','explains':None,
                    'reason':'No relevant definition match was retained and the search result was truncated; absence is not established.',
                    'evidence':{'id':'transformation-definition-'+str(uuid4()),'tool':'context',
                      'completeness':'PARTIAL','searches':searches,'excerpts':[],
                      'truncated':True}}
        if searches:
            receipt={k:searches[0][k] for k in ('asset_id','context_version','content_hash','total_characters')}
        else:
            page=context_search.read_content(self.store,identity,offset=0)
            receipt={k:page[k] for k in ('asset_id','context_version','content_hash','total_characters')}
            excerpts=[{'needle':None,'offset':page['offset'],'excerpt':page['content']}]
        evidence={'id':'transformation-definition-'+str(uuid4()),'tool':'context','completeness':'COMPLETE_RESPONSE',
                  **receipt,'searches':searches,'excerpts':excerpts,
                  'truncated':any(s['truncated'] for s in searches) if searches else page['truncated']}
        judgment=self.judge_definition({'boundary':{k:v for k,v in boundary.items() if k not in ('upper_probe','lower_probe')},
            'upper_value':boundary.get('upper_probe').value if boundary.get('upper_probe') else None,
            'lower_value':boundary.get('lower_probe').value if boundary.get('lower_probe') else None,
            'definition':evidence})
        return {**judgment,'evidence':evidence}

    def job_history(self,boundary):
        context=context_search.latest(self.store);target=boundary['lower'].get('transformation_asset_id')
        rows=[o for o in (context or {}).get('observations',[]) if o.get('asset_id')==target and o.get('capability')=='run_history']
        if not target:return {'status':'NOT_APPLICABLE'}
        return {'status':'CURRENT' if rows and any(r.get('detail') for r in rows) else 'UNAVAILABLE',
                'reason':None if rows else 'No retained job-history response covers this transformation asset.',
                'evidence':({'id':'job-history-'+str(uuid4()),'tool':'context','completeness':'COMPLETE_RESPONSE','runs':rows}
                            if rows else None)}

    def ingestion(self,path,scope):
        layer=next((x for x in path.get('layers',[]) if x.get('kind')=='declared_source'),None)
        if not layer:return {'status':'UNAVAILABLE','reason':'No declared data asset was resolved.'}
        asset=layer['binding']['asset'];lakehouse=asset['parent_id'].rsplit('/',1)[-1]
        result=self.read_ingestion({'workspace':self.config['fabric']['workspace_id'],
            'lakehouse':lakehouse,'table':asset['name'].removeprefix('dbo.')})
        evidence={'id':'ingestion-'+str(uuid4()),'tool':'context','completeness':'COMPLETE_RESPONSE',
                  'asset_id':asset['id'],'delta_commit':result}
        return {'status':'CURRENT' if result.get('status')=='AVAILABLE' else 'UNAVAILABLE',
                'reason':None if result.get('status')=='AVAILABLE' else 'Delta commit metadata unavailable.',
                'evidence':evidence}
