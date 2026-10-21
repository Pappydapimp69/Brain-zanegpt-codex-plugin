# local/engine-vocabulary-name-overlap — lessons

Project: local/engine-vocabulary-name-overlap. Newest first.

---

## E1 — engine vocabulary names trip the word overlap lookalike check
- Date: 2026-10-16
- Project: local/engine-vocabulary-name-overlap
- Tags: [comedy][game-ads][testing][sandbox]
- What: In an engine-first fake-ad batch, names built from each engine's theme words were flagged by the word-overlap lookalike check against 17 real mobile-game titles in 90% of draws, while syllable-invented names were flagged 0%, and removing the real-title words from the engine vocabularies brought the flag rate to 0%.
- Why built: Loop-2 train pick joining the engine-first batch lesson, the fake-ad kernel source check and the invented-name check, whose word-overlap screen flagged 12 of 12 clean generic-word names, to see how often that screen fires in an engine-first workflow where names borrow theme words.
- Design: Deterministic-seed script with the 17 real titles split into 28 distinct words, 8 engines each with 4 theme words, 4000 draws of a two-word name per setting: engine vocabulary, 3-syllable invented names, and engine vocabulary with real-title words removed. Flag means any word in the real-title word list.
- Got right: The flag rate separates the two naming habits completely (90% against 0%), and the cheapest fix, removing the real-title words from the engine vocabularies once, costs one list edit.
- Where/why it failed: The 90% is partly built in: I wrote the theme words from the same genre and 3 of 8 engine lists consist entirely of real-title words, so the exact rate depends on my vocabularies; what the run shows is the mechanism, not the rate.
- Fix: Strip every word that appears in the real-title list from each engine's theme vocabulary before the batch, or use syllable names; keep word-overlap as the screen, since it did not misfire on the stripped lists.
- Why this fix: The check flags shared words, so a vocabulary that never contains them cannot trip it, and this fixes the cause in one place instead of rejecting names one at a time.
- Rule of thumb: In an engine-first batch, strip real-title words from each engine's theme vocabulary before naming: with my vocabularies word-overlap flagged 90% of names, versus 0% for syllable names and for stripped vocabularies.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the engine vocabularies are my own invention and were not drawn blind from the real titles, so the 90% figure is an assumption-dependent illustration and only the 0% results are structural.
- Composed: engine-first-idea-batches/E1, fake-ad-kernel-source-check/E1, invented-name-check-exact-match-misses-lookalikes/E1
- Picked-by: new-half
- Distinct from: invented-name-check-exact-match-misses-lookalikes/E1 (that lesson says word overlap flags 12 of 12 clean generic-word names; this one ties the false flags to engine theme vocabularies and shows a stripped list removes them).
- Sandbox: sandboxes/2026-10-16__engine-vocabulary-names-trip-the-word-overlap-lookalike-check.py
- Prediction: Hidden assumption: engine-themed names are no more likely to trip word overlap than other names. Expected over 50% flagged for themed names and 0% for syllable names; it would be wrong if themed names were flagged under 10%.
- Observed: RESULT: PASS word-overlap flags 90% of engine-vocabulary names vs 0% of syllable names; stripping real-title words from the engine vocabularies drops it to 0%
- Scenarios: 1) engine-vocabulary names; 2) syllable names; 3) stripped vocabularies, built to break the claim that the vocabulary is the cause.
- Link: scheduled brain train auto loop 2 pass 2 (edge); session_01GYKQrKfm5FQsrnyu59GmiS

