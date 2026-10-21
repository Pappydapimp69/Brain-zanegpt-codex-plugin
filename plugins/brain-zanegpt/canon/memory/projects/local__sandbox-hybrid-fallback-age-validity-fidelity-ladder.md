# local/sandbox-hybrid-fallback-age-validity-fidelity-ladder — lessons

Project: local/sandbox-hybrid-fallback-age-validity-fidelity-ladder. Newest first.

---

## E1 — hybrid fallback age validity fidelity ladder
- Date: 2026-09-30
- Project: local/sandbox-hybrid-fallback-age-validity-fidelity-ladder
- Tags: [ui][input][state][gamedev][testing]
- What: Independently rebuilt the hint-first-with-fallback press policy and reproduced its match counts of 560/520/440 against 520/440/280 for pure re-resolve at lag 1/2/4.
- Why built: Re-verify the single-source edge between the age-plus-validity combined policy and the hybrid fallback resolver from a new angle.
- Design: N=600, P=15, W=5 legality window; hint is the state lag ticks ago; pure counts a match only when hint equals truth; hybrid keeps the hint unless it says yes while the live state is illegal; age-plus-validity with threshold 0 re-derives on any lag.
- Got right: pure 520/440/280 and hybrid 560/520/440 reproduced exactly, and the hybrid gap to 600 equals the frozen-hint invalid count 40/80/160, i.e. 40*lag.
- Where/why it failed: Nothing contradicted the recorded numbers. The age-plus-validity comparison is a weak result: with threshold 0 it keeps 0 hints at any lag above 0 by construction, so it shows only that this policy sits at the bottom of the ladder, not a measured tradeoff.
- Fix: Read the ladder as hybrid above pure re-resolve above age-plus-validity for hint fidelity, with all three rule-valid; test age-plus-validity with a nonzero threshold before claiming more.
- Why this fix: The 40*lag gap matches the one-sided trailing-edge invalid count, so the hybrid position follows from the same formula as the age-gate entries.
- Rule of thumb: Hint fidelity ladder at lag 1/2/4 on P15W5 is hybrid 560/520/440, pure re-resolve 520/440/280; the hybrid shortfall from 600 is exactly 40*lag, so use it to predict fallback frequency before shipping.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; counts are copied from the run. The age-plus-validity row is true by construction at threshold 0 and is flagged as such.
- Composed: local__age-cutoff-roll-up/E1, sandbox-combined-action-resolver-hybrid-fallback/E1
- Polarity: compatible
- Sandbox: sandboxes/2026-09-30__hybrid-fallback-age-validity-fidelity-ladder.py
- Prediction: pure 520/440/280, hybrid 560/520/440, hybrid gap 40*lag, age-plus-validity keeps 0 hints at lag above 0.
- Observed: RESULT: PASS pure 520/440/280, hybrid 560/520/440, gap=frozen invalid=40*lag, age+validity keeps 0 hints at lag>0
- Scenarios: 1) lag 1; 2) lag 2; 3) lag 4, the widest gap, built to break the linear 40*lag claim.
- Link: scheduled brain train pass 4

