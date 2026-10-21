# local/sandbox-hybrid-fallback-follows-mismatch-curve — lessons

Project: local/sandbox-hybrid-fallback-follows-mismatch-curve. Newest first.

---

## E1 — sandbox hybrid fallback follows mismatch curve
- Date: 2026-09-30
- Project: local/sandbox-hybrid-fallback-follows-mismatch-curve
- Tags: [ui][state][input][gamedev][testing]
- What: Sandbox showing the hint-first, re-resolve-on-invalid press policy is always valid and that its hint-match count is exactly the total minus the periodic mismatch curve, including the return at lag equal to one period.
- Why built: The hybrid fallback lesson and the full-cycle lag sweep lesson were single-source edges; test whether the hybrid's residual hint loss follows the sweep formula.
- Design: Square wave, 600 samples, P15/W5 and P20/W8, lag swept 0..P; action is a pure function of state; hybrid uses the lagged hint if it equals the current legal action, else re-resolves from live state. Counts valid actions and hint-match.
- Got right: Valid is 600/600 at every lag for both waves. Hint-match is 600 minus mismatch: P15/W5 falls 520,440,360,280,200 to a plateau of 200 over lags 5-10, then rises back to 600 at lag 15; P20/W8 falls 60 per step to a 120 plateau over lags 8-12 and returns to 600 at lag 20.
- Where/why it failed: Hint-match is not monotonic in lag, so a single lag sample (such as lag 1, 2, 4 only) understates the recovery at whole cycles and can mislead tuning of a hint buffer.
- Fix: Characterize the hybrid by sweeping lag across a full period; treat frozen-hint invalid count as the exact residual gap between hint-match and total.
- Why this fix: The re-resolve branch absorbs every invalid hint, so hint loss equals the invalid count, which is the mismatch curve already known in closed form.
- Rule of thumb: With a hint-first plus re-resolve policy, validity is free and hint fidelity equals N minus 2*(N/P)*min(lag,W,P-W,P-lag); sweep lag 0..P before choosing a buffer depth.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; observed numbers above, valid 600/600 for all 42 lag points and hint-match plus invalid equal to 600 at each.
- Composed: sandbox-combined-action-resolver-hybrid-fallback/E1, sandbox-combined-action-resolver-hint-lag-full-cycle-sweep/E1
- Link: session

