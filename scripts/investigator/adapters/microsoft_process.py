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


class MicrosoftProcessAdapter:
    def __init__(self,store,config,model,execute_native,execute_source,judge_definition=None,meter_read=None,
                 read_ingestion=None):
        self.store,self.config,self.model=store,config,model
        self.execute_native,self.execute_source=execute_native,execute_source
        self.judge_definition=judge_definition
        self.meter_read=meter_read
        self.read_ingestion=read_ingestion
        self._paths={}

    def capabilities(self):
        result={'resolve_measure_path','evaluate_scoped_quantity','presentation_context','job_history'}
        if self.judge_definition is not None:result.add('transformation_definition')
        if self.read_ingestion is not None:result.add('ingestion')
        return result

    def capability_gaps(self):
        result={'presentation_freshness':
          'Presentation refresh history is unavailable to the isolated execution reader; it is not elevated for metadata access.'}
        if self.read_ingestion is None:
            result['ingestion']='No isolated metadata transport is configured for ingestion history.'
        if self.judge_definition is None:
            result['transformation_definition']='No governed definition-judgment provider is configured.'
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
                layers.append({'id':binding['asset']['id'],'kind':'declared_source','measure':measure,
                    'semantic_table':table_name,'semantic_column':column_name,
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
        semantic_surface={'engine':'POWER_BI_DAX','connection':self.model['workspace'],
                          'object':self.model['native_id']}
        name=measure['name'].replace(']',']]')
        query=f'EVALUATE ROW("baseline", [{name}])'
        if layer.get('kind')=='declared_source':
            if scope.get('filters'):
                return Probe('NOT_COMPARABLE',layer['id'],reason='Declared source comparison does not yet translate filtered scope faithfully.')
            table=layer['semantic_table'].replace("'","''");column=layer['semantic_column'].replace(']',']]')
            query=f'EVALUATE ROW("baseline", SUM(\'{table}\'[{column}]))'
        if scope.get('filters'):
            from ..native_diagnostics import build as build_native
            native_plan={'model_id':self.model['id'],'revision':self.model['revision'],
                'context_id':self.model['context_id'],'measure_ids':[measure_id],
                'filters':scope['filters'],'dimension_id':None,'include_dependencies':False}
            query=build_native(self.model,native_plan)['query']
        plan={'model_id':self.model['id'],'revision':self.model['revision'],
              'context_id':self.model['context_id'],'query':query,'max_rows':20}
        execute=lambda:run_query(self.store,plan,self.config,'bounded_dax',self.execute_native)
        result=self.meter_read('bounded_dax',execute) if self.meter_read else execute()
        if result['status']!='COMPLETED':
            return Probe('UNAVAILABLE',layer['id'],reason='The presentation reader could not establish a baseline.',
                         query=query,execution_surface=semantic_surface)
        rows=result['result']['rows'];value=rows[0] if len(rows)==1 else rows
        definition_check=layer.get('kind')=='declared_source'
        return Probe('NOT_COMPARABLE' if definition_check else 'OBSERVED',layer['id'],evidence={'id':result['id'],'tool':'bounded_dax',
            'completeness':result['result']['completeness'],'values':rows,
            'request_hash':result['request_hash'],
            'measure_id':measure_id,'dimension_id':None,
            'test_purpose':'CHECK_DECLARED_SOURCE_DEFINITION' if definition_check else 'ESTABLISH_BASELINE'},
            value=value,query=query,
            reason='NO_INDEPENDENT_LOWER_READ' if definition_check else None,
            execution_surface=semantic_surface)

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
