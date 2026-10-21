# local/fail-ad-cutdowns-keep-the-gap — lessons

Project: local/fail-ad-cutdowns-keep-the-gap. Newest first.

---

## E1 — fail ad cutdowns keep the gap
- Date: 2026-10-15
- Project: local/fail-ad-cutdowns-keep-the-gap
- Tags: [game-ads][narrative][video][testing]
- What: A fixable-fail game ad works by ending on an open gap, but cutting a 30 s master down by the
  clock (keep the first L-4 s, add the end card) lost the fail ending in all four cut-downs
  (6, 10, 15, 20 s); anchoring the cut to the fail beat kept it in 10, 15 and 20 s.
- Why built: New-half train pick: tension-as-information-gap with the film project and the fixable-fail
  ending kernel (AppsFlyer Q1 2025: on social, endings that offer a chance to fix the
  situation perform 65% better). Ads ship in many lengths, so the composed question is whether
  the gap survives a cut-down.
- Design: Master beat sheet: hook 0-3, setup 3-8, attempt 8-20, near-win 20-22, fail 22-26, end card
  26-30. Truncate cut: first L-4 s plus the card. Anchored cut: hook, fail and card first,
  remaining time filled from setup and attempt in order. Pass = the fail beat on screen for 2
  s or more and ending within 0.5 s of the end card.
- Got right: Building cut-downs from beats keeps the gap that makes the format work: every anchored cut
  of 10 s or more ends on the 4 s fail beat right before the end card, matching the film
  lesson that reveals should hang on their beat, not on the clock.
- Where/why it failed: Clock truncation removes the ending first, because the fail sits in the last third of the
  master: 0 of 4 cut-downs kept it, so short variants silently become a different ad (all
  attempt, no gap). At 6 s even the anchored cut lost it: a 3 s hook plus a 4 s card do not
  fit, and the 10 s anchored cut drops the attempt entirely.
- Fix: Cut fail ads from a beat sheet, not a timeline: lock the fail beat and end card, then cut
  setup and attempt; for 6 s variants, shorten the card or open on the near-win so the fail
  still fits.
- Why this fix: The format's value is the open, fixable gap at the end; any cut-down rule that measures from
  the start removes exactly that beat, while a beat-anchored rule spends the shrinking time on
  the parts the viewer can infer.
- Rule of thumb: Cut fixable-fail ads by beats, not by clock: truncating from the start lost the fail ending
  in 4/4 cut-downs; anchoring the fail plus end card kept it down to 10 s.
- Provenance (verified/assumed): Verified first-hand by the sandbox below; the +65% figure is AppsFlyer's as quoted in the
  kernel; the beat lengths are my model of a typical fail ad, not measured creatives.
- Composed: ideas:SYSTEM/narrative/tension-as-information-gap, film/E19, ideas:GAME-ADS/structure/fixable-fail-ending-beats-victory-on-social
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-15__fail-ad-cutdowns-keep-the-gap.py
- Prediction: Written before running: truncation keeps the fail ending only at 30 s (0 of 4 cut-downs);
  anchoring keeps it in every cut-down of 10 s or more and fails only at 6 s.
- Observed: RESULT: PASS clock truncation keeps the fixable-fail ending in 0/4 cut-downs; beat-anchored
  keeps it in 3/4 (10, 15, 20); 6 s lost by both.
- Scenarios: 1) truncation at 6/10/15/20/30 s; 2) beat-anchored at the same lengths; 3) the 6 s cut,
  built to break the anchored method.
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-15 · projects/local__ad-length-crossover-depends-on-the-cut.md#E1 · compatible · sandboxes/2026-10-15__ad-length-crossover-depends-on-the-cut.py · observed RESULT: PASS anchored 15s cut keeps h*=0.0122; truncated 15s cut moves it to 0.0455/s (3.7x); truncated 15s never beats the 30s master at decay 1-4%/s (ratio 0.59-0.92); 10 s truncated h* 0.0376. · https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-creative-training.md#E38 · compatible · sandboxes/2026-10-15__vertical-cutdown-follow-pan-needs-per-layer-dither-anchor.py · observed RESULT: PASS centre crop keeps the gap in 0/10 cuts (goal off-frame); follow-pan beat-anchored keeps it at 10/15/20/30 s, truncated only at 30 s; master static swim 0 everywhere; follow-pan swim screen bg 0.331 fg 0.853, world-anchored fg… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 5 pass 2
- Cited-by: 2026-10-15 · projects/local__rank-ipm-times-d1-needs-fidelity-retention-link.md#E1 · compatible · sandboxes/2026-10-15__rank-ipm-times-d1-needs-fidelity-retention-link.py · observed RESULT: PASS IPM-only picks fidelity 0.4, IPM*D1 picks 1.0 (+18% retained installs); flat D1 same winner True; lower-bound flips at 1000 impr 0/3, at 100 impr 1/3; clock cut loses 23% · session_01A5ZkeepCfk7CHTSxS7qQ4k
- Audited: 2026-10-17 · modeled · Read the entry and its stored sandbox. The sandbox does not compute a surprising result: with the fail beat at 22-26 s of a 30 s master, a clock cut that keeps the first L-4 seconds must drop it for every L under 30, so "0 of 4 truncated cut-downs" is arithmetic on the chosen beat sheet, and the anchored cut keeps it by construction because it places the fail beat first. It also tests one master with the fail late in the film, so the broader rule (cut from a beat sheet, not a timeline) is only shown for that geometry; a fail beat early in the master would let truncation pass. The 6 s failure is the one non-trivial finding (a 3 s hook plus a 4 s card leave no room), and it is real arithmetic. The ad-performance premise (fixable endings lift results 65%) was not tested at all and real editing tools were not used, so the claim about real ads is only checked against a hand-written model. · scheduled brain train auto loop 1 pass 3; session_01RpeN38wP8qZN5F5czYD6HX
- Cited-by: 2026-10-20 · projects/pappydapimp69__brainwork.md#E525 · compatible · sandboxes/2026-10-20__stale-fail-tag-turns-ipm-times-d1-back-into-ipm-only.py · observed RESULT: PASS stale sidecar tag made IPM x D1 identical to IPM-only in 441/441 cells (wrong in 213) while a beats-derived tag matched measured in 441/441; flat D1 all agree=True · session_015FBsByvogibt2qnd37NTki
- Cited-by: 2026-10-20 · projects/pappydapimp69__brain.md#E233 · incompatible · sandboxes/2026-10-20__two-budget-agreement-guard-for-ipm-d1-ranking-fails-when-small-budgets-agree-on-the-wrong-winner.py · observed RESULT: PASS (revised claim) 20/40 budgets pick a non-reference winner; 42 budget pairs agree on a wrong winner (guard fooled), 33 with the larger budget at least 500; the under-30% part was refuted. · brain train auto loop 2 pass 2 (second pick); session_01LUiQ2ftChwstLtJ7LZdB3s
