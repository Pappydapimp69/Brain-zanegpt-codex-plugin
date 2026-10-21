# local/sandbox-shared-resolver-consistency-vs-timing — lessons

Project: local/sandbox-shared-resolver-consistency-vs-timing. Newest first.

---

## E1 — sandbox shared resolver consistency vs timing
- Date: 2026-09-29
- Project: local/sandbox-shared-resolver-consistency-vs-timing
- Tags: [ui][input][state][gamedev][testing]
- What: Sandbox separating two properties of the one-shared-resolver design: cross-surface agreement, which the resolver gives when surfaces sample at the same instant, and correctness against the current state, which it does not give once surfaces sample with lag.
- Why built: The single action-resolver lesson (dog#E20) and the multi-surface lesson (dog#E27) claim consistency by construction, and the period-sweep entry showed lag failures; this measures both quantities in one model so "consistent" is not read as "correct".
- Design: Deterministic, no RNG: one resolver role(s) = s mod P < W; each surface reads it at s minus its own lag; count per-surface staleness against the true role and count presses where surfaces disagree with each other; P=7/W=3 and P=11/W=4, 600 presses, three surfaces.
- Got right: With equal lags the surfaces never disagree with each other (0 disagreements), even when all are stale, and with zero lag everything is 0.
- Where/why it failed: Equal lag 2 at P=7 gives 0 disagreements but 344 stale presses per surface (1032 total); at P=11 it gives 220 per surface (660); unequal lags (0,1,2) give 344 and 220 cross-surface disagreements, and lags (1,P,3) give 515 and 329 disagreements while the lag-P surface is fully correct.
- Fix: Test shared-resolver surfaces against the true state at press time and against each other separately; a consistency-only assertion passes while every surface is stale.
- Why this fix: Agreement between surfaces and agreement with the state are independent quantities; the sandbox shows the first at 0 while the second is 660 to 1032.
- Rule of thumb: One resolver buys agreement between surfaces, not freshness; assert both, and equalize or measure lag per surface.
- Provenance: Verified first-hand by running the Python sandbox p4.py and observing the stale and disagreement counts listed above.
- Composed: dog/E20, dog/E27, sandbox-combined-action-resolver-dog-per-surface-lag-period-sweep/E1
- Link: session_012dXvqZTw6GRKUoDHUaZ6HP

