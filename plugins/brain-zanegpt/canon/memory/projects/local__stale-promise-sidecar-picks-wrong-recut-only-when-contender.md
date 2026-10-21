# local/stale-promise-sidecar-picks-wrong-recut-only-when-contender — lessons

Project: local/stale-promise-sidecar-picks-wrong-recut-only-when-contender. Newest first.

---

## E1 — stale promise sidecar picks wrong recut only when contender
- Date: 2026-10-17
- Project: local/stale-promise-sidecar-picks-wrong-recut-only-when-contender
- Tags: [game-ads][testing][model][sandbox]
- What: Sandbox putting a hand-kept sidecar of each cold-open recut's promise level under the IPM-times-D1 ranking with promise capped at delivery, to measure how often sidecar drift picks the wrong recut.
- Why built: The sidecar-drift lesson says a hand-maintained map drifts silently, and the ad lessons rank on a promise-dependent score; the open question was how often a stale promise value actually changes the pick.
- Design: Six recuts with base promise 0.2 to 0.7, delivery 0.5, IPM linear in promise, D1 falling 1.5 per unit of promise above delivery. Each recut moves its true promise by -0.3 or +0.3; the sidecar keeps the old value for each stale subset. All 64 stale subsets times 64 direction patterns, 4096 cases, with a derived-from-the-cut ranking as the reference.
- Got right: Reading the promise from the cut gives the right pick by construction (0 of 4096 wrong; that figure is a tautology, since the reference is itself the derived ranking), and one stale entry already cost the pick in 112 of 384 cases (29.2 percent).
- Where/why it failed: My prediction that a hand sidecar would pick wrong in under 25 percent of cases failed: it was wrong in 2592 of 4096 (63.3 percent), and with all six stale and all recuts up it kept recut 3 while recut 0 was best, a regret of 1.14 in score; staleness matters whenever a recut that crosses the delivery line moves, which is common when recuts change promise by a third of the range.
- Fix: Derive the promise level for ranking from the cut's own metadata at ranking time, and fail the ranking if a recut has no metadata, instead of keeping a hand-edited promise column.
- Why this fix: The derived value cannot go stale because it is read from the same artifact the viewer sees, so the only remaining error is a wrong measurement rather than silent drift.
- Rule of thumb: In a six-recut toy ranking, a hand-kept promise sidecar picked the wrong recut in 63.3 percent of 4096 drift cases (29.2 percent with one stale entry) and the derived value in none by construction, so derive the promise from the cut at ranking time.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; promise levels, the D1 slope and the plus or minus 0.3 recut step are assumed toy values, and the derived-promise result is true by construction, not measured.
- Composed: collective-reference/E1, cold-open-promise-matches-delivery/E1, rank-ipm-times-d1-needs-fidelity-retention-link/E1
- Picked-by: new-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-17__stale-promise-sidecar-picks-wrong-recut-only-when-contender.py
- Prediction: Derived promise gives 0 wrong picks; a hand sidecar is wrong in some but under 25 percent of the 4096 cases because staleness only matters when a stale entry is or becomes the argmax. Assumes promise is the only drifting field; the all-stale all-up case was built to break it.
- Observed: RESULT: FAIL derived 0/4096 wrong, hand sidecar 2592/4096 wrong (63.3 percent), one stale entry 112/384
- Scenarios: 1) all 64 stale subsets times 64 recut directions; 2) exactly one stale entry; 3) BREAK: all six stale with every recut raised by 0.3
- Link: brain train auto loop 2 pass 1, scheduled run 2026-10-17; session_01696mc4JbaRUYgcwwnaPSG1

