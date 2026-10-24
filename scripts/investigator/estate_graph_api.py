"""Compact graph tools with exact per-object gateway authority and history."""
from collections import Counter,deque
from . import estate_graph_contract as contract


class GraphAPI:
    def __init__(self,repository,gateway,*,identity,estate,allowed_objects,at=None,max_nodes=100,max_edges=250,max_bytes=128000,definition_reader=None):
        if type(max_nodes) is not int or not 1<=max_nodes<=200 or type(max_edges) is not int or not 1<=max_edges<=500:
            raise ValueError('GRAPH_SLICE_LIMIT')
        if type(max_bytes) is not int or not 1024<=max_bytes<=256000:raise ValueError('GRAPH_BYTE_LIMIT')
        self.max_bytes=max_bytes
        self.repository,self.gateway,self.identity,self.estate=repository,gateway,identity,estate
        self.allowed=set(gateway.graph_objects(estate,allowed_objects,identity=identity))
        self.at=contract.timestamp(at) if at else None;self.max_nodes=max_nodes;self.max_edges=max_edges
        self.definition_reader=definition_reader

    def intake_candidates(self,*,enriched=False,identities=None):
        """Names only from the explicitly allowed current graph; no full scan."""
        selected=self.allowed if identities is None else set(identities)
        if len(selected)>200:raise ValueError('INTAKE_CANDIDATE_SCOPE_BOUND')
        if not selected<=self.allowed:raise PermissionError('INTAKE_CANDIDATES_OUTSIDE_GRAPH_SCOPE')
        self.gateway.graph_objects(self.estate,selected,identity=self.identity)
        # Node IDs are not edge IDs. A records(identities=node_ids) query loses
        # every containment edge, making a named report/page look unresolved.
        graph=(self.repository.path_records(self.estate,selected,selected,at=self.at,max_nodes=200,
                max_edges=500,edge_kinds={'CONTAINS','COMPUTED_FROM'},edge_targets=selected) if enriched and selected else
               self.repository.records(self.estate,at=self.at,identities=selected,limit=1000))
        if graph['truncated']:raise ValueError('INTAKE_CANDIDATE_GRAPH_TRUNCATED')
        kinds={'PIPELINE','COPY_ACTIVITY','NOTEBOOK','MODEL','REPORT','PAGE','VISUAL','MEASURE'}
        if enriched:kinds|={'TABLE','VIEW','SOURCE','COLUMN','CALCULATED_COLUMN'}
        nodes=[n for n in graph['nodes']if n['id']in selected and n['kind']in kinds]
        candidates=[{'id':n['id'],'kind':n['kind'],'label':n['label']}for n in nodes]
        result={'estate':self.estate,'as_of':self.at,'candidates':candidates}
        if enriched:
            from .enrichment import EnrichmentStore
            found=EnrichmentStore(self.repository.state).projections(self.estate,
                {n['id']:n.get('provenance',{}).get('definition_hash')for n in nodes})
            for candidate,node in zip(candidates,nodes):
                candidate['properties']={k:v for k,v in node.get('properties',{}).items()if k in('asset_id','data_type','parent_id','entity_name')}
                if candidate['id']in found:
                    row=found[candidate['id']]
                    candidate['enrichment']={**row,'synonyms':[s[:120]for s in row['synonyms'][:8]],
                        'business_meaning':row['business_meaning'][:512],'search_aid_only':True}
            result['edges']=[{'source':e['source'],'target':e['target'],'kind':e['kind']}for e in graph['edges']
                             if e['source']in selected and e['target']in selected]
        return self._bounded(result)

    def as_of(self,time):
        return GraphAPI(self.repository,self.gateway,identity=self.identity,estate=self.estate,
            allowed_objects=self.allowed,at=time,max_nodes=self.max_nodes,max_edges=self.max_edges,max_bytes=self.max_bytes,
            definition_reader=self.definition_reader)

    def _bounded(self,value):
        if len(contract.canonical(value).encode())>self.max_bytes:raise ValueError('GRAPH_SLICE_BYTE_BOUND')
        return value

    def _read(self,roots,*,path=True,edge_kinds=None):
        self.gateway.graph_objects(self.estate,roots,identity=self.identity)
        if not set(roots)<=self.allowed:raise PermissionError('GRAPH_ROOT_OUTSIDE_ADMITTED_SLICE')
        graph=(self.repository.path_records(self.estate,roots,self.allowed,at=self.at,max_nodes=self.max_nodes,max_edges=self.max_edges,edge_kinds=edge_kinds)
               if path else self.repository.records(self.estate,at=self.at,limit=10000))
        if graph['truncated'] and not path:raise ValueError('GRAPH_REPOSITORY_SCAN_BOUND')
        self.path_truncated=graph['truncated']
        nodes={node['id']:node for node in graph['nodes']}
        self.unavailable=graph.get('unavailable_owners',{})
        if not set(roots)<=nodes.keys():raise KeyError('GRAPH_OBJECT_NOT_PRESENT_AT_TIME')
        return nodes,graph['edges']

    def _slice(self,roots,*,traverse=True,edge_kinds=None,path=True):
        nodes,edges=self._read(roots,path=path,edge_kinds=edge_kinds)
        if len(set(roots))>self.max_nodes:raise ValueError('GRAPH_ROOT_SLICE_BOUND')
        seen=set(roots);queue=deque(roots);selected={};stops=[];truncated=self.path_truncated
        while queue:
            current=queue.popleft()
            unavailable_owner=next((owner for owner in (nodes[current]['owner'],nodes[current].get('properties',{}).get('definition_source_owner'))if owner in self.unavailable),None)
            if unavailable_owner:
                observation=self.unavailable[unavailable_owner]
                stops.append({'node':current,'reason':observation['reason'],
                    'remedy':'Refresh this owner definition successfully before treating its path as current.'})
                continue
            linked=[edge for edge in edges if edge['source']==current and (edge_kinds is None or edge['kind'] in edge_kinds)]
            if not linked and nodes[current]['kind'] not in ('FILTER','SECURITY_ROLE','REFRESH_SCHEDULE') and not nodes[current]['properties'].get('system_of_record'):
                stops.append({'node':current,'reason':'No retained upstream dependency is declared for this object.'})
            for edge in linked:
                unavailable_owner=next((owner for owner in (edge['owner'],edge.get('properties',{}).get('definition_source_owner'))if owner in self.unavailable),None)
                if unavailable_owner:
                    stops.append({'node':current,'reason':self.unavailable[unavailable_owner]['reason'],
                        'remedy':'Refresh the unavailable edge owner before following this dependency.'});continue
                target=edge['target']
                if target not in self.allowed:
                    stops.append({'node':current,'reason':'Upstream object lies outside the admitted graph slice.'});continue
                self.gateway.graph_objects(self.estate,[current,target],identity=self.identity)
                if target not in nodes:
                    stops.append({'node':current,'reason':'Upstream object has no node at the requested time.'});continue
                if len(selected)>=self.max_edges or (target not in seen and len(seen)>=self.max_nodes):truncated=True;continue
                selected[edge['id']]=edge
                if target not in seen:
                    seen.add(target)
                    if traverse:queue.append(target)
                if edge['confidence']=='UNKNOWN':stops.append({'node':current,**edge['unknown']})
                if nodes[target]['confidence']=='UNKNOWN':stops.append({'node':target,**nodes[target]['unknown']})
        return self._bounded({'estate':self.estate,'as_of':self.at,'nodes':[nodes[i] for i in sorted(seen)],
            'unavailable_owners':{owner:obs for owner,obs in self.unavailable.items() if any(owner in (nodes[i]['owner'],nodes[i].get('properties',{}).get('definition_source_owner')) for i in seen)},
            'edges':[selected[i] for i in sorted(selected)],'stops':stops,'truncated':truncated})

    def path_to_source(self,visual):
        nodes,_=self._read([visual])
        if nodes[visual]['kind'] not in ('VISUAL','SLICER','MEASURE','TABLE','VIEW','SOURCE','COLUMN'):raise ValueError('GRAPH_VISUAL_REQUIRED')
        return self._slice([visual],edge_kinds=contract.EDGE_KINDS-{'CONTAINS','INTERACTS_WITH'})

    def calculation_path(self,node):
        """An explanation starts at an admitted visual, measure or code node.

        This uses the same history-aware bounded adjacency reader as value
        investigation; explaining a measure never loads the whole catalog.
        """
        nodes,_=self._read([node])
        if nodes[node]['kind'] not in {'VISUAL','SLICER','MEASURE','CALCULATED_COLUMN','TABLE','COLUMN','QUERY_STEP','VIEW','PROCEDURE','NOTEBOOK','PIPELINE','COPY_ACTIVITY','SOURCE','BOUNDARY'}:
            raise ValueError('GRAPH_CALCULATION_SUBJECT_REQUIRED')
        return self._slice([node],edge_kinds=contract.EDGE_KINDS-{'CONTAINS','INTERACTS_WITH'})

    def visual_context(self,report,page,visual):
        nodes,edges=self._read([report,page,visual])
        if nodes[report]['kind']!='REPORT' or nodes[page]['kind']!='PAGE' or nodes[visual]['kind'] not in ('VISUAL','SLICER'):
            raise ValueError('GRAPH_VISUAL_ADDRESS_KIND')
        contains={(edge['source'],edge['target']) for edge in edges if edge['kind']=='CONTAINS' and edge['confidence']!='UNKNOWN'}
        if (report,page) not in contains or (page,visual) not in contains:raise ValueError('GRAPH_VISUAL_ADDRESS_DIFFERS')
        slicers=[target for origin,target in contains if origin==page and target in self.allowed and nodes[target]['kind']=='SLICER']
        return self._slice([report,page,visual,*slicers],traverse=False,edge_kinds={'FILTERED_BY','INTERACTS_WITH','COMPUTED_FROM'})

    def filters_on(self,page):
        nodes,edges=self._read([page])
        if nodes[page]['kind']!='PAGE':raise ValueError('GRAPH_PAGE_REQUIRED')
        members=[edge['target'] for edge in edges if edge['source']==page and edge['kind']=='CONTAINS' and edge['target'] in self.allowed and nodes[edge['target']]['kind'] in ('VISUAL','SLICER')]
        return self._slice([page,*members],traverse=False,edge_kinds={'FILTERED_BY','INTERACTS_WITH'})

    def table_columns(self,table):
        nodes,edges=self._read([table])
        if nodes[table]['kind'] not in ('TABLE','VIEW'):raise ValueError('GRAPH_TABLE_REQUIRED')
        result=self._slice([table],traverse=False,edge_kinds={'CONTAINS'})
        columns={node['id'] for node in result['nodes'] if node['kind'] in ('COLUMN','CALCULATED_COLUMN')}
        extra=[edge for edge in edges if {edge['source'],edge['target']}&columns and edge['kind']!='CONTAINS']
        selected={node['id']:node for node in result['nodes']}
        for edge in extra:
            if {edge['owner'],edge.get('properties',{}).get('definition_source_owner')} & self.unavailable.keys():continue
            if any({nodes[edge[key]]['owner'],nodes[edge[key]].get('properties',{}).get('definition_source_owner')} & self.unavailable.keys() for key in ('source','target')):continue
            if not {edge['source'],edge['target']}<=self.allowed:continue
            if len(result['edges'])>=self.max_edges or len(selected.keys()|{edge['source'],edge['target']})>self.max_nodes:
                result['truncated']=True;continue
            self.gateway.graph_objects(self.estate,[edge['source'],edge['target']],identity=self.identity)
            result['edges'].append(edge)
            for endpoint in ('source','target'):selected[edge[endpoint]]=nodes[edge[endpoint]]
        result['nodes']=[selected[i] for i in sorted(selected)];return self._bounded(result)

    def definition_of(self,node):
        nodes,_=self._read([node]);value=nodes[node]
        result={'node':node,'provenance':value['provenance'],'definition':value['properties'].get('definition'),
                'collection_unavailable':self.unavailable.get(value['owner']) or self.unavailable.get(value.get('properties',{}).get('definition_source_owner')),
                'valid_from':value['valid_from'],'valid_to':value['valid_to']}
        # A content-addressed reference alone cannot explain a calculation.
        # Resolve it through the installation's existing immutable Files reader;
        # never ask the model to infer the missing body from a name or hash.
        if self.definition_reader is not None and result['definition']:
            result['content']=self.definition_reader(result['definition']).decode('utf-8')
        return self._bounded(result)

    def node_facts(self,node,*,now=None,max_age_seconds=3600):
        # Authority is checked before even a local ledger lookup.
        self.gateway.graph_objects(self.estate,[node],identity=self.identity)
        if node not in self.allowed:raise PermissionError('GRAPH_ROOT_OUTSIDE_ADMITTED_SLICE')
        from .facts_ledger import FactLedger
        return self._bounded(FactLedger(self.repository.state).read(self.estate,[node],
            as_of=self.at,now=now,max_age_seconds=max_age_seconds))

    def freshness(self,node,*,now=None,max_age_seconds=3600):
        result=self._slice([node],edge_kinds=contract.EDGE_KINDS-{'CONTAINS','INTERACTS_WITH'},path=True)
        from .facts_ledger import FactLedger
        ledger=FactLedger(self.repository.state).read(self.estate,[item['id'] for item in result['nodes']],
            as_of=self.at,now=now,max_age_seconds=max_age_seconds)
        return self._bounded({'facts':[{'node':item['id'],'timing':item['properties']['timing'],'provenance':item['provenance']}
                for item in result['nodes'] if 'timing' in item['properties'] and not {item['owner'],item.get('properties',{}).get('definition_source_owner')}&self.unavailable.keys()],
                'unknown':[item['id'] for item in result['nodes'] if 'timing' not in item['properties'] or {item['owner'],item.get('properties',{}).get('definition_source_owner')}&self.unavailable.keys()],
                'runtime_facts':ledger['facts'],'missing_runtime_subjects':ledger['missing_subjects'],
                'stops':result['stops'],'truncated':result['truncated'],'as_of':self.at})

    def refresh_facts(self,path,collector,*,now,max_age_seconds=3600,required_kinds=None):
        if self.at:raise ValueError('FACT_HISTORICAL_VIEW_CANNOT_REFRESH')
        if not isinstance(path,list)or not path or len(path)>self.max_nodes:raise ValueError('FACT_PATH_BOUND')
        self.gateway.graph_objects(self.estate,path,identity=self.identity)
        if not set(path)<=self.allowed:raise PermissionError('GRAPH_ROOT_OUTSIDE_ADMITTED_SLICE')
        from .facts_collectors import refresh_facts
        from .facts_ledger import FactLedger
        return self._bounded(refresh_facts(FactLedger(self.repository.state),self.estate,path,collector,
            now=now,max_age_seconds=max_age_seconds,required_kinds=required_kinds))



def coverage(graph):
    """Operator/preflight summary; no complete raw graph returned to an agent."""
    return {'nodes_by_kind':dict(Counter(v['kind'] for v in graph['nodes'])),
        'edges_by_kind':dict(Counter(v['kind'] for v in graph['edges'])),
        'edges_by_confidence':dict(Counter(v['confidence'] for v in graph['edges'])),
        'value_verification':[{'edge_id':v['id'],'confidence':v['confidence'],'state':v['verification']['state'],
            'qualification':v['properties']['value_verification']['qualification']}for v in graph['edges']
            if 'value_verification'in v['properties']],
        'unknown':[{'id':v['id'],'kind':v['kind'],**v['unknown']} for v in graph['nodes']+graph['edges'] if v['confidence']=='UNKNOWN'],
        'unavailable_owners':graph.get('unavailable_owners',{}),
        'truncated':graph.get('truncated',False)}
