# local/sandbox-stress-checker-needs-flexible-monosyllables — lessons

Project: local/sandbox-stress-checker-needs-flexible-monosyllables. Newest first.

---

## E1 — stress checker needs flexible monosyllables
- Date: 2026-09-30
- Project: local/sandbox-stress-checker-needs-flexible-monosyllables
- Tags: [songwriting][lyrics][testing]
- What: A lyric stress checker built from the natural-word-stress kernel catches mis-set words that a syllable-count check cannot see, but only if one-syllable function words are allowed on either beat; with dictionary-style stress on every syllable it falsely flags 4 of 7 well-set lines.
- Why built: Compose the stress-on-strong-beats kernel with the lesson that syllable count is a coarse proxy for stress pattern, and find where a checker built from the kernel stops holding.
- Design: Twelve 8-syllable lines on a strong-weak grid, 7 hand-labelled well set and 5 mis-set (be-CAUSE, a-GAIN starting on a strong beat). Stress per syllable hand-entered in CMUdict's style, where I, to, my, you and and carry primary stress. Three checks: syllable count, strict dictionary stress, and strict stress with one-syllable function words treated as flexible.
- Got right: Syllable count passed all 12 lines including all 5 mis-set ones, so it is blind to stress as predicted; the flexible-monosyllable checker flagged 5 of 5 mis-set lines and 0 of 7 well-set lines.
- Where/why it failed: Strict dictionary stress flagged 4 of 7 well-set lines (hold me down and keep me waiting got 3 flags) because dictionary entries give many one-syllable function words primary stress, and in sung English those words take whichever beat the line gives them.
- Fix: Treat one-syllable function words (pronouns, articles, short prepositions and conjunctions) as fitting either beat, and check stress only on content words and on every syllable of multi-syllable words.
- Why this fix: The false flags all came from one-syllable function words, and multi-syllable words carry the fixed stress a listener actually hears mis-set, so relaxing only the monosyllables removed every false flag without losing a hit.
- Rule of thumb: Check lyric stress on content words and multi-syllable words only; strict dictionary stress on I, to, my, you and and falsely flagged 4 of 7 well-set lines while syllable count missed all 5 mis-set ones.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; counts are copied from its output. Stress values are hand-entered in CMUdict's style for 50 words; the mis-set fixture is built from iambic words only, and a line made entirely of function words would pass the flexible checker unchecked.
- Composed: sandbox-lyrical-composition/E5, ideas:SONGWRITING/prosody/natural-word-stress-lands-on-strong-beats
- Polarity: compatible
- Sandbox: sandboxes/2026-09-30__stress-checker-needs-flexible-monosyllables.py
- Prediction: proxy passes 12/12; strict stress flags 5/5 mis-set and at least 2/7 well-set; flexible monosyllables flags 5/5 and 0/7.
- Observed: RESULT: PASS proxy 12/12 blind to stress; strict stress hits 5/5 with 4/7 false flags; flexible monosyllables hits 5/5 with 0/7
- Scenarios: 1) well-set lines of content words only; 2) well-set lines heavy with one-syllable function words, built to break the strict checker; 3) mis-set lines of iambic words on a trochaic grid.
- Link: https://claude.ai/code/session_01FPKwCG4xnKWiiLWPC1nvdo
- Audited: 2026-10-12 · modeled · Read the entry and its stored sandbox and reran it (RESULT: PASS, proxy 12/12, strict 5/5 hits with 4/7 false flags, flexible 5/5 with 0/7). Q1: the flags are computed per syllable against the grid, not printed constants, so the checker computes. But the premise that drives the headline number is typed in by hand: the lexicon marks I, to, my, you and and as primary stress "in CMUdict's style", and the 12 lines were labelled well-set or mis-set by the author, so the 4/7 false-flag figure follows from those two choices. Q2: the rule says to check content and multi-syllable words only; the sandbox tests that against 12 lines and 50 words, and the entry itself says the mis-set fixture uses iambic words only and an all-function-word line would pass unchecked. Q3: the claim is about what a dictionary-stress checker does with real CMUdict stress and sung lyrics, but CMUdict was not loaded and no sung or real lyric lines were used, only a hand-written model of it, so the verdict is modeled rather than pass. · session_01XCe61chZn6agE2zVwbgxdQ
