"""Consumer invariants, including dishonest and incomplete synthetic adapters."""
import copy
import json
import unittest
from investigator import declaration_inventory as inventory, declared_reproduction as reproduction, report_scope
from investigator.synthesis_digest import _context_evidence, _process_evidence
from test_declared_reproduction import NeutralAdapter, SCOPE


class InventoryTests(unittest.TestCase):
    def declaration(self):
        return NeutralAdapter().declared_context({'id': 'top'}, 'measure', SCOPE)

    def validate(self, declaration):
        return report_scope.validate_inventory(declaration['inventory'], declaration['restrictions'],binding=declaration['evidence']['report_binding'],reports=declaration['evidence']['report_catalog'])

    def test_required_inventory_missing_refuses_before_any_read(self):
        class Missing(NeutralAdapter):
            def declared_context(self, *args):
                d = super().declared_context(*args); del d['inventory']; return d
        adapter = Missing()
        result = reproduction.run(adapter, {'id': 'top'}, 'measure', SCOPE)
        self.assertEqual(result['status'], 'UNDECLARED')
        self.assertEqual(adapter.read_scopes, [])

    def test_missing_disposition_is_contract_violation(self):
        d = self.declaration(); del d['inventory']['entries'][0]['disposition']
        with self.assertRaisesRegex(ValueError, 'disposition'): self.validate(d)

    def test_multiple_dispositions_are_unrepresentable(self):
        d = self.declaration(); d['inventory']['entries'][0]['disposition'] = ['ACTIVE', 'CONDITIONAL']
        with self.assertRaisesRegex(ValueError, 'disposition'): self.validate(d)

    def test_discovered_declaration_without_disposition_fails_conservation(self):
        d = self.declaration(); d['inventory']['discovered'].append({'location': 'second', 'content_hash': 'b'*64})
        with self.assertRaisesRegex(ValueError, 'conservation'): self.validate(d)

    def test_duplicate_disposition_fails_conservation(self):
        d = self.declaration(); d['inventory']['entries'].append(copy.deepcopy(d['inventory']['entries'][0]))
        with self.assertRaisesRegex(ValueError, 'conservation'): self.validate(d)

    def test_undiscovered_inventory_entry_fails_conservation(self):
        d = self.declaration(); entry=copy.deepcopy(d['inventory']['entries'][0]);entry['source']['location']='extra'
        entry['id']=report_scope.inventory_identity(entry['source']);d['inventory']['entries'].append(entry)
        with self.assertRaisesRegex(ValueError, 'conservation'): self.validate(d)

    def test_active_restriction_without_inventory_trace_fails(self):
        d = self.declaration();d['restrictions'].append({'field_id': 'untraced', 'operator': 'IN', 'values': [1]})
        with self.assertRaisesRegex(ValueError, 'coverage'): self.validate(d)

    def test_active_entry_without_active_restriction_fails(self):
        d=self.declaration();d['restrictions'].pop()
        with self.assertRaisesRegex(ValueError, 'coverage'): self.validate(d)

    def test_restriction_may_not_trace_to_conditional_entry(self):
        d=self.declaration();e=d['inventory']['entries'][0];e['disposition']='CONDITIONAL';e['restrictions']=[];e['effect']='EXCLUDED'
        with self.assertRaisesRegex(ValueError, 'coverage'): self.validate(d)

    def test_empty_active_entry_is_not_falsely_accounted_for(self):
        d=self.declaration();d['inventory']['entries'][0]['restrictions']=[];d['restrictions']=[]
        with self.assertRaisesRegex(ValueError, 'nonempty'): self.validate(d)

    def test_reordering_preserves_derived_identity_and_neutral_projection(self):
        d=self.declaration();e=copy.deepcopy(d['inventory']['entries'][0]);e['source']['location']='alternative'
        e['id']=report_scope.inventory_identity(e['source']);e.update(disposition='CONDITIONAL',restrictions=[],assumption='INVOCATION_UNKNOWN',effect='EXCLUDED')
        d['inventory']['discovered'].append(e['source']);d['inventory']['entries'].append(e)
        before=inventory.neutral(self.validate(d));d['inventory']['entries'].reverse();d['inventory']['discovered'].reverse()
        self.assertEqual(before,inventory.neutral(self.validate(d)))
        self.assertEqual(e['id'],report_scope.inventory_identity(e['source']))

    def test_identity_cannot_be_iteration_counter(self):
        d=self.declaration();d['inventory']['entries'][0]['id']='0'
        with self.assertRaisesRegex(ValueError, 'identity differs'): self.validate(d)

    def test_consumer_vocabulary_rejects_unknown_values(self):
        for field in inventory.SCHEMA:
            d=self.declaration();d['inventory']['entries'][0][field]='unrecognised'
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'Invalid declaration'): self.validate(d)

    def test_unknown_active_applicability_cannot_be_assumed(self):
        d=self.declaration();d['inventory']['entries'][0]['volatility']='UNKNOWN'
        with self.assertRaisesRegex(ValueError,'applicability'):self.validate(d)

    def test_unsupported_unrelated_declaration_blocks_capability_before_reads(self):
        class Unsupported(NeutralAdapter):
            def declared_context(self,*args):
                d=super().declared_context(*args);source={'report_id':'report','location':'unrelated','content_hash':'c'*64}
                d['inventory']['discovered'].append(source)
                d['inventory']['entries'].append({'id':report_scope.inventory_identity(source),'source':source,
                    'disposition':'UNSUPPORTED','volatility':'UNKNOWN','assumption':'APPLICABILITY_UNKNOWN',
                    'opaque_provenance':'unfamiliar-kind','restrictions':[],'effect':'EXCLUDED'})
                return d
        adapter=Unsupported();result=reproduction.run(adapter,{'id':'top'},'measure',SCOPE)
        self.assertEqual(result['status'],'UNDECLARED');self.assertEqual(adapter.read_scopes,[])
        self.assertEqual(result['inventory'][-1 if result['inventory'][-1]['disposition']=='UNSUPPORTED' else 0]['disposition'],'UNSUPPORTED')
        self.assertIn('Unsupported declarations',result['reason'])

    def execute(self, provenance, volatile=False, value=3):
        class Candidate(NeutralAdapter):
            def declared_context(self,*args):
                d=super().declared_context(*args);e=d['inventory']['entries'][0];e['opaque_provenance']=provenance
                if volatile:e.update(volatility='VIEWER_CHANGEABLE',assumption='SAVED_DEFAULT')
                return d
        return reproduction.run(Candidate(value),{'id':'top'},'measure',SCOPE)

    def test_opaque_provenance_never_changes_engine_actions_findings_or_qualifications(self):
        a=self.execute('native-kind-A');b=self.execute('totally-different-native-kind')
        for field in ('status','finding','business_output','technical_output'):
            self.assertEqual(json.dumps(a[field],sort_keys=True),json.dumps(b[field],sort_keys=True))
        for result in (a,b):
            projected=_context_evidence(result['observations'][0])
            self.assertNotIn('native-kind',json.dumps(projected['result']))
            self.assertIn('declarations',projected['result'])
            self.assertNotIn('opaque_provenance',json.dumps(projected))

    def test_saved_default_reproduction_is_explicitly_weaker_in_both_outputs(self):
        fixed=self.execute('opaque');volatile=self.execute('opaque',True)
        for field in ('business_output','technical_output'):
            self.assertIn('assumes saved default',volatile[field]);self.assertNotIn('assumes saved default',fixed[field])
            self.assertNotIn('confirmed',volatile[field].lower())

    def test_non_reproduction_names_moved_default_in_both_outputs(self):
        result=self.execute('opaque',True,value=4)
        for field in ('business_output','technical_output'):self.assertIn('moved slicer',result[field])

    def test_synthesis_revalidates_original_inventory_not_marker_assertion(self):
        result=self.execute('opaque',True);by_id={o['id']:o for o in result['observations']}
        by_id['declaration']['declaration_inventory']['entries'][0]['assumption']='NONE'
        with self.assertRaisesRegex(ValueError,'inventory differs'):
            _process_evidence(result['finding'],by_id)

    def test_claim_cannot_omit_saved_default_qualification(self):
        result=self.execute('opaque',True);result['finding']['limitations'].pop()
        with self.assertRaisesRegex(ValueError,'limitations differ'):
            reproduction.validate(result['finding'],{o['id']:o for o in result['observations']})

    def test_only_conditional_inventory_is_undeclared_without_crash(self):
        class Conditional(NeutralAdapter):
            def declared_context(self,*args):
                d=super().declared_context(*args);d['restrictions']=[]
                d['inventory']['entries'][0].update(disposition='CONDITIONAL',restrictions=[],assumption='INVOCATION_UNKNOWN',effect='EXCLUDED')
                return d
        adapter=Conditional();result=reproduction.run(adapter,{'id':'top'},'measure',SCOPE)
        self.assertEqual(result['status'],'UNDECLARED');self.assertEqual(adapter.read_scopes,[])

    def test_conditional_alternative_qualification_comes_from_neutral_field(self):
        fields=[{'id':'opaque','disposition':'CONDITIONAL','volatility':'FIXED','assumption':'INVOCATION_UNKNOWN'}]
        self.assertIn('invoked bookmark',inventory.qualifications(fields,'NOT_REPRODUCED')[-1])

    def test_malformed_active_set_is_contract_violation_not_type_error(self):
        d=self.declaration();d['restrictions']=None
        with self.assertRaisesRegex(ValueError,'requires a list'):self.validate(d)

    def test_combined_active_bound_is_checked_before_reads(self):
        class TooMany(NeutralAdapter):
            def declared_context(self,*args):
                d=super().declared_context(*args)
                restrictions=[{'field_id':'f'+str(i),'operator':'IN','values':[i]} for i in range(33)]
                first=d['inventory']['entries'][0];first['restrictions']=restrictions[:20]
                second=copy.deepcopy(first);second['source']['location']='second';second['id']=report_scope.inventory_identity(second['source'])
                second['restrictions']=restrictions[20:]
                d['inventory']['entries'].append(second);d['inventory']['discovered'].append(second['source']);d['restrictions']=restrictions
                return d
        adapter=TooMany();result=reproduction.run(adapter,{'id':'top'},'measure',SCOPE)
        self.assertEqual(result['status'],'UNDECLARED');self.assertEqual(adapter.read_scopes,[])
        self.assertEqual(result['unsupported_form'],'DECLARATION_INVENTORY_CONTRACT')

    def test_native_provenance_and_source_location_are_absent_from_model_projection(self):
        result=self.execute('native-provenance-should-never-be-model-input',True)
        projected=_context_evidence(result['observations'][0])
        text=json.dumps(projected)
        self.assertNotIn('native-provenance-should-never-be-model-input',text)
        self.assertNotIn('definition/selection',text)
        self.assertIn('SAVED_DEFAULT',text)
