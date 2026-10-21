# local/give-first-ratio-binds-standalone-posts-not-thread-slots — lessons

Project: local/give-first-ratio-binds-standalone-posts-not-thread-slots. Newest first.

---

## E1 — give first ratio binds standalone posts not thread slots
- Date: 2026-10-17
- Project: local/give-first-ratio-binds-standalone-posts-not-thread-slots
- Tags: [distribution][platform-etiquette][sandbox][model]
- What: Sandbox applying three DISTRIBUTION kernels at once under a fixed action budget: the 9:1 give-first ratio with weekly corral threads, the 15-day devlog cadence, and the rewrite-per-venue rule, to see which rule actually decides what a poster should do.
- Why built: The kernels were filed as etiquette notes and never exercised together; the open question was whether the ratio or the thread slots is the binding constraint when effort is limited.
- Design: Per 90 days, 13 weekly thread slots (cost 2 with a rewritten copy), at most 6 devlogs 15 days apart (cost 4), and unlimited standalone posts each costing 2 plus R comments; assumed reach 1, 2 and 5. Exhaustive search over thread, devlog and standalone counts for budgets 30 to 2000, R of 9, 3 and 1, and standalone reach from 4 to 8.
- Got right: The break-even is closed form: a standalone post beats a thread slot only when its reach exceeds (2+R)/2 times a thread post's, 5.5 at R=9; at budget 2000 reach 5.4 kept 9 thread posts and reach 5.6 dropped every thread post.
- Where/why it failed: My prediction that no standalone posts would appear at budget 60 was wrong; the optimum was 7 thread posts, 6 devlogs and 2 standalone, and standalone first entered at budget 11 (R=9), 5 (R=3) and 3 (R=1), because thread slots are capped at 13 while standalone is not, so the ratio only sets the price.
- Fix: Treat the give-first ratio as a price (R+2 actions per standalone post) and compare reach per action across venues, instead of treating it as a gate; fill the capped thread slots and devlog cadence first, then spend leftover effort on comments that unlock standalone posts.
- Why this fix: Capped venues have a hard ceiling while the standalone path scales with comments, so which one wins depends on reach per action, which the etiquette kernels do not state.
- Rule of thumb: Under a fixed effort budget the 9:1 ratio acts as a price not a ban: a standalone post at 11 actions beats a 2-action thread post only above 5.5x its reach (flip between 5.4 and 5.6 in the sweep), so measure reach per action before choosing the venue.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; every cost and reach value is an assumed toy number and no subreddit or itch.io data was measured.
- Composed: ideas:DISTRIBUTION/reddit-containment-not-prohibition, ideas:DISTRIBUTION/itch-devlog-cadence-discipline, ideas:DISTRIBUTION/never-duplicate-copy-across-venues
- Picked-by: current-half
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-17__give-first-ratio-binds-standalone-posts-not-thread-slots.py
- Prediction: At budget 60 no standalone posts, all 13 thread slots and 6 devlogs used; standalone enters only above a budget of about 150, earlier at R=3. Assumed reach values are fixed; a standalone post appearing at budget 60 would prove that wrong.
- Observed: RESULT: FAIL predicted zero standalone at budget 60 but plan was (7, 6, 2); standalone enters at budget 11 (R=9), 5 (R=3), 3 (R=1); break-even reach (2+R)/2 means reach decides, not the ratio
- Scenarios: 1) budgets 30, 60, 100, 150, 300 at R=9; 2) first budget where standalone enters at R=9, 3 and 1; 3) BREAK: budget 2000 with standalone reach 4.0 to 8.0 around the 5.5 break-even
- Link: brain train auto loop 1 pass 5, scheduled run 2026-10-17; session_01696mc4JbaRUYgcwwnaPSG1
- Cited-by: 2026-10-19 · projects/pappydapimp69__brainwork.md#E505 · compatible · sandboxes/2026-10-19__give-actions-with-own-reach-lower-the-standalone-post-flip-point.py · observed RESULT: PASS flips g0=5.6 g.2=3.8 g.6=0.2 capped=5.0 (first run FAIL from an over-strict check) · brain train auto pass 2 (loop 1); session_01TLYDN658tW4ZQFUr2wQFj7
