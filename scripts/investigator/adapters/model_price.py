"""Public GPT-5.4 Global Standard rate card used by the bounded live round.

This is a conservative price estimate, not Azure invoice attestation. Cached
input is charged at the ordinary rate. Source and deployment are pinned in the
round ledger; another deployment requires its own documented price policy.
"""
def price(input_tokens, output_tokens):
    from decimal import Decimal, ROUND_CEILING
    i, o = ('5', '22.5') if input_tokens > 272000 else ('2.5', '15')
    return int((Decimal(i)*input_tokens + Decimal(o)*output_tokens).to_integral_value(rounding=ROUND_CEILING))
