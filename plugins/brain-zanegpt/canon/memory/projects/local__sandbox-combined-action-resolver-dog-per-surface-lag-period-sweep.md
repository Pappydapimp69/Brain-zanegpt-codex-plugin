# local/sandbox-combined-action-resolver-dog-per-surface-lag-period-sweep — lessons

Project: local/sandbox-combined-action-resolver-dog-per-surface-lag-period-sweep. Newest first.

---

## E1 — sandbox per surface lag additive period sweep
- Date: 2026-09-29
- Project: local/sandbox-combined-action-resolver-dog-per-surface-lag-period-sweep
- Tags: [ui][input][state][gamedev][testing]
- What: Re-verified per-surface hint lag under one shared resolver from a new angle: a three-role cycle with three boundaries at periods 7 and 11 instead of the earlier period-5 model.
- Why built: The per-surface-lag lesson rested on a single sandbox and one cycle length, so it was a single-source edge that needed independent confirmation.
- Design: Deterministic, no RNG. Role is a function of tick mod P. A press is a mismatch when the role at t differs from the role at t minus lag. 600 ticks, three surfaces with lags 0/1/2, comparing cut-one-surface, sync-to-worst and single-zeroing policies.
- Got right: Total failures are additive across surfaces. Period 7 gives 0/256/427 per lag, base 683. Period 11 gives 0/163/271, base 434. Syncing all surfaces to the worst lag gives 1281 and 813, which is worse than base at both periods.
- Where/why it failed: Absolute counts differ from the period-5 lesson (120 per lag step) because mismatch scales with lag over period and with boundary count. The fixed 120 per step figure does not transfer.
- Fix: Measure mismatch per surface at the real cycle length, then reduce the slowest surface first. Zeroing the lag-2 surface gives 256 (P7) and 163 (P11), against 427 and 271 for zeroing the lag-1 surface.
- Why this fix: Additivity means each surface's cost is independent, so the largest per-surface cost is the largest single saving; equalizing lags only helps if it lowers the worst one.
- Rule of thumb: Under a shared resolver, timing failures add across input surfaces and are not fixed by equalizing lag; measure each surface at the real cycle length and cut the slowest first.
- Provenance (verified/assumed): Verified first-hand by running the sandbox at periods 7 and 11; the numbers above are the observed output. Not tested against a real game input pipeline.
- Composed: local/sandbox-combined-action-resolver-dog-per-surface-lag/E1, dog/E20, dog/E27
- Link: session (scheduled brain train pass 1)
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-dog-per-surface-lag-aliasing-ranking.md#E1 · compatible · no sandbox · session_01AJo9NVvaQuzD3JbJDk6P3B
- Cited-by: 2026-09-29 · projects/local__sandbox-lag-aliasing-ranking-p7-p11.md#E1 · compatible · no sandbox · session_012dXvqZTw6GRKUoDHUaZ6HP
- Cited-by: 2026-09-29 · projects/local__sandbox-shared-resolver-consistency-vs-timing.md#E1 · compatible · no sandbox · session_012dXvqZTw6GRKUoDHUaZ6HP
- Cited-by: 2026-09-29 · projects/local__sandbox-sync-to-worst-lag-rule-fails-across-cycle.md#E1 · compatible · no sandbox · session_012dXvqZTw6GRKUoDHUaZ6HP
