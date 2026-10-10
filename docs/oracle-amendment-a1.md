# Oracle amendment A1 ? 2026-10-10

Owner: Chiranjeevi Bhogireddy. Reviewer: Claude. Explicit decision supplied in round-twelve-d-amend-fix-go-live.md. Only true_reported_figure changes; no other record field, golden, split or expectation changes.

## original:family-E-mention

Verbatim statement: The global Handled Quantity currently shows 8765.

Numeric span 169:173: `8765`.

Old: `{"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}`

New: `{"state": "DETERMINED", "value": {"state": "NUMBER", "value": "8765", "precision": {"state": "EXACT"}, "source": {"start": 169, "end": 173, "quote": "8765"}}, "reason": "Owner/reviewer amendment A1, 2026-10-10: a figure explicitly stated as displayed is a stated figure."}`

## original:family-A-mention

Verbatim statement: The global Handled Quantity currently shows 8765.

Numeric span 148:152: `8765`.

Old: `{"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}`

New: `{"state": "DETERMINED", "value": {"state": "NUMBER", "value": "8765", "precision": {"state": "EXACT"}, "source": {"start": 148, "end": 152, "quote": "8765"}}, "reason": "Owner/reviewer amendment A1, 2026-10-10: a figure explicitly stated as displayed is a stated figure."}`

## original:family-G-mention

Verbatim statement: The global Handled Quantity currently shows 8765.

Numeric span 218:222: `8765`.

Old: `{"state": "NOT_STATED", "reason": "The admitted sealed record explicitly records no reported figure."}`

New: `{"state": "DETERMINED", "value": {"state": "NUMBER", "value": "8765", "precision": {"state": "EXACT"}, "source": {"start": 218, "end": 222, "quote": "8765"}}, "reason": "Owner/reviewer amendment A1, 2026-10-10: a figure explicitly stated as displayed is a stated figure."}`

## Exclusions

No other NOT_STATED record explicitly states a displayed numeric figure. No ambiguous displayed figure was amended. Non-figure numeral-bearing records remain unchanged:

- original:family-B-noisy: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-B-terse: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-B-typo: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-D-noisy: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-D-terse: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-D-typo: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-H-noisy: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-H-terse: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-H-typo: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-I-noisy: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-I-terse: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-I-typo: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-B: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-D: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-E: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-H: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-I: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- rebuilt:family-B: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- rebuilt:family-D: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- rebuilt:family-E: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- rebuilt:family-H: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- rebuilt:family-I: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-A-noisy: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-A-terse: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-A-typo: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-C-noisy: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-C-terse: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-C-typo: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-F-noisy: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-F-terse: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-F-typo: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-A: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-C: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-F: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- original:family-G: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- rebuilt:family-A: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- rebuilt:family-C: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- rebuilt:family-F: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.
- rebuilt:family-G: No explicit displayed numeric figure; names, references and identifier numerals are not metric values.

New seal: `bc2819f1ab12ae93d2203a519a6318a6f9ecbc1a3220a466e664a00c495a9a6b`. Old seal `be029b56a6de27195dac507bfb5010f0ce7abc2732702d9a230e5f4a8d38406c` retained as superseded, never removed. Saved responses, result files and tapes unchanged; zero new model calls, zero estate reads.

| Partition/group | Old settled | Amended settled | Old harmful | Amended harmful | Questions (unchanged) | Illegitimate (unchanged) |
|---|---:|---:|---:|---:|---:|---:|
| dev/complete | 27/28 | 28/28 | 1 | 0 | 0 | 0 |
| dev/visual-skipped | 4/5 | 4/5 | 0 | 0 | 0 | 0 |
| dev/incomplete-controls | 4/12 | 4/12 | 0 | 0 | 3 | 3 |
| held_out/complete | 18/21 | 20/21 | 2 | 0 | 0 | 0 |
| held_out/visual-skipped | 2/2 | 2/2 | 0 | 0 | 0 | 0 |
| held_out/incomplete-controls | 1/7 | 1/7 | 0 | 0 | 1 | 1 |
