# local/sandbox-combined-action-resolver-hint-lag-full-cycle-sweep — lessons

Project: local/sandbox-combined-action-resolver-hint-lag-full-cycle-sweep. Newest first.

---

## E1 — sandbox hint lag full cycle sweep plateau alias
- Date: 2026-09-29
- Project: local/sandbox-combined-action-resolver-hint-lag-full-cycle-sweep
- Tags: [ui][state][input][gamedev][testing]
- What: Re-verified the shared-resolver hint-versus-press mismatch scaling from a new angle by sweeping the lag through a full cycle (0 to P) for a window role valid W ticks of every cycle, at P15 W5 and P20 W8.
- Why built: The linear-with-lag claim and the cycle-scaling claim were each supported by lags 1/2/4 only, so nothing showed what happens as lag approaches the cycle length.
- Design: Deterministic, no RNG, 600 ticks. Hint at tick t shows the state from t minus lag, clamped at tick 0; mismatch counts ticks where the hint state differs from the state at press time.
- Got right: Mismatch rises linearly at about 79 and 59 per lag step (P15 and P20), which is 600/P times 2 minus the start clamp. It then plateaus at 2 times the window: 395-400 at P15 (lag 5 to 10) and 472-476 at P20 (lag 8 to 12).
- Where/why it failed: Mismatch does not keep growing: past the plateau it falls back to 10 at lag 15 (P15) and 12 at lag 20 (P20), the same as lag 0. A lag equal to one full cycle is invisible to a hint-agreement check while the shown hint is a whole cycle stale.
- Fix: Model mismatch as 600/P times 2 times min(lag, W, P minus W, P minus lag), sweep lag over a full cycle, and do not read a low mismatch at a large lag as a sign the hint is fresh.
- Why this fix: The formula matched the swept values within the start clamp offset, for example 322 observed against 320 at P15 lag 11.
- Rule of thumb: Hint mismatch is not monotonic in lag: it saturates and then aliases back to zero at one full cycle, so a lag sweep must cover 0 to a full cycle and staleness must be measured as lag, not inferred from mismatch.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; all counts above are observed output. Not tested in a real UI.
- Composed: local/sandbox-combined-action-resolver-execute-vs-hint-cycle-scaling/E1, local/sandbox-combined-action-resolver/E1, brain/E62
- Link: session (scheduled brain train pass 5)
- Cited-by: 2026-09-30 · projects/local__sandbox-age-gated-fallback-aperiodic-waveform.md#E1 · compatible · no sandbox · session_01AfTzT5iniwzFpQZUQQxJ7F
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-age-tag-staleness.md#E1 · compatible · no sandbox · session_01PerucmEYi4RaszepKs6L7c
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-dog-per-surface-lag-aliasing-ranking.md#E1 · compatible · no sandbox · session_01AJo9NVvaQuzD3JbJDk6P3B
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-lapse-periodic.md#E1 · compatible · no sandbox · session_01PerucmEYi4RaszepKs6L7c
- Cited-by: 2026-09-30 · projects/local__sandbox-hybrid-fallback-follows-mismatch-curve.md#E1 · compatible · no sandbox · session
- Cited-by: 2026-09-29 · projects/local__sandbox-lag-closed-form-predicts-surface-ranking.md#E1 · compatible · no sandbox · session_012dXvqZTw6GRKUoDHUaZ6HP
- Cited-by: 2026-09-30 · projects/local__sandbox-mismatch-formula-vs-aperiodic-lag.md#E1 · compatible · no sandbox · session
- Cited-by: 2026-09-29 · projects/local__sandbox-sync-to-worst-lag-rule-fails-across-cycle.md#E1 · compatible · no sandbox · session_012dXvqZTw6GRKUoDHUaZ6HP
