import copy
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from investigator.agent_catalog_guard import CatalogGuard
from investigator.onboarding import Conflict


class CatalogGuardTests(unittest.TestCase):
    def setUp(self):
        self.models = [{'id': 'model', 'context': {'scope': ['North']}, 'enabled': True}]
        self.context = {'version': 'context', 'assets': []}
        self.workspace = SimpleNamespace(store=SimpleNamespace(list=Mock(side_effect=lambda enabled: copy.deepcopy(self.models))),
            agent=SimpleNamespace(config={'layer_roles': []}), intake_configuration={})
        self.latest = patch('investigator.agent_catalog_guard.latest', side_effect=lambda store: copy.deepcopy(self.context))
        self.latest.start(); self.addCleanup(self.latest.stop)
        self.engine = patch('investigator.agent_catalog_guard.fingerprint', return_value='engine')
        self.engine.start(); self.addCleanup(self.engine.stop)
        self.producer = Mock(return_value={'models': [{'scope': ['North']}]})

    def test_unchanged_inputs_parse_once_but_validate_each_read(self):
        guard = CatalogGuard(self.workspace, self.producer)
        first = guard.read(); first['models'][0]['scope'].append('invented')
        self.assertEqual(guard.read(), self.producer.return_value)
        self.assertEqual(self.producer.call_count, 1)
        self.assertEqual(self.workspace.store.list.call_count, 4)

    def test_every_retained_field_change_refuses_including_unknown_future_field(self):
        for field, value in [('context', {'scope': ['South']}), ('name', 'Renamed'),
                             ('future_scope_field', 'different'), ('enabled', False)]:
            with self.subTest(field=field):
                original = copy.deepcopy(self.models)
                guard = CatalogGuard(self.workspace, self.producer)
                self.models[0][field] = value
                with self.assertRaises(Conflict): guard.read()
                self.models[:] = original

    def test_context_configuration_engine_and_added_model_changes_refuse(self):
        for mutate in [lambda: self.context.update(version='new'),
                       lambda: self.workspace.agent.config.update(extra='changed'),
                       lambda: self.workspace.intake_configuration.update(extra='changed'),
                       lambda: self.models.append({'id': 'new'})]:
            with self.subTest(mutate=mutate):
                guard = CatalogGuard(self.workspace, self.producer)
                mutate()
                with self.assertRaises(Conflict): guard.read()
        guard = CatalogGuard(self.workspace, self.producer)
        with patch('investigator.agent_catalog_guard.fingerprint', return_value='changed'):
            with self.assertRaises(Conflict): guard.read()

    def test_integrity_failure_is_propagated_not_cached_over(self):
        guard = CatalogGuard(self.workspace, self.producer)
        self.workspace.store.list.side_effect = Conflict('Context integrity differs')
        with self.assertRaisesRegex(Conflict, 'integrity'): guard.read()

    def test_change_during_initial_parse_refuses(self):
        def changing(workspace):
            self.models[0]['context'] = {'scope': ['South']}
            return {}
        with self.assertRaisesRegex(Conflict, 'while building'): CatalogGuard(self.workspace, changing)
