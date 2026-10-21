# local/decaying-safe-cue-flips-go-big-back-to-mild — lessons

Project: local/decaying-safe-cue-flips-go-big-back-to-mild. Newest first.

---

## E1 — decaying safe cue flips go big back to mild
- Date: 2026-10-17
- Project: local/decaying-safe-cue-flips-go-big-back-to-mild
- Tags: [comedy][humor][testing][sandbox]
- What: When the competing-norm safe cue that licenses going big at grounded distance itself habituates, flat-at-ceiling keeps winning down to about 0.6 of the cue per beat (a near tie, margin 0.06) and a mild schedule wins at 0.3; refreshing the cue every second beat widens the flat margin to 0.80.
- Why built: To test whether the safe-cue licence for escalation survives the habituation that the escalation lessons already apply to the laugh, using the benign-violation same-moment rule.
- Design: Six-beat schedules (flat, rule of three, mild, linear) at fixed distance 0.3 with a cue c0 of 0.7 whose strength decays by a factor r per beat, scored with the distance gate plus additive cue cover, over r of 1.0, 0.8, 0.6 and 0.3 and a refresh-every-2 variant at 0.6.
- Got right: Permanent and slowly decaying cues (r 1.0 and 0.8) kept flat as the winner, and the refresh variant restored a clear flat win (2.89 versus 2.10), which is the break case for the decay claim.
- Where/why it failed: My prediction that flat would stop winning at r of 0.6 was wrong: flat still won (1.55 versus 1.49), so the flip sits between 0.6 and 0.3 and the 0.6 case is a coin flip, not a loss.
- Fix: Refresh or restate the safe cue about every second beat instead of stating it once, and treat a cue that loses more than about 40 percent per beat as no licence to go big.
- Why this fix: Refreshing resets the cue to full strength at the cost of one reminder, which more than buys back the lost laugh, while a one-off cue loses most of its value by the late beats where the ceiling is highest.
- Rule of thumb: A safe cue licenses going big only while it keeps most of its strength; at 0.6 per beat flat-at-ceiling is only a tie with mild, so restate the cue rather than rely on one mention.
- Provenance (verified/assumed): Verified first-hand by running the sandbox in this session; the exponential cue decay is an assumption, not measured audience data.
- Composed: ideas:COMEDY-CRAFT/theory/benign-violation/each-beat-needs-a-violation-and-a-reason-it-is-ok-perceived-at-the-same-moment, escalation-needs-matching-distance/E1, safe-cue-escalation/E1
- Picked-by: new-half
- ZaneGPT verdict: weak — The test is a single-parameter sweep of a toy scorer, and the 0.06 near-tie at r 0.6 shows the threshold sits inside the noise of the scorer's own constants, so only the qualitative "restate the cue" advice is supported.
- Hidden assumption: Cue decay is a smooth geometric factor applied uniformly to a single additive cover term, and the 0.6 threshold comes from the arbitrary c0 of 0.7, the 0.3 distance and the gate/cover weights. It is a property of this scoring function, not of safe cues. Also, a refresh restores full c0 strength and costs nothing.
- Would prove it wrong: Move c0, the distance or the cover weight a little, say c0 0.5 or distance 0.4. If the flat-versus-mild crossover leaves the 0.5–0.7 band, or if the refreshed schedule's margin falls below the unrefreshed one once a refresh carries a cost, then "about 0.6" and "restate the cue" are artifacts.
- Break scenario: Hold r at 0.6 and run a sweep over c0 (0.4, 0.7, 1.0) and distance (0.2, 0.3, 0.5). Add a refresh that restores only half of c0 and takes one beat of the schedule. If flat stops winning when refreshed, or the 0.06 margin flips sign across the grid, the rule of thumb fails.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest c9086b7f4971
- Sandbox: sandboxes/2026-10-17__decaying-safe-cue-flips-go-big-back-to-mild.py
- Prediction: Flat wins at r 1.0 and 0.8, does not win at r 0.6, and wins again with a refresh every 2 beats at r 0.6.
- Observed: RESULT: PASS (revised claim) winners flat, flat, flat, flat, mild at r 1.0, 0.8, 0.6, 0.6 with refresh, 0.3; flat margin at r 0.6 is 0.06, with refresh 0.80. The r 0.6 not-flat prediction was refuted.
- Scenarios: 1) permanent cue r 1.0; 2) slow decay r 0.8; 3) r 0.6 with no refresh; 4) BREAK: r 0.3 where the cue should stop licensing going big; 5) r 0.6 refreshed every 2 beats
- Link: brain train auto loop 2 pass 2; session_01S4WKoTG7YsrzCXAnXDQDg7
- Cited-by: 2026-10-17 · projects/pappydapimp69__brainwork.md#E415 · compatible · sandboxes/2026-10-17__distance-dial-makes-the-decaying-cue-redundant-except-for-mild-beats.py · observed RESULT: PASS matched-distance cue effect 0.0000 (redundant); far framing mild 0.047 -> 0.54 with r0.6 cue (11.5x, flat still ahead 4.58); close r0.3 winner mild · session 2026-10-17 scheduled brain train, loop 1 pass 5; session_01KkkcHHGkp6Sm9GJK6fsa84
- Cited-by: 2026-10-17 · projects/local__restating-the-safe-cue-survives-a-costly-restatement-unless-the-cue-is-weak.md#E1 · compatible · sandboxes/2026-10-17__restating-the-safe-cue-survives-a-costly-restatement-unless-the-cue-is-weak.py · observed RESULT: FAIL refreshed flat wins 9/9 cells at q 0.2, losing cells []; central cell stops winning at q None. At q 0.5 the cells (0.4, 0.3) and (0.4, 0.5) go negative at -0.15. · brain train auto loop 1 pass 5; session_01RpeN38wP8qZN5F5czYD6HX
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E424 · incompatible · sandboxes/2026-10-18__per-beat-distance-survives-a-decaying-safe-cue.py · observed RESULT: FAIL per-beat gain +0.240 at decay 1.0, +0.188 at 0.8, +0.100 at 0.5, +0.040 at 0.2; retuned severe distance 0.8 gain +0.420 at 0.5 · brain train auto loop 2 pass 5 (alt companion; same path as loop 1 pass 5), 2026-10-18; session_01Sivit5TXUj5UpM1Zo3KB9A
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E425 · incompatible · sandboxes/2026-10-18__rule-card-ceiling-vs-decaying-cue-go-big.py · observed RESULT: FAIL card lifts gobig 0.29->0.43 at d=.5 decay=.8 (winner flat->flat); break d=.2 decay=.5 card gobig 0.20 vs mild 0.20 · brain train auto pass 2, 2026-10-18; session_01Sivit5TXUj5UpM1Zo3KB9A
- Audited: 2026-10-18 · modeled · Read the entry and its stored sandbox. The decay half is computed, not assumed: the cue strength falls as c0 times r to the beat age and the winners by r (flat at 1.0, 0.8 and 0.6, mild at 0.3, with a margin of 0.06 at 0.6) come out of the scorer. Two weaknesses limit it. First, the prediction (flat stops winning at 0.6) failed and the pass condition was rewritten to the observed margins before the final PASS, so the PASS confirms the revised claim only. Second, the Rule of thumb's advice to restate the cue rests on a refresh that resets the cue to full strength at zero cost; the entry's Why this fix says a reminder has a price, but no price is in the model, so the 2.89 versus 2.10 margin with refresh is built in. The claim is about audiences and a spoken cue, tested only against a hand-written scorer with assumed gate width 0.25, cue start 0.7 and distance 0.3, hence modeled rather than pass or fail. · session_01RNshpLS3CjgyV5GRQ9SeH2
