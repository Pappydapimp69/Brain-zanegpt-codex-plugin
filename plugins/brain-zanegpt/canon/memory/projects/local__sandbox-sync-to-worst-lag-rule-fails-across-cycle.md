# local/sandbox-sync-to-worst-lag-rule-fails-across-cycle — lessons

Project: local/sandbox-sync-to-worst-lag-rule-fails-across-cycle. Newest first.

---

## E1 — sandbox sync to worst lag rule fails across cycle
- Date: 2026-09-29
- Project: local/sandbox-sync-to-worst-lag-rule-fails-across-cycle
- Tags: [ui][input][state][gamedev][testing]
- What: Sandbox over every three-surface lag triple in 0..P at P=7, 11 and 15, checking how often the recorded "syncing all surfaces to the worst lag is worse" rule holds once the full-cycle aliasing is in play.
- Why built: The period-sweep and per-surface entries state sync-to-worst is worse using lags below one period; the full-cycle sweep says lag equal to the period aliases to zero, which should break that rule.
- Design: Deterministic, no RNG: per-surface failures from the exact closed form 600/P*2*min(lag mod P, W, P-W, -lag mod P); compare the sum of independent surfaces with three times the failures at the max lag; windows W=3,4,5 for P=7,11,15.
- Got right: For lags below the period the rule holds where it was recorded, and additivity of failures across surfaces holds at every triple.
- Where/why it failed: Over all triples sync-to-worst is worse in only 168 of 512, 600 of 1728 and 1470 of 4096 cases, and better in 288, 960 and 2250; e.g. lags (0,1,P) at P=7 total 170 failures but syncing to lag 7 gives 0.
- Fix: Do not apply the sync-to-worst rule when any lag can reach a multiple of the period; compute the predicted total for the candidate sync lag and compare against the base sum before choosing.
- Why this fix: Sync-to-worst is only a heuristic for lags below min(W, P-W); the closed form gives the exact total for any candidate sync lag at no cost.
- Rule of thumb: Treat sync everything to the slowest surface as valid only below the aliasing threshold; otherwise evaluate candidate sync lags with the closed form.
- Provenance: Verified first-hand by running the Python sandbox p3.py and observing the triple counts and the (0,1,P) example listed above.
- Composed: sandbox-combined-action-resolver-dog-per-surface-lag-period-sweep/E1, sandbox-combined-action-resolver-hint-lag-full-cycle-sweep/E1, sandbox-combined-action-resolver-dog-per-surface-lag/E1
- Link: session_012dXvqZTw6GRKUoDHUaZ6HP

