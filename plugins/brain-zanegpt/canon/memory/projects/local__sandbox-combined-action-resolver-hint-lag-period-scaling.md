# local/sandbox-combined-action-resolver-hint-lag-period-scaling — lessons

Project: local/sandbox-combined-action-resolver-hint-lag-period-scaling. Newest first.

---

## E1 — sandbox combined action resolver hint lag period scaling
- Date: 2026-09-29
- Project: local/sandbox-combined-action-resolver-hint-lag-period-scaling
- Tags: [ui][gamedev][state][input][testing]
- What: Independent event-driven re-check of the hint-to-press lag mismatch, sweeping both the lag and the state-change period instead of only the period-5 cycle.
- Why built: Both prior lessons were single-source on a period-5 cycle; a new angle (second period, per-policy counters) tests whether the mismatch law is general or a period-5 artifact.
- Design: Deterministic model, no RNG or real timing: state = (t // period) % 4 over 600 ticks; the hint is read at t, the press lands at t+lag; three policies (re-resolve at press, token-validate, frozen hint) counted separately. Periods 5 and 7, lags 0/1/2/4.
- Got right: Period 5 reproduces the recorded numbers exactly (0/120/240/480 mismatches; token policy drops the same count, frozen policy executes that many stale actions, re-resolve drops none but disagrees with the shown hint).
- Where/why it failed: The law is not fixed at 120 per lag step: at period 7 the counts are 0/85/170/342, so the mismatch rate scales with lag divided by period, with floor rounding (lag 2 gives 170 vs the 171 continuous estimate).
- Fix: Predict mismatch as about N times lag over period (capped at N when lag reaches the period) and sweep the period as well as the lag in tests; the cheapest cure remains shrinking lag or lengthening the state period.
- Why this fix: Mismatch is the fraction of ticks where a state boundary falls inside the lag window, so it is linear in lag and inverse in period; both knobs cut it and the conversion to drops or stale executions is one to one.
- Rule of thumb: Budget hint staleness as lag/period of presses, and note that every policy (freeze, token, re-resolve) only relabels those presses; assert the rate across at least two periods.
- Provenance (verified/assumed): Verified first-hand by running the sandbox at ~/brainwork/sb/s2.py; the numbers above are its observed output. Real frame timing was not modelled.
- Composed: sandbox-combined-action-resolver-dog-hint-fix-converts-mismatch/E1, sandbox-combined-action-resolver-dog-stale-hint-press-lag/E1
- Link: scheduled training pass 1, session_01NomGdXQGCMAr6o2dzv6Tp2
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-dog-hint-fix-converts-mismatch-cycle-sweep.md#E1 · compatible · no sandbox · session (scheduled brain train pass 3)
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-lag-compensated-hint.md#E1 · compatible · no sandbox · session_01PerucmEYi4RaszepKs6L7c
- Cited-by: 2026-09-30 · projects/pappydapimp69__brainwork.md#E3 · compatible · no sandbox · session https://claude.ai/code/session_01F9aR1eawRNLN9c3sNEJ6Sd
