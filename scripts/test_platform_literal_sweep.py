"""CI ratchet for pre-existing platform/fixture literals above adapters.

The historical ceiling is sealed, not an updateable snapshot. Delete/lower debt
entries when fixing them; a new file or more matches cannot join the allowance.
"""
import hashlib,json,re,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PATTERNS={
    'account':r'\b[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b|\b(?:skynwhy\.com|investigator-reader|orderops_investigator)\b',
    'guid':r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b',
    'fixture_column':r'\b(?:movement_type|warehouse_name|product_name|event_day|product_id|warehouse_id|movement_id|rate_version|unit_rate|unit_cost|ordered_units|reason_code|adjustment_id|purchase_order_id)\b',
    'fixture_value':r'\b(?:North|Central|Coastal|RECEIPT|ISSUE|DAMAGE|Q49|Component [0-9]+)\b',
    'product':r'(?i)\b(?:fabric|azure|power\s*bi|microsoft|onelake|xmla|adomd|msal|analysis services)\b',
}

def scan(root):
    result={}
    for path in sorted(root.rglob('*')):
        if not path.is_file() or {'adapters','__pycache__'}&set(path.relative_to(root).parts):continue
        if path.suffix in {'.pyc','.pyo'}:continue
        text=path.read_text(encoding='utf8')
        counts={key:len(re.findall(pattern,text)) for key,pattern in PATTERNS.items()}
        counts={key:n for key,n in counts.items() if n}
        if counts:result[path.relative_to(root).as_posix()]=counts
    return result

def ratchet(actual,allowed,ceiling):
    for name,counts in allowed.items():
        if name not in ceiling:raise AssertionError('New debt file: '+name)
        for key,n in counts.items():
            if n>ceiling[name].get(key,0):raise AssertionError('Debt allowance grew: '+name+' '+key)
    for name,counts in actual.items():
        for key,n in counts.items():
            if n>allowed.get(name,{}).get(key,0):raise AssertionError('New platform/fixture literal: '+name+' '+key)


class PlatformLiteralSweepTests(unittest.TestCase):
    def test_production_above_adapter_debt_can_only_shrink(self):
        frozen=(ROOT/'platform-literal-debt-ceiling.json').read_bytes()
        self.assertEqual(hashlib.sha256(frozen).hexdigest(),CEILING_SHA256)
        allowed=json.loads((ROOT/'platform-literal-debt.json').read_text())
        ratchet(scan(ROOT/'investigator'),allowed,json.loads(frozen))
    def test_new_file_new_category_or_increased_count_is_refused(self):
        baseline={'old.py':{'product':2}}
        for actual in ({'new.py':{'product':1}},{'old.py':{'guid':1}},{'old.py':{'product':3}}):
            with self.assertRaises(AssertionError):ratchet(actual,baseline,baseline)
        with self.assertRaises(AssertionError):ratchet({},dict(baseline,new={}),baseline)
        ratchet({}, {},baseline)
        ratchet({'old.py':{'product':1}},{'old.py':{'product':1}},baseline)
    def test_known_literal_forms_are_detected_without_receipt_tag_false_positive(self):
        for key,text in [('account','reader@skynwhy.com'),('guid','12345678-1234-1234-1234-123456789012'),
                         ('fixture_column','event_day'),('fixture_value','North RECEIPT'),('product','Fabric Azure Power BI')]:
            self.assertTrue(re.findall(PATTERNS[key],text))
        self.assertFalse(re.findall(PATTERNS['fixture_value'],'CANCELLED_RECEIPT'))

# Hash of the initial 2026-10-03 debt ceiling; never regenerate for new debt.
CEILING_SHA256='b048c50ac2fd4b7ff4dbaa732ef758d1ba04cbf5a222d1da592a4274fe761382'

if __name__=='__main__':unittest.main()
