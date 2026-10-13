"""Compact graph tools with exact per-object gateway authority and history."""
from collections import Counter,deque
from . import estate_graph_contract as contract


class GraphAPI:
    def __init__(self,repository,gateway,*,identity,estate,allowed_objects,at=None,max_nodes=100,max_edges=250,max_bytes=128000):
        if type(max_nodes) is not int or not 1<=max_nodes<=200 or type(max_edges) is not int or not 1<=max_edges<=500:
            raise ValueError('GRAPH_SLICE_LIMIT')
        if type(max_bytes) is not int or not 1024<=max_bytes<=256000:raise ValueError('GRAPH_BYTE_LIMIT')
        self.max_bytes=max_bytes
        self.repository,self.gateway,self.identity,self.estate=repository,gateway,identity,estate
        self.allowed=set(gateway.graph_objects(estate,allowed_objects,identity=identity))
        self.at=contract.timestamp(at) if at else None;self.max_nodes=max_nodes;self.max_edges=max_edges

    def as_of(self,time):
        return GraphAPI(self.repository,self.gateway,identity=self.identity,estate=self.estate,
            allowed_objects=self.allowed,at=time,max_nodes=self.max_nodes,max_edges=self.max_edges,max_bytes=self.max_bytes)

    def _bounded(self,value):
        if len(contract.canonical(value).encode())>self.max_bytes:raise ValueError('GRAPH_SLICE_BYTE_BOUND')
        return value

    def _read(self,roots):
        self.gateway.graph_objects(self.estate,roots,identity=self.identity)
        if not set(roots)<=self.allowed:raise PermissionError('GRAPH_ROOT_OUTSIDE_ADMITTED_SLICE')
        graph=self.repository.records(self.estate,at=self.at,limit=10000)
        if graph['truncated']:raise ValueError('GRAPH_REPOSITORY_SCAN_BOUND')
        nodes={node['id']:node for node in graph['nodes']}
        if not set(roots)<=nodes.keys():raise KeyError('GRAPH_OBJECT_NOT_PRESENT_AT_TIME')
        return nodes,graph['edges']

    def _slice(self,roots,*,traverse=True,edge_kinds=None):
        nodes,edges=self._read(roots)
        if len(set(roots))>self.max_nodes:raise ValueError('GRAPH_ROOT_SLICE_BOUND')
        seen=set(roots);queue=deque(roots);selected={};stops=[];truncated=False
        while queue:
            current=queue.popleft()
            linked=[edge for edge in edges if edge['source']==current and (edge_kinds is None or edge['kind'] in edge_kinds)]
            if not linked and nodes[current]['kind'] not in ('FILTER','SECURITY_ROLE','REFRESH_SCHEDULE') and not nodes[current]['properties'].get('system_of_record'):
                stops.append({'node':current,'reason':'No retained upstream dependency is declared for this object.'})
            for edge in linked:
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
            'edges':[selected[i] for i in sorted(selected)],'stops':stops,'truncated':truncated})

    def path_to_source(self,visual):
        nodes,_=self._read([visual])
        if nodes[visual]['kind'] not in ('VISUAL','SLICER'):raise ValueError('GRAPH_VISUAL_REQUIRED')
        return self._slice([visual],edge_kinds=contract.EDGE_KINDS-{'CONTAINS','INTERACTS_WITH'})

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
            if not {edge['source'],edge['target']}<=self.allowed:continue
            if len(result['edges'])>=self.max_edges or len(selected.keys()|{edge['source'],edge['target']})>self.max_nodes:
                result['truncated']=True;continue
            self.gateway.graph_objects(self.estate,[edge['source'],edge['target']],identity=self.identity)
            result['edges'].append(edge)
            for endpoint in ('source','target'):selected[edge[endpoint]]=nodes[edge[endpoint]]
        result['nodes']=[selected[i] for i in sorted(selected)];return self._bounded(result)

    def definition_of(self,node):
        nodes,_=self._read([node]);value=nodes[node]
        return {'node':node,'provenance':value['provenance'],'definition':value['properties'].get('definition'),
                'valid_from':value['valid_from'],'valid_to':value['valid_to']}

    def freshness(self,node):
        result=self._slice([node],edge_kinds=contract.EDGE_KINDS-{'CONTAINS','INTERACTS_WITH'})
        return {'facts':[{'node':item['id'],'timing':item['properties']['timing'],'provenance':item['provenance']}
                for item in result['nodes'] if 'timing' in item['properties']],
                'unknown':[item['id'] for item in result['nodes'] if 'timing' not in item['properties']],
                'stops':result['stops'],'truncated':result['truncated'],'as_of':self.at}


def coverage(graph):
    """Operator/preflight summary; no complete raw graph returned to an agent."""
    return {'nodes_by_kind':dict(Counter(v['kind'] for v in graph['nodes'])),
        'edges_by_kind':dict(Counter(v['kind'] for v in graph['edges'])),
        'edges_by_confidence':dict(Counter(v['confidence'] for v in graph['edges'])),
        'unknown':[{'id':v['id'],'kind':v['kind'],**v['unknown']} for v in graph['nodes']+graph['edges'] if v['confidence']=='UNKNOWN'],
        'truncated':graph.get('truncated',False)}
