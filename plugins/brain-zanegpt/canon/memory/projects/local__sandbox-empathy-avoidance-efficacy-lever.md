# local/sandbox-empathy-avoidance-efficacy-lever — lessons

Project: local/sandbox-empathy-avoidance-efficacy-lever. Newest first.

---

## E1 — empathy avoidance efficacy feedback lever hot state and cost ceiling
- Date: 2026-10-11
- Project: local/sandbox-empathy-avoidance-efficacy-lever
- Tags: [empathy][motivation][simulation][method]
- What: A deterministic cost-benefit model of the empathy selection task: 100 agents with evenly spaced effort costs choose the empathy deck when believed efficacy minus cost is positive, tested under control, false efficacy feedback, honest feedback, a cost-ceiling population and a hot-state cost shift.
- Why built: The EMPATHY motivation kernel says people avoid empathy because it feels costly and ineffective, and that raising perceived efficacy removed the avoidance; I wanted to see where that lever stops working.
- Design: Choice rule is belief*benefit - cost > 0 with benefit 1.0, baseline belief 0.355 so control share matches the kernel's 35.5 percent. Levers: belief raised to 0.51 (false feedback, true accuracy held at 0.30), belief set to true accuracy (honest feedback), an additive moral term of the same size, a 40 percent overloaded subpopulation whose cost exceeds the benefit, and a calm-forecast versus hot-state cost shift of 0.25 taken from the hot-cold gap kernel.
- Got right: Control gave 0.35 and false feedback 0.51, mirroring the reported .33 to .51 rise. Honest feedback lowered the share to 0.30, because real accuracy sat under the prior belief, so the lever works through belief and not through skill.
- Where/why it failed: Pre-registered breakers held rather than failed, but one expectation was wrong: I expected exhortation to differ from the efficacy lever, yet an equal-size moral term gave the identical 0.51, so the model cannot separate them in calm conditions; the only distinguishing evidence is the kernel's own data.
- Fix: State the lever as conditional: perceived efficacy raises empathy choice only for agents whose cost is below benefit (overloaded subpopulation moved 0.35 to 0.60, never to 1.0), and a calm-state forecast of the effect overstates it (forecast 0.51 versus hot-state 0.26).
- Why this fix: Both limits come from the same threshold structure, so naming them in the claim stops a feedback-based design from promising more than the cost term allows.
- Rule of thumb: In this model efficacy feedback lifts empathy choice only up to the share of people whose cost is under the benefit (40 percent overloaded stayed out) and a cold-state forecast of the lift roughly halves under hot-state cost (0.51 to 0.26), so lower the cost or cap the load too, and test the intervention in the loaded state.
- Provenance (verified/assumed): Verified first-hand by running the saved sandbox, 7 of 7 checks pass with deterministic output; the model's threshold choice rule and cost distribution are my own assumptions, not human data.
- Composed: ideas:EMPATHY/motivation/people-avoid-empathy-because-it-feels-costly-and-ineffective-not-because-they-cannot-do-it, ideas:EMPATHY/self-prediction/you-cannot-model-your-own-aroused-self-from-a-calm-state-let-alone-someone-elses, sandbox-empathy-map-density-hides-evidence-gap/E1
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__empathy-avoidance-efficacy-feedback-lever-hot-state-and-cost-ceiling.py
- Prediction: Control share 0.35 plus or minus 0.02; false feedback 0.51 plus or minus 0.02; honest feedback below control; with 40 percent overloaded agents the share stays at or under 0.60 at maximum efficacy; hot-state share at least 0.2 below the calm forecast.
- Observed: RESULT: PASS 7/7 checks; control 0.35, false-feedback 0.51, honest 0.30, overloaded 0.35->0.60, calm-forecast 0.51 vs hot 0.26
- Scenarios: 1) control; 2) false feedback with true accuracy fixed; 3) honest feedback; 4) BREAK: overloaded subpopulation at maximum efficacy; 5) BREAK: calm forecast versus hot-state cost; 6) exhortation of equal size, calm and hot
- Link: brain train auto loop 1 pass 1 (kernel); session_012QzNKQEGhirAziWZ2Cg9Tj

