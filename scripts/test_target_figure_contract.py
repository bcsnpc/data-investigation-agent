"""Hostile contract producers and server-only intake-to-adapter forwarding."""
import copy
import unittest
from unittest.mock import patch
from investigator import definition_target as target, declaration_inventory as inventory, reported_figure, report_scope
from investigator.question_intake import Intake, wire_contract, azure_resolve
from intake_regression_fixture import IntakeFixture

class TargetContractTests(unittest.TestCase):
    binding={'resolution_kind':'STATED','report_id':'report','source':{'start':0,'end':6,'quote':'Report'}}
    reports=[{'id':'report','name':'Report'}]
    source={'start':0,'end':5,'quote':'North'}
    def declaration(self,disposition='ACTIVE'):
        source={'report_id':'report','location':'retained#predicate','content_hash':'a'*64}
        entry={'id':report_scope.inventory_identity(source),'source':source,'disposition':disposition,
            'volatility':'FIXED','assumption':'NONE','opaque_provenance':'native',
            'effect':'RESTRICTED' if disposition=='ACTIVE' else 'EXCLUDED','restrictions':[{'field_id':'column','operator':'IN','values':['North']}] if disposition=='ACTIVE' else []}
        return {'report_id':'report','discovered':[source],'entries':[entry]},entry

    def test_missing_resolution_and_missing_entry_refuse(self):
        for value in ({'column_id':'column','source':self.source},
                      {'resolution_kind':'EVIDENCE','column_id':'column','source':self.source}):
            with self.assertRaises(ValueError):target.validate(value,ticket='North')

    def test_conditional_evidence_is_refused(self):
        inv,entry=self.declaration('CONDITIONAL')
        with self.assertRaisesRegex(ValueError,'ACTIVE'):
            target.evidence('column',self.source,entry['id'],ticket='North',inventory=inv,active=[],binding=self.binding,reports=self.reports)

    def test_active_evidence_requires_conserved_inventory_and_matching_column(self):
        inv,entry=self.declaration();active=entry['restrictions']
        value=target.evidence('column',self.source,entry['id'],ticket='North',inventory=inv,active=active,binding=self.binding,reports=self.reports)
        self.assertEqual(value['resolution_kind'],'EVIDENCE')
        for kwargs in ({'active':[]},{'inventory':None},{'column_id':'different'}):
            args=dict(column_id='column',source=self.source,inventory_entry_id=entry['id'],ticket='North',inventory=inv,active=active,binding=self.binding,reports=self.reports)
            args.update(kwargs)
            with self.assertRaises(ValueError):target.evidence(**args)

    def test_stated_provenance_and_refused_candidate_shape(self):
        target.validate({'resolution_kind':'STATED','column_id':'column','source':self.source},ticket='North')
        for candidates in ([],['a','b']):
            target.validate({'resolution_kind':'REFUSED','candidates':candidates,'source':self.source},ticket='North')
        for candidates in (['a'],['a','a']):
            with self.assertRaises(ValueError):target.shape({'resolution_kind':'REFUSED','candidates':candidates,'source':self.source})
        with self.assertRaises(ValueError):target.shape({'resolution_kind':'STATED','column_id':'column','source':self.source},'South')

    def test_closed_schema_excludes_model_owned_resolution(self):
        _,schema,_=wire_contract({'text':'North','models':[{'id':'m','measures':[],'columns':[]}]})
        self.assertNotIn('definition_target',schema['properties'])
        self.assertFalse(schema['additionalProperties'])
        self.assertEqual(set(target.KINDS),{'EVIDENCE','STATED','REFUSED'})
        for spec in target.SCHEMA['anyOf'][1:]:self.assertFalse(spec['additionalProperties'])

    def test_hostile_model_cannot_supply_an_evidence_resolution(self):
        payload={'text':'North','models':[{'id':'m','measures':[],'columns':[]}]}
        _,schema,_=wire_contract(payload)
        response={key:None for key in schema['required']}
        response['definition_target']={'resolution_kind':'EVIDENCE','column_id':'column',
            'inventory_entry_id':'invented','source':self.source}
        with patch('ticket_planner.azure_generate',return_value=(response,{})):
            with self.assertRaisesRegex(ValueError,'Unexpected fields'):azure_resolve(payload)

class FigureForwardingTests(unittest.TestCase):
    def test_intake_figure_reaches_actual_adapter_boundary_without_resend(self):
        for wording in ('123','about 3.4M','empty',None):
            with self.subTest(wording=wording):
                h=IntakeFixture();h.setUp()
                try:
                    model=h.workspace.models()['models'][0];measure=model['measures'][0]
                    ticket=measure['name']+' looks wrong'+(' and shows '+wording if wording else '')+'.'
                    spans=[] if wording is None else [{'start':ticket.index(wording),'end':ticket.index(wording)+len(wording),'quote':wording}]
                    figure=reported_figure.from_candidates(spans,ticket)
                    proposal={'action':'PROPOSE','model_id':model['id'],'measure_id':measure['id'],
                        'metric_quote':measure['name'],'question':None,'ticket_shape':'MISMATCH_COMPLAINT',
                        'comparison_mode':'VERTICAL','filters':[],'dimension_ids':[],'scope_quotes':[],
                        'reported_figure':figure,'definition_target':None}
                    h.workspace.intake=Intake(h.workspace,lambda payload:(copy.deepcopy(proposal),{}))
                    saved=h.workspace.intake.resolve({'text':ticket,'request_key':'forward','parent_id':None})
                    self.assertEqual(saved['status'],'PROPOSED',saved.get('error'))
                    request={k:proposal[k] for k in ('model_id','measure_id','filters','dimension_ids')}
                    request.update(symptom=ticket,predecessor=None,intake_id=saved['id'])
                    self.assertNotIn('reported_figure',request)
                    preview=h.workspace.preview(request)
                    self.assertEqual(preview['envelope']['reported_figure'],figure)
                    session=h.workspace.start(preview['id'])
                    seen=[]
                    def vertical(adapter,measure_id,scope):
                        adapter.declared_context({'id':'presentation'},measure_id,scope)
                        raise ValueError('Test stops after adapter-boundary capture')
                    def capture(layer,measure_id,scope):seen.append(copy.deepcopy(scope));return {'status':'UNDECLARED'}
                    with patch('investigator.process_debugging.vertical',side_effect=vertical),patch(
                            'investigator.adapters.microsoft_process.MicrosoftProcessAdapter.declared_context',side_effect=capture):
                        h.agent.run(session['id'])
                    self.assertEqual(len(seen),1)
                    self.assertEqual(seen[0]['reported_figure'],figure)
                    self.assertIn('definition_target',seen[0])
                finally:h.doCleanups()

    def test_scope_preserves_target_and_precision_without_aliasing(self):
        f=reported_figure.from_candidates([{'start':0,'end':10,'quote':'about 3.4M'}],'about 3.4M')
        t={'resolution_kind':'STATED','column_id':'column','source':{'start':0,'end':6,'quote':'Region'}}
        envelope={'filters':[],'dimension_ids':[],'reported_figure':f,'definition_target':t}
        scope=target.procedure_scope(envelope)
        self.assertEqual(scope['reported_figure'],f);self.assertEqual(scope['definition_target'],t)
        scope['reported_figure']['value']='changed'
        self.assertNotEqual(scope['reported_figure'],envelope['reported_figure'])

if __name__=='__main__':unittest.main()
