# local/sandbox-contrast-check-against-the-verse-not-the-prechorus — lessons

Project: local/sandbox-contrast-check-against-the-verse-not-the-prechorus. Newest first.

---

## E1 — contrast check against the verse not the prechorus
- Date: 2026-09-30
- Project: local/sandbox-contrast-check-against-the-verse-not-the-prechorus
- Tags: [songwriting][structure][testing]
- What: The verse-chorus contrast check must compare the chorus with the most recent verse by role, not with the section just before it: with a pre-chorus in between, the previous-section check was right on 3 of 6 outlines, failing in both directions, while the verse-by-role check was right on 6 of 6.
- Why built: Compose the verse-and-chorus-differ kernel, whose checker compares a chorus with the section before it, with the pop-structure kernel (verse, pre-chorus, chorus) and the judge-sections-by-role lesson.
- Design: Six outlines with hand-set mean syllables per line, lines per section and rhyme scheme, hand-labelled as proper contrast or verse 1b; three include a pre-chorus. A chorus contrasts when two or more axes differ (mean syllables by 2 or more).
- Got right: Comparing with the most recent verse by role judged all 6 outlines as labelled, and both methods caught the plain verse-1b song with no pre-chorus.
- Where/why it failed: The previous-section check gave false warnings on both songs whose pre-chorus already ramps down to short lines, and I missed the third failure in my prediction: it passed a verse-1b chorus because the short pre-chorus before it differed from the chorus on two axes.
- Fix: Compare the chorus with the most recent section whose role is verse; treat the pre-chorus as a ramp that is allowed to resemble either side.
- Why this fix: A pre-chorus exists to move from verse to chorus, so it resembles the chorus when it ramps and differs when it is short, which corrupts a previous-section comparison both ways; the verse is the section the chorus has to stand out from.
- Rule of thumb: Check verse-chorus contrast against the last verse by role, not the section before the chorus: a pre-chorus made the previous-section check wrong on 3 of 6 outlines, in both directions.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; counts are copied from its output. The outlines are synthetic, with the same syllable count on every line of a section.
- Composed: ideas:SONGWRITING/section-contrast/verse-and-chorus-differ-in-line-length-rhythm-and-rhyme, ideas:SONGWRITING/structure/standard-pop-structure-and-the-bridges-real-job, sandbox-structure-check-by-section-role-not-tag-name/E1
- Polarity: compatible
- Sandbox: sandboxes/2026-09-30__contrast-check-against-the-verse-not-the-prechorus.py
- Prediction: previous-section check right on 4/6 (2 false warnings from ramping pre-choruses); verse-by-role right on 6/6; the verse-1b song caught by both.
- Observed: RESULT: FAIL chorus-vs-previous-section right on 3/6, chorus-vs-verse-by-role right on 6/6
- Scenarios: 1) verse then chorus with strong contrast; 2) verse 1b with no pre-chorus; 3) two ramping pre-choruses built to break the previous-section check; 4) a long chorus; 5) a verse 1b hidden behind a short pre-chorus.
- Link: https://claude.ai/code/session_01FPKwCG4xnKWiiLWPC1nvdo
- Cited-by: 2026-09-30 · projects/local__suno.md#E18 · incompatible · sandboxes/2026-09-30__chorus-contrast-is-repetition-not-line-length.py · observed RESULT: FAIL 1/4; >=2 axes 50% (n 44); paired chorus 49% vs control 49% (n 39); axes length 66% end-repeat 43% token-repeat 52%; deduped 56% · session 2026-09-30 brain train loop 9 (settles the verse/chorus contrast tension)
- Audited: 2026-10-09 · modeled · Read the entry and its stored sandbox, then ran it unchanged in a scratch copy (reproduces RESULT: FAIL previous-section 3/6, verse-by-role 6/6; the FAIL line is the prediction of 4/6 missing, not a refuted claim, and the entry's compatible polarity is fair). The model does compute both comparators from section features, so the answer is not hard-coded. But the want-labels are hand-set to mean "contrasts with the verse", so the 6/6 for verse-by-role is largely built in. Mutation tests in scratch copies: (1) lowering the axis threshold from 2 to 1 drops verse-by-role to 5/6 (the scheme-only song flips), so the 6/6 depends on one hand-picked threshold; (2) flipping the verse-1b label drops previous-section to 2/6 and verse-by-role to 5/6, so scores follow the labels; (3) adding a song whose second verse drifts toward the chorus makes verse-by-role 6/7, because the last verse by role is also fooled; (4) a chorus with no earlier verse crashes with IndexError, an unhandled case the rule never states; (5) comparing against the first section instead of the last verse still scores 6/6, so the fixture does not tell "last verse" from "any verse". The rule of thumb is about real songs, yet every outline is synthetic with identical syllable counts per line, and a later real-lyrics test (suno#E18) found the two-axes contrast premise itself holds only about 50% (n 44). So the narrow comparator ordering is shown only on a hand-written model, not on real songs. Verdict modeled, not pass. · session_01YFLLRpDsfZpRstb2KT2MQy
