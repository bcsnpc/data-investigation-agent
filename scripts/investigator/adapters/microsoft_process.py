"""Microsoft Fabric/Power BI/Azure SQL adapter for the neutral process engine."""
import json
import hashlib
import re
from ..process_tape import uuid4
from .. import context_search
from ..declared_pointer import resolve as resolve_declared
from ..flexible_tools import run as run_query
from ..model_context import assets
from ..process_debugging import Probe
from ..process_quantity import quantity as _quantity
from ..refresh_comparison import whole_entity_context


SURFACE_IDENTITY='surface_identity'
SEMANTIC_ENGINE='OLAP Server'
SQL_ENGINE='Microsoft Azure SQL Data Warehouse'
SEMANTIC_REPORT={'identity':SURFACE_IDENTITY,'engine':'surface_engine','object':'surface_object'}
SEMANTIC_TYPES={'identity':'PRINCIPAL_NAME','engine':'ENGINE_PRODUCT','object':'MODEL_CATALOG_ID'}
SQL_TYPES={'identity':'PRINCIPAL_NAME','engine':'ENGINE_PRODUCT','object':'DATABASE_CATALOG_NAME'}


from .microsoft_self_report import compose as semantic_self_report

# Service errors this surface reports only generically through Execute Queries.
# The same model's XMLA interface can expose the underlying failure.
GENERIC_SERVICE_ERRORS=frozenset(('DatasetExecuteQueriesError',))


