# local/tennis-tiebreak-server-rotation — lessons

Project: local/tennis-tiebreak-server-rotation. Newest first.

---

## E1 — tennis tiebreak server rotation is one then pairs
- Date: 2026-10-16
- Project: local/tennis-tiebreak-server-rotation
- Tags: [tennis][scoring][testing][sandbox]
- What: Seeding the tennis tie-break domain: the real server rotation (first server serves point 1, then the opponent serves 2 and 3, then pairs) gives the order 0,1,1,0,0,1, while a pairs-from-the-start rotation and a one-by-one alternation each give different, wrong orders yet identical serve counts (6-6 after 12 points, 7-6 after 13), so a count-based fairness check cannot tell them apart.
- Why built: New-domain train pick from published ITF tie-break rules: first to 7 points with a 2-point lead, server change after the first point then every two points, ends changed every 6 points; 7-6 is not a legal final score.
- Design: Deterministic script with three server functions of the 0-indexed point number, the rule ((n+1)//2) mod 2, pairs from the start (n//2) mod 2, and alternation n mod 2, compared on the first six servers, the serve split after 12 and 13 points, and a legality check for ten candidate final scores.
- Got right: The rule matched the expected order 0,1,1,0,0,1 and split 6-6 after 12 points, and the legality check rejected 7-6 and kept 7-0 to 7-5, 8-6 and 9-7.
- Where/why it failed: My first version of the check said alternation would split serves unequally after 13 points; it did not, all three rotations give 7-6, so the first run printed FAIL and the claim had to change from totals to order: counts are the same, only the sequence differs.
- Fix: Test a tie-break rotation by comparing the full server sequence for the first six points against 0,1,1,0,0,1, not the totals served, and test legal final scores separately.
- Why this fix: Total serves are equal for several wrong rotations, so only the order exposes a first server who serves twice in a row or a receiver who never gets the double serve.
- Rule of thumb: Check a tie-break serve rotation by its sequence (0,1,1,0,0,1 for the first six points), not its counts: both wrong rotations tied the correct one on serves at 12 and 13 points.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the rotation and 7-point, 2-point-lead rules are the standard ITF tie-break rules as I know them and were not fetched from the rulebook during this run.
- Picked-by: new-domain
- Sandbox: sandboxes/2026-10-16__tennis-tiebreak-server-rotation-is-one-then-pairs.py
- Prediction: Hidden assumption: a serve-count fairness check separates the right rotation from wrong ones. Expected alternation to differ from the rule in the 13-point split; it would be wrong if all counts matched.
- Observed: RESULT: PASS rule serves 0,1,1,0,0,1 and splits 6-6 after 12 points; the pairs-from-start and one-by-one rotations give the same 12- and 13-point serve counts but the wrong order; 7-6 is illegal (first run printed FAIL: the count-split expectation was refuted)
- Scenarios: 1) the rule; 2) pairs from the start, built to break the first-server rule; 3) one-by-one alternation; 4) ten candidate final scores for legality.
- Link: scheduled brain train auto loop 2 pass 6 (newdomain); session_01GYKQrKfm5FQsrnyu59GmiS
- Cited-by: 2026-10-16 · projects/pappydapimp69__brain.md#E205 · compatible · sandboxes/2026-10-16__tiebreak-log-scorer-must-stop-at-the-deciding-point.py · observed RESULT: PASS tally-everything 5/8, stop-at-decision 8/8; sequence check separates 3 rotations, counts at 12 points all equal=True · scheduled brain train auto session, loop 2 edge pass; session_01K2o9Pz3SxQVCm2V4Z7ZhLe
