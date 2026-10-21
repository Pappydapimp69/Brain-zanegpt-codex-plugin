# local/held-pause-needs-matching-distance — lessons

Project: local/held-pause-needs-matching-distance. Newest first.

---

## E1 — a held pause before the peak beat cannot rescue a severe beat under fixed grounded distance
- Date: 2026-10-15
- Project: local/held-pause-needs-matching-distance
- Tags: [comedy][humor][narrative][sandbox]
- What: Adding a held pause before the final beat to the escalation-with-distance model: under a fixed
  grounded distance the pause gains nothing for a severe peak (0.269 with and without) and a mild
  schedule still wins (0.283); under matched distance the same pause lifts a setup-then-peak arc
  from 0.461 to 0.721. The pause amplifies a beat only when the framing already lets it land.
- Why built: New-half train pick joining the absurd-premise rule (wrong cue plus safe cue), the one-peak
  held-pause rule and the escalation-needs-matching-distance lesson, to test whether a held pause
  could stand in for distance and rescue a single big beat in a grounded piece.
- Design: Escalation model from escalation-needs-matching-distance/E1: habituation exp(-0.2 X), X += 1/(1+I/5),
  response I/C with ceiling 10, six beats, benign gate exp(-((d - I/C)/0.25)^2) with d fixed 0.3 or
  matched to I/C. A pause cuts accumulated habituation by 80% before the last beat; the score is 0.7
  times the peak response plus 0.3 times the mean (my assumed one-peak weighting). Schedules mild, flat big, setup-then-peak, ramp.
- Got right: The pause did what the one-peak rule says on habituation when distance matched (+0.26 on
  setup-then-peak, +0.20 for ramp), and the grounded case reproduced the gate result: flat big scored 0.000.
- Where/why it failed: I expected setup-then-peak to be the best schedule under matched distance with the pause, and
  it was not: flat big scored 0.967 against 0.721, because with a mean term and a matched gate the
  repeated ceiling beats keep paying. That ranking depends on my assumed peak weight and mean term, so it is not a finding.
- Fix: Treat the held pause as a multiplier on a beat that already has its cue, not a substitute for
  it: set the framing distance first (surreal or cartoon framing for a severe peak), then add the pause
  before the one peak beat; in a grounded piece keep the peak mild.
- Why this fix: The gate multiplies the response, so a pause that restores the habituated response multiplies
  a value the gate has already pushed to about 0 for severe beats; distance has to come first.
- Rule of thumb: A held pause before the peak beat adds nothing when the framing distance does not fit the beat: pause gain 0.00 under fixed grounded distance versus +0.26 under matched distance; set distance first.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the model form, the gate width and the 0.7/0.3 peak weighting are my assumptions,
  so only the direction of the pause-by-distance interaction is claimed.
- Composed: ideas:COMEDY/an-absurd-premise-needs-a-wrong-cue-and-a-safe-cue, ideas:COMEDY/one-peak-violation-with-a-held-pause, escalation-needs-matching-distance/E1
- Picked-by: new-half
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-15__a-held-pause-before-the-peak-beat-cannot-rescue-a-severe-beat-under-fixed-grounded-distance.py
- Prediction: Hidden assumption: a held pause helps any peak beat. Expected pause gain near 0 under fixed grounded distance
  and a clear gain under matched distance, and expected setup-then-peak to be best when matched; it would
  be wrong if the pause lifted the severe peak under fixed distance.
- Observed: RESULT: FAIL fixed: peak+pause 0.269 vs mild+pause 0.283; matched: peak+pause 0.721 best=flat_big (the FAIL is my expectation that setup-then-peak wins when matched; pause gains 0.00 fixed vs 0.26 matched held)
- Scenarios: 1) fixed grounded distance, four schedules with and without pause, built to break the claim that a pause helps any peak; 2) matched distance, same
  schedules; 3) pause gain compared across the two framings.
- Link: scheduled brain train auto loop 1 pass 2 (edge); session_01Twuh3aqxvcX5mmf7uhRTr7

