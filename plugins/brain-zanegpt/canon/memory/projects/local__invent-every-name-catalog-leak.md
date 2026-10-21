# local/invent-every-name-catalog-leak — lessons

Project: local/invent-every-name-catalog-leak. Newest first.

---

## E1 — catalog examples leak real brand names into an invent every name batch and generic word names still collide
- Date: 2026-10-15
- Project: local/invent-every-name-catalog-leak
- Tags: [game-ads][legal][comedy][sandbox]
- What: The invent-every-name rule for fake game ads meets a trope catalog that names real games: 15 of the 20
  catalog entries carry a real game as their example, so a script built from a catalog entry as written leaks a brand.
  Inventing names from the catalog's own vocabulary is no safer: 4 of 60 two-word names (Royal Match, Top War,
  Hero Wars, Last War) reproduced real games exactly, while 60 syllable-built names produced 0.
- Why built: A new-half train pick joining the anti-template rule, the fake-ad kernel source check and the legal
  kernel (parody the genre, invent every game name), to test whether the catalog the batches draw from respects
  the legal rule it sits beside.
- Design: Transcribed the 20 trope labels with their named example games, scrubbed every example, and generated two
  deterministic sets of 60 names: ordered pairs of 12 generic words taken from the catalog's own game names,
  and ordered pairs of 10 invented syllables; each was compared with 16 real game names by exact match and by shared word.
- Got right: Scrubbing the examples leaves 0 of 20 entries naming a real game, and the syllable names never collided
  with a real game by exact match or by shared word.
- Where/why it failed: I expected the generic-word names to avoid real games exactly (0 of 60) and 4 reproduced real titles; shared-word overlap
  was 60 of 60, but that is by construction because the words were taken from the real names, so it is not a finding.
- Fix: Strip the named example from each catalog entry before it reaches a script, and make game names from
  syllables or from words that appear in no real title, then check the result against the list of real names.
- Why this fix: The catalog is where real names enter, so removing them there is one change instead of a check on
  every script, and an invented name is only safe if its words are not the genre's own vocabulary.
- Rule of thumb: Scrub the real game named in each catalog entry and build invented names from syllables: 15/20 entries named a real game, and generic-word names matched real titles 4/60 against 0/60 for syllables.
- Provenance (verified/assumed): Verified first-hand by running the sandbox over the catalog as transcribed and 16 real names from it; no trademark search was run and this is not legal advice.
- Composed: ideas:AI-VIDEO/every-video-gets-its-own-joke-and-script, fake-ad-kernel-source-check/E1, ideas:LEGAL/parody-the-genre-not-the-brand
- Picked-by: new-half
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-15__catalog-examples-leak-real-brand-names-into-an-invent-every-name-batch-and-generic-word-names-still-collide.py
- Prediction: Hidden assumption: the catalog is brand-free so generic-word names are safe. Expected 15 of 20 entries naming a game, 0 of 60 exact collisions for generic-word names
  and 0 for syllable names; it would be wrong if any generic-word name equalled a real title.
- Observed: RESULT: PASS 15/20 catalog entries name a real game; generic-word names exact 4/60 (word-overlap by construction); syllable names 0/60 (the 0 of 60 expectation for generic words was refuted)
- Scenarios: 1) catalog scan and scrub; 2) generic-word names, built to break the safe-vocabulary assumption; 3) syllable names.
- Link: scheduled brain train auto loop 2 pass 1 (kernel); session_01Twuh3aqxvcX5mmf7uhRTr7

