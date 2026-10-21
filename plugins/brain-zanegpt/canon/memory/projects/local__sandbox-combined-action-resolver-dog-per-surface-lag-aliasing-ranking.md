# local/sandbox-combined-action-resolver-dog-per-surface-lag-aliasing-ranking — lessons

Project: local/sandbox-combined-action-resolver-dog-per-surface-lag-aliasing-ranking. Newest first.

---

## E1 — sandbox combined action resolver dog per surface lag aliasing ranking
- Date: 2026-09-29
- Project: local/sandbox-combined-action-resolver-dog-per-surface-lag-aliasing-ranking
- Tags: [ui][input][state][gamedev][testing]
- What: Sandbox of per-surface hint-to-press lag under a shared resolver when one surface's lag aliases to a full state cycle, testing whether "fix the slowest surface first" still ranks correctly.
- Why built: Recorded per-surface-lag entries assume failures grow with lag and rank by slowest lag; the full-cycle sweep shows lag equal to the period aliases back to zero, so the ranking rule may break.
- Design: Deterministic model, no RNG: role active when s mod P < W with P=10, W=4; 600 presses per surface; surfaces given lag tuples, failures counted as hint vs press-time role disagreements.
- Got right: Lags (0,1,2) give 0/120/240 (sum 360, sync-to-worst 720, zeroing slowest saves 240); additivity holds when lags are below the period.
- Where/why it failed: With lags (1,10,4) failures are 120/0/480 (sum 600); the surface with the largest lag (10) fails 0 times, so zeroing the slowest-by-lag saves 0 and syncing all to lag 10 gives 0 total, better than any per-surface fix; with (3,10,20) the two highest lags both fail 0.
- Fix: Rank surfaces by measured failure count per surface, not by nominal lag, and sweep lag modulo the state period in the test.
- Why this fix: Failure count is the quantity the user feels; nominal lag only predicts it below min(W, P-W) and aliases back to zero at multiples of the period.
- Rule of thumb: Never rank input surfaces by latency alone when the gated state is periodic; measure failures per surface and include lags at multiples of the cycle.
- Provenance: Verified first-hand by running the Python sandbox (s2.py) and observing the failure counts listed above.
- Composed: sandbox-combined-action-resolver-dog-per-surface-lag/E1, sandbox-combined-action-resolver-hint-lag-full-cycle-sweep/E1, sandbox-combined-action-resolver-dog-per-surface-lag-period-sweep/E1
- Link: session_01AJo9NVvaQuzD3JbJDk6P3B
- Cited-by: 2026-09-29 · projects/local__sandbox-lag-aliasing-ranking-p7-p11.md#E1 · compatible · no sandbox · session_012dXvqZTw6GRKUoDHUaZ6HP
- Cited-by: 2026-09-29 · projects/local__sandbox-lag-closed-form-predicts-surface-ranking.md#E1 · compatible · no sandbox · session_012dXvqZTw6GRKUoDHUaZ6HP
