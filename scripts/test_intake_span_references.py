import copy,json,re,unittest
from pathlib import Path
from unittest.mock import patch
from investigator import intake_span_references as refs,intake_extraction as extraction
from test_intake_extraction import fixture

def reference(text,quote,occurrence=1):
    positions=[m.start() for m in re.finditer('(?='+re.escape(quote)+')',text)]
    start=positions[occurrence-1];end=start+len(quote);ts=refs.tokens(text)
    return [next(t['id'] for t in ts if t['start']==start),next(t['id'] for t in ts if t['end']==end)]
def response(text,**updates):
    value={k:[] for k in extraction.SCHEMA['properties']}
    value.update(version=refs.VERSION,kind='FIGURE_DIFFERENCE',triage='MISMATCH_COMPLAINT:VERTICAL',primary=[1,len(refs.tokens(text))])
    value.update(updates);return value
class ReferenceTests(unittest.TestCase):
    def test_exact_billing_ticket_wording_no_copied_quote_needed(self):
        root=Path(__file__).resolve().parents[1]/'acceptance/tickets/billing/tester'
        for path in sorted(root.glob('ticket-*.txt')):
            with self.subTest(ticket=path.name):
                text=path.read_text(encoding='utf-8-sig');raw=response(text)
                from investigator.proposal_limits import INTAKE_QUOTE
                end=next(t['id'] for t in reversed(refs.tokens(text)) if t['end']-refs.tokens(text)[0]['start']<=INTAKE_QUOTE)
                raw['primary'][1]=end
                numbers=list(re.finditer(r'(?<!\w)\d+(?:\.\d+)?(?!\w)',text))
                if numbers:
                    quote=numbers[0].group();raw['figures']=[{'quote':reference(text,quote),'role':'PRIMARY','state':'NUMBER','precision_quote':None}]
                decoded=refs.decode(raw,text);spans=extraction.spans(decoded,text)
                self.assertEqual(spans['primary']['quote'],text[refs.tokens(text)[0]['start']:refs.tokens(text)[end-1]['end']])
                if numbers:self.assertEqual(spans['figures'][0]['quote']['start'],numbers[0].start())
                self.assertNotIn('quote',json.dumps(raw['primary']))
    def test_duplicate_numeral_reference_preserves_actual_occurrence(self):
        text='The invoice is 950; the card shows 950.'
        raw=response(text,figures=[{'quote':reference(text,'950',2),'role':'PRIMARY','state':'NUMBER','precision_quote':None}])
        decoded=refs.decode(raw,text);span=extraction.spans(decoded,text)['figures'][0]['quote']
        self.assertEqual(span['start'],text.rindex('950'));self.assertEqual(decoded['figures'][0]['occurrence'],2)
    def test_bad_reference_and_outside_nested_reference_refuse(self):
        text='North is mentioned. I selected warehouse South.'
        raw=response(text)
        for ref in ([0,1],[5,2],[1,999]):
            raw['primary']=ref
            with self.assertRaises(Exception):refs.decode(raw,text)
        raw=response(text,selections=[{'quote':reference(text,'warehouse South'),'column':reference(text,'warehouse'),'value':reference(text,'North'),'role':'PRIMARY'}])
        with self.assertRaisesRegex(ValueError,'outside relationship'):refs.decode(raw,text)
    def test_original_whitespace_and_nonfigure_occurrence_are_retained(self):
        text='North. I selected warehouse  North.'
        raw=response(text,selections=[{'quote':reference(text,'warehouse  North'),'column':reference(text,'warehouse'),'value':reference(text,'North',2),'role':'PRIMARY'}])
        spans=extraction.spans(refs.decode(raw,text),text)
        self.assertEqual(spans['selections'][0]['quote']['quote'],'warehouse  North')
        self.assertEqual(spans['selections'][0]['value']['start'],text.rindex('North'))
    def test_tampered_canonical_text_refuses(self):
        text='The card shows 950.';decoded=refs.decode(response(text),text);decoded['primary']='The card shows 900.'
        with self.assertRaisesRegex(ValueError,'differs'):extraction.spans(decoded,text)
    def test_archived_quote_protocol_remains_selected_for_old_tape(self):
        class Tape:
            replaying=True;bootstrap={'state':{}}
        from investigator.process_tape import ACTIVE
        token=ACTIVE.set(Tape())
        try:
            _,payload=fixture('In Report, Quantity differs.')
            data,instructions,schema=extraction.producer_contract(payload)
            self.assertNotIn('ticket_tokens',data);self.assertEqual(schema,extraction.SCHEMA)
        finally:ACTIVE.reset(token)
    def test_same_role_rival_figures_still_refuse(self):
        text='In Report, Global card Quantity shows 16 or 17.'
        raw=response(text,reports=[{'quote':reference(text,'Report'),'role':'PRIMARY'}],measures=[{'quote':reference(text,'Quantity'),'role':'PRIMARY'}],visuals=[{'quote':reference(text,'Global card'),'role':'PRIMARY','form':'TITLE'}],figures=[{'quote':reference(text,x),'role':'PRIMARY','state':'NUMBER','precision_quote':None} for x in ('16','17')])
        _,payload=fixture(text)
        with self.assertRaises(ValueError):extraction.resolve(refs.decode(raw,text),payload)

    def test_form_document_relocation_requires_exact_unchanged_description(self):
        text='The card shows 950.';raw=response(text,figures=[{'quote':reference(text,'950'),'role':'PRIMARY','state':'NUMBER','precision_quote':None}])
        decoded=refs.decode(raw,text);prefix='Description supplied by user:\n'
        rebased=refs.relocate(decoded,text,prefix+text,len(prefix))
        self.assertEqual(extraction.spans(rebased,prefix+text)['figures'][0]['quote']['start'],len(prefix)+text.index('950'))
        with self.assertRaisesRegex(ValueError,'not byte-identical'):refs.relocate(decoded,text,prefix+'The card shows 900.',len(prefix))
