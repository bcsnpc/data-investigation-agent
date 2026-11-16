import unittest
from unittest.mock import Mock
from investigator.ai_investigation import Investigator


class AccessFirstTests(unittest.TestCase):
    def instance(self,issue):
        obj=Investigator.__new__(Investigator)
        obj.context={'intake':{'issue_type':issue,'table':'table'},
            'path':{'nodes':[{'id':'table','kind':'TABLE'}]}}
        obj.read_tools={'get_security_definitions':{'schema':{'properties':{'node':{'enum':['table']}}}}}
        obj.state={'cache':{},'pending':None,'tools_used':0,'messages':[]}
        obj.refresh_tools=Mock();obj.save=Mock();obj.dispatch=Mock(return_value={'roles':[]})
        obj.evidence=Mock(return_value='security-proof')
        return obj

    def test_access_fetches_security_first_and_never_repeats_it(self):
        obj=self.instance('OTHERS_SEE_DIFFERENT_NUMBER')
        obj.prime_access_definitions();obj.prime_access_definitions()
        obj.dispatch.assert_called_once_with('get_security_definitions',{'node':'table'})
        self.assertEqual(obj.state['tools_used'],1)
        self.assertIsNone(obj.state['pending'])

    def test_normal_calculation_does_not_gain_an_access_read(self):
        obj=self.instance('NUMBER_LOOKS_WRONG');obj.prime_access_definitions()
        obj.dispatch.assert_not_called()
