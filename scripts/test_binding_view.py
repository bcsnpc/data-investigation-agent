import copy
import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from investigator.binding_view import read


class BindingViewTests(unittest.TestCase):
    def test_original_values_locations_and_failed_attempts_survive_without_current_claim(self):
        rows=[{'proposal':{'location':{'item':'code','path':'file','cell':'c','line_start':1,'line_end':2,'content_hash':'hash'},
                          'boundary':{'from_layer':'a','to_layer':'b'},'target':{'table':'table','column':'col'}},
               'context':'original','status':'FALSIFIED','reason':'Different sample',
               'observations':[{'status':'COMPLETED','quantities':{'sum':'1','count':2},'evidence':{'id':'left'}},
                               {'status':'COMPLETED','quantities':{'sum':'2','count':2},'evidence':{'id':'right'}}]}]
        installation=SimpleNamespace(ledger=SimpleNamespace(records=Mock(return_value=rows)))
        before=copy.deepcopy(rows);view=read(installation)
        self.assertEqual(rows,before)
        self.assertEqual(view[0]['recorded_verdict'],'FALSIFIED')
        self.assertEqual(view[0]['current_eligibility'],'NOT_EVALUATED')
        self.assertEqual(view[0]['values'][0]['value'],{'sum':'1','count':2})
        self.assertEqual(view[0]['values'][1]['receipt_id'],'right')
        self.assertEqual(view[0]['location'],rows[0]['proposal']['location'])
        view[0]['location']['path']='changed';self.assertEqual(rows,before)
        installation.ledger.records.assert_called_once_with()

    def test_absent_installation_does_not_open_anything_or_invent_a_binding(self):
        self.assertEqual(read(None),[])


if __name__=='__main__':unittest.main()