class MicrosoftProcessAdapter:
    def __init__(self,store,config,model,execute_native,execute_source,judge_definition=None,meter_read=None,
                 read_ingestion=None,lower_surface=None,read_failure_detail=None,execute_lower=None,
                 max_boundaries=1,read_endpoint=None,read_refresh_timing=None,read_snapshot_identity=None,remaining_diagnostic_reads=None):
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
        if type(max_boundaries) is not int or not 0<=max_boundaries<=32:raise ValueError('Boundary ceiling must be 0 through 32')
        self.max_boundaries=max_boundaries;self.read_endpoint=read_endpoint
        self.read_refresh_timing=read_refresh_timing
        self.read_snapshot_identity=read_snapshot_identity
        self.remaining_diagnostic_reads=remaining_diagnostic_reads
        self._paths={}
        self._declared_checks={}
        self._native_result_cache={}
        self._job_history_cache={}
        self.duplicate_read_events=[]

    def capabilities(self):
        result={'resolve_measure_path','evaluate_scoped_quantity','presentation_context','job_history','declared_source_comparison',
                'declared_context_reproduction'}
        if self.judge_definition is not None:result.add('transformation_definition')
        if self.read_ingestion is not None:result.add('ingestion')
        if (self.lower_surface or {}).get('status')=='READY' and self.execute_lower is not None:
            result.add('independent_lower_surface')
        if self.read_failure_detail is not None:result.add('failure_detail')
        if self.read_refresh_timing is not None:result.add('refresh_timing')
        if self.read_snapshot_identity is not None:result.add('snapshot_identity')
        if self.config and self.config.get('source_delivery') and self.config.get('load_audits'):
            result.add('source_delivery')
        if self.config and self.config.get('source_delivery'):result.add('expected_record_presence')
        return result

    def capability_gaps(self):
        result={'presentation_freshness':
          'Refresh timestamps are unavailable to the diagnostic reader: REST requires dataset Write and XMLA requires administrator; both were tested and refused.'}
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

    def declared_context(self,layer,measure_id,scope):
        from .report_predicates import pinned, extract, quantity_query, Refusal
        from ..declared_reproduction import compose, UnsupportedRestriction
        from ..flexible_tools import build as admit_query
        self._declared_checks.pop(measure_id,None)
        if layer.get('kind')!='presentation':
            return {'status':'UNDECLARED','reason':'Declared reproduction requires a presentation layer.'}
        try:
            model=pinned(self)
            declaration=extract(model,measure_id,scope)
            # Collection status is not capability eligibility. Return the complete
            # inventory for the engine's UNSUPPORTED gate; do not cache partial reads.
            if any(e['disposition']=='UNSUPPORTED' for e in declaration['inventory']['entries']):
                return declaration
            # Leave invalid inventories to the consumer gate, including combined
            # bounds, before preflight can attempt to compose an inadmissible set.
            from ..report_scope import validate_inventory
            try: validate_inventory(declaration['inventory'], declaration['restrictions'],binding=declaration['evidence']['report_binding'],reports=declaration['evidence']['report_catalog'])
            except ValueError: return declaration
            # Preflight both queries, so an unsupported rendering cannot consume a baseline read.
            for applied in (([],compose(declaration['restrictions'])) if declaration['restrictions'] else ()):
                query=semantic_self_report(quantity_query(model,measure_id,applied))
                admit_query(self.store,{'model_id':model['id'],'revision':model['revision'],
                    'context_id':model['context_id'],'query':query,'max_rows':20,
                    'surface_report':SEMANTIC_REPORT},self.config,'bounded_dax')
        except (Refusal,UnsupportedRestriction) as exc:
            return {'status':'UNDECLARED','reason':str(exc),'unsupported_form':exc.form}
        self._declared_checks[measure_id]=declaration
        return declaration

    def declared_cells(self, layer, measure_id, scope):
        from .report_predicates import pinned, cells, quantity_query, Refusal
        from ..declared_reproduction import compose, UnsupportedRestriction
        from ..flexible_tools import build as admit_query
        from .. import declaration_inventory, report_scope
        if layer.get('kind') != 'presentation':
            return {'status': 'UNDECLARED', 'reason': 'Declared reproduction requires a presentation layer.'}
        self._declared_checks = {k: v for k, v in self._declared_checks.items() if not isinstance(k, tuple) or k[0] != measure_id}
        try:
            model = pinned(self); batch = cells(model, measure_id, scope)
            for declaration in batch['cells']:
                address = declaration['cell']
                # Engine still owns inventory eligibility. Do not preflight a partial set.
                if any(e['disposition'] == 'UNSUPPORTED' for e in declaration['inventory']['entries']): continue
                try: entries = report_scope.validate_inventory(declaration['inventory'], declaration['restrictions'],binding=scope['report_binding'],reports=self.report_catalog())
                except ValueError: continue
                if any(e['disposition'] == 'UNSUPPORTED' for e in entries): continue
                applied = compose(declaration['restrictions'] + address['key_restrictions'])
                for restrictions in ([], applied):
                    query = semantic_self_report(quantity_query(model, measure_id, restrictions))
                    admit_query(self.store, {'model_id': model['id'], 'revision': model['revision'],
                        'context_id': model['context_id'], 'query': query, 'max_rows': 20,
                        'surface_report': SEMANTIC_REPORT}, self.config, 'bounded_dax')
                self._declared_checks[(measure_id, address['id'])] = declaration
            return batch
        except (Refusal, UnsupportedRestriction) as exc:
            return {'status': 'UNDECLARED', 'reason': str(exc), 'unsupported_form': exc.form}

    def evaluate_declared_context(self,layer,measure_id,scope):
        import copy
        from .report_predicates import pinned, quantity_query
        from ..declared_reproduction import compose
        from ..onboarding import Conflict
        model=pinned(self)
        declaration=getattr(self,'_declared_checks',{}).get((measure_id,scope['cell_id']) if 'cell_id' in scope else measure_id)
        if not declaration:raise Conflict('No complete pinned declaration admitted for reproduction')
        applied=scope.get('restrictions')
        keys=declaration.get('cell',{}).get('key_restrictions',[])
        expected_fields={'restrictions','dimension_ids'} | ({'cell_id','probe_purpose'} if 'cell' in declaration else set())
        if (set(scope)!=expected_fields or scope['dimension_ids']!=[]
                or ('cell' in declaration and scope.get('probe_purpose') not in ('DECLARED_CONTEXT','UNDECLARED_CONTEXT'))
                or not isinstance(applied,list) or applied not in ([],compose(declaration['restrictions'] + keys))):
            raise Conflict('Reproduction scope differs from the pinned composed declaration')
        measure=next(a for a in assets(model['context']) if a['id']==measure_id)
        if layer.get('kind')!='presentation' or layer['id']!=measure['parent_id']:
            raise Conflict('Reproduction layer differs from the resolved measure layer')
        query=semantic_self_report(quantity_query(model,measure_id,applied))
        plan={'model_id':model['id'],'revision':model['revision'],'context_id':model['context_id'],
              'query':query,'max_rows':20,'surface_report':SEMANTIC_REPORT}
        if 'cell' in declaration and scope['probe_purpose']=='DECLARED_CONTEXT':
            plan['cell_address']=copy.deepcopy(declaration['cell'])
        from ..read_address import baseline,cell
        plan['read_address']=cell(plan['cell_address']) if 'cell_address' in plan else baseline(applied)
        from ..onboarding import digest
        from ..flexible_tools import build as admit_query
        compiled=admit_query(self.store,plan,self.config,'bounded_dax')
        fingerprint=self._compiled_quantity_fingerprint(compiled)
        result=self._native_read(plan, declaration['evidence'].get('report_binding'))
        reader=self.config['fabric']['native_reader']
        surface={'engine':SEMANTIC_ENGINE,'connection':model['workspace'],
                 'object':model['native_id'],'identity':reader['account']}
        if result['status']!='COMPLETED':
            return Probe('UNAVAILABLE',layer['id'],reason='Declared reproduction read did not complete.',
                         query=query,execution_surface=surface)
        body=result['result'];rows=body['rows']
        probe=Probe('OBSERVED',layer['id'],evidence={'id':result['id'],'tool':'bounded_dax',
            'completeness':body['completeness'],'values':rows,'request_hash':result['request_hash'],
            'measure_id':measure_id,'applied_restrictions':copy.deepcopy(applied),
            'context_id':model['context_id'],'model_revision':model['revision'],
            'definition_evidence_id':declaration['evidence']['id'],
            'read_address':copy.deepcopy(plan['read_address']),
            **({'cell_address':copy.deepcopy(plan['cell_address'])} if 'cell_address' in plan else {}),
            'conditional_declarations':copy.deepcopy(declaration['evidence']['conditional_declarations'])},
            value=_quantity(rows,plan['surface_report']),query=query,execution_surface=surface,
            surface_report=body.get('surface_report'),surface_reportable=('identity','engine','object'),
            surface_report_types=SEMANTIC_TYPES,surface_report_binding='VALUE_QUERY')
        return probe

    def _native_read(self,plan,binding=None):
        import copy
        from ..flexible_tools import build
        from ..onboarding import digest
        from ..process_debugging import attest_surface
        compiled=build(self.store,plan,self.config,'bounded_dax')
        from ..read_address import validate as validate_address
        validate_address(plan.get('read_address'))
        key=digest({'compiled':self._compiled_quantity_fingerprint(compiled),'report':binding,
            'address':plan['read_address']})
        if key in self._native_result_cache:
            result=copy.deepcopy(self._native_result_cache[key])
            self.duplicate_read_events.append({'id':'duplicate-read-'+str(uuid4()),'tool':'process',
                'check_kind':'COMPILED_DUPLICATE_REFUSED','prior_evidence_id':result['id'],
                'compiled_fingerprint':key,'diagnostic_reads':0,'prior_result':_quantity(result['result']['rows'],plan['surface_report'])})
            return result
        if self.remaining_diagnostic_reads is not None and self.remaining_diagnostic_reads()<1:
            return {'id':'probe-not-executed-'+str(uuid4()),'status':'NOT_EXECUTED'}
        execute=lambda:run_query(self.store,plan,self.config,'bounded_dax',self.execute_native)
        result=self.meter_read('bounded_dax',execute) if self.meter_read else execute()
        surface={'engine':SEMANTIC_ENGINE,'connection':self.model['workspace'],
                 'object':self.model['native_id'],'identity':self.config['fabric']['native_reader']['account']}
        if result['status']=='COMPLETED' and result['result']['completeness']=='COMPLETE_RESPONSE':
            report=attest_surface(surface,result['result'].get('surface_report'),('identity','engine','object'))
            if report['consistency']=='MATCHED' and not report['missing_required_fields']:
                self._native_result_cache[key]=copy.deepcopy(result)
        return result

    def declared_probe_cost(self,measure_id,declaration,restrictions,purpose=None):
        from .report_predicates import quantity_query
        from ..flexible_tools import build
        from ..onboarding import digest
        model=self.model
        plan={'model_id':model['id'],'revision':model['revision'],'context_id':model['context_id'],
              'query':semantic_self_report(quantity_query(model,measure_id,restrictions)),
              'max_rows':20,'surface_report':SEMANTIC_REPORT}
        compiled=build(self.store,plan,self.config,'bounded_dax')
        from ..read_address import baseline,cell
        address=cell(declaration['cell']) if purpose=='DECLARED_CONTEXT' and 'cell' in declaration else baseline(restrictions)
        key=digest({'compiled':self._compiled_quantity_fingerprint(compiled),
                    'report':declaration['evidence'].get('report_binding'),
                    'address':address})
        return int(key not in self._native_result_cache)

    @staticmethod
    def _cell_key(cell):
        return cell

    def _compiled_quantity_fingerprint(self,compiled):
        from ..onboarding import digest
        # Do not fingerprint proposal text or proposal scope_hash. Native canonical
        # compilation carries resolved references and expression/filter structure.
        if compiled.get('compiled_read') is None: raise ValueError('Volatile quantity cannot be reused')
        return digest({k:compiled[k] for k in ('tool','compiled_read','asset_ids','workspace','native_model_id',
            'context_id','context_hash','policy_hash','surface_report_columns')} | {'reader':self.config['fabric']['native_reader']})

    def report_catalog(self):
        from .report_predicates import report_catalog
        return report_catalog(self.model)

    def selection_columns(self):
        return [{'id':a['id'],'name':a['name']} for a in assets(self.model['context']) if a['kind']=='SemanticColumn']

    def report_selection_inventory(self,measure_id,binding):
        from .report_predicates import pinned,scoped_options,_document
        from .report_cells import roles
        model=pinned(self)
        from .report_predicates import Refusal
        from ..declared_reproduction import UnsupportedRestriction
        try: declarations=scoped_options(model,measure_id,binding)
        except Refusal as exc: raise UnsupportedRestriction(exc.form) from exc
        grouping=set()
        for declaration in declarations:
            target=declaration['evidence']['metadata']['definition_target_id']
            try: columns,_=roles(model,_document(model,target))
            except Refusal as exc: raise UnsupportedRestriction(exc.form) from exc
            grouping.update(c['id'] for c in columns)
        return declarations,sorted(grouping)

    def observe_selection_value(self,layer,column_id,quote,binding):
        from .report_predicates import Refusal
        from ..declared_reproduction import UnsupportedRestriction
        try: return self._observe_selection_value(layer,column_id,quote,binding)
        except Refusal as exc: raise UnsupportedRestriction(exc.form) from exc

    def _observe_selection_value(self,layer,column_id,quote,binding):
        from .report_predicates import pinned,Refusal
        from ..flexible_tools import build as admit_query
        model=pinned(self); catalog=assets(model['context']); by_id={a['id']:a for a in catalog}
        column=by_id[column_id]; table=by_id[column['parent_id']]
        typ=column.get('metadata',{}).get('dataType')
        if typ=='string': value=quote; literal='"'+quote.replace('"','""')+'"'
        elif typ=='int64':
            try: value=int(quote)
            except ValueError: raise Refusal('SELECTION_VALUE_TYPE')
            if str(value)!=quote: raise Refusal('SELECTION_VALUE_PRECISION')
            literal=str(value)
        else: raise Refusal('SELECTION_VALUE_TYPE_'+str(typ))
        reference="'"+table['name'].replace("'","''")+"'["+column['name'].replace(']',']]')+']'
        query=semantic_self_report('EVALUATE ROW("quantity",COUNTROWS(FILTER(VALUES('+reference+'),'+reference+' == '+literal+')))')
        plan={'model_id':model['id'],'revision':model['revision'],'context_id':model['context_id'],'query':query,'max_rows':20,'surface_report':SEMANTIC_REPORT}
        from ..read_address import baseline
        plan['read_address']=baseline([{'field_id':column_id,'operator':'IN','values':[value]}])
        admit_query(self.store,plan,self.config,'bounded_dax')
        result=self._native_read(plan,binding)
        surface={'engine':SEMANTIC_ENGINE,'connection':model['workspace'],'object':model['native_id'],'identity':self.config['fabric']['native_reader']['account']}
        if result['status']!='COMPLETED': return Probe('UNAVAILABLE',layer['id'],reason='Value-existence read did not complete.',query=query,execution_surface=surface)
        body=result['result']; rows=body['rows']; quantity=_quantity(rows,plan['surface_report'])
        if not isinstance(quantity,dict) or quantity.get('quantity') not in ('0','1'): raise Refusal('VALUE_EXISTENCE_RESULT')
        exists=quantity['quantity']=='1'
        return Probe('OBSERVED',layer['id'],value=quantity,query=query,execution_surface=surface,
            evidence={'id':result['id'],'tool':'bounded_dax','check_kind':'COLUMN_VALUE_EXISTENCE','column_id':column_id,
                'request_hash':result['request_hash'],
                'read_address':plan['read_address'],
                'searched_value':value,'value_exists':exists,'report_id':binding['report_id'],
                'context_id':model['context_id'],'model_revision':model['revision'],'completeness':body['completeness'],'values':rows},
            surface_report=body.get('surface_report'),surface_reportable=('identity','engine','object'),
            surface_report_types=SEMANTIC_TYPES,surface_report_binding='VALUE_QUERY')

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
        from .direct_source import connection_proof
        resolved['unchanged_connection']=connection_proof(document,expression,source,partitions[0],definition)
        if resolved['unchanged_connection'] is not None:
            resolved['unchanged_connection']['semantic_table_id']=table['id']
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
                from .direct_source import quantity_proof
                layers[-1]['direct_source_proof']=quantity_proof(metadata,layers[-1],self.config)
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
        if self.max_boundaries>1 and len(layers)>1:
            from .declared_chain import extend
            path['layers'],contracts,gap=extend(context_search.latest(self.store) or {},layers)
            path['quantity_contracts']=contracts
            path['unresolved_boundary']=gap
            path['evidence']['quantity_contracts']=contracts
            path['evidence']['unresolved_boundary']=gap
            if gap:path['stopped_by']='NO_LINEAGE'
        path['max_boundaries']=self.max_boundaries
        context=context_search.latest(self.store) if self.store is not None else None
        from ..layer_display import discovered_labels
        path['layer_labels']=discovered_labels((context or {}).get('assets',[]),path['layers'])
        from ..layer_roles import apply
        path['layer_labels']=apply(path['layer_labels'],path['layers'],(self.config or {}).get('layer_roles',[]))
        if 'system_of_record' in (self.config or {}):
            from ..system_of_record import declaration
            path['system_of_record']=declaration(self.config['system_of_record'])
        self._paths[measure_id]=path
        return path

    def snapshot_identity(self,probe):
        if self.read_snapshot_identity is None:return {'status':'UNAVAILABLE','reason':'NOT_CONFIGURED'}
        context=context_search.latest(self.store) or {}
        workspace=next((a['name'] for a in context.get('assets',[])
                        if a.get('kind')=='Workspace' and a.get('id')=='fabric://'+self.model['workspace']),None)
        try:return self.read_snapshot_identity(probe,workspace)
        except Exception as exc:
            from ..usage_governance import UsageHold
            if isinstance(exc,UsageHold):raise
            profile=self.config['fabric'].get('snapshot_identity_reader',{})
            return {'status':'UNAVAILABLE','reason':'OPTIONAL_METADATA_FAILED','error_type':type(exc).__name__,
                    'identity_provenance':{'account':profile.get('account'),'profile':profile.get('profile'),
                                           'execution_reader':False,'purpose':'OPTIONAL_SNAPSHOT_IDENTITY_ONLY'}}

    def refresh_timing(self,path):
        if self.read_refresh_timing is None:return {'status':'UNAVAILABLE','reason':'No optional metadata identity configured.'}
        try:return self.read_refresh_timing()
        except Exception as exc:
            from ..usage_governance import UsageHold
            if isinstance(exc,UsageHold):raise
            profile=self.config['fabric'].get('refresh_timing_reader',{})
            return {'status':'UNAVAILABLE','error_type':type(exc).__name__,
                    'reason':'Optional metadata timing could not be obtained; the comparison remains authoritative.',
                    'identity_provenance':{'purpose':'OPTIONAL_REFRESH_TIMING_ONLY',
                        'account':profile.get('account'),'profile':profile.get('profile'),
                        'execution_reader':False,'authentication_established':False}}

    def direct_source_comparison(self,boundary,scope):
        if scope.get('filters') or scope.get('dimension_ids'):return None
        layer=boundary['lower']
        if layer.get('kind')!='declared_source':return None
        compiled,_=self._lower_quantity(layer,scope)
        proof=layer.get('direct_source_proof')
        if not compiled or not proof or compiled['source_column']!=proof['source_column']:return None
        return dict(proof)

    def evaluate(self,layer,measure_id,scope):
        if layer.get('kind')=='application_quantity':
            if scope.get('filters') or scope.get('dimension_ids'):
                return Probe('NOT_COMPARABLE',layer['id'],reason='Declared application quantity supports only whole-entity scope without filters or grouping.')
            compiled=layer['compiled'];source=self.config.get('sql',{})
            account=source.get('auth',{}).get('account')
            if not account:
                return Probe('UNAVAILABLE',layer['id'],reason='Application quantity reader identity is not explicitly declared in configuration.')
            if (compiled['server'].casefold()!=source['server'].casefold() or compiled['database']!=source['database']
                    or compiled['schema']!=source['visibility_schema']):
                return Probe('UNAVAILABLE',layer['id'],reason='Application declaration leaves the approved source connection or schema.')
            from ..source_diagnostics import quote
            from application_sql_surface import read,ENGINE
            plan={'model_id':self.model['id'],'revision':self.model['revision'],'context_id':self.model['context_id'],
                'query':'SELECT SUM('+quote(compiled['source_column'])+') AS [quantity] FROM '+quote(compiled['schema'])+'.'+quote(compiled['table']),
                'max_rows':20}
            from ..read_address import baseline
            plan['read_address']=baseline([])
            execute=lambda:run_query(self.store,plan,self.config,'bounded_sql',lambda request:read(self.config,request))
            result=self.meter_read('bounded_sql',execute) if self.meter_read else execute()
            surface={'engine':ENGINE,'connection':'sql://'+source['server'],'object':source['database'],'identity':account}
            if result['status']!='COMPLETED':
                return Probe('UNAVAILABLE',layer['id'],reason='Application quantity was not established; the original receipt records the failure.',
                    execution_surface=surface,query=plan['query'],
                    failure={'interface':'APPLICATION_SQL','receipt_id':result.get('id'),'read_status':result['status'],
                        'error_type':(result.get('result') or {}).get('error_type'),'codes':[],
                        'specificity':'UNCERTAIN' if result['status']=='INTERRUPTED' else 'SPECIFIC'})
            body=result['result'];rows=body['rows']
            return Probe('OBSERVED',layer['id'],value=_quantity(rows),query=plan['query'],execution_surface=surface,
                evidence={'id':result['id'],'tool':'bounded_sql','completeness':body['completeness'],'values':rows,
                    'request_hash':result['request_hash'],'measure_id':measure_id,'dimension_id':None,
                    'read_address':plan['read_address'],'declared_context':whole_entity_context(),
                    'test_purpose':'COMPARE_DECLARED_SOURCE','binding_provenance':'DECLARED_BY_DEFINITION',
                    'quantity_contract':layer['quantity_contract'],'copy_mapping_proof':layer['copy_mapping_proof']},
                surface_report=body.get('surface_report'),surface_reportable=('identity','engine','object'),
                surface_report_types=SQL_TYPES,surface_report_binding=body.get('surface_report_binding'))
        if layer.get('kind')=='declared_quantity':
            if scope.get('filters') or scope.get('dimension_ids'):
                return Probe('NOT_COMPARABLE',layer['id'],reason='Declared quantity trace supports only whole-entity scope without filters or grouping.')
            if 'independent_lower_surface' not in self.capabilities() or self.read_endpoint is None:
                return Probe('UNAVAILABLE',layer['id'],reason='Independent endpoint lookup or reader unavailable.')
            parent=layer['binding']['asset']['parent_id'];parts=parent.removeprefix('fabric://').split('/')
            if len(parts)!=2 or parts[0]!=self.config['fabric']['workspace_id']:
                return Probe('UNAVAILABLE',layer['id'],reason='Declared input leaves the approved workspace.')
            endpoint=self.read_endpoint({'workspace':parts[0],'lakehouse':parts[1]})
            props=endpoint.get('properties',{}).get('sqlEndpointProperties',{})
            context=context_search.latest(self.store) or {}
            matches=[a for a in context.get('assets',[]) if a.get('kind')=='SQLEndpoint'
                     and a.get('availability')=='CURRENT' and a['id']==parent.rsplit('/',1)[0]+'/'+str(props.get('id'))]
            reader=self.config['fabric']['sql_reader']
            if (endpoint.get('id')!=parts[1] or props.get('connectionString')!=reader['server'] or len(matches)!=1):
                return Probe('UNAVAILABLE',layer['id'],reason='Endpoint declaration does not match the approved server and discovered object.')
            from ..source_diagnostics import quote
            compiled=dict(layer['compiled'],database=matches[0]['name'])
            compiled['query']='SELECT SUM('+quote(compiled['source_column'])+') AS [quantity] FROM '+quote(compiled['schema'])+'.'+quote(compiled['table'])
            layer['binding']['declared_connection_asset_id']=matches[0]['id']
            layer['endpoint_evidence']={'lakehouse':parent,'endpoint_id':props['id'],'server':props['connectionString']}
            return self._evaluate_lower(layer,measure_id,compiled)
        measure=next(a for a in assets(self.model['context']) if a['id']==measure_id)
        reader=((self.config or {}).get('fabric') or {}).get('native_reader') or {}
        # The declared identity is what we intend to connect as; the surface's
        # quantity query carries its identity, engine product and catalog.
        # Workspace connection identity remains unattested.
        semantic_surface={'engine':SEMANTIC_ENGINE,'connection':self.model['workspace'],
                          'object':self.model['native_id'],'identity':reader.get('account')}
        name=measure['name'].replace(']',']]')
        query=f'EVALUATE ROW("baseline", [{name}])'
        if layer.get('kind')=='declared_source':
            if scope.get('filters'):
                return Probe('NOT_COMPARABLE',layer['id'],reason='Declared source comparison does not yet translate filtered scope faithfully.')
            if 'independent_lower_surface' in self.capabilities():
                compiled,refusal=self._lower_quantity(layer,scope)
                if compiled:return self._evaluate_lower(layer,measure_id,compiled)
                layer=dict(layer,lower_refusal=refusal)
            table=layer['semantic_table'].replace("'","''");column=layer['semantic_column'].replace(']',']]')
            query=f'EVALUATE ROW("baseline", SUM(\'{table}\'[{column}]))'
        if scope.get('filters'):
            from ..native_diagnostics import build as build_native
            native_plan={'model_id':self.model['id'],'revision':self.model['revision'],
                'context_id':self.model['context_id'],'measure_ids':[measure_id],
                'filters':scope['filters'],'dimension_id':None,'include_dependencies':False}
            native=build_native(self.model,native_plan)['query'].removeprefix('EVALUATE ')
            query='EVALUATE '+native
        query=semantic_self_report(query)
        plan={'model_id':self.model['id'],'revision':self.model['revision'],
              'context_id':self.model['context_id'],'query':query,'max_rows':20,
              'surface_report':SEMANTIC_REPORT}
        from ..read_address import baseline
        plan['read_address']=baseline(scope.get('filters',[]))
        from ..flexible_tools import build as admit_query
        admit_query(self.store,plan,self.config,'bounded_dax')
        result=self._native_read(plan,scope.get('report_binding'))
        if result['status']=='NOT_EXECUTED':
            reason='Diagnostic read cap stopped the presentation quantity probe.'
            return Probe('UNAVAILABLE',layer['id'],reason=reason,evidence={'id':result['id'],'tool':'process',
                'check_kind':'PROBE_NOT_EXECUTED','reason':reason,'target_id':layer['id'],
                'would_establish':'the selected measure under the resolved ticket scope'})
        if result['status']!='COMPLETED':
            body=result.get('result') or {};code=body.get('service_error_code')
            failure={'interface':'EXECUTE_QUERIES','receipt_id':result.get('id'),'read_status':result['status'],
                     'error_type':body.get('error_type'),'http_status':body.get('http_status'),
                     'codes':[code] if isinstance(code,str) else [],
                     'specificity':('GENERIC' if code in GENERIC_SERVICE_ERRORS else
                                    'UNCERTAIN' if result['status']=='INTERRUPTED' else 'SPECIFIC')}
            return Probe('UNAVAILABLE',layer['id'],reason='The presentation reader could not establish a baseline.',
                         query=query,execution_surface=semantic_surface,failure=failure)
        rows=result['result']['rows'];value=_quantity(rows,plan['surface_report'])
        report=result['result'].get('surface_report')
        definition_check=layer.get('kind')=='declared_source'
        return Probe('NOT_COMPARABLE' if definition_check else 'OBSERVED',layer['id'],evidence={'id':result['id'],'tool':'bounded_dax',
            'completeness':result['result']['completeness'],'values':rows,
            'request_hash':result['request_hash'],
            'declared_context':(whole_entity_context() if not scope.get('filters') and not scope.get('dimension_ids') else None),
            'measure_id':measure_id,'dimension_id':None,
            'read_address':plan['read_address'],
            'test_purpose':'CHECK_DECLARED_SOURCE_DEFINITION' if definition_check else 'ESTABLISH_BASELINE',
            **({'binding_provenance':(layer.get('binding') or {}).get('provenance'),
                'independent_read_refused':layer.get('lower_refusal')} if definition_check else {})},
            value=value,query=query,
            reason='NO_INDEPENDENT_LOWER_READ' if definition_check else None,
            execution_surface=semantic_surface,surface_report=report,surface_reportable=('identity','engine','object'),
            surface_report_types=SEMANTIC_TYPES,surface_report_binding='VALUE_QUERY')

    def _lower_quantity(self,layer,scope):
        """Compile the declared-source quantity for an independent surface, or say why not.

        Faithful equivalence only: the measure is a plain SUM over one semantic
        column (checked when the layer was resolved). The partition is a single
        whole-entity partition. The column declares a source column. The model
        declares no security roles that could filter one side and not the other.
        The SQL endpoint is declared by the binding. Anything else is refused;
        nothing is approximated or matched by name.
        """
        if scope.get('filters') or scope.get('dimension_ids'):
            return None,'Declared source comparison does not yet translate filtered scope faithfully.'
        binding=layer.get('binding') or {}
        partition=binding.get('declared_partition') or {}
        if binding.get('status')!='RESOLVED':return None,'The declared source binding is not resolved.'
        if partition.get('partition_count')!=1 or partition.get('source_type')!='entity':
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
        surface={'engine':SQL_ENGINE,'connection':'sql://'+str(reader.get('server')),'object':compiled['database'],
                 'identity':reader.get('account')}
        plan={'model_id':self.model['id'],'revision':self.model['revision'],'context_id':self.model['context_id'],
              'query':compiled['query'],'max_rows':20}
        from ..read_address import baseline
        plan['read_address']=baseline([])
        execute=lambda:run_query(self.store,plan,self.config,'bounded_fabric_sql',
            lambda request:self.execute_lower(compiled['database'],request),catalog=compiled['catalog'])
        result=self.meter_read('bounded_fabric_sql',execute) if self.meter_read else execute()
        provenance=(layer.get('binding') or {}).get('provenance')
        if result['status']=='NOT_EXECUTED':
            reason='Diagnostic read cap stopped the presentation quantity probe.'
            return Probe('UNAVAILABLE',layer['id'],reason=reason,evidence={'id':result['id'],'tool':'process',
                'check_kind':'PROBE_NOT_EXECUTED','reason':reason,'target_id':layer['id'],
                'would_establish':'the selected measure under the resolved ticket scope'})
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
            'read_address':plan['read_address'],
            'binding_provenance':provenance,'lower_quantity':{'source_column':compiled['source_column'],
                'catalog_provenance':'DECLARED_BY_DEFINITION'},
            'declared_context':whole_entity_context(),
            **({'quantity_contract':layer['quantity_contract'],'endpoint_declaration':layer.get('endpoint_evidence')}
               if 'quantity_contract' in layer else {})},
            value=_quantity(rows),query=compiled['query'],execution_surface=surface,
            surface_report=result['result'].get('surface_report'),surface_reportable=('identity','engine','object'),
            surface_report_types=SQL_TYPES,surface_report_binding=result['result'].get('surface_report_binding'))

    def failure_detail(self,layer,probe):
        """Re-issue the failed query through XMLA to obtain the surface's specific error."""
        context=context_search.latest(self.store) or {}
        workspace=next((a['name'] for a in context.get('assets',[])
                        if a.get('kind')=='Workspace' and a.get('id')=='fabric://'+self.model['workspace']),None)
        if not workspace or not probe.query:
            return {'interface':'XMLA','specificity':'GENERIC','codes':[],'status':'NOT_ADDRESSABLE'}
        request={'workspace_name':workspace,'model_name':self.model['name'],'query':probe.query}
        from ..failure_detail import record
        read=lambda:self.read_failure_detail(request)
        execute=lambda:self.meter_read('xmla_failure',read) if self.meter_read else read()
        receipt_id,status,result=record(self.store,self.model['id'],
            dict(request,interface='XMLA',refines_receipt_id=(probe.failure or {}).get('receipt_id')),execute)
        return {'interface':'XMLA','status':result['interface_status'],'codes':result['codes'],
                'specificity':'SPECIFIC' if result['codes'] else 'GENERIC','error_type':result['error_type'],
                'receipt_id':receipt_id,'receipt_status':status}

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
        contract=boundary['lower'].get('quantity_contract')
        if contract:
            definition={'id':'transformation-definition-'+str(uuid4()),'tool':'context','completeness':'COMPLETE_RESPONSE',
                'asset_id':contract['definition_asset_id'],'content_hash':contract['definition_hash'],
                'operations':contract['operations'],'quantity_contract':contract,
                'limitation':'Only the supported operations on this declared quantity path are included; other business rules and a shared snapshot are not established.'}
            judgment=self.judge_definition({'upper_value':boundary['upper_probe'].value,
                'lower_value':boundary['lower_probe'].value,
                'boundary':{'upper':boundary['upper']['id'],'lower':boundary['lower']['id']},'definition':definition})
            definition['judgment']=dict(judgment)
            # Naming evidence is for output rendering, not a change to judge input.
            definition['business_vocabulary']=boundary['lower'].get('business_vocabulary',{})
            return {**judgment,'evidence':definition}
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
        target=boundary['lower'].get('transformation_asset_id')
        if target not in self._job_history_cache:
            self._job_history_cache[target]=self._read_job_history(boundary)
        return self._job_history_cache[target]

    def _read_job_history(self,boundary):
        context=context_search.latest(self.store);target=boundary['lower'].get('transformation_asset_id')
        from ..load_audits import declarations
        entries=declarations(self.config['load_audits']) if 'load_audits' in self.config else []
        selected=[e for e in entries if e['delivery_asset_id']==target]
        if selected:
            from .load_audit import read
            return read(self,selected[0])
        rows=[o for o in (context or {}).get('observations',[]) if o.get('asset_id')==target and o.get('capability')=='run_history']
        if not target:return {'status':'NOT_APPLICABLE'}
        from .job_history import classify
        return {**classify(rows),
                'evidence':({'id':'job-history-'+str(uuid4()),'tool':'context',
                             'completeness':'COMPLETE_RESPONSE','runs':rows,
                             'context_version':(context or {}).get('version')}
                            if rows else None)}

    def freshness_boundaries(self,path):
        context=context_search.latest(self.store) or {}
        by_id={a['id']:a for a in context.get('assets',[])}
        layers=list(path.get('layers',[]))
        return [{'upper':upper,'lower':lower,'index':i}
                for i,(upper,lower) in enumerate(zip(layers,layers[1:]),1)
                if by_id.get(lower.get('transformation_asset_id'),{}).get('kind') in ('DataPipeline','CopyJob','Notebook')]

    def source_delivery(self,boundary,scope):
        from .source_delivery import read
        return read(self,boundary,scope)

    def record_presence(self,path,layer,requested,scope):
        from .record_presence import read
        return read(self,path,layer,requested,scope)

    def ingestion(self,path,scope):
        layer=next((x for x in path.get('layers',[]) if x.get('kind')=='declared_source'),None)
        if not layer:return {'status':'UNAVAILABLE','reason':'No declared data asset was resolved.'}
        asset=layer['binding']['asset'];lakehouse=asset['parent_id'].rsplit('/',1)[-1]
        result=self.read_ingestion({'workspace':self.config['fabric']['workspace_id'],
            'lakehouse':lakehouse,'table':asset['name'].removeprefix('dbo.')})
        evidence={'id':'ingestion-'+str(uuid4()),'tool':'context','completeness':'COMPLETE_RESPONSE',
                  'asset_id':asset['id'],'delta_commit':result}
        observed=(result.get('status')=='AVAILABLE' and isinstance(result.get('latest_commit'),str)
                  and bool(result['latest_commit']) and isinstance(result.get('commit_info'),dict))
        return {'status':'COMMIT_OBSERVED' if observed else 'UNAVAILABLE',
                'reason':'A commit was observed; source-to-destination completeness and freshness were not established.' if observed else 'Delta commit metadata unavailable or incomplete.',
                'evidence':evidence}
