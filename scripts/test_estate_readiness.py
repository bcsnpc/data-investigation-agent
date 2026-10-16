import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from investigator.estate_readiness import (PINS, STAGES, VERSION, assess, bind_sources,
    discovery, inventory, publication, proposals, score_prospectively, sha, verification)


class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.pins = {k: 'pinned-' + k for k in PINS}
        self.manifest = {'layers': [{'asset_id': 'a'}, {'asset_id': 'b'}], 'resources': [],
                         'lineage': {'bindings': [{'from_layer': 'one', 'to_layer': 'two'}]}}

    def test_missing_evidence_never_infers_readiness_from_limits(self):
        m = dict(self.manifest, accepted_limits=[{'status': 'ACCEPTED'}])
        result = assess(m, self.pins)
        self.assertEqual(result['scoring'], 'NOT_SCORED')
        self.assertEqual([s['status'] for s in result['stages']], ['BLOCKED'] * 6)

    def test_every_stage_and_current_pin_required(self):
        index = {'version': VERSION, 'pins': dict(self.pins, engine_hash='old'), 'stages': {}}
        self.assertEqual(assess(self.manifest, self.pins, index)['status'], 'BLOCKED')

    def test_bridge_cannot_invent_a_fact_or_omit_source(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / 'receipt.json'; raw = b'{"observed": "PARTIAL"}'; p.write_bytes(raw)
            ref = {'path': str(p), 'sha256': sha(raw), 'field': 'status', 'pointer': '/observed'}
            r = {'pins': self.pins, 'status': 'COMPLETE', 'sources': [ref]}
            with self.assertRaisesRegex(ValueError, 'AUTHORITATIVE_FIELD_DIFFERS'):
                bind_sources(r, folder)
            r['status'] = 'PARTIAL'; bind_sources(r, folder)
            r['sources'] = []
            with self.assertRaisesRegex(ValueError, 'CONSERVATION'):
                bind_sources(r, folder)

    def test_original_receipt_edit_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / 'receipt.json'; p.write_text('{}')
            r = {'pins': self.pins, 'facts': {}, 'sources': [
                {'path': str(p), 'sha256': 'bad', 'field': 'facts', 'pointer': ''}]}
            with self.assertRaisesRegex(ValueError, 'HASH_DIFFERS'):
                bind_sources(r, folder)

    def test_partial_discovery_or_missing_layer_fails(self):
        r = {'pins': self.pins, 'scan': {'status': 'COMPLETE', 'coverage': {'items': {'status': 'COMPLETE'}},
                                       'assets': [{'id': 'a'}, {'id': 'b'}]}}
        discovery(r, self.manifest, self.pins)
        r['scan']['coverage']['items']['status'] = 'PARTIAL'
        with self.assertRaisesRegex(ValueError, 'PARTIAL'): discovery(r, self.manifest, self.pins)
        r['scan']['coverage']['items']['status'] = 'COMPLETE'; r['scan']['assets'].pop()
        with self.assertRaisesRegex(ValueError, 'ASSET_MISSING'): discovery(r, self.manifest, self.pins)

    def inventory_receipt(self):
        return {'pins': self.pins, 'discovered_declarations': [
            {'id': 'decl', 'content_hash': 'hash', 'form': 'opaque', 'operation': 'DIRECT_REFERENCE'}],
            'inventory': [{'id': 'decl', 'disposition': 'DIRECT', 'declaration_hash': 'hash'}],
            'boundary_inventory': [{'from_layer': 'one', 'to_layer': 'two', 'declarations': ['decl']}],
            'extraction_status': 'COMPLETE'}

    def test_direct_source_requires_explicit_complete_inventory(self):
        r = self.inventory_receipt(); inventory(r, self.manifest, self.pins)
        r['extraction_status'] = 'PARTIAL'
        with self.assertRaisesRegex(ValueError, 'INCOMPLETE'): inventory(r, self.manifest, self.pins)

    def test_unknown_declaration_and_omission_block(self):
        r = self.inventory_receipt(); r['inventory'][0]['disposition'] = 'UNSUPPORTED'
        with self.assertRaisesRegex(ValueError, 'UNSUPPORTED:opaque'): inventory(r, self.manifest, self.pins)
        r['inventory'] = []
        with self.assertRaisesRegex(ValueError, 'DECLARATION_CONSERVATION'): inventory(r, self.manifest, self.pins)

    def test_omitted_binding_blocks_even_with_verified_label(self):
        r = {'pins': self.pins, 'proposals': [], 'status': 'VERIFIED'}
        with self.assertRaisesRegex(ValueError, 'CONSERVATION'):
            proposals(r, self.manifest, self.pins)

    def test_verified_label_is_recomputed_and_requires_live_receipts(self):
        v = {'proposal': {'boundary': {'from_layer': 'one', 'to_layer': 'two'}},
             'context': 'ctx', 'status': 'VERIFIED', 'observations': [{}, {}]}
        r = {'pins': self.pins, 'verifications': [v], 'model_contexts': {'model': 'ctx'}}
        with patch('investigator.lineage_binding.revalidate_verification', return_value=dict(v, status='UNVERIFIED')):
            with self.assertRaisesRegex(ValueError, 'NOT_VERIFIED'): verification(r, self.manifest, self.pins)
        with patch('investigator.lineage_binding.revalidate_verification', return_value=v):
            with self.assertRaisesRegex(ValueError, 'LIVE_READER_RECEIPT_MISSING'): verification(r, self.manifest, self.pins)

    def test_publication_cannot_bypass_failed_replay(self):
        r = {'pins': self.pins, 'replay': {'status': 'COMPLETED', 'matched': False},
             'publication': {'status': 'PROFILE_APPEND_ACCEPTED'}}
        with self.assertRaisesRegex(ValueError, 'NOT_MATCHED'): publication(r, self.manifest, self.pins)
        r['replay']['matched'] = True; r['publication']['status'] = 'VERIFIED'
        with self.assertRaisesRegex(ValueError, 'UNPUBLISHED'): publication(r, self.manifest, self.pins)

    def test_snapshot_unverified_does_not_block_valid_publication(self):
        replay = {'status': 'COMPLETED', 'matched': True, 'capture_sha256': 'tape'}
        r = {'pins': self.pins, 'replay': replay, 'publication': {
            'status': 'PROFILE_APPEND_ACCEPTED', 'capture_sha256': 'tape', 'verification_pins': self.pins,
            'replay_receipt_sha256': 'original'}, 'sources': [{'field': 'replay', 'sha256': 'original'}],
            'snapshot_status': 'SNAPSHOT_UNVERIFIED'}
        publication(r, self.manifest, self.pins)

    def test_unready_score_never_invokes_evaluator_historical_remains_untouched(self):
        scorer = Mock(return_value={'passed': True})
        result = score_prospectively(scorer, readiness=assess(self.manifest, self.pins))
        scorer.assert_not_called(); self.assertIsNone(result['passed'])
        ready = {'version': VERSION, 'status': 'READY', 'stages': [
            {'stage': stage, 'status': 'VERIFIED'} for stage in STAGES]}
        self.assertIsNone(score_prospectively(scorer, readiness=ready)['passed'])
        scorer.assert_not_called()

    def test_complete_original_receipts_admit_and_mutation_revokes_score(self):
        from test_lineage_binding import BindingTests
        from investigator.onboarding import digest
        verified, _ = BindingTests().verification()
        manifest = {'layers': [{'asset_id': 'a'}, {'asset_id': 'b'}], 'resources': [],
                    'lineage': {'bindings': [{'from_layer': 'input', 'to_layer': 'output'}]}}
        pins = dict(self.pins, manifest_hash=digest(manifest))
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            raw_manifest = json.dumps(manifest).encode(); (base / 'manifest.json').write_bytes(raw_manifest)
            replay = {'status': 'COMPLETED', 'matched': True, 'capture_sha256': 'capture'}
            replay_raw = json.dumps(replay).encode(); (base / 'replay.json').write_bytes(replay_raw)
            approved = {'authority': {'owner': 'Owner'}, 'manifest_sha256': sha(raw_manifest),
                        'context_id': pins['context_identity'], **{k: pins[k] for k in ('context_hash', 'config_hash', 'engine_hash')}}
            facts = {
                'discovery': {'scan': {'status': 'COMPLETE', 'coverage': {'all': {'status': 'COMPLETE'}}, 'assets': [{'id': 'a'}, {'id': 'b'}]}},
                'discovery_approval': {'approval': approved, 'manifest': manifest},
                'transformations': {'discovered_declarations': [{'id': 'd', 'content_hash': 'h', 'form': 'opaque', 'operation': 'DIRECT_REFERENCE'}],
                                    'inventory': [{'id': 'd', 'disposition': 'DIRECT', 'declaration_hash': 'h'}], 'extraction_status': 'COMPLETE',
                                    'boundary_inventory': [{'from_layer': 'input', 'to_layer': 'output', 'declarations': ['d']}]},
                'bindings': {'proposals': [verified['proposal']]},
                'reader_verification': {'verifications': [verified], 'model_contexts': {'model': verified['context']}},
                'publication': {'replay': replay, 'publication': {'status': 'PROFILE_APPEND_ACCEPTED', 'capture_sha256': 'capture',
                                'verification_pins': pins, 'replay_receipt_sha256': sha(replay_raw)}}}
            index = {'version': VERSION, 'pins': pins, 'stages': {}}
            for stage, fields in facts.items():
                raw = json.dumps(fields).encode(); original = base / (stage + '-original.json'); original.write_bytes(raw)
                sources = [{'path': str(original), 'sha256': sha(raw), 'field': field, 'pointer': '/' + field} for field in fields]
                for source in sources:
                    if stage == 'discovery_approval' and source['field'] == 'manifest':
                        source.update(path=str(base / 'manifest.json'), sha256=sha(raw_manifest), pointer='')
                    if stage == 'publication' and source['field'] == 'replay':
                        source.update(path=str(base / 'replay.json'), sha256=sha(replay_raw), pointer='')
                bridge = json.dumps(dict(fields, pins=pins, sources=sources)).encode()
                target = base / (stage + '.json'); target.write_bytes(bridge)
                index['stages'][stage] = {'path': str(target), 'sha256': sha(bridge)}
            self.assertEqual(assess(manifest, pins, index, base=base)['status'], 'READY')
            scorer = Mock(return_value={'passed': True})
            inputs = {'manifest': manifest, 'pins': pins, 'index': index, 'base': base}
            self.assertTrue(score_prospectively(scorer, readiness=inputs)['passed'])
            # Hostile producer leaves the same boundary covered by one live
            # verification, while silently omitting a second proposed binding.
            # Boundary-set equality alone cannot detect this class of loss.
            second = copy.deepcopy(verified['proposal'])
            second.update(extractor='MODEL', confidence=0.8)
            facts['bindings']['proposals'].append(second)
            original = base / 'bindings-original.json'
            raw = json.dumps(facts['bindings']).encode(); original.write_bytes(raw)
            bridge_path = base / 'bindings.json'
            bridge = json.loads(bridge_path.read_text())
            bridge['proposals'] = facts['bindings']['proposals']
            bridge['sources'][0]['sha256'] = sha(raw)
            bridge_raw = json.dumps(bridge).encode(); bridge_path.write_bytes(bridge_raw)
            index['stages']['bindings']['sha256'] = sha(bridge_raw)
            report = assess(manifest, pins, index, base=base)
            self.assertEqual(report['status'], 'BLOCKED')
            reader = next(r for r in report['stages'] if r['stage'] == 'reader_verification')
            self.assertEqual(reader['reason'], 'PROPOSED_VERIFIED_IDENTITY_CONSERVATION_FAILED')
            scorer.reset_mock(); (base / 'replay.json').write_text('{}')
            self.assertIsNone(score_prospectively(scorer, readiness=inputs)['passed'])
            scorer.assert_not_called()


if __name__ == '__main__': unittest.main()
