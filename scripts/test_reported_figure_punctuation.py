import unittest

from investigator import reported_figure
from investigator import intake_extraction
from test_intake_extraction import fixture


class ReportedFigurePunctuationTests(unittest.TestCase):
    def test_sentence_punctuation_preserves_exact_number_and_source(self):
        text = 'In Report, Global card Quantity shows 950.'
        quote = 'Quantity shows 950.'
        raw, payload = fixture(text,
            visuals=[{'quote': 'Global card', 'role': 'PRIMARY', 'form': 'TITLE'}],
            figures=[{'quote': quote, 'role': 'PRIMARY', 'state': 'NUMBER',
                      'precision_quote': '950'}])
        value = intake_extraction.resolve(raw, payload)['reported_figure']
        self.assertEqual(value['value'], '950')
        self.assertEqual(value['precision'], {'state': 'EXACT'})
        self.assertEqual(value['source']['quote'], quote)
        self.assertEqual(reported_figure.label(value, '950'), 'REPRODUCED')
        self.assertEqual(reported_figure.label(value, '950.1'), 'NOT_REPRODUCED')

    def test_decimal_and_suffix_precision_survive_sentence_punctuation(self):
        for quote, number, place in [('The card shows about 950.00.', '950.00', -2),
                                     ('The card shows about 3.4M.', '3400000.0', 5)]:
            with self.subTest(quote=quote):
                self.assertEqual(reported_figure.stated(quote),
                                 (number, {'state': 'STATED_PLACE', 'place': place}))

    def test_punctuation_does_not_admit_partial_or_competing_numerals(self):
        for quote in ['950.1.2', 'schema.950', '950.foo', '950 and 700.', 'about 950.']:
            with self.subTest(quote=quote):
                with self.assertRaises(reported_figure.UnavailablePrecision):
                    reported_figure.stated(quote)


if __name__ == '__main__':
    unittest.main()
