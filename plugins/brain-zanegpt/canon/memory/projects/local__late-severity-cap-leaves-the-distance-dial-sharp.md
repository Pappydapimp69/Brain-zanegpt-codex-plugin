# local/late-severity-cap-leaves-the-distance-dial-sharp — lessons

Project: local/late-severity-cap-leaves-the-distance-dial-sharp. Newest first.

---

## E1 — late severity cap leaves the distance dial sharp
- Date: 2026-10-17
- Project: local/late-severity-cap-leaves-the-distance-dial-sharp
- Tags: [comedy][humor][testing][sandbox]
- What: In a toy six-beat escalation a severity cap that takes effect late keeps the distance dial forgiving only while it lands by beat 3 (7 or more of 11 distances within 95 percent of best); landing at beat 4 leaves 4, and beats 5 and 6 leave 2 and 1, so the cap has to be stated before the gag escalates.
- Why built: To test the benign-violation requirement that cover and violation arrive at the same moment against the earlier finding that a mild severity cap flattens the distance dial.
- Design: The go-big schedule s equals i over 6 for the first L beats and a capped s equals 0.05 times i afterwards, scored with the mild-closeness and severe-distance cover functions at 11 distances, counting the distances within 95 percent of the best total for L from 0 to 6.
- Got right: L of 0 reproduced the earlier flat dial (9 of 11) and L of 6 reproduced the sharp go-big dial (1 of 11), so the sweep interpolates between two known results.
- Where/why it failed: My prediction that the window would fall to 4 or fewer by L of 3 was wrong: it was still 7, and the collapse comes at L of 4 (4 of 11), because early beats are mild enough for close framing to cover them.
- Fix: State the cap in the first half of the set; if it cannot come before beat 4 of 6, tune distance as if there were no cap.
- Why this fix: The early beats are only dangerous once they reach the severe zone, so cover needs to be in place before escalation crosses it, not at the first beat.
- Rule of thumb: A severity cap flattens the distance dial only if it lands before the escalation crosses the mild zone (here by beat 3 of 6); later than that, treat the dial as sharp again.
- Provenance (verified/assumed): Verified first-hand by running the sandbox in this session; the cover functions and the mild/severe split of 0.3 are assumptions carried over from the earlier toy, not audience data.
- Composed: ideas:COMEDY-CRAFT/theory/benign-violation/each-beat-needs-a-violation-and-a-reason-it-is-ok-perceived-at-the-same-moment, escalation-needs-matching-distance/E1, rule-card-severity-cap-flattens-the-distance-dial/E1
- Picked-by: new-half
- ZaneGPT verdict: weak — one toy run shows a cliff between L=3 and L=4, but the rule generalizes it to "treat the dial as sharp again" without any variation of schedule shape, tolerance, or cap strength, and the prediction was already wrong once at L=3.
- Hidden assumption: The "by beat 3 of 6" threshold is a property of escalation geometry in general, but it is fitted to one toy: a single linear schedule (s = i/6), a single cap slope (0.05·i), two specific cover functions, 11 distances, and a 95% tolerance, so a different cutoff could just as easily come out of any of those five choices.
- Would prove it wrong: Move the cutoff to beat 2 or beat 4 by changing the tolerance (90% or 99%), the distance grid (21 points) or the cap slope (0.02 or 0.10), and see "7 or more of 11" fail to line up at the same beat. Since L=3 already refuted your own prediction (7 observed against 4 or fewer predicted), a second miss of that size would show the rule describes this parameter set, not a law.
- Break scenario: Keep the toy but make the schedule convex (s = (i/6)² or an early spike at beat 1) and rerun L from 0 to 6 at 95% tolerance. If the cap at L=1 or 2 now leaves the window sharp, or a late cap at L=4 still leaves it flat, "land before the mild zone" is unsupported because the mild zone moves with the schedule. Also test non-monotone decay of the window: if L=3 → 4 isn't the only cliff, "by beat 3" is a coincidence of the grid.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest b7a60108298e
- Sandbox: sandboxes/2026-10-17__late-severity-cap-leaves-the-distance-dial-sharp.py
- Prediction: The window is at least 8 of 11 at L of 0 and falls to 4 or fewer by L of 3; L of 6 matches go-big at 2 or fewer.
- Observed: RESULT: PASS (revised claim) window by cap arrival beat L: 0:9, 1:9, 2:9, 3:7, 4:4, 5:2, 6:1. The L of 3 prediction (4 or fewer) was refuted; it was 7.
- Scenarios: 1) cap from the start (L 0); 2) cap from beats 1 to 3; 3) cap from beat 4 or 5; 4) BREAK: cap never arrives (L 6), which must behave like go-big
- Link: brain train auto loop 2 pass 1; session_01S4WKoTG7YsrzCXAnXDQDg7
- Cited-by: 2026-10-17 · projects/local__late-severity-cap-deadline-is-the-schedule-midpoint-not-the-mild-split.md#E1 · compatible · sandboxes/2026-10-17__late-severity-cap-deadline-is-the-schedule-midpoint-not-the-mild-split.py · observed RESULT: FAIL L* within 1 of n*split in 2/9 cells; monotone in split False; break window 7; L* [((6, 0.2), 3), ((6, 0.3), 3), ((6, 0.4), 2), ((9, 0.2), 4), ((9, 0.3), 4), ((9, 0.4), 4), ((12, 0.2), 6), ((12, 0.3), 6), ((12, 0.4), 6)] · brain train auto loop 2 pass 5; session_01RpeN38wP8qZN5F5czYD6HX
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E434 · incompatible · sandboxes/2026-10-18__late-cap-under-the-peaked-distance-gate.py · observed RESULT: PASS window by cap beat L (W 0.25) [1, 1, 1, 2, 2, 3, 3]; forgiving at L=3 False; W0.15 L0 1 vs W0.5 L0 2; best d at L=0 0.3 vs L=6 0.8. Cap level sweep at L 0: windows 1, 1, 2, 1 for cap 0.1, 0.3, 0.5, 0.8. · session_01RNshpLS3CjgyV5GRQ9SeH2
