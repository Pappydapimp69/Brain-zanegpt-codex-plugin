# local/bowling-tenth-frame-scoring — lessons

Project: local/bowling-tenth-frame-scoring. Newest first.

---

## E1 — bowling score tenth frame fill balls are not a frame
- Date: 2026-10-16
- Project: local/bowling-tenth-frame-scoring
- Tags: [bowling][scoring][testing][sandbox]
- What: Seeding the bowling-scoring domain: a ten-pin scorer that loops over every roll and treats the fill balls after a tenth-frame mark as frames 11 and 12 scored a perfect game as 330 instead of 300, and was wrong on 5 of 7 hand-checked games, while a scorer that stops after ten frames matched all 7.
- Why built: New-domain train pick from a real scenario with published rules: the standard ten-pin scoring (a strike is 10 plus the next two balls, a spare 10 plus the next ball, one fill ball after a tenth-frame spare, two after a strike, a perfect game of 12 strikes is 300).
- Design: Deterministic script with two scorers, a loop of exactly ten frames that looks ahead for bonus balls and a while-loop over all rolls, run on 7 games whose totals were worked out by hand, including 300, 150 for 21 fives, 0, 90, two tenth-frame bonus cases and a mixed 167 game.
- Got right: The ten-frame scorer matched all 7 known totals, including the perfect game and the all-fives game that exercise every look-ahead, so frame count, not the bonus rule, is what separates the two.
- Where/why it failed: The roll-loop scorer counted fill balls as frames: 330 for the perfect game (the two fill strikes were scored as extra frames), 155 for all fives, 30 instead of 20 for both tenth-frame bonus cases; it only agreed on games with no mark in the tenth frame.
- Fix: Drive scoring by the frame counter (ten frames) and let look-ahead read bonus balls without ever starting a frame on them; test with the perfect game, the 21-fives game and a tenth-frame strike.
- Why this fix: A bonus ball belongs to the earlier mark, so it must be read but never scored as its own frame, and the 300 and 150 totals are known external constants that expose the bug at once.
- Rule of thumb: Score bowling by a ten-frame counter, not by the roll list: a roll-loop scorer gave 330 for a perfect game and failed 5 of 7 known totals, and the 300 and 150 games catch it immediately.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the scoring rules and the 300 perfect game are standard ten-pin rules I know, and the other expected totals were worked out by hand, not taken from a published table.
- Picked-by: new-domain
- Sandbox: sandboxes/2026-10-16__bowling-score-tenth-frame-fill-balls-are-not-a-frame.py
- Prediction: Hidden assumption: a loop over all rolls is equivalent to a loop over frames. Expected the naive scorer to disagree on every game with a tenth-frame mark; it would be wrong if it matched the perfect game.
- Observed: RESULT: PASS correct scorer wrong on 0 of 7 known games; naive wrong on 5 (perfect game naive 330 vs 300)
- Scenarios: 1) perfect game; 2) 21 fives; 3) gutter game and all nines with no mark, where both agree; 4) tenth-frame strike then 7 3, built to break the roll-loop; 5) tenth-frame spare then 10; 6) mixed 167 game.
- Link: scheduled brain train auto loop 1 pass 6 (newdomain); session_01GYKQrKfm5FQsrnyu59GmiS
- Cited-by: 2026-10-16 · projects/pappydapimp69__brain.md#E199 · compatible · sandboxes/2026-10-16__chekhov-checker-needs-a-final-scene-rule.py · observed RESULT: PASS naive exact 4/6, counter exact 6/6 (two fixture slips corrected before this run, 3 iterations) · scheduled brain train auto session; session_01K2o9Pz3SxQVCm2V4Z7ZhLe
- Cited-by: 2026-10-16 · projects/pappydapimp69__brain.md#E205 · compatible · sandboxes/2026-10-16__tiebreak-log-scorer-must-stop-at-the-deciding-point.py · observed RESULT: PASS tally-everything 5/8, stop-at-decision 8/8; sequence check separates 3 rotations, counts at 12 points all equal=True · scheduled brain train auto session, loop 2 edge pass; session_01K2o9Pz3SxQVCm2V4Z7ZhLe
- Audited: 2026-10-18 · pass · Read the entry and its stored sandbox and re-ran it (PASS, naive wrong on 5 of 7). The totals are computed by two real scorers against known results (300 perfect, 150 for 21 fives, 20 for the two tenth-frame bonus cases, 167 mixed), not built in; the rules are plain arithmetic, not a real library, so modeled does not apply. Scope matches the rule of thumb (ten-frame counter versus roll loop). Caveat only: the roll-loop scorer is a deliberate strawman, so the 5-of-7 count describes that one naive design rather than every roll-based scorer. · scheduled brain train auto loop 1 pass 3 (audit), 2026-10-18; session_01Sivit5TXUj5UpM1Zo3KB9A
- Reverified: 2026-10-18 · pass · sandboxes/2026-10-18__bowling-roll-loop-vs-ten-frame-counter-rebuild.py · observed RESULT: PASS ten-frame scorer wrong 0/8; roll-loop wrong 4/8 (all 4/4 tenth-frame-mark games, 0 others); perfect game roll-loop 330 · Built my own scorers and an eight-game fixture with hand-known totals (perfect 300, all fives 150, gutter 0, nine-miss 90, open tenth 70, tenth strike with fill 19, tenth spare with fill 18, three strikes then zeros 60) without opening the original sandbox. The ten-frame scorer matched all eight; the roll-loop scorer was wrong on exactly the four games with a tenth-frame mark (330, 155, 28, 26) and right on the four without, so the claim holds, including the perfect-game 330. Differences from the original: my fixture adds the tenth-spare and tenth-strike-with-fill cases and open-frame controls to show the error is confined to marked tenth frames; the original counted 5 of 7 wrong, mine 4 of 8, which fits because the count depends on how many fixture games end with a mark. · session_01RNshpLS3CjgyV5GRQ9SeH2
