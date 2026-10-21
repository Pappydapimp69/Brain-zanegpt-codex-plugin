# local/storyteller-perseus-mirror — lessons

Project: local/storyteller-perseus-mirror. Newest first.

---

## E1 — perseus mirror indirect view works only within its error
- Date: 2026-10-17
- Project: local/storyteller-perseus-mirror
- Tags: [gamedesign][combat][simulation][sandbox]
- What: Modelled the mirror shield from Perseus and the Gorgon as a strike on a hazard that kills when looked at
  directly, comparing a direct view (fatal), a blind strike at the lair centre, a raw reflection acted on as
  if direct, and a corrected reflection that is coarse (rounded to steps of q) and possibly stale by a lag.
- Why built: Brain train on Jim Henson's The StoryTeller; canon had sight-as-exposure and latency-driven control
  choice, but nothing on what an indirect view's own error does to a strike that must land within a tolerance.
- Design: Stdlib deterministic loop, no randomness: 13 start offsets (-6..6) on one reach axis, sword speed 2, 10
  steps, strike when the view says aligned or on the last step; hit if the miss is within w. Target asleep
  (still) or awake (sways +1, 0, -1); rounding q of 1 or 3; lag 0 or 1; tolerance w of 0, 1, 2 or 6.
- Got right: Direct view died 13/13. Against a still target the corrected mirror hit 13/13 exactly with a fine image
  and 7/13 exactly with a coarse one (q=3), back to 13/13 once w=1 covered the rounding. The raw reflection
  moves the sword away from the target and hit 1/13 at w=1, worse than striking blind (3/13).
- Where/why it failed: Run 1 missed two awake predictions: a current fine view hit only 3/13 exactly (predicted 13) and a
  one-step-stale view 7/13 at w=1 (predicted 13). Not a code bug: acting on a view takes a step and the target
  sways meanwhile, so the budget must count that step. BREAK: with w=6, wider than the prior's error, blind
  tied the mirror at 13/13, so the indirect view bought nothing; the budget is a bound, not exact, and
  the sweep stays on one fixed grid (sway up to 2, lag up to 1), so a hit at the budget is near arithmetic.
- Fix: Budget the indirect channel's error before committing to it: rounding + (lag + 1 act step) x target speed,
  and set the strike tolerance at or above it; correct the reversed axis before acting on the image.
- Why this fix: Every awake case reached 13/13 once w met that budget (q=1 lag 0 at w=1, q=1 lag 1 at w=2, q=3 lag 0 at
  w=2, a target as fast as the sword at w=4 but 7/13 at w=2), and every still case once w met the rounding;
  an uncorrected reversal does not shrink with tolerance.
- Rule of thumb: A hazard you may only watch through an indirect view is beatable when the strike tolerance covers the
  view's rounding plus (lag + 1) steps of target motion; correct the view's reversal first, and skip the
  indirect view when the tolerance already covers a blind guess.
- Provenance (verified/assumed): Verified first-hand by the sandbox; the episode details checked against Wikipedia's
  Storyteller article and an Ancient World Magazine episode review, and the reflection strike against
  Apollodorus 2.4.2 on theoi.com. The reach axis, speeds, rounding and lag are toy values.
- Composed: ideas:RPG/perception/echolocation, ideas:SYSTEM/input/control-scheme-by-latency-not-taste
- Sandbox: sandboxes/2026-10-17__perseus-mirror-indirect-view-works-only-within-its-error.py
- Prediction: Direct 0 hits, 13 deaths; blind still w=0 1/13, w=1 3/13, w=6 13/13; raw reflection w=0 and w=1 1/13;
  corrected still q=1 13/13 at w=0, q=3 7/13 at w=0 and 13/13 at w=1; awake q=1 lag 0 13/13 at w=0 (missed:
  3); awake q=1 lag 1 w=0 1/13, w=1 13/13 (missed: 7); awake q=3 lag 1 w=0 at most 4, w=1 4 to 11, w=2 13/13.
  Added before run 2: awake q=1 lag 0 w=1, q=1 lag 1 w=2 and q=3 lag 0 w=2 all 13/13. Added before run 3:
  a fast target (sway 2, as fast as the sword), q=1 lag 1, budget 4: w=4 13/13, w=2 below 13.
- Observed: RESULT: PASS direct view kills 13/13; corrected mirror hits whenever tolerance >= its error (asleep q=3:
  7/13 exact, 13/13 at w=1; awake: 13/13 once w >= rounding + (lag+1) x sway); uncorrected mirror 1/13 at
  w=1 is worse than blind 3/13; BREAK: at w=6 blind ties the mirror 13/13; fast target (sway 2) needs w=4:
  13/13 there, 7/13 at w=2; run 1 missed 2 awake predictions by leaving out the act step
- Scenarios: 1) direct view, still and awake; 2) still target: blind, raw reflection, corrected q=1 and q=3; 3) awake
  target: corrected with lag 0 or 1 and q of 1 or 3 across w of 0, 1, 2; 4) BREAK: tolerance w=6 wider than
  the blind guess's error; 5) fast target swaying 2 per step, as fast as the sword, at and below the budget
- ZaneGPT verdict: weak — the rule is an arithmetic restatement of "tolerance ≥ error" that was confirmed on a deterministic grid and already failed its own boundary (blind ties the mirror at w=6, and the fast target needed a revised budget), so it holds only for the bounded-sway model it was built from.
- Hidden assumption: Target motion is bounded and non-adversarial (sway ≤ 1 per step, no drift or direction change), and the error terms simply add (rounding + (lag+1) × sway). The rule is also fitted to a 13-offset grid in a 1-D toy that has no occlusion, no noise and no cost of a miss. The "tolerance covers the error" threshold is therefore a property of this simulator's arithmetic, not evidence about real hazards.
- Would prove it wrong: A run where w ≥ rounding + (lag+1) × sway still misses. Examples: a target that sways 1 per step but reverses within the lag window, or a stale view combined with q=3 whose rounding error and lag error compound beyond the additive bound. Equally damaging: a case where w is below the stated budget and still hits 13/13, which would mean the budget is not the real threshold.
- Break scenario: Make the target's motion depend on the strike (it flinches toward the sword's approach line). Pair it with q=3, lag 1 and w set exactly to rounding + (lag+1) × 1 = 5. Run 13 offsets with the target reacting to the sword's position, not swaying on a fixed script. The fixed-sway budget should then fail. A second break: add a cost for a wasted swing, so "skip the indirect view when tolerance covers a blind guess" gets tested against the strike cost, not just hit rate.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest 0fc8bd150f5e
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-19 · projects/pappydapimp69__brainwork.md#E479 · compatible · sandboxes/2026-10-19__billiards-bank-shot-mirror-unfold-replays-exactly-but-needs-ball-radius-inset.py · observed RESULT: PASS unfolded aim reached the target in 840/840 one-cushion and 2520/2520 two-cushion plans, but with the PLANNED cushion order in only 750 and 1500; nominal-table aim missed by up to 4.85 with r=2.5 while inset unfolding missed by… · brain train auto loop 1 pass 6; session_01Xs9BRpt5ZfygjApJGsbMEk
