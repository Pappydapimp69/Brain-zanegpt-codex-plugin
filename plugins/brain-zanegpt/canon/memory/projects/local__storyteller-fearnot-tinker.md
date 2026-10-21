# local/storyteller-fearnot-tinker — lessons

Project: local/storyteller-fearnot-tinker. Newest first.

---

## E1 — fearnot tinker contingent companion carries tension
- Date: 2026-10-17
- Project: local/storyteller-fearnot-tinker
- Tags: [narrative][stakes][simulation][sandbox]
- What: Modelled The StoryTeller's Fearnot as a fearless hero and a crafty tinker who is paid only if he finds
  something that frightens the boy, travelling an itinerary of ever scarier places (pond, castle, and on).
- Why built: Brain train on Jim Henson's The StoryTeller; canon already had stakes coming from the hero's attachment,
  but nothing on how a fearless lead's companion supplies the scene-by-scene tension the lead cannot.
- Design: Stdlib loop over places of scariness 2, 6, 18, 54, 162; the guide believes p = s/(s+D) that a place
  scares the hero, his doubt D grows by a factor k after each failed scare, and he goes on only while
  purse*p beats a trip cost of 0.1*s; scene tension = stake * 4p(1-p) summed over characters, and the
  immune hero stakes nothing. Runs: hero alone, contingent guide (k=2.5 and k=10), flat-fee guide,
  small purse, a BREAK where the greedy guide knows the hero is immune, and a BREAK sweep of the
  uninformed guide's prior doubt D0 = 0.5, 2, 8, 32, 128.
- Got right: The hero alone made 5 scenes with tension 0.0; the contingent guide made 4 scenes with tension
  10.0, 9.92, 9.67, 9.29 (total 38.9) before the trip cost beat his hope; a guide who learns faster
  (k=10) made only 2 scenes (17.1); a flat-fee guide made 0; a 0.5 purse made 1 scene at 0.5. An
  overconfident guide (D0=0.5) kept the road for 4 scenes but at only 21.6 tension (p near 0.8).
- Where/why it failed: The BREAK greedy guide who knows the hero cannot be frightened made 0 scenes and 0 tension, so
  greed alone carries nothing; the companion's stake has to hang on an outcome he still thinks could
  go either way. The doubt sweep broke the plain claim further: an uninformed, contingent guide with
  prior doubt D0=128 also made 0 scenes and D0=32 only 2 at 4.8 tension, so ignorance is not enough;
  he has to start out hopeful. Comedy and the tinker's own peril are left out of the model.
- Fix: Give the fearless lead a companion whose payoff hangs on an outcome the lead does not care about, and
  keep that companion unsure of it; let his doubt grow slowly so the road lasts, and end the road when
  his hope no longer covers the cost of the next stop.
- Why this fix: An immune hero makes every outcome certain, so the open question has to live in someone else's
  head; the companion's stake times his uncertainty is what each scene carries.
- Rule of thumb: When the lead cannot lose, put the open question in a companion who is paid on it and starts out
  hopeful but unsure; pay him flat, make him doubtful from the start, or let him learn the lead is immune,
  and the scenes go flat and the road ends.
- Provenance (verified/assumed): Verified first-hand by the sandbox; the tinker's role (a dishonest, crafty
  guide paid only if he finds something that frightens the boy, who leads him to a pond and a castle)
  checked against Wikipedia's Storyteller article and two episode reviews cited in the kernel.
  Model parameters are toy values.
- Composed: ideas:NPC-SIM/decision-making/multiplicative-combination-preserves-vetoes, ideas:SYSTEM/narrative/tension-as-information-gap
- Sandbox: sandboxes/2026-10-17__fearnot-tinker-contingent-companion-carries-tension.py
- Prediction: Hero alone 5 scenes at 0 tension; contingent guide (purse 10, k=2.5) 4 scenes, about 10.0, 9.9, 9.7,
  9.3, total about 38.9; fast learner (k=10) 2 scenes, about 17.1; flat fee 0 scenes; purse 0.5 gives
  1 scene at 0.5; BREAK informed greedy guide 0 scenes. Added after the first check, before its run:
  prior doubt D0 0.5/2/8/32/128 gives 4, 4, 3, 2, 0 scenes.
- Observed: RESULT: PASS immune hero alone gives 0 tension; contingent guide gives 4 scenes / 38.9 tension, fast
  learner 2 / 17.1; flat fee and informed greedy guide give 0 scenes; uninformed guide with prior doubt
  D0 0.5/2/8/32/128 gives [4, 4, 3, 2, 0] scenes (tension 21.6, 38.9, 21.3, 4.8, 0.0).
- Scenarios: 1) hero alone; 2) contingent guide k=2.5; 3) contingent guide fast learner k=10; 4) flat-fee guide;
  5) small purse 0.5; 6) BREAK greedy guide who knows the hero is immune; 7) BREAK prior-doubt sweep
  D0 = 0.5, 2, 8, 32, 128
- ZaneGPT verdict: weak — the prediction was revised after the first check to fit the D0 sweep, and the PASS shows the code is consistent with itself, not that the rule transfers beyond the chosen constants.
- Hidden assumption: The model hard-codes the "hopeful but unsure" prior (p = s/(s+D), purse*p > 0.1*s) and a single scare curve. The sweep only varies D0 and k, so the rule is a statement about those constants, not about story structure. Tension is also defined as stake*4p(1-p), so "scenes go flat" is partly the metric's own shape rather than an independent finding.
- Would prove it wrong: Hold D0 and k fixed and change the trip-cost coefficient (0.1) or the place scariness ratios (the ×3 progression). If the 4-scene, ~38.9-tension result flips to 0 or 5 scenes under modest changes, the rule is an artifact of tuned constants. A guide who is hopeful, unsure and contingent but still produces flat scenes, or a flat-fee guide who produces tension, would also refute it.
- Break scenario: Keep the guide hopeful, unsure and contingent (D0=2, purse 10, k=2.5), but make the hero fallible, with a small nonzero chance of being scared, and make the guide's update Bayesian rather than a fixed multiplier. Then run a guide who is wrongly confident (D0=0.1, k=1.2) beside a doubtful one. If tension is highest for the overconfident guide and the "hopeful but unsure" band no longer wins, the rule fails.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest d5f10fc58c8d
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

