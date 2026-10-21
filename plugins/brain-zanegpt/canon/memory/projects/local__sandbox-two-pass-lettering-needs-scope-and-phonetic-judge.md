# local/sandbox-two-pass-lettering-needs-scope-and-phonetic-judge — lessons

Project: local/sandbox-two-pass-lettering-needs-scope-and-phonetic-judge. Newest first.

---

## E1 — two pass lettering needs scope and phonetic judge
- Date: 2026-10-08
- Project: local/sandbox-two-pass-lettering-needs-scope-and-phonetic-judge
- Tags: [songwriting][rhyme][testing]
- What: Deterministic sandbox re-verifying the two-pass letter-assignment kernel against single-pass lettering on four stanzas, then building two cases to break it: a section-blind candidate search and a spelling-based rhyme judge.
- Why built: The kernel was only quoted in prose by several memory entries, never declared as applied; I wanted a fresh run that shows where two-pass helps and where it stops mattering.
- Design: Hand-written (vowel, coda) pronunciations for 17 words, no RNG. Single-pass joins a line to the first earlier line that matches at any rhyme level. Two-pass letters perfect pairs first, then assonance among still-unlettered lines. Stanzas: day/gaze/way/haze, gaze/day/haze/way, cat/hat/dog/log, day/gaze/shade/pain; then an 8-line verse plus chorus; then truck/mud/blood/flood under a last-two-letters judge.
- Got right: Single-pass collapses both ABAB stanzas to AAAA because gaze steals day's letter by assonance, while two-pass returns ABAB; the clean AABB stanza is identical under both, so the benefit is conditional on assonance competing with perfect rhyme.
- Where/why it failed: Two-pass alone does not fix scope: with a section-blind search the chorus coincidentally reuses verse letters (ABABACAC) and only a section-aware search gives ABABCDCD. It also does not fix the judge: a spelling judge gives ABCC on truck/mud/blood/flood where the phonetic judge gives ABBB.
- Fix: Treat lettering as three independent stages, judge then scope then pass order, and test each with a fixture built so that stage alone changes the output.
- Why this fix: Each stage decides a different thing (what counts as a rhyme, which lines may be candidates, which kind claims a letter first), so repairing one cannot show up in a fixture that only exercises another.
- Rule of thumb: Two-pass lettering only helps when assonance and perfect rhyme compete for the same line; on clean stanzas it ties, and it never repairs a wrong rhyme judge or an unscoped candidate search, so test those stages separately.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the phoneme fixture is hand-made, not CMUdict, so the direction of each result is confirmed but not real-word coverage.
- Composed: ideas:SONGWRITING/rhyme-tooling/two-pass-letter-assignment-keeps-schemes-legible, sandbox-lyrical-composition/E7, suno-builder/E3, suno-builder/E1
- Sandbox: sandboxes/2026-10-08__two-pass-lettering-needs-scope-and-phonetic-judge.py
- Prediction: Single-pass gives AAAA on both ABAB stanzas and two-pass gives ABAB; both tie on AABB; section-blind gives ABABACAC; spelling judge differs from phonetic.
- Observed: RESULT: PASS two-pass fixes steal on 2 stanzas, ties on clean stanza; scope and spelling judge remain separate failure axes (single AAAA vs two ABAB; scope ABABACAC vs ABABCDCD; judge ABCC vs ABBB)
- Scenarios: 1) day/gaze/way/haze steal; 2) gaze/day/haze/way assonance leads; 3) clean AABB control built to BREAK the claim (ties); 4) assonance-only stanza; 5) verse+chorus scope; 6) spelling judge on truck/mud/blood/flood
- Link: scheduled training session, kernel pass 1
- Cited-by: 2026-10-15 · projects/pappydapimp69__zanegpt.md#E22 · compatible · sandboxes/2026-10-15__hyphenated-rhyme-words-need-the-joined-word.py · observed RESULT: PASS 13 rhyme words hyphenated; rejoined 4/4, raw token 0/4, first fragment 0/4. · brain train (creative arts, loop 2, new half), session 2026-10-15; session_011p52L2CkFXcsYRwjDu6tG9
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-creative-training.md#E18 · compatible · sandboxes/2026-10-15__split-rushed-line-exposes-midline-word-to-two-pass-lettering.py · observed RESULT: FAIL split at midpoint: words/line 11.2->5.6; two-pass kept end pattern 5/6, single-pass kept 5/6; exposed mid-line words lettered in 3/6 natural stanzas (0 uppercase); internal-rhyme break stanza: 1 exposed word(s) promoted to UPP… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 1 pass 1
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-creative-training.md#E21 · compatible · sandboxes/2026-10-15__cluster-coda-fork-flips-the-shape-verdict-by-position.py · observed RESULT: FAIL cluster-coda policy flips the shape verdict in 16/26 typed configurations (1 toward open when cluster counts as resolved, 15 the other way); named shapes with one cluster pair flip 3/7; real-word stanzas flip 3/7. Both criteri… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 2 pass 5
- Cited-by: 2026-10-19 · projects/local__hyphenating-end-words-breaks-two-pass-letters-only-under-a-last-segment-judge.md#E1 · compatible · sandboxes/2026-10-19__hyphenating-end-words-breaks-two-pass-letters-only-under-a-last-segment-judge.py · observed RESULT: PASS last-segment judge broke the perfect-rhyme partition in 1794/6561 stanzas (27.3%), whole-word judge in 0; 3 falsely merged word pairs · scheduled brain train auto, loop 1 pass 2; session_01Q5Z2SdcUKr5yLCVU7Ma7tK
