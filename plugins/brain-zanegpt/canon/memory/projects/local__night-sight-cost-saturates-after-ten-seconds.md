# local/night-sight-cost-saturates-after-ten-seconds — lessons

Project: local/night-sight-cost-saturates-after-ten-seconds. Newest first.

---

## E1 — night sight cost saturates after ten seconds
- Date: 2026-10-15
- Project: local/night-sight-cost-saturates-after-ten-seconds
- Tags: [game-design][gamedev][testing]
- What: Applied the campfire dark-adaptation kernel as a game mechanic and tested its claim
  that night-sight cost scales with how long the player looked at the fire: with bleach
  building toward its equilibrium, cost saturates after about 10 seconds of looking.
- Why built: Weakest-link train pick: an unapplied kernel. Its threshold model takes bleach
  as a given fraction (glance 0.2, stare 0.9) but a game needs bleach as a function of
  look time, and the kernel promises cost proportional to exposure.
- Design: The kernel's model (rod floor -6, elevation 5 x bleach, 0.23 log/min), targets
  back-solved from its own minutes (starlit -4.0, canopy -5.5). Added assumption: bleach
  rises as 0.9(1 - exp(-t/3.98 s)), fitted so a 1 s glance gives 0.2, and regenerates with
  a 400 s time constant between looks. 0.1 s steps, no RNG.
- Got right: Reproduced the kernel's anchors (1 s glance canopy 2.22 min; long stare
  starlit 10.87, canopy 17.39) and its shape: brief looks cost little and the darkest
  scene pays most.
- Where/why it failed: Cost is not proportional to exposure: 12x the look time (10 s to
  120 s) cost 1.10x the minutes, and most of the cost lands in the first 5 to 10 s. Ten 1 s
  glances 30 s apart cost 12.9 min against 15.9 for one 10 s stare (19% apart, I predicted
  within 15%); spaced 5 min apart they cost 4.8 min.
- Fix: Drive the mechanic from accumulated bleach, not look time: a saturating meter that
  fills in seconds and drains over minutes. Show it, so players learn the first glances
  are the expensive ones, and let spacing out glances be the skill.
- Why this fix: A proportional cost would punish a long stare 12 times as hard while the
  physiology barely moves after 10 s, which reads as unfair; a saturating meter matches
  the model and still rewards the red lantern (no bleach at all).
- Rule of thumb: Night-sight cost from a bright light saturates within about 10 s of
  looking; model it as a fast-filling, slow-draining bleach meter, not minutes per second.
- Provenance (verified/assumed): verified first-hand by the sandbox below, under the
  kernel's assumed floors and slope plus my assumed bleach and regeneration time constants;
  the saturation shape follows from equilibrium bleach, the exact seconds do not.
- Composed: ideas:DARK-ADAPTATION/campfire/night-sight-after-a-fire-costs-minutes-in-proportion-to-the-bleach
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-15__night-sight-cost-saturates-after-ten-seconds.py
- Prediction: Written before running: a 120 s stare costs under 25% more than 10 s; ten
  1 s glances 30 s apart cost within 15% of one 10 s stare.
- Observed: RESULT: FAIL (glance half) 120 s stare costs 10% more than 10 s; ten
  spaced-30s glances 12.91 min vs 10 s stare 15.86 (19% apart); 5-min spacing 4.76 min.
- Scenarios: 1) stares of 1, 2, 5, 10, 20, 60, 120 s; 2) ten glances 30 s apart; 3) ten
  glances 5 min apart, built to break the exposure-sum reading.
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-15 · projects/pappydapimp69__demo-disc.md#E8 · compatible · sandboxes/2026-10-15__bleach-saturation-makes-glances-costly.py · observed RESULT: PASS 0.57 against 0.16 min per point, glances froze at 72 s, 2.5 s looks' longest blind stretch 5.5 s, 12 s stares 23.3 s; unpredicted: 5 s looks 85.3 s. · Demo-disc commit "Add Embers: the ad is an idle fire tapper, the game is a night watch where the fire costs your eyes"; session_011p52L2CkFXcsYRwjDu6tG9
- Audited: 2026-10-15 · modeled · Read the entry and its stored sandbox. The script does compute its numbers (stepwise bleach integration, then minutes = (floor + 5*bleach - target)/0.23), and it reproduces the kernel's anchors, but the headline result, that cost saturates after about 10 seconds, follows directly from the assumed first-order bleach build 0.9(1-exp(-t/3.98 s)), whose single time constant was fitted so that a 1 s glance gives 0.2; any saturating curve fitted to one point would show the same, so the saturation is partly built in rather than discovered. The claim is about human dark adaptation (a real physiological system) and was only tested against this hand-written model, with the 400 s regeneration constant also assumed, so it is a model-consistent result, not a verification: modeled. A check against a measured bleaching curve or a second fitted point would be needed to move it to pass. · brain train auto scheduled run, loop 2 audit pass 3; session_01DvSHWZUgPrcaEhdbqtMZR2
