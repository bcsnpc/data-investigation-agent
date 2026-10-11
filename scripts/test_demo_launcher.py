"""One start command creates only ephemeral local browser authentication."""
import os
import unittest
import json
import re
import subprocess
from pathlib import Path
from unittest.mock import MagicMock,patch
import serve_investigator_workspace as launcher


class LauncherTests(unittest.TestCase):
    def test_page_outline_is_an_accessible_target_choice(self):
        source=(Path(__file__).resolve().parents[1]/'apps/investigator-workspace/form.js').read_text(encoding='utf-8')
        function=source[source.index('async function loadFormPagePicture()'):source.index('function formTargetChanged()')]
        script='''const vm=require('node:vm'),assert=require('node:assert/strict');
const box={attributes:{},listeners:{},setAttribute(k,v){this.attributes[k]=v;},addEventListener(k,v){this.listeners[k]=v;}};
const drawing={children:[box],attributes:{},setAttribute(k,v){this.attributes[k]=v;}};
const elements={'form-report':{value:'report'},'form-page':{value:'page'},'form-target':{value:''},'form-page-picture':{replaceChildren(){},append(){}}};
let changed=0;const context={formLayoutEpoch:0,$:id=>elements[id],
api:async()=>({page:{visuals:[{target_id:'card',name:'Global card'}]},qualification:'Retained geometry'}),
layoutDrawing:()=>drawing,node:()=>({}),reportFormVisuals:()=>[{target_id:'card'}],formTargetChanged:()=>changed++};
vm.createContext(context);vm.runInContext(FUNCTION,context);
(async()=>{await context.loadFormPagePicture();assert.equal(drawing.attributes.role,'group');
assert.equal(box.attributes.role,'button');assert.equal(box.attributes['aria-label'],'Select Global card');
let prevented=0;box.listeners.keydown({key:'Enter',preventDefault(){prevented++;}});
assert.equal(elements['form-target'].value,'card');assert.equal(changed,1);assert.equal(prevented,1);})();
'''.replace('FUNCTION',json.dumps(function))
        result=subprocess.run(['node','-e',script],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_classic_script_globals_preserve_browser_history_for_fragment_login(self):
        source=(Path(__file__).resolve().parents[1]/'apps/investigator-workspace/workspace.js').read_text(encoding='utf-8')
        # Classic-script function declarations become window properties. Test
        # the actual declaration names and actual bootstrap, without a browser
        # or credentials, so a newly added conflicting global also fails.
        names=re.findall(r'^(?:async )?function ([A-Za-z_$][\w$]*)\(',source,re.M)
        bootstrap=source[source.index('const initialAccess='):]
        script='''const vm=require('node:vm'),assert=require('node:assert/strict');
let submitted=0,removed=0;const input={value:''};
const nativeHistory={replaceState(){removed++;}};
const context={URLSearchParams,location:{hash:'#access=synthetic-ephemeral',pathname:'/'},
history:nativeHistory,$:id=>id==='access-key'?input:{requestSubmit(){submitted++;}}};
context.window=context;vm.createContext(context);
vm.runInContext(NAMES.map(n=>'function '+n+'() {}').join('\\n'),context);
assert.equal(context.history,nativeHistory);
vm.runInContext(BOOTSTRAP,context);
assert.equal(removed,1);assert.equal(submitted,1);assert.equal(input.value,'synthetic-ephemeral');
'''.replace('NAMES',json.dumps(names)).replace('BOOTSTRAP',json.dumps(bootstrap))
        result=subprocess.run(['node','-e',script],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_open_browser_uses_ephemeral_key_without_environment_or_secret_write(self):
        workspace=MagicMock();manifest={'model':{'credential':{},'endpoint':'https://example.invalid','deployment':'test'}}
        server=MagicMock();server.__enter__.return_value=server
        server.serve_forever.side_effect=KeyboardInterrupt
        with patch.dict(os.environ,{},clear=True),patch('sys.argv',['demo','--manifest','estate.json','--open-browser']),\
             patch('investigator.estate_installation.build',return_value=(manifest,workspace)),\
             patch.object(launcher,'create_app') as app,patch.object(launcher,'make_server',return_value=server),\
             patch.object(launcher,'local_azure_key'),patch.object(launcher.webbrowser,'open') as browser,\
             patch('builtins.print') as output:
            with self.assertRaises(KeyboardInterrupt):launcher.main()
            key=app.call_args.args[1]
            self.assertGreaterEqual(len(key),32)
            browser.assert_called_once_with('http://127.0.0.1:8776/#access='+key)
            self.assertNotIn('INVESTIGATOR_WORKSPACE_TOKEN',os.environ)
            self.assertNotIn(key,str(output.call_args_list))
            workspace.work.assert_not_called()
            workspace.stopping.set.assert_called_once()

if __name__=='__main__':unittest.main()
