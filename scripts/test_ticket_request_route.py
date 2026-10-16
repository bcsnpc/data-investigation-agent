import copy
import unittest
from jsonschema import ValidationError
from investigator import ticket_route, intake_extraction
from investigator.question_intake import validate
from test_intake_extraction import fixture


class RequestRouteTests(unittest.TestCase):
    def test_visual_content_question_has_an_intrinsic_subject_not_an_external_comparator(self):
        from investigator.ticket_clarification import DEFAULTS
        raw,payload=fixture('In Report, what does Global card Quantity show?',kind='VISUAL_CONTENT',
            triage='BUSINESS_QUESTION:NONE',visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        proof=ticket_route.settlement(raw,payload['text'],DEFAULTS)
        self.assertEqual(proof['route'],'DECLARED_SUBJECT')
        payload['_ticket_route']=proof
        proposal=intake_extraction.resolve(raw,payload);validate(proposal,payload)
        self.assertEqual(proposal['target_visual']['target_id'],'card')
        self.assertFalse(ticket_route.wants_freshness(proposal))
        required={**DEFAULTS,'must_confirm':['COMPARISON']}
        self.assertIsNone(ticket_route.settlement(raw,payload['text'],required))

    def test_visual_content_kind_cannot_erase_a_named_external_or_temporal_comparison(self):
        from investigator.ticket_clarification import DEFAULTS
        for ask,comparisons in [('what does Quantity show compared with another report?',['another report']),
                                ('what did Quantity show yesterday?',[]),
                                ('what does Quantity show against the application?',[])]:
            raw,payload=fixture('In Report, '+ask,kind='VISUAL_CONTENT',comparisons=comparisons)
            self.assertIsNone(ticket_route.settlement(raw,payload['text'],DEFAULTS))

    def test_default_never_overrides_named_comparison_or_required_confirmation(self):
        from investigator.ticket_clarification import DEFAULTS
        config=copy.deepcopy(DEFAULTS);config['default_route']='LOOKS_WRONG'
        raw,payload=fixture('In Report, Quantity differs from the application.')
        proof=ticket_route.settlement(raw,payload['text'],config)
        self.assertEqual(proof['route'],'APPLICATION')
        self.assertEqual(proof['version'],ticket_route.EVIDENCE_VERSION)
        self.assertNotEqual(proof['version'],ticket_route.DEFAULT_VERSION)
        required={**config,'must_confirm':['COMPARISON']}
        self.assertIsNone(ticket_route.settlement(raw,payload['text'],required))
        raw,payload=fixture('In Report, Quantity looks wrong.')
        proof=ticket_route.settlement(raw,payload['text'],config)
        self.assertEqual(proof['route'],'LOOKS_WRONG')
        self.assertEqual(proof['version'],ticket_route.DEFAULT_VERSION)
        config['must_confirm']=['COMPARISON']
        self.assertIsNone(ticket_route.settlement(raw,payload['text'],config))

    def test_changed_default_policy_cannot_validate_retained_proof(self):
        from investigator.ticket_clarification import DEFAULTS
        config=copy.deepcopy(DEFAULTS);config['default_route']='LOOKS_WRONG'
        raw,payload=fixture('In Report, Global card Quantity looks wrong.',
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        payload['_comparison_configuration']=config
        payload['_ticket_route']=ticket_route.settlement(raw,payload['text'],config)
        value=intake_extraction.resolve(raw,payload);validate(value,payload)
        config['default_route']='APPLICATION'
        with self.assertRaises(ValueError):validate(value,payload)

    def test_only_explicit_primary_subject_settles_comparison(self):
        for kind,ask,route in [('FRESHNESS','is this stale','STALE'),
                               ('SOURCE_CORRECTNESS','differs from the application','APPLICATION')]:
            raw,payload=fixture('In Report, Global card Quantity '+ask+'.',kind=kind,
                visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
            proof=ticket_route.from_request(raw,payload['text'])
            self.assertEqual(proof['route'],route)
            original=intake_extraction.resolve(raw,payload)
            self.assertNotIn('ticket_route',original)
            payload['_ticket_route']=proof
            proposal=intake_extraction.resolve(raw,payload);validate(proposal,payload)
            self.assertEqual(proposal['ticket_route'],proof)
            with self.assertRaises(ValueError):validate(proposal,{k:v for k,v in payload.items() if k!='_ticket_route'})

    def test_kind_and_triage_do_not_manufacture_comparison(self):
        for changes in ({'kind':'FRESHNESS'}, {'kind':'SOURCE_CORRECTNESS'},
                        {'triage':'MISMATCH_COMPLAINT:VERTICAL'}):
            raw,payload=fixture('In Report, Global card Quantity differs.',**changes)
            self.assertIsNone(ticket_route.from_request(raw,payload['text']))

    def test_comparator_and_competing_routes_stay_open(self):
        raw,payload=fixture('In Report, Quantity is stale compared with another report.',
                            kind='FRESHNESS',comparisons=['another report'])
        self.assertIsNone(ticket_route.from_request(raw,payload['text']))
        raw,payload=fixture('In Report, Quantity is stale and differs from the application.',kind='FRESHNESS')
        self.assertIsNone(ticket_route.from_request(raw,payload['text']))

    def test_request_proof_is_closed_and_recomputed(self):
        raw,payload=fixture('In Report, Global card Quantity is stale.',kind='FRESHNESS',
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}])
        proof=ticket_route.from_request(raw,payload['text'])
        with self.assertRaises(ValueError):ticket_route.validate(proof,payload['text']+'x')
        bad=copy.deepcopy(proof);bad['route']='APPLICATION'
        with self.assertRaises(ValidationError):ticket_route.validate(bad)
        bad=copy.deepcopy(proof);bad['source']['end']-=1
        with self.assertRaises(ValueError):ticket_route.validate(bad,payload['text'])

