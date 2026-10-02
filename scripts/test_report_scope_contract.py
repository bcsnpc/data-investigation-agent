"""Hostile report-scoped targets, conserved inventories, and receipt-owned observations."""
import copy
import unittest
from investigator import report_scope as scope
from investigator.process_debugging import attest_surface


class ReportScopeTests(unittest.TestCase):
    reports = [{'id': 'report-a', 'name': 'Inventory report'}, {'id': 'report-b', 'name': 'Other report'}]
    ticket = 'Inventory report North'
    report_source = {'start': 0, 'end': 16, 'quote': 'Inventory report'}
    value_source = {'start': 17, 'end': 22, 'quote': 'North'}

    def setUp(self):
        self.binding = scope.resolve_report(self.report_source, self.reports, self.ticket)
        source = {'report_id': 'report-a', 'location': 'retained-part#selection', 'content_hash': 'a'*64}
        self.entry = {'id': scope.inventory_identity(source), 'source': source,
            'disposition': 'ACTIVE', 'volatility': 'FIXED', 'assumption': 'NONE',
            'opaque_provenance': 'opaque-kind', 'effect': 'RESTRICTED',
            'restrictions': [{'field_id': 'column-a', 'operator': 'IN', 'values': ['North']}]}
        self.inventory = {'report_id': 'report-a', 'discovered': [source], 'entries': [self.entry]}
        self.active = copy.deepcopy(self.entry['restrictions'])
        self.target = {'resolution_kind': 'EVIDENCE', 'report_binding': self.binding,
            'column_id': 'column-a', 'inventory_entry_id': self.entry['id'], 'source': self.value_source}

    def validate(self, target=None, **kwargs):
        return scope.validate_target(target or self.target, reports=self.reports, ticket=self.ticket,
            inventory=self.inventory, active=self.active, **kwargs)

    def empty(self):
        self.entry.update(effect='FULL_DOMAIN', restrictions=[], volatility='VIEWER_CHANGEABLE', assumption='SAVED_DEFAULT')
        self.active = []

    def receipt(self, column='column-a', exists=True, identity='reader'):
        surface = {'engine': 'synthetic', 'connection': 'connection', 'object': 'model', 'identity': identity}
        report = {'identity': identity}
        return {'id': 'receipt-' + column, 'status': 'COMPLETED', 'completeness': 'COMPLETE_RESPONSE',
            'check_kind': 'COLUMN_VALUE_EXISTENCE', 'column_id': column, 'report_id': 'report-a',
            'searched_value': 'North', 'value_exists': exists, 'execution_surface': surface,
            'surface_report': report, 'surface_attestation': attest_surface(surface, report, ('identity',)),
            'surface_report_binding': 'VALUE_QUERY', 'surface_report_receipt_id': 'receipt-' + column}

    def observed(self):
        self.empty()
        return {'resolution_kind': 'OBSERVED', 'report_binding': self.binding,
            'column_id': 'column-a', 'receipt_id': 'receipt-column-a', 'source': self.value_source}

    def test_exact_named_report_resolves_with_ticket_provenance(self):
        self.assertEqual(self.binding, {'resolution_kind': 'STATED', 'report_id': 'report-a', 'source': self.report_source})
        scope.report_binding(self.binding, reports=self.reports, ticket=self.ticket)

    def test_partial_case_changed_and_missing_names_never_bind(self):
        for quote in ('Inventory', 'inventory report', 'No such report'):
            source = {'start': 0, 'end': len(quote), 'quote': quote}
            result = scope.resolve_report(source, self.reports, quote)
            self.assertEqual(result['resolution_kind'], 'REFUSED')
            self.assertEqual(result['reason'], 'NO_EXACT_MATCH')
        result = scope.resolve_report(None, self.reports)
        self.assertEqual(result['reason'], 'UNNAMED'); self.assertEqual(result['candidates'], ['report-a', 'report-b'])

    def test_duplicate_report_names_refuse_and_name_both_candidates(self):
        reports = [self.reports[0], {'id': 'report-b', 'name': 'Inventory report'}]
        result = scope.resolve_report(self.report_source, reports, self.ticket)
        self.assertEqual(result['candidates'], ['report-a', 'report-b'])
        self.assertEqual(result['reason'], 'MULTIPLE_EXACT_MATCHES')
        with self.assertRaisesRegex(ValueError, 'Report ambiguity'):
            scope.report_binding(result, reports=reports, ticket=self.ticket)

    def test_hostile_target_without_report_binding_refuses(self):
        target = copy.deepcopy(self.target); del target['report_binding']
        with self.assertRaises(ValueError): self.validate(target)

    def test_hostile_report_binding_with_changed_identity_refuses(self):
        target = copy.deepcopy(self.target); target['report_binding']['report_id'] = 'report-b'
        with self.assertRaisesRegex(ValueError, 'exact retained'): self.validate(target)

    def test_foreign_declaration_in_discovery_manifest_fails_conservation(self):
        self.inventory['discovered'].append({**self.inventory['discovered'][0], 'report_id': 'report-b'})
        foreign = copy.deepcopy(self.entry); foreign['source'] = self.inventory['discovered'][-1]
        foreign['id'] = scope.inventory_identity(foreign['source']); self.inventory['entries'].append(foreign)
        self.active.extend(foreign['restrictions'])
        with self.assertRaisesRegex(ValueError, 'conservation.*foreign'): self.validate()

    def test_two_reports_sharing_the_column_and_value_cannot_cross_scope(self):
        self.validate()
        other = copy.deepcopy(self.inventory); other['report_id'] = 'report-b'
        for source in other['discovered']: source['report_id'] = 'report-b'
        for entry in other['entries']:
            entry['source']['report_id'] = 'report-b'; entry['id'] = scope.inventory_identity(entry['source'])
        with self.assertRaisesRegex(ValueError, 'conservation'):
            scope.validate_target(self.target, reports=self.reports, ticket=self.ticket, inventory=other, active=self.active)
        self.assertNotEqual(self.entry['id'], other['entries'][0]['id'])

    def test_undiscovered_missing_or_duplicate_dispositions_fail_conservation(self):
        for change in ('missing', 'extra', 'duplicate'):
            with self.subTest(change=change):
                inventory = copy.deepcopy(self.inventory)
                if change == 'missing': inventory['entries'] = []
                elif change == 'extra': inventory['discovered'].append({**inventory['discovered'][0], 'location': 'another'})
                else: inventory['entries'].append(copy.deepcopy(inventory['entries'][0]))
                with self.assertRaisesRegex(ValueError, 'conservation'):
                    scope.validate_inventory(inventory, self.active, binding=self.binding, reports=self.reports)

    def test_active_set_must_be_inventory_coverage_not_a_second_source(self):
        with self.assertRaisesRegex(ValueError, 'ACTIVE coverage'):
            scope.validate_inventory(self.inventory, [], binding=self.binding, reports=self.reports)
        with self.assertRaisesRegex(ValueError, 'ACTIVE coverage'):
            scope.validate_inventory(self.inventory, self.active + [{'field_id': 'untraceable', 'operator': 'IN', 'values': ['North']}], binding=self.binding, reports=self.reports)

    def test_full_domain_is_explicit_active_empty_not_unsupported_or_omitted(self):
        self.empty()
        entries = scope.validate_inventory(self.inventory, [], binding=self.binding, reports=self.reports)
        self.assertEqual(len(entries), 1); self.assertEqual(entries[0]['disposition'], 'ACTIVE')
        self.assertEqual(entries[0]['effect'], 'FULL_DOMAIN'); self.assertEqual(entries[0]['restrictions'], [])
        self.assertEqual(entries[0]['volatility'], 'VIEWER_CHANGEABLE')

    def test_restricted_empty_list_and_full_domain_with_predicate_refuse(self):
        self.entry['restrictions'] = []; self.active = []
        with self.assertRaisesRegex(ValueError, 'nonempty'): self.validate()
        self.entry['effect'] = 'FULL_DOMAIN'; self.entry['restrictions'] = [{'field_id': 'x', 'operator': 'IN', 'values': []}]
        with self.assertRaisesRegex(ValueError, 'cannot restrict'): self.validate()

    def test_empty_intersection_is_restricted_not_full_domain(self):
        self.entry['restrictions'][0]['values'] = []; self.active = copy.deepcopy(self.entry['restrictions'])
        scope.validate_inventory(self.inventory, self.active, binding=self.binding, reports=self.reports)
        self.assertEqual(self.entry['effect'], 'RESTRICTED')

    def test_observed_without_an_original_receipt_refuses(self):
        target = self.observed()
        with self.assertRaisesRegex(ValueError, 'coverage is incomplete'):
            self.validate(target, grouping_columns=['column-a'], observations={})

    def test_observed_requires_complete_existence_coverage_and_exactly_one_match(self):
        target = self.observed(); a = self.receipt(); b = self.receipt('column-b', False)
        self.validate(target, grouping_columns=['column-a', 'column-b'], observations={a['id']: a, b['id']: b})
        for mode in ('second matches', 'second absent', 'foreign report', 'incomplete response'):
            with self.subTest(mode=mode):
                changed = copy.deepcopy(b)
                if mode == 'second matches': changed['value_exists'] = True
                elif mode == 'foreign report': changed['report_id'] = 'report-b'
                elif mode == 'incomplete response': changed['completeness'] = 'TRUNCATED'
                observations = {a['id']: a} if mode == 'second absent' else {a['id']: a, changed['id']: changed}
                with self.assertRaises(ValueError): self.validate(target, grouping_columns=['column-a', 'column-b'], observations=observations)

    def test_observed_cannot_assert_no_filter_with_an_unsupported_declaration(self):
        target = self.observed()
        self.entry.update(disposition='UNSUPPORTED', effect='EXCLUDED', volatility='UNKNOWN', assumption='APPLICABILITY_UNKNOWN')
        receipt = self.receipt()
        with self.assertRaisesRegex(ValueError, 'supported declaration coverage'):
            self.validate(target, grouping_columns=['column-a'], observations={receipt['id']: receipt})

    def test_observed_cannot_replace_declared_filter_evidence(self):
        target = {**self.target, 'resolution_kind': 'OBSERVED', 'receipt_id': 'receipt-column-a'}
        del target['inventory_entry_id']
        with self.assertRaisesRegex(ValueError, 'cannot replace'): self.validate(target, grouping_columns=['column-a'], observations={})

    def test_failed_missing_or_unbound_existence_attestation_is_not_observed(self):
        target = self.observed()
        for change in ({'status': 'FAILED'}, {'value_exists': None}, {'surface_report_binding': 'METADATA_QUERY'}, {'surface_report': None}):
            with self.subTest(change=change):
                receipt = self.receipt(); receipt.update(change)
                with self.assertRaises(ValueError): self.validate(target, grouping_columns=['column-a'], observations={receipt['id']: receipt})

    def test_evidence_and_observed_have_distinct_engine_written_explanations(self):
        self.assertIn('report declares', scope.render(self.target, business=True))
        target = self.observed(); self.assertIn('no declared report filter', scope.render(target, business=True))
        self.assertIn('Resolution OBSERVED', scope.render(target))

    def test_stated_column_keeps_a_value_mismatch_in_the_audit(self):
        self.empty(); source = {'start': 0, 'end': 6, 'quote': 'Region'}
        value = {'start': 7, 'end': 12, 'quote': 'North'}
        binding = scope.resolve_report({'start': 13, 'end': 29, 'quote': 'Inventory report'}, self.reports, 'Region North Inventory report')
        receipt = self.receipt(exists=False)
        target = {'resolution_kind': 'STATED', 'report_binding': binding, 'column_id': 'column-a',
            'source': source, 'value_source': value, 'lookup': {'status': 'MISMATCH', 'receipt_ids': [receipt['id']]}}
        scope.validate_target(target, reports=self.reports, ticket='Region North Inventory report', columns=[{'id': 'column-a', 'name': 'Region'}], observations={receipt['id']: receipt})
        target['lookup']['status'] = 'MATCH'
        with self.assertRaisesRegex(ValueError, 'mismatch'):
            scope.validate_target(target, reports=self.reports, columns=[{'id': 'column-a', 'name': 'Region'}], observations={receipt['id']: receipt})

    def test_unknown_enums_and_extra_fields_never_reach_outputs(self):
        for name, value in (('effect', 'guessed'), ('disposition', ['ACTIVE', 'CONDITIONAL']), ('assumption', 'guessed'), ('volatility', 'guessed')):
            with self.subTest(name=name):
                inventory = copy.deepcopy(self.inventory); inventory['entries'][0][name] = value
                with self.assertRaises(ValueError): scope.validate_inventory(inventory, self.active, binding=self.binding, reports=self.reports)
        target = {**self.target, 'guessed_report': 'report-b'}
        with self.assertRaises(ValueError): self.validate(target)

    def test_unresolved_report_cannot_be_encoded_as_value_absence(self):
        binding = scope.resolve_report(None, self.reports)
        target = {'resolution_kind': 'REFUSED', 'report_binding': binding, 'source': self.value_source, 'candidates': [], 'reason': 'VALUE_ABSENT'}
        with self.assertRaisesRegex(ValueError, 'Report ambiguity'): self.validate(target)
        target['reason'] = 'REPORT_UNRESOLVED'
        self.validate(target)
        target['report_binding'] = self.binding
        with self.assertRaisesRegex(ValueError, 'unresolved report binding'): self.validate(target)

    def test_request_is_not_a_resolution_and_does_not_guess_a_column(self):
        properties = scope.REQUEST_SCHEMA['properties']
        self.assertEqual(properties['state']['enum'], ['REQUESTED'])
        self.assertNotIn('column_id', properties); self.assertNotIn('resolution_kind', properties)
        self.assertFalse(scope.REQUEST_SCHEMA['additionalProperties'])


if __name__ == '__main__': unittest.main()
