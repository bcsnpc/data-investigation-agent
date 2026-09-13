"""Compare a downloaded READY Gold report with independent Azure SQL totals."""
import json
from decimal import Decimal
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'infra/fabric'))
from gold_models import ADDITIVE


def compare(source, report):
    assert report['status'] == 'READY', 'Gold is not READY'
    assert report['checks'] and all(report['checks'].values()), 'Gold checks failed'
    expected = {row['currency']: row for row in source}
    actual = report['totals_by_currency']
    assert expected.keys() == actual.keys(), 'Currency sets differ'
    for currency, values in expected.items():
        for metric in ADDITIVE:
            assert Decimal(str(values[metric])) == Decimal(str(actual[currency][metric])), f'{currency}: {metric}'
    return len(expected) * len(ADDITIVE)


if __name__ == '__main__':
    source = json.loads((ROOT / '.local/gold-source-totals.json').read_text(encoding='utf-8-sig'))
    report = json.loads((ROOT / '.local/fabric-gold-report.json').read_text(encoding='utf-8'))
    print(f'{compare(source, report)} independent Azure SQL/Gold totals match exactly.')
