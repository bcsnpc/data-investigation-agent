"""Shared primary-role admission against immutable billing wording, not expectations."""
import copy,re,json,unittest
from pathlib import Path
from investigator import intake_extraction as extract,reported_figure,ticket_question_gate as gate,ticket_protocol as protocol,ticket_clarification as planner
from test_intake_extraction import fixture

class BillingSharedIntake(unittest.TestCase):
    def test_all_18_inputs_conserve_context_amounts_without_competing_for_primary_role(self):
        directory=Path(__file__).resolve().parents[1]/'acceptance/tickets/billing/tester'
        cases={'01':('950','The card shows 950.'),'02':('550','collections looks low - 550'),
               '03':('600','It says 600.'),'04':('1','Churned Accounts = 1.'),
               '05':('600','The Usage Overage card says 600'),
               '06':('600','MRR All Plans 600'),'13':('950','The first page has 950 invoiced'),
               '14':('950','950 Invoiced Amount card'),'15':('600','MRR All Plans 600')}
        for number,(token,quote) in cases.items():
            text=(directory/('ticket-'+number+'.txt')).read_text()
            # Forms and free-text twins share this immutable description; picked
            # container authority is covered independently below.
            form={'description':text}
            for mode in ('FORM','CHAT'):
                with self.subTest(ticket=number,mode=mode):
                    if mode=='FORM':self.assertTrue(form)
                    other=next((m.group() for m in re.finditer(r'(?<![\w.])\d+(?![\w.])',text) if m.group()!=token),None)
                    figures=[{'quote':quote,'role':'PRIMARY','state':'NUMBER','precision_quote':None}]
                    if other:figures.append({'quote':other,'occurrence':1,'role':'CONTEXT','state':'NUMBER','precision_quote':None})
                    raw,payload=fixture(text,primary=quote,reports=[],measures=[],figures=figures)
                    if mode=='FORM':payload['_ticket_reference']={'model_id':'model','report_id':'report','page_id':None}
                    extraction=extract.spans(raw,text,figure_occurrences=True)
                    primary=[i['quote'] for i in extract.primary_figures(extraction,text)]
                    result=reported_figure.from_candidates(primary,text)
                    self.assertEqual(result['value'],token);self.assertEqual(result['precision'],{'state':'EXACT'})
                    offered=gate.offer(protocol.new('t'),{'retained_extraction':raw},payload,planner.settings(),{'questions':[],'values':{},'blocked':None})
                    self.assertNotIn('FIGURE',[q['field'] for q in offered['questions']])

    def test_full_resolver_does_not_compare_other_role_values(self):
        text='In Report, Global card Quantity shows 950. Its components sum to 700, or 600 without one component.'
        raw,payload=fixture(text,visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}],
            figures=[{'quote':n,'role':r,'state':'NUMBER','precision_quote':None} for n,r in [('950','PRIMARY'),('700','COMPARISON'),('600','CONTEXT')]])
        result=extract.resolve(raw,payload)
        self.assertEqual(result['reported_figure']['value'],'950')
        self.assertEqual(len(result['extracted_ticket']['response']['figures']),3)
        raw['figures'][1]['role']='PRIMARY'
        with self.assertRaises(reported_figure.AmbiguousFigure):extract.resolve(raw,payload)

    def test_question_builder_returns_refusal_for_exact_billing_crash_wording(self):
        directory=Path(__file__).resolve().parents[1]/'acceptance/tickets/billing/tester'
        text=(directory/'ticket-05.txt').read_text()
        raw,payload=fixture(text,primary='An invented question not present in the ticket',reports=[],measures=[])
        result=gate.offer(protocol.new('t'),{'retained_extraction':raw},payload,planner.settings(),{})
        self.assertEqual(result['questions'],[]);self.assertIn('RETAINED_EXTRACTION_INVALID',result['blocked'])

    def test_explicit_report_header_survives_narrow_primary_quote(self):
        text='Report: Report\nPage: Overview\nGlobal card Quantity shows 950. Why is it wrong?'
        raw,payload=fixture(text,primary='Why is it wrong?',reports=[],
            visuals=[{'quote':'Global card','role':'PRIMARY','form':'TITLE'}],
            figures=[{'quote':'950','role':'PRIMARY','state':'NUMBER','precision_quote':None}])
        for v in payload['models'][0]['visuals']:v.update(page_id='overview',page_names=['Overview'])
        extraction=extract.spans(raw,text)
        self.assertEqual(extract.declared_pages(extraction,text,payload['models'][0])[0]['quote']['quote'],'Overview')
        self.assertEqual(extract.literal_reports(extraction,text,payload['models'])[0]['quote']['quote'],'Report')
        self.assertEqual(extract.resolve(raw,payload)['reported_figure']['value'],'950')
        offered=gate.offer(protocol.new('t'),{'retained_extraction':raw},payload,planner.settings(),{'questions':[],'values':{},'blocked':None})
        self.assertEqual(offered['questions'],[])

    def test_written_digits_are_exact_without_rounding_signal(self):
        for quote in ('950','950.00','The card shows 950.'):
            self.assertEqual(reported_figure.stated(quote)[1],{'state':'EXACT'})
        self.assertEqual(reported_figure.stated('about 950.00')[1],{'state':'STATED_PLACE','place':-2})
        with self.assertRaises(reported_figure.UnavailablePrecision):reported_figure.stated('about 950')

if __name__=='__main__':unittest.main()
