# local/sandbox-kernel-text-unicode — lessons

Project: local/sandbox-kernel-text-unicode. Newest first.

---

## E1 — slicing by code units cuts most non ascii graphemes
- Date: 2026-09-28
- Project: local/sandbox-kernel-text-unicode
- Tags: [text][unicode][javascript][correctness]
- What: Applied the ideas kernel that one visible character can have three lengths in JavaScript (the ZWJ family emoji is .length 11, 7 code points, 1 grapheme) and that anything a human counts must use grapheme clusters. It reproduced in real Node, and the sandbox measured how often the everyday operations built on code units break text.
- Why built: brain train gap listed the kernel as unapplied, and memory had no Unicode handling entry.
- Design: Real Node v22 with ICU 78.2 (Unicode 17.0). Ten strings: ASCII, composed and decomposed e-acute, a flag, a skin-tone emoji, the ZWJ family, a Devanagari conjunct with vowel sign, decomposed Hangul jamo, Thai, and a mix. For each: .length, code points, Intl.Segmenter graphemes, UTF-8 bytes, and .length after NFC. Then .slice(0, n) at every interior n, and reversal by spread versus by graphemes.
- Got right: Including scripts beyond emoji. The Devanagari conjunct and Hangul jamo show the gap is not an emoji quirk.
- Where/why it failed: The family emoji measured 11 code units, 7 code points, 1 grapheme and 25 UTF-8 bytes, as the kernel says. The Devanagari conjunct was 4 units and 1 grapheme under Unicode 17, and decomposed Hangul jamo 3 units, 1 grapheme, and 1 unit after NFC. Across the 48 interior slice points, 34 cut a grapheme and 13 left a lone high surrogate. Reversing with [...s] changed the grapheme count of 5 of 10 strings; reversing by graphemes changed none.
- Fix: Truncate, count, step a cursor and reverse over Intl.Segmenter graphemes; budget storage in UTF-8 bytes; normalise to NFC before comparing lengths or strings.
- Why this fix: Code units are an encoding detail, code points still split combining marks and ZWJ sequences, and only grapheme clusters match what a person sees; bytes are what storage limits count.
- Rule of thumb: Code-unit string operations break most non-ASCII text: slicing at every interior point of 10 mixed strings cut a grapheme 34 of 48 times and left a lone surrogate 13 times, and [...s].reverse() broke 5 of 10; use Intl.Segmenter graphemes for anything a person counts (the family emoji is 11 units, 7 code points, 1 grapheme, 25 UTF-8 bytes).
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b08.py loop 36 in Pappydapimp69/Brain, running real Node v22.22.2 with ICU 78.2 and Unicode 17.0, deterministic. Observed: the length table for all 10 strings, 34/48 slices cutting a grapheme, 13 lone surrogates, 5/10 spread reversals broken and 0/10 grapheme reversals. Older ICU versions segment the Devanagari conjunct differently.
- Composed: ideas:TEXT/unicode/grapheme-not-code-unit-is-a-user-character/three-different-lengths-for-one-visible-character
- Link: session 2026-09-28, brain train gap batch 8 loop 36
- Sandbox: sandboxes/2026-09-28__train-gap-b08.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)
- Cited-by: 2026-10-10 · projects/pappydapimp69__brainwork.md#E58 · compatible · sandboxes/2026-10-10__normalize-forms-not-sufficient.py · observed RESULT: PASS NFC fixes combining-vs-precomposed (1 case), NFKC needed for ligature, neither fixes Cyrillic lookalike, NFC still truncates 2-mark grapheme · brain train auto session_01XCLxkNXY7PFU6NguwSNufH
- Cited-by: 2026-10-10 · projects/pappydapimp69__brainwork.md#E84 · compatible · sandboxes/2026-10-10__grapheme-cap-order-and-byte-budget.py · observed RESULT: PASS flags: code-unit cut well-formed=False, grapheme cut=3 flags; cap-before-upper 7 graphemes vs cap-after 6; cap10 family=250 bytes, byte-bounded=100 bytes/4 graphemes · brain train auto loop 1 pass 5; session_01AA8Uvte5UTxtoXrEfFp3KE
