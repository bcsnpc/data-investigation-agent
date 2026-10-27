"""Existing workspace's guided-intake surface, backed by an admitted GraphAPI."""
from .guided_intake import Catalog, SCHEMA, admit, prefill


class GuidedIntakeService:
    def __init__(self, workspace): self.workspace = workspace

    def catalog(self):
        graph = getattr(self.workspace, 'guided_graph', None)
        if graph is None:
            raise RuntimeError('GUIDED_INTAKE_GRAPH_NOT_CONFIGURED')
        return Catalog.from_graph(graph)

    def handle(self, method, parts, body):
        if method == 'GET' and parts == ['schema']: return SCHEMA
        if method=='POST' and parts==['free-text']:
            resolver=getattr(self.workspace,'guided_text_resolver',None)
            if resolver is None:raise RuntimeError('GUIDED_TEXT_MODEL_NOT_INSTALLED')
            if not isinstance(body,dict) or set(body)!={'text'}:raise ValueError('TEXT_REQUIRED')
            return resolver.resolve(body['text'])
        if parts and parts[0]=='cases':
            cases=getattr(self.workspace,'guided_cases',None)
            if cases is None:raise RuntimeError('GUIDED_CASE_ENGINE_NOT_INSTALLED')
            if method=='POST' and len(parts)==1:return cases.submit(body)
            if method=='GET' and len(parts)==2:return cases.poll(parts[1])
            raise KeyError('Guided case route not found')
        catalog = self.catalog()
        if method == 'GET' and parts == ['reports']: return catalog.reports()
        if method == 'GET' and parts == ['sources']: return catalog.sources()
        if method == 'GET' and parts == ['catalog']: return catalog.view()
        if method == 'GET' and len(parts) == 3 and parts[0] == 'reports' and parts[2] == 'pages':
            return catalog.pages(parts[1])
        if method == 'GET' and len(parts) == 5 and parts[0] == 'reports' and parts[2] == 'pages' and parts[4] == 'visuals':
            return catalog.visuals(parts[1], parts[3])
        if method == 'POST' and parts == ['validate']: return admit(body, catalog)
        if method == 'POST' and parts == ['prefill']:
            if not isinstance(body, dict) or not {'text','proposal'}<=set(body)<={'text','proposal','provenance'}:
                raise ValueError('TEXT_AND_PROPOSAL_REQUIRED')
            return prefill(body['text'], body['proposal'], catalog,provenance=body.get('provenance'))
        raise KeyError('Guided intake route not found')
