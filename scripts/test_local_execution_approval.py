import copy
import sqlite3
import unittest
from contextlib import contextmanager
from unittest.mock import patch
from test_local_exported_process import LocalExportTests
from investigator import local_execution_approval as approval
from investigator.onboarding import digest, Conflict


class LocalApprovalTests(unittest.TestCase):
    def setUp(self):
        self.fixture = LocalExportTests(); self.fixture.setUp(); self.addCleanup(self.fixture.doCleanups)
        folder = self.fixture.folder
        self.source = {'_estate': {'manifest_hash': 'a'*64, 'execution': {'mode': 'LIVE'}}, 'fabric': {'scope': 'unchanged'}}
        self.model = {'id': 'model', 'context_id': 'context', 'revision': 1,
            'context': {'definition': 'actual retained'}, 'enabled': True,
            'discovery': {'policy_hash': digest(self.source)}}
        self.enterprise = {'version': 'enterprise', 'assets': []}
        self.fixture.manifest.update(estate_manifest_hash='a'*64,
            enterprise_context={'id': 'enterprise', 'hash': digest({'assets': []})},
            contexts=[{'model_id': 'model', 'context_id': 'context', 'revision': 1, 'context_hash': digest(self.model['context'])}])
        self.fixture.write_manifest()
        from investigator.local_bundle import sha
        self.config = {'_estate': {'manifest_hash': 'b'*64, 'execution': {'mode': 'LOCAL_EXPORTED',
            'bundle': str(folder), 'manifest_sha256': sha(folder/'manifest.json'), 'source_manifest_hash': 'a'*64}},
            'fabric': {'scope': 'unchanged'}}
        outer = self
        class Store:
            @contextmanager
            def connect(self):
                db = sqlite3.connect(folder/'evidence.sqlite')
                try:
                    yield db; db.commit()
                except BaseException: db.rollback(); raise
                finally: db.close()
            def get(self, identity):
                if identity != 'model': raise KeyError(identity)
                return copy.deepcopy(outer.model)
        self.store = Store()
        for name, value in [('investigator.context_search.latest', self.enterprise), ('investigator.local_execution_approval.fingerprint', 'engine')]:
            guard = patch(name, return_value=value); guard.start(); self.addCleanup(guard.stop)

    def approve(self):
        return approval.approve(self.store, self.config, self.source, owner='Chaitu',
            decision='Explicit exported local execution switch', approved_at='2026-10-10')

    def test_separate_local_authority_preserves_source_policy_context(self):
        before = copy.deepcopy(self.model)
        with self.assertRaises(Conflict): approval.validate(self.store, self.config, self.model)
        record = self.approve()
        self.assertEqual(approval.validate(self.store, self.config, self.model)['source_live_config_hash'], digest(self.source))
        self.assertNotEqual(record['config_hash'], record['source_live_config_hash'])
        self.assertEqual(self.model, before)
        self.assertEqual(self.approve()['id'], record['id'])

    def test_model_body_or_config_change_never_reuses_authority(self):
        self.approve()
        self.model['context']['definition'] = 'changed'
        with self.assertRaises(Conflict): approval.validate(self.store, self.config, self.model)
        self.model['context']['definition'] = 'actual retained'
        changed = copy.deepcopy(self.config); changed['fabric']['scope'] = 'broader'
        with self.assertRaises(Conflict): approval.approve(self.store, changed, self.source, owner='owner', decision='decision', approved_at='date')

    def test_engine_or_record_tamper_refuses(self):
        self.approve()
        with patch('investigator.local_execution_approval.fingerprint', return_value='different'):
            with self.assertRaises(Conflict): approval.validate(self.store, self.config, self.model)
        with self.store.connect() as db: db.execute("UPDATE local_execution_approvals SET body='{}'")
        with self.assertRaises(Conflict): approval.validate(self.store, self.config, self.model)

    def test_normal_workspace_preview_and_start_use_separate_approval(self):
        from test_agent_intake_settlement import SettlementTests
        from investigator.agent_intake_settlement import Settlement
        f = SettlementTests(); f.setUp(); self.addCleanup(f.doCleanups)
        workspace = f.workspace
        source = copy.deepcopy(workspace.agent.config)
        source['_estate'] = {'manifest_hash': 'a'*64, 'execution': {'mode': 'LIVE'}}
        model = workspace.store.get(f.catalog['models'][0]['id'])
        # The retained fixture uses an injected model. Preserve its native
        # policy exactly; only this new local approval authorizes the new config.
        f.f.helper.h.model['discovery']['policy_hash'] = digest(source)
        enterprise = {'version': 'enterprise', 'assets': []}
        self.fixture.manifest.update(contexts=[{'model_id': model['id'], 'context_id': model['context_id'],
            'context_hash': digest(model['context']), 'revision': model['revision']}])
        self.fixture.write_manifest()
        from investigator.local_bundle import sha
        config = copy.deepcopy(source)
        config['_estate'] = {'manifest_hash': 'b'*64, 'execution': {'mode': 'LOCAL_EXPORTED',
            'bundle': str(self.fixture.folder), 'manifest_sha256': sha(self.fixture.folder/'manifest.json'),
            'source_manifest_hash': 'a'*64}}
        workspace.agent.config.clear(); workspace.agent.config.update(config)
        with patch('investigator.context_search.latest', return_value=enterprise):
            approval.approve(workspace.store, config, source, owner='Chaitu', decision='Local switch', approved_at='2026-10-10')
            tool = Settlement(workspace, text=f.form['description'], key_prefix='local-control',
                record_evidence=lambda _: 'evidence', form_request=f.form)
            result = tool.resolve_ticket(f.raw)
            self.assertEqual(result['status'], 'INTAKE_ADMITTED', result)
            started = tool.start()
            self.assertEqual(workspace.agent.get(started['id'])['status'], 'READY')
        self.assertEqual(f.f.helper.h.model['discovery']['policy_hash'], digest(source))
        f.f.helper.h.native.assert_not_called(); f.f.helper.h.source.assert_not_called()


if __name__ == '__main__': unittest.main()
