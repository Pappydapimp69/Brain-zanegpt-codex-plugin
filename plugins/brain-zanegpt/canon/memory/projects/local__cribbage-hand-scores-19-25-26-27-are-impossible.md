# local/cribbage-hand-scores-19-25-26-27-are-impossible — lessons

Project: local/cribbage-hand-scores-19-25-26-27-are-impossible. Newest first.

---

## E1 — cribbage hand scores 19 25 26 27 are impossible
- Date: 2026-10-17
- Project: local/cribbage-hand-scores-19-25-26-27-are-impossible
- Tags: [cribbage][exhaustive][testing][sandbox]
- What: Seeds the CRIBBAGE domain with an exhaustive scorer over every four-card hand and starter (12,994,800 combinations) that finds which totals from 0 to 29 can never occur and how often the maximum does.
- Why built: The domain had no records; the gaps in the cribbage score table are a published fact that a full enumeration can confirm or refute, and the engine can be cross-checked against known hands.
- Design: All 2,598,960 five-card sets times 5 starter choices; scoring by fifteens over every card subset, pairs, runs with duplicate multipliers, a four-card flush with a bonus for a matching starter, and nobs; a per-rank-pattern cache for the suit-free part; three known hands as cross-checks. The crib flush rule is not used.
- Got right: Impossible totals were exactly 19, 25, 26 and 27, the maximum 29 occurred 4 times (5-5-5-J with the matching five as starter, one per suit), the modal score was 4 (2,855,676 combinations), and 1,009,008 combinations scored 0; the cross-checks gave 29, 24 and 0.
- Where/why it failed: Nothing in the table contradicted the prediction. The first draft of the prediction note carried a stray guess about the most common score, removed before the run's result was recorded, and the crib-only flush rule was left out so crib scores are not covered.
- Fix: When a scoring table has gaps, enumerate the whole space once with a cross-checked scorer instead of listing cases by hand.
- Why this fix: Hand reasoning about which totals are reachable misses interactions (a double run, a nobs bonus on top of a flush); a full enumeration finds the gaps and counts the extremes in about 25 seconds.
- Rule of thumb: The cribbage hand scores 19, 25, 26 and 27 cannot occur (0 of 12,994,800), 29 occurs only 4 times, and the modal score is 4, so enumerate a scoring space exhaustively and cross-check the scorer on 29, 24 and 0 before trusting its gaps.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the scoring rules are the standard hand rules, the crib flush variant was not modelled, and this domain has no adjacent record in Brain so the entry is isolated and cites nothing.
- Composed: N/A
- Picked-by: current-half
- Sandbox: sandboxes/2026-10-17__cribbage-hand-scores-19-25-26-27-are-impossible.py
- Prediction: Impossible totals exactly 19, 25, 26 and 27; maximum 29 occurs for exactly 4 combinations; modal score 4. Assumes the scoring function is right; the three known-hand cross-checks (29, 24, 0) were built to break it.
- Observed: RESULT: PASS impossible scores [19, 25, 26, 27]; 29 occurs 4 times; modal score 4 (2855676x) over 12994800 combinations
- Scenarios: 1) full enumeration of all five-card sets with each card as starter; 2) BREAK: cross-check on the 5-5-5-J hand (29); 3) 7-7-8-8 with a 9 starter (24); 4) a no-score hand (0)
- Link: brain train auto loop 2 pass 6 (newdomain), scheduled run 2026-10-17; session_01696mc4JbaRUYgcwwnaPSG1
- Cited-by: 2026-10-17 · projects/local__cribbage-subdeck-impossible-scores-grow-monotonically.md#E1 · compatible · sandboxes/2026-10-17__cribbage-subdeck-impossible-scores-grow-monotonically.py · observed RESULT: PASS subdeck A-8 impossible=[0, 1, 3, 19, 22, 25, 26, 27, 28, 29] max=24; one-suit gaps 0-4 and 19-29. · brain train auto pass 2; session_011LtaNZCrPYhhAtwJpZ1y8i
