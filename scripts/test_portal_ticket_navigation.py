"""Opening an existing ticket must preserve the tab's memory-only authentication."""
import json
from pathlib import Path
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]

class TicketNavigationTests(unittest.TestCase):
    def test_existing_ticket_opens_in_place_without_losing_key_or_submitting(self):
        source=(ROOT/'apps/investigator-workspace/questionnaire.js').read_text(encoding='utf-8')
        handler=source.split("$('simple-ticket-link').addEventListener",1)[1].split('\nfunction renderQuestionnaireTicket',1)[0]
        script="""
const assert=require('node:assert/strict');
let callback,smartTicket={ticket:{id:'saved-ticket'}},smartTicketGeneration=0;
let key='synthetic-in-memory-session-key', prevented=0, calls=[], displayed=[];
const $=()=>({addEventListener:(kind,fn)=>{assert.equal(kind,'click');callback=fn;}});
const guard=fn=>fn;
const api=async path=>{calls.push(path);return {ticket:{id:'saved-ticket',state:'FINDINGS_SHARED'}};};
const showSmartTicket=saved=>displayed.push(saved);
"""+"$('simple-ticket-link').addEventListener"+handler+"""
(async()=>{
 await callback({preventDefault:()=>prevented++});
 assert.equal(prevented,1);assert.equal(key,'synthetic-in-memory-session-key');
 assert.deepEqual(calls,['tickets/saved-ticket']);
 assert.equal(displayed[0].ticket.state,'FINDINGS_SHARED');
 smartTicket=null;await callback({preventDefault:()=>prevented++});
 assert.equal(calls.length,1);
})().catch(error=>{console.error(error);process.exitCode=1;});
"""
        result=subprocess.run(['node','-e',script],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)

if __name__=='__main__':unittest.main()
