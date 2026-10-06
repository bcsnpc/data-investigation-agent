"""Observed comparison flags retain their original query and exact surface."""
import copy
import unittest
from jsonschema.exceptions import ValidationError
from investigator.string_semantics import observation,resolve,validate,Observations,FLAGS,resolve_layers
from investigator.adapters.microsoft_string_semantics import dax,sql,spark,PAIRS
import test_binding_sample as samples

BINARY={'collation':'BINARY','case_fold':False,'trim':False,'accent_fold':False,
        'kana':False,'width':False,'resolution':'DECLARED'}


def record(**flags):
    surface={'engine':'synthetic','version':'1','object':'target','identity':'reader'}
    return {'row':{**{k:False for k in FLAGS},**flags,**{'surface_'+k:v for k,v in surface.items()}},'query':'synthetic comparison statement',
            'receipt_id':'synthetic-receipt','surface_report_binding':'VALUE_QUERY',
            'surface':surface}


class ObservedStringTests(unittest.TestCase):
    def test_all_five_flags_required_and_partial_never_defaults(self):
        full=record(case_fold=True)
        value=observation(full)
        self.assertEqual(value['resolution'],'OBSERVED')
        self.assertEqual(value['collation'],'OBSERVED_COMPARISON_PROBE')
        self.assertEqual(validate(value),value)
        for flag in FLAGS:
            partial=copy.deepcopy(full);del partial['row'][flag]
            with self.assertRaisesRegex(ValueError,'Complete five'):observation(partial)
        for bad in ('true',None,2,0.0):
            with self.assertRaises(ValueError):observation(record(case_fold=bad))

    def test_observation_cannot_be_forged_by_changing_resolved_flags(self):
        value=observation(record(case_fold=True))
        with self.assertRaises(ValueError):validate({**value,'case_fold':False})
        with self.assertRaises(ValidationError):validate({**value,'resolution':'guessed'})
        with self.assertRaises(ValidationError):validate({k:v for k,v in value.items() if k!='width'})
        with self.assertRaises(ValueError):validate({**BINARY,'observation':record()})

    def test_binary_declaration_vs_observed_fold_blocks_with_both_named(self):
        with self.assertRaisesRegex(ValueError,'DECLARATION_CONTRADICTED') as raised:
            resolve(BINARY,record(case_fold=True))
        self.assertIn('"declared"',str(raised.exception))
        self.assertIn('"observed"',str(raised.exception))
        self.assertEqual(resolve(BINARY,record())['resolution'],'OBSERVED')
        manifest={'layers':[{'id':'target','string_semantics':BINARY}]}
        before=copy.deepcopy(manifest)
        with self.assertRaises(ValueError):resolve_layers(manifest,{'target':record(case_fold=True)})
        self.assertEqual(manifest,before)
        self.assertEqual(resolve_layers(manifest,{'target':record()})['layers'][0]['string_semantics']['resolution'],'OBSERVED')

    def test_memo_is_exact_surface_and_version_and_rechecks_declaration(self):
        cache=Observations();r=record();cache.remember(BINARY,r)
        self.assertIsNotNone(cache.lookup(r['surface'],BINARY))
        for field in ('engine','version','object','identity'):
            self.assertIsNone(cache.lookup({**r['surface'],field:'different'}))
        with self.assertRaises(ValueError):cache.lookup(r['surface'],{**BINARY,'collation':'fold','case_fold':True})
        for key in ('version','identity'):
            bad=record();del bad['surface'][key]
            with self.assertRaises(ValidationError):observation(bad)
        with self.assertRaises(ValidationError):observation({**r,'surface_report_binding':'SEPARATE_QUERY'})
        bad=record();bad['row']['surface_version']='other'
        with self.assertRaisesRegex(ValueError,'same-query'):observation(bad)

    def test_observed_case_fold_dedup_requires_target_semantics_on_both_sides(self):
        trial=samples.BindingSampleTests();trial.setUp()
        declarations={'sources':{'input-table':BINARY},'target':observation(record(case_fold=True)),
                      'comparison':'TARGET_SEMANTICS_ON_BOTH_SIDES'}
        self.assertEqual(trial.trial('STRING',['Houston','houston'],['houston'])['status'],'FALSIFIED')
        good=trial.trial('STRING',['Houston','houston'],['houston'],semantics=declarations,deduplicate=True)
        self.assertEqual(good['status'],'VERIFIED')
        self.assertEqual(good['string_semantics'],declarations)
        self.assertEqual(trial.trial('STRING',['Houston','houston'],['Dallas'],semantics=declarations,deduplicate=True)['status'],'FALSIFIED')

    def test_adapter_probes_are_five_unicode_pairs_with_same_statement_self_report(self):
        for text in (dax(),sql(),spark()):
            for flag,left,right in PAIRS:
                self.assertIn(flag,text);self.assertIn(left,text);self.assertIn(right,text)
            self.assertIn('surface_version',text);self.assertIn('surface_identity',text)
        self.assertIn('N\'\u30a2\'',sql())
        self.assertIn('DB_NAME()',sql());self.assertIn('INFO.PROPERTIES()',dax())


if __name__=='__main__':unittest.main()
