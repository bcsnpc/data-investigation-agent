import random,unittest
from investigator.archive_migration import credential_pattern,SECRET_BYTES

class Tests(unittest.TestCase):
    def test_same_regex_semantics_across_nested_token_prefixes(self):
        values=[b'eyJ'*100000,b'eyJ'*100000+b'.too-short.',b'eyJ'+b'x'*20+b'.'+b'y'*20+b'.'+b'z'*20,
                b'eyJinsideeyJ'+b'a'*15+b'.'+b'b'*15+b'.'+b'c'*15,
                b'eyJ'+b'a'*15+b'.short.'+b'eyJ'+b'q'*15+b'.'+b'r'*15+b'.'+b's'*15]
        # Large negative examples are quadratic in the old search; their exact
        # reasons for failure are explicit rather than exercising that slowdown.
        self.assertFalse(credential_pattern(values[0]));self.assertFalse(credential_pattern(values[1]))
        rng=random.Random(234)
        chunks=[b'eyJ',b'eyj',b'.',b'-',b'_',b' ',b'x'*14,b'y'*20,b'password=',b'public',b'Bearer token']
        values.extend(b''.join(rng.choice(chunks) for _ in range(12)) for i in range(500))
        for value in values[2:]:
            self.assertEqual(credential_pattern(value),bool(SECRET_BYTES.search(value)),repr(value))

if __name__=='__main__':unittest.main()
