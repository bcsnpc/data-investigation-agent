"""Retained route is an explicit pinned alternative, never a current graph repair."""
import copy
import unittest
from types import SimpleNamespace
from investigator import estate_graph_contract as c
from investigator.adapters.retained_graph_continuation import RetainedApprovedContinuation,required_objects


class RetainedContinuationTests(unittest.TestCase):
    def setUp(self):
        self.time='2026-10-21T00:00:00Z';self.measure='model/table/t/measures/m';self.visual='visual-id'
        def asset(id,kind,parent=None,**extra):
            return {'id':id,'kind':kind,'parent_id':parent,'name':id.rsplit('/',1)[-1],
                    'content_hash':c.digest(id),'metadata':{},**extra}
        self.context={'version':'approved','created':self.time,
            'retained_metadata_approval':{'owner':'human','decision':'Use pinned unchanged metadata','metadata_not_recollected':True},
            'report_bindings':{'report':'model'},'assets':[
                asset('workspace','Workspace'),asset('model','SemanticModel','workspace'),
                asset('report','Report','workspace'),asset('visual','ReportVisual','report',metadata={
                    'field':{'Measure':{'Expression':{'SourceRef':{'Entity':'t'}},'Property':'m'}}}),
                asset('model/table/t','Table','model'),asset(self.measure,'Measure','model/table/t',metadata={'expression':'SUM(t[x])'}),
                asset('lake','Lakehouse','workspace'),asset('lake/table/source','LakehouseTable','lake'),
                asset('definition','SemanticModelPart','model')]}
        self.path={'layers':[{'id':'model/table/t','measure':{'id':self.measure}},
                            {'id':'lake/table/source','measure':{'id':self.measure},
                             'binding':{'status':'RESOLVED','provenance':'DECLARED_BY_DEFINITION'},
                             'direct_source_proof':{'provenance':'DECLARED_BY_DEFINITION','definition_asset_id':'definition'}}],
            'quantity_contracts':[],'stopped_by':'NO_LINEAGE',
            'evidence':{'metadata':{'context_version':'approved'}}}
        self.process=SimpleNamespace(resolve_path=lambda measure:copy.deepcopy(self.path))
        self.pin={'context_id':'approved','context_hash':c.digest(self.context),'as_of':self.time,
                  'visual':self.visual,'measure_id':self.measure}
        self.original={'estate':'test','as_of':None,'nodes':[],'edges':[],
                       'stops':[{'node':self.visual,'reason':'owner refresh failed'}],
                       'unavailable_owners':{'model':{'reason':'HTTP 403'}},'truncated':False}
        allowed=set(required_objects(self.process,context=self.context,estate='test',measure_id=self.measure))|{self.visual}
        self.current=SimpleNamespace(at=None,estate='test',identity='reader',allowed=allowed,
            gateway=SimpleNamespace(graph_objects=lambda *args,**kw:args[1]),
            _read=lambda roots:({self.visual:{'properties':{'asset_id':'visual'}}},[]),
            path_to_source=lambda visual:copy.deepcopy(self.original),_bounded=lambda value:value,
            as_of=lambda time:('current',time),node_facts=lambda node:{'current_fact':node})
    def view(self,**change):
        args={'context':self.context,'pin':self.pin,'visual':self.visual,'measure_id':self.measure};args.update(change)
        return RetainedApprovedContinuation(self.current,self.process,**args)
    def test_retained_path_preserves_the_admitted_visible_visual_name(self):
        self.current._read=lambda roots:({self.visual:{'properties':{'asset_id':'visual'},'label':'Displayed quantity card'}},[])
        result=self.view().path_to_source(self.visual)
        visual=next(n for n in result['nodes']if n['id']==self.visual)
        self.assertEqual(visual['label'],'Displayed quantity card')
        self.assertEqual(visual['properties']['asset_id'],'visual')
    def test_explicit_view_preserves_current_refusal_and_labels_retained_edges(self):
        before=copy.deepcopy(self.original);view=self.view();result=view.path_to_source(self.visual)
        self.assertEqual(before,self.current.path_to_source(self.visual))
        self.assertEqual(result['context_basis']['current_unavailable_owners'],before['unavailable_owners'])
        self.assertEqual(len(result['edges']),3)
        for edge in result['edges']:
            self.assertEqual(edge['confidence'],'DECLARED');self.assertEqual(edge['verification']['state'],'NOT_VERIFIED')
            self.assertFalse(edge['properties']['context_basis']['verified'])
        self.assertEqual(len(view.warning_labels),2);self.assertIn('hash '+self.pin['context_hash'],view.warning_labels[0])
        self.assertIn('HTTP 403',view.warning_labels[1]);self.assertEqual(view.node_facts('x'),{'current_fact':'x'})
        self.assertEqual(view.as_of(self.time),('current',self.time))

    def test_build_mode_reuses_existing_approved_compiler_path_without_new_pin_or_authority(self):
        from cloud_investigator import retained_view
        from investigator.build_phase import operating_mode
        with operating_mode():
            view,labels=retained_view(self.current,self.process,{},context=self.context,
                visual=self.visual,measure_id=self.measure)
            self.assertIsInstance(view,RetainedApprovedContinuation)
            self.assertIn('not current or value-verified',labels[0])
            self.assertEqual(self.current.path_to_source(self.visual),self.original)
            self.current.allowed={self.visual}
            fallback,labels=retained_view(self.current,self.process,{},context=self.context,
                visual=self.visual,measure_id=self.measure)
            self.assertIs(fallback,self.current)
            self.assertIn('OUTSIDE_ADMITTED_SLICE',labels[0])
            unapproved={**self.context};unapproved.pop('retained_metadata_approval')
            self.assertEqual(retained_view(self.current,self.process,{},context=unapproved,
                visual=self.visual,measure_id=self.measure),(self.current,[]))

    def test_build_mode_does_not_replace_a_healthy_current_graph(self):
        from cloud_investigator import retained_view
        from investigator.build_phase import operating_mode
        healthy={**self.original,'unavailable_owners':{}}
        self.current.path_to_source=lambda visual:copy.deepcopy(healthy)
        with operating_mode():
            self.assertEqual(retained_view(self.current,self.process,{},context=self.context,
                visual=self.visual,measure_id=self.measure),(self.current,[]))
    def test_wrong_context_hash_visual_measure_or_asof_refuses(self):
        for key in self.pin:
            bad={**self.pin,key:'wrong'}
            with self.subTest(key=key),self.assertRaises(ValueError):self.view(pin=bad)
    def test_native_path_wrong_context_refuses(self):
        self.path['evidence']['metadata']['context_version']='other'
        with self.assertRaisesRegex(ValueError,'NATIVE_CONTEXT_DIFFERS'):self.view()
    def test_similar_visual_or_measure_name_never_substitutes(self):
        self.context['assets'][3]['metadata']['field']['Measure']['Property']='almost m'
        self.pin['context_hash']=c.digest(self.context)
        with self.assertRaisesRegex(ValueError,'VISUAL_MEASURE_DIFFERS'):self.view()
    def test_report_binding_is_exact_and_authority_is_not_widened(self):
        self.context['report_bindings']['report']='other-model';self.pin['context_hash']=c.digest(self.context)
        with self.assertRaisesRegex(ValueError,'REPORT_MODEL_DIFFERS'):self.view()
        self.context['report_bindings']['report']='model';self.pin['context_hash']=c.digest(self.context)
        self.current.allowed={self.visual}
        with self.assertRaisesRegex(PermissionError,'OUTSIDE_ADMITTED_SLICE'):self.view()
    def test_source_connection_boundary_keeps_existing_static_owner_identity(self):
        from investigator.adapters.retained_graph_continuation import _owner
        assets={'connection':{'id':'connection','kind':'SourceConnection','parent_id':None},
                'table':{'id':'table','kind':'SourceTable','parent_id':'connection'}}
        self.assertEqual(_owner('table',assets),'table')

    def test_no_undeclared_or_unresolved_native_layer(self):
        self.path['layers'][1]['binding']['status']='AMBIGUOUS'
        with self.assertRaisesRegex(ValueError,'DECLARED_SOURCE_REQUIRED'):self.view()


if __name__=='__main__':unittest.main()
