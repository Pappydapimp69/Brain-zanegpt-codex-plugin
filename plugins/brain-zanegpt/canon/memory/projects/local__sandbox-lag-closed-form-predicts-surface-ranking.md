# local/sandbox-lag-closed-form-predicts-surface-ranking — lessons

Project: local/sandbox-lag-closed-form-predicts-surface-ranking. Newest first.

---

## E1 — sandbox lag closed form predicts surface ranking
- Date: 2026-09-29
- Project: local/sandbox-lag-closed-form-predicts-surface-ranking
- Tags: [ui][input][state][gamedev][testing]
- What: Sandbox joining the hint-lag full-cycle closed form with the per-surface aliasing ranking: the closed form 600/P*2*min(lag mod P, W, P-W, P-lag mod P) predicts each surface's failures and therefore the correct fix order.
- Why built: The aliasing-ranking entry and the full-cycle sweep entry were only linked by prose; this checks that the formula alone reproduces the per-surface ranking, giving a cheap predictor instead of simulation.
- Design: Deterministic model, no RNG: role active when s mod P < W, 600 presses; compared simulated mismatch counts with the formula for every lag 0..2P at (P,W)=(15,5),(20,8),(10,4),(12,3), then ranked three-surface lag sets.
- Got right: All 118 lag/period/window combinations matched the formula exactly, including lags beyond one cycle, which the sweep entry had not covered.
- Where/why it failed: Ranking by nominal lag still fails: at P=15/W=5 lags (2,15,7) give 160/0/400 and at P=20/W=8 lags (4,20,10) give 240/0/480; the max-lag surface saves 0 when zeroed while the true worst saves 400 and 480.
- Fix: Compute per-surface failures from the formula with lag reduced modulo the period, and fix surfaces in order of predicted failures.
- Why this fix: The formula is exact on every tested point, so it ranks correctly without a run, and the modulo makes aliasing explicit rather than a surprise.
- Rule of thumb: For periodic gated state, predict failures from lag mod period with the min(lag,W,P-W,P-lag) closed form, and rank surfaces by that number, never by raw lag.
- Provenance: Verified first-hand by running the Python sandbox p2.py: zero mismatches across 118 points and the ranking numbers listed above.
- Composed: sandbox-combined-action-resolver-hint-lag-full-cycle-sweep/E1, sandbox-combined-action-resolver-dog-per-surface-lag-aliasing-ranking/E1
- Link: session_012dXvqZTw6GRKUoDHUaZ6HP

