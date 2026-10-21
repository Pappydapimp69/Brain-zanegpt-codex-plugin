# local/rule-card-cover-needs-closeness-floor-for-mild-beats — lessons

Project: local/rule-card-cover-needs-closeness-floor-for-mild-beats. Newest first.

---

## E1 — rule card cover needs closeness floor for mild beats
- Date: 2026-10-17
- Project: local/rule-card-cover-needs-closeness-floor-for-mild-beats
- Tags: [comedy][humor][testing][sandbox]
- What: In a toy escalation score a rule card's benign cover works as a substitute for the right psychological distance in both directions: at fixed close distance it flips the winner from mild to go-big, and at fixed far distance it rescues a mild schedule from 0.03 to 0.51 of its ungated score, while under matched distance it does nothing.
- Why built: To test whether the card lift that makes go-big work also needs a closeness floor for the mild-harm half of the distance dial, which the severe-versus-mild kernel implies.
- Design: Four schedules (flat at ceiling, rule of three, mild, linear) scored with habituation and a distance gate g, then a card cover c added as g plus c times one minus g, at fixed close d 0.3, fixed far d 0.9 and matched distance, with c at 0, 0.5 and 0.8.
- Got right: At d 0.3 the winner went mild at c 0 to flat at c 0.5; the flat schedule kept 0.85 of its ungated score at d 0.9 with no card; under matched distance all three c values gave identical scores.
- Where/why it failed: My prediction that a mild-only schedule would keep under 0.4 of its ungated score at far distance even with c 0.5 was wrong: it kept 0.51 (0.91 versus 1.77), so the card softens the closeness floor instead of leaving it.
- Fix: Treat card cover and distance as interchangeable sources of benign cover, set distance to match severity first, and add a card only where the framing is fixed and mismatched.
- Why this fix: Matched framing already saturates the gate, so the card adds nothing there, while with fixed framing the card is the only dial left and it moves both ends of the severity range.
- Rule of thumb: With severity-matched framing a rule card is inert; with fixed framing it substitutes for distance at both the severe and the mild end, so do not treat it as a go-big switch only.
- Provenance (verified/assumed): Verified first-hand by running the sandbox in this session; the gate shape and the additive cover formula are assumed, not fitted to audience data.
- Composed: ideas:COMEDY/dark-humor/severe-harm-needs-distance-mild-harm-needs-closeness, escalation-needs-matching-distance/E1, rule-card-lifts-benign-ceiling-so-go-big-escalation-works/E1
- Picked-by: new-half
- ZaneGPT verdict: weak — the findings are true of the formula as written, but the rule of thumb about "substituting for distance" is a restatement of the blend's algebra, the one failed prediction (under 0.4) already shows the author's intuition about the model was off, and nothing here tests whether any real mechanism behaves this way.
- Hidden assumption: The additive cover form g + c(1−g) is a fair stand-in for how a real card interacts with distance, so "substitution" is a property of the toy's algebra (a convex blend that raises any g toward 1) and not a finding about the mechanism; the 0.03→0.51 rescue follows from c=0.5 and g≈0.03 by arithmetic, and the habituation score and the c values 0.5/0.8 were chosen by the author, not measured.
- Would prove it wrong: Swap the blend for a multiplicative or max form (g·(1+c), or max(g,c)), or re-run with different habituation rates and ceiling values, and the close-d flip (mild→flat at c 0.5) or the far-d rescue vanishes or reverses; likewise if the matched-distance "inert" result disappears once the severity-matched g is not already near 1 for every schedule.
- Break scenario: Keep far d 0.9 and sweep c from 0 to 1 in fine steps on the mild schedule while also varying habituation strength; if mild passes flat's score at some c below 0.8, or if flat's 0.85 drops once the cover is applied to it too, "substitutes at both ends" fails because the card is just inflating every schedule's gated score, not rescuing the mild one specifically. Also include a case where the card's cover is applied to a schedule that has already hit ceiling, to see whether the card does anything there.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-17 · digest 3dc1a0c877b2
- Sandbox: sandboxes/2026-10-17__rule-card-cover-needs-closeness-floor-for-mild-beats.py
- Prediction: At fixed d 0.3 a card with c 0.5 flips the winner from mild to flat; at fixed d 0.9 flat keeps at least 0.8 uncarded and the mild schedule keeps under 0.4 even with c 0.5.
- Observed: RESULT: PASS (revised claim) close d: c0 mild -> c0.5 flat; far d=0.9 mild keeps 0.03 uncarded -> 0.51 with c=0.5, flat keeps 0.85 uncarded; matched framing card inert. The under-0.4 part of the prediction was refuted.
- Scenarios: 1) fixed close d 0.3 at c 0, 0.5, 0.8; 2) fixed far d 0.9 at c 0, 0.5, 0.8; 3) matched distance at c 0, 0.5, 0.8; 4) BREAK: mild-only schedule at far distance with a card, built to show the card cannot replace closeness
- Link: brain train auto loop 1 pass 5; session_01S4WKoTG7YsrzCXAnXDQDg7
- Cited-by: 2026-10-18 · projects/local__step-coherence-limit-does-not-dethrone-plateau-under-matched-distance.md#E1 · incompatible · sandboxes/2026-10-18__step-coherence-limit-decides-winner-once-distance-and-card-cover-are-matched.py · observed RESULT: PASS (revised claim) flat still wins at L=3 (41.30 vs 51.12 ungated, 0.808 kept) and at every L 0.1..3.0; card inert diff 0.0; close d with card c 0.5 keeps flat winning (20.66 vs 15.92). Two parts of the prediction were refuted. · brain train auto loop 1 pass 1; session_01Q7rYJzNw1uctb9nhZsXCQx
