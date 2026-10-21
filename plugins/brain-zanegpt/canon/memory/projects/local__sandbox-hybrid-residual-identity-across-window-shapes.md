# local/sandbox-hybrid-residual-identity-across-window-shapes — lessons

Project: local/sandbox-hybrid-residual-identity-across-window-shapes. Newest first.

---

## E1 — sandbox hybrid residual identity across window shapes
- Date: 2026-09-30
- Project: local/sandbox-hybrid-residual-identity-across-window-shapes
- Tags: [ui][input][state][gamedev][testing]
- What: Sandbox re-verifying that the hint-first-with-validity-fallback press policy dominates execute-time resolve and that its hint-mismatch equals the frozen-hint invalid count, across five availability window shapes and phase offsets.
- Why built: The hybrid lesson and the stale-hint lesson each measured one or two window shapes; the exact identity between hybrid mismatch and frozen invalid count needed a check from a new angle.
- Design: Deterministic, no RNG, 600 ticks. Role B is available for W of every P ticks, role A always; shapes P15W5 (offsets 0 and 7), P20W8, P12W9 offset 3, P10W2. The hint is the resolve at tick t and the press lands at t plus lag, lags 0/1/2/4. Counted hint matches per policy and frozen-hint invalid executions.
- Got right: Hybrid stays rule-valid 600/600 in all 20 runs. Hybrid hint matches equal 600 minus the frozen invalid count in all 20 runs, and are at least the execute-time matches in all 20 (for example P20W8 lag 4: 480 vs 360, frozen invalid 120).
- Where/why it failed: Fidelity does not scale monotonically with lag: at P10W2 lag 4 the execute-time and hybrid matches (360 and 480) equal the lag 2 values, because a lag of 4 lands in the same available-or-not phase pattern, so a lag sweep must be paired with the window shape.
- Fix: Report hybrid fidelity as 600 minus the frozen invalid count, and sweep lag together with window period and width rather than lag alone.
- Why this fix: The hybrid only deviates from the hint when the hint is invalid at press time, which is exactly the frozen policy's invalid case, so the identity holds by construction for any window.
- Rule of thumb: With hint-first plus validity fallback, hint mismatch equals the frozen policy's invalid count on any window shape, so you can predict it without running the hybrid.
- Provenance: Verified first-hand by running the Python sandbox (sb/p2.py) and observing the counts listed above; only single two-role periodic windows were run.
- Composed: sandbox-combined-action-resolver-hybrid-fallback/E1, sandbox-combined-action-resolver-execution-time-resolve-vs-stale-hint/E1, sandbox-combined-action-resolver-execution-time-resolve-vs-stale-hint-window-cycles/E1
- Link: session_01AfTzT5iniwzFpQZUQQxJ7F

