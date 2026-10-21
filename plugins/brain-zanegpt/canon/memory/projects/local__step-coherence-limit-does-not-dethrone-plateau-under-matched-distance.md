# local/step-coherence-limit-does-not-dethrone-plateau-under-matched-distance — lessons

Project: local/step-coherence-limit-does-not-dethrone-plateau-under-matched-distance. Newest first.

---

## E1 — step coherence limit does not dethrone plateau under matched distance
- Date: 2026-10-18
- Project: local/step-coherence-limit-does-not-dethrone-plateau-under-matched-distance
- Tags: [comedy][humor][testing][sandbox]
- What: In a toy escalation score with a distance gate, a rule-card cover and a step-coherence limit all active, the flat-at-ceiling schedule still wins under matched distance at every coherence limit from 3.0 down to 0.1 (41.30 versus 24.45 for linear), so the coherence limit does not take over once distance is matched.
- Why built: Train pick joining the matching-distance lesson and the closeness-floor card lesson with the escalation lesson that said escalating needs a step-coherence limit, to see whether that limit decides the winner once the gate is saturated and the card is inert.
- Design: Four schedules (flat, linear, rule of three, mild), six beats, ceiling 10, habituation exp(-0.2 X), gate exp(-((d - I/C)/0.25)^2), card cover g + c(1-g), and a per-beat jump penalty exp(-((jump-L)/3)^2) for jumps over L. Cases are matched, fixed close d 0.3, with and without card and coherence, plus a sweep of L.
- Got right: The card stayed exactly inert under matched distance (difference 0.0), and at fixed close d 0.3 the card flipped the winner from mild to flat, and that flip survived the coherence term (flat 20.66 versus 15.92 for linear).
- Where/why it failed: My prediction that coherence would make a ramp beat flat under matched distance was wrong: flat only lost a factor of 0.808 (41.30 versus 51.12 ungated) because a plateau schedule pays the jump cost once, on beat 1, and no L down to 0.1 changed the winner.
- Fix: Treat the coherence limit as a penalty on the number of big jumps, not on the ceiling itself, so test it on schedules that jump repeatedly before concluding a ramp is needed.
- Why this fix: A single entry jump is amortized over five more beats at the ceiling, so only schedules that keep re-escalating pay the penalty each time.
- Rule of thumb: In this toy model a single-step coherence penalty cannot dethrone a go-big plateau under matched distance; do not rely on a coherence limit to justify a ramp unless the schedule has repeated large jumps.
- Provenance (verified/assumed): Verified first-hand by running the sandbox in this session; the penalty shape, the gate width and the card formula are assumed, not fitted to audience data.
- Composed: escalation-needs-matching-distance/E1, rule-card-cover-needs-closeness-floor-for-mild-beats/E1, sandbox-comedy-escalation/E1
- Picked-by: new-half
- ZaneGPT verdict: weak — Flat winning at every L is a result about one penalty form with one width and one gate setting, and the card test shows 0.0 only because the card was never an active variable, so the rule of thumb outruns the evidence.
- Hidden assumption: The matched-distance gate holds each schedule at its own optimal distance, so the 0.808 gate retention in flat's 41.30 is a fair handicap. The rule also assumes a per-beat jump penalty, which only touches jumps above L, is the right model of coherence. Flat has one jump, from start to ceiling. The rule would not survive any model in which big jumps cost more than a single beat of penalty.
- Would prove it wrong: Any L at or below 3.0 where linear or rule-of-three scores above flat under matched distance, with the gate and card on. The sweep stops at L=0.1, and the penalty has a 3-unit width, so a flip may only show up for a different width, a cumulative penalty, or more beats. Flat's lead is also narrow in places, 41.30 against 51.12 ungated, so a small change to the gate width of 0.25 or the habituation rate of 0.2 could reverse it.
- Break scenario: Run the same sweep with the penalty width cut from 3 to 1, then to 0.5. Set it to also fire on the first beat's jump from zero, and make that penalty cumulative across beats. Hold the matched distance and the card at c 0.8. Repeat at 12 beats and with gate widths of 0.15 and 0.5. If flat still wins in every cell, the rule is robust. If it loses in any cell, the rule only covers the tuned setup.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-18 · digest 08dcf16d7928
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-18__step-coherence-limit-decides-winner-once-distance-and-card-cover-are-matched.py
- Prediction: Under matched distance with a coherence limit of 3 a ramp (linear or three) beats flat; the card at c 0.8 changes matched scores by under 1e-9; at fixed close d with c 0.5 and coherence the flat schedule does not win.
- Observed: RESULT: PASS (revised claim) flat still wins at L=3 (41.30 vs 51.12 ungated, 0.808 kept) and at every L 0.1..3.0; card inert diff 0.0; close d with card c 0.5 keeps flat winning (20.66 vs 15.92). Two parts of the prediction were refuted.
- Scenarios: 1) matched distance, no coherence; 2) matched distance, coherence L=3; 3) matched with card c 0.8; 4) fixed close d 0.3 no card with coherence; 5) fixed close d with card c 0.5, with and without coherence; 6) BREAK: sweep L from 3.0 to 0.1 hunting for a flip to a ramp
- Link: brain train auto loop 1 pass 1; session_01Q7rYJzNw1uctb9nhZsXCQx

