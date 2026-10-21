# local/sandbox-lag-aliasing-ranking-p7-p11 — lessons

Project: local/sandbox-lag-aliasing-ranking-p7-p11. Newest first.

---

## E1 — sandbox lag aliasing ranking p7 p11
- Date: 2026-09-29
- Project: local/sandbox-lag-aliasing-ranking-p7-p11
- Tags: [ui][input][state][gamedev][testing]
- What: Re-verification of the lag-aliasing ranking failure at periods 7 and 11 with different active windows, extending the earlier single P=10 result.
- Why built: The aliasing-ranking entry was single-source at P=10/W=4; the period sweep only covered additivity, so independence of the ranking claim needed a new angle.
- Design: Deterministic model, no RNG: role active when s mod P < W, 600 presses per surface, failure when hint (lag steps stale) and press-time role disagree; tested (P,W)=(7,3),(11,4),(11,5) with lags at and beyond one period.
- Got right: Below the period failures rise with lag as expected, e.g. P=7 lag 1 gives 172 and lag 3 gives 515.
- Where/why it failed: The slowest-by-lag surface (lag equal to P or 2P) fails 0 times in all four runs, so zeroing it saves 0 and syncing all surfaces to it gives 0 total; e.g. P=7 lags (1,7,3) give 172/0/515, P=11 lags (2,11,5) give 220/0/437, P=11 lags (3,22,1) give 328/0/110.
- Fix: Rank surfaces by measured failures per surface and include lags that are multiples of the state period in the test matrix.
- Why this fix: Aliasing is a property of lag modulo period, so it holds at any P and W; failure count is the quantity that matters.
- Rule of thumb: Nominal latency never ranks periodic-gated surfaces; check lag mod period and measure failures, at more than one period.
- Provenance: Verified first-hand by running the Python sandbox p1.py and observing the failure counts listed above.
- Composed: sandbox-combined-action-resolver-dog-per-surface-lag-aliasing-ranking/E1, sandbox-combined-action-resolver-dog-per-surface-lag-period-sweep/E1, sandbox-combined-action-resolver-dog-per-surface-lag/E1
- Link: session_012dXvqZTw6GRKUoDHUaZ6HP

