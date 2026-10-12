"""Execute the actual screenshot renderer without a browser or estate calls."""
import pathlib,subprocess,unittest

class Tests(unittest.TestCase):
    def test_unresolved_names_show_locator_question_without_candidate_buttons(self):
        source=(pathlib.Path(__file__).resolve().parents[1]/'apps/investigator-workspace/claims.js').read_text(encoding='utf8')
        renderer=source[source.index('  function renderScreenshot(review)'):source.index('  function portalContext()')]
        harness='''let screenshot; const buttons=[]; const text=[];
        const box={hidden:true,replaceChildren(){},appendChild(value){buttons.push(value)}};
        const el=()=>box;const paragraph=(box,value)=>text.push(value);
        const node=(tag,label)=>({tag,label,addEventListener(){}});
        '''+renderer+'''
        renderScreenshot({status:'NEEDS_LOCATOR',question:{text:'Give a distinguishing portal tab'},candidates:[{label:'Same',candidate_id:'a'},{label:'Same',candidate_id:'b'}]});
        if(buttons.length!==0||!text.includes('Give a distinguishing portal tab'))throw Error('Hidden-ID candidate controls exposed');
        '''
        result=subprocess.run(['node','-e',harness],capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_actual_check_renderer_uses_both_prose_outputs_never_serializes_evidence(self):
        source=(pathlib.Path(__file__).resolve().parents[1]/'apps/investigator-workspace/claims.js').read_text(encoding='utf8')
        renderer=source[source.index('  function renderInvestigation(result)'):source.index('  function renderScreenshot(review)')]
        harness='''const texts=[]; const box={hidden:true,replaceChildren(){},appendChild(){}};
        const el=()=>box;const paragraph=(parent,value)=>texts.push(value);
        const node=(tag,label)=>({appendChild(){}});
        '''+renderer+'''
        renderInvestigation({outputs:{business_explanation:'A plain result.',technical_narrative:'Evidence and its limits.'},checks:{secret:'DO_NOT_SERIALIZE'}});
        if(texts.join('|')!=='A plain result.|Evidence and its limits.')throw Error('Narrative altered or raw evidence leaked');
        let refused=false;try{renderInvestigation({outputs:{business_explanation:'Only one'}})}catch(e){refused=true}
        if(!refused)throw Error('Incomplete output pair accepted');
        '''
        result=subprocess.run(['node','-e',harness],capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)

if __name__=='__main__':unittest.main()
