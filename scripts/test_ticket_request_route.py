import copy
import unittest
from jsonschema import ValidationError
from investigator import ticket_route, intake_extraction
from investigator.question_intake import validate
from test_intake_extraction import fixture


class RequestRouteTests(unittest.TestCase):
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

