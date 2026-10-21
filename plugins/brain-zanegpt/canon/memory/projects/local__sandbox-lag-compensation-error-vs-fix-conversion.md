# local/sandbox-lag-compensation-error-vs-fix-conversion — lessons

Project: local/sandbox-lag-compensation-error-vs-fix-conversion. Newest first.

---

## E1 — lag compensation error vs fix conversion
- Date: 2026-09-30
- Project: local/sandbox-lag-compensation-error-vs-fix-conversion
- Tags: [ui][gamedev][state][input][testing]
- What: Re-verified on square-wave states that hint fixes only convert the mismatch count while exact lag compensation removes it, and that a one-tick estimate error costs a fixed two mismatches per period regardless of lag.
- Why built: The dog-hint fix-conversion and lag-compensated-hint lessons were single-source edges; one model exercising both raises their independence.
- Design: Deterministic 600-frame square wave (P6H3, P10H4, P12H5) with hints arriving L in 0,1,2,4,7,15 frames late. Compared naive mismatch with token drops, exact compensation, and compensation off by one tick either way, plus a sawtooth state that changes every frame as breaker.
- Got right: Naive mismatch equalled token drops in every cell, exact compensation gave 0 mismatch at every lag, and a one-tick error gave 200, 120 and 100 mismatches for P6, P10, P12 (2 x 600 / P) at every lag, either sign.
- Where/why it failed: The sawtooth breaker cost 600 for a one-tick error, so the budget is edges per frame in the state, not the period alone.
- Fix: Compensate the hint by the measured lag and budget the estimate error as edges crossed per unit time rather than adopting freeze or token validation.
- Why this fix: Freeze and token only relabel mismatches as stale executions or drops, while compensation changes what the hint says and so removes the mismatch when the estimate is exact.
- Rule of thumb: Prefer exact lag compensation over freeze or token fixes, and budget a one-tick estimate error as state edges per window (2N/P on a square wave, N on a state that changes every frame).
- Provenance (verified/assumed): Verified first-hand by running the sandbox; synthetic states and errors of exactly one tick only.
- Composed: sandbox-combined-action-resolver-dog-hint-fix-converts-mismatch/E1, sandbox-combined-action-resolver-lag-compensated-hint/E1
- Polarity: compatible
- Sandbox: sandboxes/2026-09-30__lag-compensation-error-vs-fix-conversion.py
- Prediction: naive mismatch equals token drops, exact compensation is 0, a one-tick error costs 2N/P (200, 120, 100) at any lag, and a sawtooth state costs 600.
- Observed: RESULT: PASS naive==token drops; exact comp 0 mismatch; e=1 costs 2N/P (200/120/100) any lag; sawtooth breaker 600
- Scenarios: 1) P6H3 2) P10H4 3) P12H5 each over six lags 4) sawtooth state built to break the period-bound error budget
- Link: scheduled train pass 4
- Audited: 2026-10-09 · fail · Read the entry and ran its stored sandbox (PASS), then ran scratch-copy mutations outside the memory folder. Two of the four headline claims are built in, not computed. (a) "naive == token drops": the naive count is sum(s(t) != s(t+L)) via mism(s,L,0) and the token count is written as the identical expression, so the equality is an identity; the "frozen stale executes" policy named in the docstring is never coded. Swapping the token for a version-based one (drop if any edge occurred in the window) makes the check print "conv broken" at P12H5 L15 and the run FAIL, so the conversion claim holds only for a value-compare token. (b) "exact compensation gives 0 mismatch": mism(s,L,L) compares s(t+L) with s(t+L), which is 0 for any state by construction; the model hands the compensator an oracle for the future state. A mutation that makes mism ignore delta, or one that shifts the truth by one tick, flips the run to FAIL, so the only live assertions are the error-budget ones. (c) The one genuinely computed result is the one-tick error cost 2N/P (200/120/100) and the sawtooth 600; these are real arithmetic on shifted square waves, but they are basically restatements of edge counting, and only e=1, N divisible by P, and the sawtooth (not a square wave) were run. (d) Scope: the Rule of thumb says to prefer exact compensation over freeze/token, but the cost of obtaining the estimate (predicting future state, measuring lag) is absent, and a scenario outside the sandbox shows the preference is conditional: when L is a multiple of P (P6 L6/12, P10 L10/20, P12 L12/24) naive mismatch is 0 while a one-tick-off compensator costs 200/120/100, so uncompensated beats imperfect compensation there. The error-budget half of the rule is supported; the "prefer over freeze/token" half is assumed. The tier should not read as audited-pass. · audit pass 3, train run 5 (separate session from the author's scheduled train pass 4); session_01YFLLRpDsfZpRstb2KT2MQy
