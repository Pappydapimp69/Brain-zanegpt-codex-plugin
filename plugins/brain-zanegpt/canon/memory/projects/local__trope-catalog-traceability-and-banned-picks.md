# local/trope-catalog-traceability-and-banned-picks — lessons

Project: local/trope-catalog-traceability-and-banned-picks. Newest first.

---

## E1 — trope catalog claims verified but only a third traceable and 10 percent banned
- Date: 2026-10-15
- Project: local/trope-catalog-traceability-and-banned-picks
- Tags: [game-ads][comedy][verification][sandbox]
- What: The 20-trope game-ad catalog says each trope was verified on a ruling, report or article. Checked
  against its own Source line, only 7 of 20 tropes name an example that the cited sources cover
  (Playrix, Evony, Project Makeover, Hero Wars twice, Mafia City, Lily's Garden), and 2 of the 20
  (won-real-money testimonial, sexualised reveal) are banned in real ads, so a uniform pick lands on one.
- Why built: The new-half train pick joined the anti-template rule (every video its own joke and script), the
  fake-ad kernel source check (verify labels, not just numbers) and the trope catalog, to ask whether
  a batch built from the catalog is both distinct enough and safe enough to use as written.
- Design: Transcribed the catalog's 20 tropes with the example each names and a banned flag, matched the
  examples to the Source line, then computed the chance a batch of k distinct tropes drawn uniformly
  contains a banned one, by formula and by enumerating all 125,970 eight-trope batches.
- Got right: The distinct-trope rule is satisfiable: 18 safe tropes allow an 18-video batch with no repeated
  trope, and the formula and the enumeration agree (0.653 at k=8).
- Where/why it failed: I assumed 'each verified' would mostly hold; only 7/20 trace to a cited source (13 name no
  covered example) and the catalog mixes the two banned tropes in with no marker, so 8 distinct picks
  hit a banned one 65% of the time (k=5 0.447, k=10 0.763). A 19th or 20th video cannot be both distinct and safe.
- Fix: Mark the banned tropes in the catalog and draw only from the 18 safe ones; treat an unsourced trope
  as unverified until a ruling or article is attached; plan a batch no larger than 18 distinct tropes.
- Why this fix: The catalog is a source for generated batches, so a flag at the source removes the risk from
  every draw, while per-video checks would only catch it after a script was already written.
- Rule of thumb: Before drawing from a trope catalog, filter out its banned entries and check which entries trace to a cited source: 7/20 traced and 2/20 were banned, so 8 uniform picks hit a banned one 65% of the time.
- Provenance (verified/assumed): Verified first-hand by running the sandbox over a transcription of the kernel text and its Source line; the
  banned status of the two tropes comes from the kernel itself and I did not re-check the rulings.
- Composed: ideas:AI-VIDEO/every-video-gets-its-own-joke-and-script, fake-ad-kernel-source-check/E1, ideas:GAME-ADS/tropes/twenty-trope-catalog-pick-one-name-the-genre-it-sells
- Picked-by: new-half
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-15__trope-catalog-claims-verified-but-only-a-third-traceable-and-10-percent-banned.py
- Prediction: Hidden assumption: the catalog is clean to draw from as written. Expected at most 8 of 20 tropes
  traceable to the Source line, 2 banned, and P(banned in 8 distinct picks) near 0.65; it would be
  wrong if most tropes traced or the banned ones were already excluded.
- Observed: RESULT: PASS traceable 7/20 (claim 'each verified' fails); banned 2/20; P(banned in 8 distinct)=0.653; safe distinct cap 18
- Scenarios: 1) trope-to-Source matching, built to break the 'each verified' claim; 2) closed-form chance of a
  banned trope at k=1,5,8,10; 3) full enumeration of 8-trope batches; 4) a 20-video distinct batch,
  which cannot be safe.
- Link: scheduled brain train auto loop 1 pass 1 (kernel); session_01Twuh3aqxvcX5mmf7uhRTr7

