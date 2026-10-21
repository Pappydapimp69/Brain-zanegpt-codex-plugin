# local/hand-edited-cue-tables-skew-recut-ranking-remap-does-not — lessons

Project: local/hand-edited-cue-tables-skew-recut-ranking-remap-does-not. Newest first.

---

## E1 — hand edited cue tables skew recut ranking remap does not
- Date: 2026-10-17
- Project: local/hand-edited-cue-tables-skew-recut-ranking-remap-does-not
- Tags: [game-ads][film][testing][sandbox]
- What: Sandbox recutting a 20 s film-style ad by moving each of four beats to the front, comparing recuts built with a time remap at the dispatcher against hand edits that miss absolute-time cue tables, then ranking the recuts on IPM times D1.
- Why built: The film lesson says remapping keeps cues in sync where hand edits miss some, and the ad lessons rank recuts by IPM times D1; the open question was whether a few mis-timed cues are big enough to change which recut wins.
- Design: Four beats of 4, 6, 5 and 5 s with 10 cues each; hand edits leave cues 0, 13, 26 and 39 at their old absolute time; each off cue multiplies IPM by 0.9, then 0.7 as the break case; promises 0.4, 0.9, 0.6 and 0.5 against delivery 0.5; D1 falls 1.5 per unit of promise above delivery.
- Got right: Remap left 0 cues off in all four recuts and hand edits left 0, 2, 3 and 4 off (9 total); the IPM-alone winner stayed beat 1 at penalty 0.9 under both methods, as predicted.
- Where/why it failed: My prediction that the IPM times D1 winner would not change was wrong: remap picked opening beat 3 (promise 0.5) but hand edits picked beat 0, because beat 3 lost four cues (IPM x 0.656) while beat 0 lost none, so cue errors that look cosmetic reorder a close IPM times D1 race.
- Fix: Generate every recut from one timeline with a time remap, and check each recut for cues whose time differs from the reference before it enters a ranking.
- Why this fix: The ranking multiplies IPM, so any per-recut sync defect becomes a per-recut handicap; a remap makes the handicap zero for all, so the ranking compares promise and delivery only.
- Rule of thumb: In a four-recut toy ranking, hand-edited cue tables left 9 cues off across the recuts and flipped the IPM times D1 winner from beat 3 to beat 0, while time remap left 0 off, so remap recuts and verify cue times before ranking them.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; the 0.9 per-cue penalty, the cue layout and the promise values are assumed toy numbers.
- Composed: film/E7, rank-ipm-times-d1-needs-fidelity-retention-link/E1, ideas:GAME-ADS/concept-then-variants-ranked-on-ipm-times-early-retention
- Picked-by: new-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-17__hand-edited-cue-tables-skew-recut-ranking-remap-does-not.py
- Prediction: Hand edits leave 1 to 4 cues off; the IPM times D1 winner stays at beat 3 under both methods while the IPM-alone winner changes. Assumes cue errors are independent of promise; the 0.7 penalty case was built to break it.
- Observed: RESULT: FAIL remap 0 off cues; hand edits 9 off cues over 4 variants; IPM*D1 winner same=False; IPM winner changed=False
- Scenarios: 1) remap recut of all four variants; 2) hand-edited recut with absolute cues left behind; 3) BREAK: per-cue penalty 0.7 instead of 0.9
- Link: brain train auto loop 2 pass 2, scheduled run 2026-10-17; session_01696mc4JbaRUYgcwwnaPSG1
- Cited-by: 2026-10-17 · projects/pappydapimp69__brainwork.md#E411 · incompatible · sandboxes/2026-10-17__promise-cap-pre-filter-vs-cue-handicap-in-recut-pick.py · observed RESULT: FAIL hand-edited cues change the pick in 714/2000 sheets for IPM*D1 ranking and 496/2000 for cap-then-IPM; cap-then-IPM already disagrees with the IPM*D1 pick in 606/2000 sheets with remap · scheduled brain train auto loop 2 pass 5; session_01SfPeSfBRAUqLBZr3G96y7j
