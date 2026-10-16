"""Route gate CLI keeps whole-estate status informational."""
import importlib.util,io,json,tempfile,unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('readiness_cli',Path(__file__).with_name('estate_readiness.py'))
cli=importlib.util.module_from_spec(spec);spec.loader.exec_module(cli)

class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.routes=self.root/'routes.json'
  self.routes.write_text(json.dumps({'routes':[{'id':'route','label':'Quantity','measure_id':'metric'}],
                                    'certificates':[{'version':'route-readiness-v1'}]}))
  self.args=['--manifest',str(self.root/'estate.json'),'--approval',str(self.root/'approval.json'),
             '--routes',str(self.routes),'--replay-output',str(self.root/'exclusive')]
 def run_cli(self,result):
  output=io.StringIO()
  with patch.object(cli,'current_pins',return_value=({},{})),patch.object(cli,'assess',return_value={'status':'BLOCKED'}),\
       patch('investigator.route_readiness.assess_routes',return_value=result)as port,redirect_stdout(output):
   exit_code=cli.main(self.args)
  return exit_code,json.loads(output.getvalue()),port
 def test_ready_route_exits_success_even_with_informational_blocked_estate(self):
  result={'ready_routes':[{'label':'Quantity'}],'routes':[],'whole_estate':{'informational':True,'readiness':{'status':'BLOCKED'}}}
  code,actual,port=self.run_cli(result)
  self.assertEqual(code,0);self.assertEqual(actual,result)
  self.assertEqual(len(port.call_args.kwargs['route_inventory']),1)
  self.assertEqual(port.call_args.kwargs['whole_estate']['status'],'BLOCKED')
 def test_no_ready_routes_exits_blocked_without_manufacturing_estate_status(self):
  code,result,_=self.run_cli({'ready_routes':[],'routes':[],'whole_estate':{'informational':True}})
  self.assertEqual(code,2);self.assertEqual(result['ready_routes'],[])
 def test_missing_replay_output_cannot_reuse_ready_label(self):
  self.args=self.args[:-2]
  code,result,port=self.run_cli({'ready_routes':[{'id':'forged'}]})
  self.assertEqual(code,2);self.assertEqual(result['status'],'BLOCKED');port.assert_not_called()

if __name__=='__main__':unittest.main()
