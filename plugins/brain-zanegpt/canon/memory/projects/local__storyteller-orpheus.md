# local/storyteller-orpheus — lessons

Project: local/storyteller-orpheus. Newest first.

---

## E1 — orpheus test the one condition at the threshold
- Date: 2026-10-17
- Project: local/storyteller-orpheus
- Tags: [narrative][pacing][simulation][sandbox]
- What: Modelled Orpheus and Eurydice as a 20-step climb under one fixed condition (do not look back), where the urge to
  break it is eagerness to reach the exit (N over steps left) times silence (steps since the last sign she is behind).
- Why built: Brain train on Jim Henson's The StoryTeller; canon had the goal-gradient kernel for progress bars but
  nothing on where a story or game should place the single fragile condition so its test lands at the climax.
- Design: Stdlib step loop; strain = pull x silence, break at the first step strain passes the resolve (20); cues every
  other step; scenarios move a 6-step silence along the walk, add a late cue, sweep resolve 10-40 for the
  shortest breaking silence early vs late, repeat with an additive strain, and a BREAK run with flat pull.
- Got right: The Ovid layout (cues to step 12, silent from 13) breaks at step 17 of 20; the same silence early never
  breaks; a cue at step 16 only delays the break to 19; across resolve 10-40 a late silence breaks it at 1-3
  steps against 7-14 steps early, and an additive strain gives the same ordering or breaks at the exit unaided.
- Where/why it failed: Early silence is cheaper, not free: 7-14 steps of it still break the condition, and with flat pull an
  early silence breaks at step 7, so the exit only matters because pull rises. Predicted a cutoff at step 10,
  observed 9 (cues on even steps make odd starts one step longer); a mislabelled BREAK printout was fixed.
- Fix: Keep the condition constant for the whole journey and take the reassurance away only in the final stretch,
  so the single test lands next to the exit, where pull is highest, and keep early silences short.
- Why this fix: The same 6-step silence peaks at strain 20 early and 33 late, and near the exit the safe silence
  shrinks to one step, so a short late gap does the work a long early gap cannot.
- Rule of thumb: Put the one fragile condition's real test in the last quarter, where eagerness peaks, and remove
  reassurance there; early silence must be several times longer to break it, but only if eagerness rises.
- Provenance (verified/assumed): Verified first-hand by the sandbox; the tale details checked against
  Wikipedia's Storyteller article and Ovid, Metamorphoses Book X (Kline translation). Model parameters are toy values.
- Composed: ideas:REINFORCEMENT/progress-design/effort-accelerates-as-remaining-distance-to-a-fixed-goal-shrinks
- Sandbox: sandboxes/2026-10-17__orpheus-test-the-one-condition-at-the-threshold.py
- Prediction: Ovid layout breaks at step 17 of 20; the same 6-step silence early never breaks; silences from step 10
  break; a cue at 16 delays the break to 19; round 2: late breaking silence shorter than early at every resolve.
- Observed: RESULT: PASS break at step 17 of 20 late, never for the same silence early; cutoff at step 9 (predicted
  10); late cue delays to 19; resolve 10-40: late 1-3 steps vs early 7-14; flat pull: early silence breaks at 7.
- Scenarios: 1) Ovid layout; 2) same silence early; 3) silence-start sweep; 4) late cue; 5) resolve sweep; 6) additive strain; 7) BREAK: flat pull
- ZaneGPT verdict: weak — the PASS confirms the simulator's own algebra (pull x silence rises as steps left shrink), not that real fragile conditions behave this way, and the 1-vs-9 cutoff miss shows the point predictions are loose.
- Hidden assumption: Eagerness rises toward the exit (pull = N over steps left) and strain is multiplicative with silence, so the rule's "late is worse" is built into the model rather than discovered by it.
- Would prove it wrong: A run where pull is flat or falls late, or strain is a different form (capped, saturating, decaying with fatigue), and a 6-step silence late is still no more likely to break than the same silence early. The flat-pull run already shows early silence breaking at step 7, so the early/late gap depends entirely on pull rising.
- Break scenario: Keep the 20-step climb, but make the late cue unreliable, with 30% of cues dropped at random and the resolve drawn per run. Add a habituation term that dampens pull after long silence. Then check whether the late-quarter placement still wins across 1000 seeds, or whether the dominant breaker is cumulative silence regardless of position.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest 4d611cd37a52
- Link: session https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

