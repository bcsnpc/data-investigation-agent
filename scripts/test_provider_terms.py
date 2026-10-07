import copy
import unittest
import test_estate_manifest as fixture
from investigator import estate_manifest
from investigator.adapters.estate_installation import configuration
from investigator.provider_terms import declaration, from_bootstrap


class ProviderTermsTests(unittest.TestCase):
    def test_explicit_region_is_closed_and_recorded_without_credentials(self):
        value = fixture.ManifestTests().fixture()
        value['model']['region'] = {'status':'DECLARED','name':'owner-specified-region','evidence':'deployment control-plane record'}
        config = configuration(estate_manifest.validate(value))
        terms = from_bootstrap({'config':config,'profile':{'adapter':'azure'}})
        self.assertEqual(terms, declaration(value['model']))
        self.assertNotIn('credential', terms)
        self.assertNotIn('generation_options', terms)
        terms['region']['name'] = 'modified copy'
        self.assertEqual(config['_estate']['provider_terms']['region']['name'], 'owner-specified-region')

    def test_no_region_is_explicitly_unknown_not_inferred_from_hostname(self):
        value = fixture.ManifestTests().fixture()
        self.assertNotIn('region', value['model'])
        self.assertEqual(declaration(value['model'])['region']['status'], 'UNDECLARED')
        self.assertEqual(from_bootstrap({'config':{},'profile':{'adapter':'azure'}})['region']['status'], 'UNRECORDED')

    def test_region_declaration_requires_evidence_and_changes_whole_approval_hash(self):
        from investigator.onboarding import digest
        value = fixture.ManifestTests().fixture()
        old = configuration(estate_manifest.validate(value))['_estate']['manifest_hash']
        value['model']['region'] = {'status':'DECLARED','name':'region','evidence':'control-plane observation'}
        new = configuration(estate_manifest.validate(value))['_estate']['manifest_hash']
        self.assertNotEqual(old, new)
        for bad in ({'status':'DECLARED','name':'region'}, {'status':'UNDECLARED'}, {'status':'DECLARED','name':'region','evidence':'record','secret':'forbidden'}):
            item = copy.deepcopy(value); item['model']['region'] = bad
            with self.assertRaisesRegex(ValueError, 'region'): estate_manifest.validate(item)


if __name__ == '__main__': unittest.main()
