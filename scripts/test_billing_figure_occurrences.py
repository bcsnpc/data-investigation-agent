"""Immutable tester wording; repeat provenance never selects a referent or target."""
import copy,json,re,unittest
from pathlib import Path
from investigator.question_intake import locate,FigureQuoteAmbiguous,QuoteRefused
from investigator import intake_extraction as extract,reported_figure
from test_intake_extraction import fixture

class BillingFigureOccurrences(unittest.TestCase):
    def test_all_nine_exact_tickets_allow_unique_context_and_explicit_occurrence(self):
        directory=Path(__file__).resolve().parents[1]/'acceptance/tickets/billing/tester'
        cases={'01':('950','The card shows 950.'),'02':('550','collections looks low - 550'),
               '03':('600','It says 600.'),'04':('1','Churned Accounts = 1.'),
               '05':('600','The Usage Overage card says 600'),
               '06':('600','MRR All Plans 600'),'13':('950','The first page has 950 invoiced'),
               '14':('950','950 Invoiced Amount card'),'15':('600','MRR All Plans 600')}
        for number,(token,context) in cases.items():
            with self.subTest(ticket=number):
                ticket=(directory/('ticket-'+number+'.txt')).read_text()
                self.assertEqual(ticket.count(context),1)
                exact=locate({'quote':context},ticket,field='reported_figure')
                self.assertEqual(ticket[exact['start']:exact['end']],context)
                positions=[m.start() for m in re.finditer(re.escape(token),ticket)]
                selected=ticket.index(token,ticket.index(context))
                source=locate({'quote':token,'occurrence':positions.index(selected)+1},ticket,field='reported_figure')
                self.assertEqual(source['start'],selected)
                self.assertEqual(reported_figure.from_candidates([source],ticket)['value'],token)
                if len(positions)>1:
                    with self.assertRaises(FigureQuoteAmbiguous):locate({'quote':token},ticket,field='reported_figure')
    def test_explicit_occurrence_reaches_consumer_offsets_without_changing_reported_contract(self):
        ticket='Report Quantity shows 16. The note repeats 16.'
        raw,payload=fixture(ticket,figures=[{'quote':'16','occurrence':2,'role':'PRIMARY','state':'NUMBER','precision_quote':None}])
        spans=extract.spans(raw,ticket)
        self.assertEqual(spans['figures'][0]['quote']['start'],ticket.rindex('16'))
        self.assertEqual(set(spans['figures'][0]['quote']),{'start','end','quote'})
    def test_repair_sends_occurrences_to_model_instead_of_generic_correction_only(self):
        _,payload=fixture('Quantity shows 16; note 16.')
        payload['_figure_quote_repair']={'quote':'16','occurrences':[{'start':15,'end':17,'quote':'16'},{'start':24,'end':26,'quote':'16'}]}
        self.assertEqual(extract.wire(payload)['reported_figure_quote_repair']['occurrences'],payload['_figure_quote_repair']['occurrences'])
    def test_occurrence_cannot_invent_provenance_or_mask_competing_primary_figures(self):
        ticket='First card shows 950; second card shows 600.'
        for occurrence in (0,True,3):
            with self.subTest(occurrence=occurrence),self.assertRaises(QuoteRefused):
                locate({'quote':'950','occurrence':occurrence},ticket,field='reported_figure')
        with self.assertRaisesRegex(QuoteRefused,'verbatim'):
            locate({'quote':'960','occurrence':1},ticket,field='reported_figure')
        sources=[locate({'quote':v,'occurrence':1},ticket,field='reported_figure') for v in ('950','600')]
        with self.assertRaises(reported_figure.AmbiguousFigure):reported_figure.from_candidates(sources,ticket)

if __name__=='__main__':unittest.main()
