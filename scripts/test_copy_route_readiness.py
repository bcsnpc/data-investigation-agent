"""Declared Copy plans must be conserved, not skipped as unfamiliar writers."""
import copy
import unittest
from investigator.estate_readiness import required_code_binding_identities, binding_identity
from investigator.adapters.copy_quantity import approval_sample, resolve
from test_application_quantity import CopyQuantityTests


class CopyRouteReadinessTests(unittest.TestCase):
    def setUp(self):
        fixture=CopyQuantityTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
        self.scan=fixture.context;self.target=fixture.target
        proof,_=resolve(self.scan,self.target,'id');self.source=proof['source']['id']
        self.manifest={'adapters':[{'implementation':'microsoft'}],
            'layers':[{'id':'source','asset_id':self.source},{'id':'arrival','asset_id':self.target}]}
        declaration={'id':'copy','form':'DECLARED_COPY','owner':self.target,
            'content_hash':proof['definition_hash'],'column':'id'}
        self.inventory={'discovered_declarations':[declaration],
            'declarations':[dict(declaration,disposition='RESOLVED',dependencies=[self.source])]}

    def required(self):
        return required_code_binding_identities({'scan':self.scan},self.manifest,self.inventory)

    def test_copy_requires_the_current_declared_plan_identity(self):
        proposal=approval_sample(self.scan,self.target,'id',boundary={'from_layer':'source','to_layer':'arrival'},
            context_id='ctx',cell={},precision={})['proposal']
        self.assertEqual(self.required(),[binding_identity(proposal)])
        self.assertNotEqual(self.required(),[])

    def test_changed_source_or_definition_cannot_be_omitted_or_borrowed(self):
        self.inventory['declarations'][0]['dependencies']=['different-source']
        with self.assertRaisesRegex(ValueError,'DECLARATION_DIFFERS'):self.required()
        self.inventory['declarations'][0]['dependencies']=[self.source]
        self.inventory['discovered_declarations'][0]['content_hash']='other-definition'
        with self.assertRaisesRegex(ValueError,'DECLARATION_DIFFERS'):self.required()

    def test_unrenderable_copy_predicate_refuses_before_verification(self):
        import json
        part=next(a for a in self.scan['assets']if a['kind']=='DefinitionPart'and a['metadata'].get('path')=='copyjob-content.json')
        body=json.loads(part['metadata']['content']);body['activities'][0]['properties']['source']['query']='unsupported'
        part['metadata']['content']=json.dumps(body)
        with self.assertRaisesRegex(ValueError,'MAPPING_UNESTABLISHED'):self.required()

    def test_direct_disposition_cannot_hide_copy_inputs(self):
        self.inventory['declarations'][0].update(disposition='DIRECT',dependencies=[])
        with self.assertRaisesRegex(ValueError,'DECLARATION_DIFFERS'):self.required()


if __name__=='__main__':unittest.main()
