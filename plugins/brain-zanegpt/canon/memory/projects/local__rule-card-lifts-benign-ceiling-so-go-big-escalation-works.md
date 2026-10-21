# local/rule-card-lifts-benign-ceiling-so-go-big-escalation-works — lessons

Project: local/rule-card-lifts-benign-ceiling-so-go-big-escalation-works. Newest first.

---

## E1 — rule card lifts benign ceiling so go big escalation works
- Date: 2026-10-17
- Project: local/rule-card-lifts-benign-ceiling-so-go-big-escalation-works
- Tags: [comedy][humor][testing][sandbox]
- What: Toy model of a six-beat gag escalation where each beat is funny only up to its benign cover, comparing a go-big and a mild schedule with no rule card, a Jones-style rule card that adds benign cover, and a strict card that also caps violation.
- Why built: The benign-violation kernel needs violation and a reason it is ok at the same moment, the matching-distance lesson says go-big fails at fixed grounded distance, and the rule-card kernel says the lead is humiliated more than harmed; unknown whether the card is what supplies the distance.
- Design: Laugh per beat is v when v is at most b, else v minus three times the excess clipped at zero; go-big violation climbs 1/6 to 1, mild 1/12 to 1/2; benign cover 0.40 without a card, 0.70 with the card (an added 0.30 for sympathy and humiliation-not-harm), and the strict card keeps 0.70 but caps violation at 0.30.
- Got right: Without a card mild won (1.40 versus 0.70 for go-big); with the card go-big won (2.20 versus 1.75), so the card restores escalation by raising cover; the strict card still let go-big win but fell to 1.67, below the plain card.
- Where/why it failed: My written totals were wrong (I predicted 1.25 versus 1.75 and 3.00 versus 1.75 by hand) though the ordering held; and the 0.30 benign gain is an assumed constant, not measured, so the size of the lift is not evidence.
- Fix: Treat the rule card as a benign-cover source and check, per schedule, that the card's cover meets the schedule's peak violation, and do not over-constrain violation as a way to get safety.
- Why this fix: The laugh only drops once violation passes cover, so lifting cover is what keeps a big schedule safe, while capping violation removes the payoff the schedule was built for.
- Rule of thumb: In this toy model a rule card that adds benign cover flipped the winner from mild (1.40 versus 0.70) to go-big (2.20 versus 1.75), but capping violation as well cost 0.53 of the go-big total; the size of the lift depends on an assumed cover constant, so measure it in real material.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the laugh function and the 0.30 cover constant are assumed, there is no audience data.
- Composed: ideas:COMEDY-CRAFT/theory/benign-violation, escalation-needs-matching-distance/E1, ideas:COMEDY-CRAFT/gag-world/write-the-rules-before-the-gags
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-17__rule-card-lifts-benign-ceiling-so-go-big-escalation-works.py
- Prediction: Ordering only (totals were mis-computed): mild beats go-big without a card, go-big beats mild with the card, and the strict card scores below the plain card. Assumption: the card raises cover without capping violation.
- Observed: RESULT: PASS no card big 0.70 vs mild 1.40; card big 2.20 vs mild 1.75; strict card big 1.67
- Scenarios: 1) no card at b 0.40; 2) rule card at b 0.70; 3) strict card with violation capped at 0.30, built to break the card-always-helps idea.
- Link: scheduled brain train auto loop 2 pass 2 (edge); session_011LtaNZCrPYhhAtwJpZ1y8i
- Cited-by: 2026-10-17 · projects/local__rule-card-cover-needs-closeness-floor-for-mild-beats.md#E1 · compatible · sandboxes/2026-10-17__rule-card-cover-needs-closeness-floor-for-mild-beats.py · observed RESULT: PASS (revised claim) close d: c0 mild -> c0.5 flat; far d=0.9 mild keeps 0.03 uncarded -> 0.51 with c=0.5, flat keeps 0.85 uncarded; matched framing card inert. The under-0.4 part of the prediction was refuted. · brain train auto loop 1 pass 5; session_01S4WKoTG7YsrzCXAnXDQDg7
- Cited-by: 2026-10-18 · projects/pappydapimp69__brainwork.md#E421 · incompatible · sandboxes/2026-10-18__benign-cover-sources-saturate-when-stacked.py · observed RESULT: FAIL cue and card interchangeable=True; second source adds 53% of the first; go-big flips from losing to winning once covered; far-framing extra cover adds 0.00 · brain train auto loop 2 pass 1, 2026-10-18; session_01Sivit5TXUj5UpM1Zo3KB9A
