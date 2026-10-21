# local/storyteller-icarus — lessons

Project: local/storyteller-icarus. Newest first.

---

## E1 — icarus band width sets the drift a guide can absorb
- Date: 2026-10-17
- Project: local/storyteller-icarus
- Tags: [gamedesign][difficulty][simulation][sandbox]
- What: Modelled Daedalus and Icarus as altitude inside a band with a failure on each side, spray below 20 and sun
  above 80, under a steady drift, a sine wobble, and a guide that pulls back toward a setpoint.
- Why built: Brain train on Jim Henson's The StoryTeller; canon had a fail-rate band and a fragile sweet-spot kernel
  but nothing on how a band between two opposite failures behaves as it narrows or as the flyer drifts.
- Design: Stdlib 60-step loop; per step h += drift + wobble + k x (setpoint - seen altitude); a meter per side gains 1
  each step outside the band and recovers 0.5 inside, falling at 3; scenarios abandon the guide, narrow the band,
  bias the setpoint, sweep drift, sweep gain x reaction delay with drift up and down, and a BREAK late strong guide.
- Got right: Guided flyer stays at 49-59 in [20,80]; with the guide gone it falls to the sun at step 36 (drift up) or
  the sea at step 33 (drift down); smallest safe band 16 centered, 8 with the setpoint biased by drift/k;
  tolerated drift 13 at width 60 to 2 at 16, about k x (half-width minus wobble) plus one for the meter grace.
- Where/why it failed: Predicted smallest widths 20 and 12, observed 16 and 8 (meters let brief peaks pass). The BREAK guide was
  predicted to fall in the sea; it dipped to 13 there but fell in the sun at step 11. Round 2 predicted drift
  still picks the side for unstable guides; refuted: they split 12 sun / 8 sea whichever way the drift points.
- Fix: Aim the setpoint against the known drift instead of at the middle, and keep the guide's gain under the limit
  its reaction delay allows, so a narrow band absorbs the wobble without the guide swinging into either wall.
- Why this fix: Biasing by drift/k halved the smallest safe band from 16 to 8; the largest safe gain fell from 2.0 with
  no delay to 0.9, 0.5 and 0.3 at delays 1-3, and above it every guide fell sooner than no guide (36).
- Rule of thumb: In a two-sided band a stable guide fails on the drift side and band width sets how much drift it
  absorbs; a guide stronger than its delay allows oscillates and fails sooner than none, and which wall it hits depends on its swing, not on the drift.
- Provenance (verified/assumed): Verified first-hand by the sandbox; the tale details checked against
  Wikipedia's Storyteller article and Ovid, Metamorphoses Book VIII (Kline translation). Model parameters are toy values.
- Composed: ideas:MOTION/physics/critically-damped-spring-not-fixed-duration-tween
- Sandbox: sandboxes/2026-10-17__icarus-band-width-sets-the-drift-a-guide-can-absorb.py
- Prediction: Guided flyer safe near 54; abandoned guide falls to the sun around step 35-37; smallest safe width about 20
  centered and 12 biased; late strong guide falls into the sea; round 2: unstable guides fall on the drift side.
- Observed: RESULT: PASS guided safe; abandoned falls on the drift side (sun 36, sea 33); safe band 16 vs 8 biased;
  safe gain 2.0/0.9/0.5/0.3 at delay 0-3; BREAK falls at 11 (sun); unstable split 12/8 either drift (refuted).
- Scenarios: 1) guided; 2) guide abandoned; 3) narrowing band; 4) biased setpoint; 5) drift sweep; 6) gain x delay, drift up; 7) same, drift down; 8) BREAK: late strong guide
- ZaneGPT verdict: weak — The prediction was refuted on the unstable-guide split (12/8 either drift), and the rule's claim that the wall "depends on swing, not drift" is only a negative result from one wobble, one meter and one horizon, with the two-sided "stable guide fails on the drift side" still supported by a single abandoned-guide run.
- Hidden assumption: Drift is a constant bias the guide merely has to out-pull, and the 60-step horizon is long enough for slow failure modes to show. The meter's 1-per-step gain against 0.5 recovery and 3 falling also lets a brief excursion pass, so "fails" means "sustained out-of-band" and not "touched a wall". The rule then reads the wall-hit as a property of the dynamics when the meter's asymmetry and the fixed 60 steps may be doing part of the work.
- Would prove it wrong: Rerun the gain x delay sweep with a different wobble phase or amplitude, a different meter threshold, or 200 steps. If the unstable-guide wall still splits 12/8 regardless of drift direction but the split moves with phase (or swaps when the sine starts at the opposite sign), then the wall follows the initial condition, not "swing". Likewise, if the abandoned guide's fall side flips when the setpoint, not the drift, is moved, "fails on the drift side" is wrong.
- Break scenario: Zero drift, a centered setpoint, a stable-looking gain/delay pair just inside the swept safe edge (e.g. gain 0.9 at delay 1), plus a wobble whose period matches the guide's oscillation period (resonance). Add a second run with sensor noise on "seen altitude". The rule predicts a safe, centered flyer. The resonant or noisy case should push it into either wall, which would show the safe gain edge belongs to this one wobble and not to the guide.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest 75364ea36f6f
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

