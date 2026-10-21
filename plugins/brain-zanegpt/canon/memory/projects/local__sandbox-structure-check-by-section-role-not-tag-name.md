# local/sandbox-structure-check-by-section-role-not-tag-name — lessons

Project: local/sandbox-structure-check-by-section-role-not-tag-name. Newest first.

---

## E1 — structure check by section role not tag name
- Date: 2026-09-30
- Project: local/sandbox-structure-check-by-section-role-not-tag-name
- Tags: [songwriting][lyrics][structure][testing]
- What: A bridge-must-lead-back check has to find the returning section by its repeated lyric text; keyed on the literal tag Chorus it was wrong on 4 of 8 forms, and keyed on the most repeated tag it was wrong on 2 and missed the one real defect.
- Why built: Compose the bridge's job (withhold the returning section, then bring it back) with the finding that a bracket-tag parser only knows tag text and that authored variants like a final chorus are not repeat markers.
- Design: Eight forms written as (tag, set of line ids): pop, pop with a Chorus - Final evolved variant sharing 3 of 4 lines, hip-hop Hook, folk Refrain without bridge, AABA, pop without bridge, a defect where the bridge leads to a verse, and a verse-heavy form. Three checks: literal tag name, most repeated normalised tag, and repeated-text role (returning section = the pair of sections with the highest line overlap, at least 50 percent).
- Got right: Literal name was wrong on the final variant, Hook, Refrain and AABA forms (4 of 8); the repeated-text role check was right on all 8 and flagged the bridge-to-verse defect.
- Where/why it failed: My first role check used the most repeated tag and failed 2 of 8. Verses repeat as often as choruses (3 verses against 2 choruses), so it named the verse as the returning section, missed the real defect and raised a false notice on the verse-heavy form.
- Fix: Identify the returning section by repeated lyric content (line overlap of at least half) rather than by tag name or tag count, and treat an evolved final chorus as the same role when most lines are shared.
- Why this fix: Only the text-based role matched all 8 hand-labelled expectations, including renamed sections (Hook, Refrain, A) and the evolved final chorus that literal matching rejects.
- Rule of thumb: Find a song's returning section by its repeated text, not its tag name or tag count; the literal Chorus check failed 4 of 8 forms and the most-repeated-tag check missed the real bridge-to-verse defect because verses repeat too.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; counts are copied from its output. The forms and expected verdicts are my own hand labels and no real songs were parsed.
- Composed: sandbox-bridge-hides-the-final-chorus-post-chorus-re-anchors/E1, sandbox-lyrics-structure/E5, sandbox-lyrics-structure/E1, ideas:SONGWRITING/structure/standard-pop-structure-and-the-bridges-real-job
- Polarity: compatible
- Sandbox: sandboxes/2026-09-30__structure-check-by-section-role-not-tag-name.py
- Prediction: literal tag check wrong on at least 3 of 8, a role check wrong on at most 1, and both catch the bridge-to-verse defect (the first role check, by tag count, came out wrong: 2 of 8 and missed the defect).
- Observed: RESULT: PASS wrong on 8 forms: literal tag name 4, most-repeated-tag role 2 (misses the real defect=True), repeated-text role 0; text role flags the bridge->verse defect
- Scenarios: 1) pop; 2) evolved final chorus; 3) Hook; 4) Refrain without bridge; 5) AABA; 6) pop without bridge; 7) bridge-to-verse defect; 8) verse-heavy form built to break a count-based role check.
- Link: https://claude.ai/code/session_01PXuEX9SfJcr8Mxg6sK6stu
- Cited-by: 2026-09-30 · projects/local__sandbox-contrast-check-against-the-verse-not-the-prechorus.md#E1 · compatible · sandboxes/2026-09-30__contrast-check-against-the-verse-not-the-prechorus.py · observed RESULT: FAIL chorus-vs-previous-section right on 3/6, chorus-vs-verse-by-role right on 6/6 · https://claude.ai/code/session_01FPKwCG4xnKWiiLWPC1nvdo
- Cited-by: 2026-09-30 · projects/local__suno.md#E8 · incompatible · sandboxes/2026-09-30__text-repeat-chorus-detection-misses-half-of-real-lyrics.py · observed RESULT: FAIL 2/4; title first/last 0.89 vs chance 0.78 (n 18; deduped 0.86 vs 0.72, n 14); chorus shorter 0.62 (n 45; deduped 0.59); text-vs-tag agree 0.93 (n 14), text-repeat empty in 14 · session 2026-09-30 brain train, related pass on songwriting kernels
- Audited: 2026-10-08 · modeled · Read the entry and its stored sandbox. The checks do compute their outputs from the forms (literal tag, most-repeated tag and repeated-text overlap are each real functions, and the printed counts 4/2/0 follow from the code), so the answer is not built in. But the forms are eight hand-written section lists whose lyric content is abstract line ids (c1, v1a), so repeated lines are exact set matches by construction, and the expected verdicts are the author's own labels; the text rule (50 percent overlap) was also added in a second iteration after the first rule failed, so 0 of 8 wrong is fitted to this fixture. The Rule of thumb claims text beats tag name for real songs, yet no real lyric was parsed, and the entry's own later incompatible Cited-by (text-repeat empty in 14 real lyrics, 2/4 right) shows exact-repeat text is far weaker on real data than the toy suggests. What is solid: the tag-count check fails on verse-heavy forms, a structural point the model does demonstrate. What is unverified: the text check on real, varied lyrics. Hence modeled, not pass. · scheduled brain train pass 3
