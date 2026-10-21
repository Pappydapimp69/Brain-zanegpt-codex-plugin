# local/cold-open-promise-matches-delivery — lessons

Project: local/cold-open-promise-matches-delivery. Newest first.

---

## E1 — cold open promise matches delivery
- Date: 2026-10-17
- Project: local/cold-open-promise-matches-delivery
- Tags: [game-ads][testing][model][sandbox]
- What: A toy ranking of 15 ad variants (3 hook strengths x 5 cold-open promise levels, where a film-style cold open shows the payoff first) on IPM alone versus IPM times D1, with the game delivering 0.5. IPM-only picks the maximum promise 1.0 in every scenario; IPM times D1 picks promise 0.5 (equal to what is delivered) whenever D1 falls with the promise gap, and picks 1.0 only when D1 is flat.
- Why built: The ranked-variants kernel plus the film companion suggest a cold open is a cheap variant axis. I wanted to know whether the second rank factor corrects an over-promising cold open or whether it rewards it.
- Design: IPM = 10 x hook x (1 + 0.8 x promise); D1 = 0.30 - pen x max(0, promise - delivered), floored at 0.05. Scenarios: linear penalty 0.3, flat (control), steep 0.8, and a cliff (D1 drops to 0.05 beyond a 0.25 gap, built to BREAK the claim that the pick sits mid-range). No randomness.
- Got right: The flat-D1 control gives the same pick as IPM-only (promise 1.0), so the correction comes only from the D1 term, and the hook strength 1.2 is chosen under both rankings, so the two factors separate cleanly.
- Where/why it failed: My prediction was wrong for the cliff case: I expected the pick at promise 0.75, the last level before the cliff, but it was 0.5, because the extra 0.25 of promise adds only 20% x hook to IPM while the linear D1 cost already exceeds that. The cliff was not what set the pick.
- Fix: Rank cold-open variants on IPM times D1 and expect the winner to sit at the promise the game can deliver; do not treat the highest-IPM cold open as the base to recut.
- Why this fix: In all three penalised scenarios the D1 term moved the pick from 1.0 to 0.5 while the flat control did not, so the correction is attributable to retention cost of over-promising, not to ranking noise.
- Rule of thumb: With a cold-open axis, IPM alone picks the biggest promise (1.0) but IPM times D1 picks the promise equal to what the game delivers (0.5 in linear, steep and cliff cases), so cap the cold-open promise at delivery before recutting.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; every constant and functional form is an assumed toy model, not measured ad data.
- Composed: ideas:GAME-ADS/iteration/concept-then-variants-ranked-on-ipm-times-early-retention/decompose-the-winner-and-recut, rank-ipm-times-d1-needs-fidelity-retention-link/E1, film
- Picked-by: new-half
- Polarity: compatible
- Sandbox: sandboxes/2026-10-17__cold-open-hook-ipm-d1-rank.py
- Prediction: IPM-only picks promise 1.0; IPM times D1 picks a mid promise below 1.0 under linear and steep penalties and exactly 0.75 under the cliff; flat D1 agrees with IPM-only. Assumption: over-promising lifts IPM and lowers D1.
- Observed: RESULT: FAIL IPM->promise 1.00; IPM*D1 linear 0.50, steep 0.50, cliff 0.50, flat agrees True (only the cliff 0.75 prediction missed)
- Scenarios: 1) linear D1 penalty; 2) flat D1 control; 3) steep penalty; 4) cliff beyond gap 0.25 (BREAK)
- Link: session_01FKz3vbJ5KozVVes2fUyYJ8
- Cited-by: 2026-10-17 · projects/pappydapimp69__brainwork.md#E405 · compatible · sandboxes/2026-10-17__two-stage-recut-screen-recovers-ipm-d1-gain.py · observed RESULT: PASS two-stage (top2) reaches 96% of best at 8400 impressions vs one-stage 3000 98% at 24000; top4 98% at 14400; one-stage 300 95% at 2400 · brain train auto loop 2 pass 5; session_01PTu5uBJqYTUhgm91RqrjQ3
- Cited-by: 2026-10-17 · projects/local__hook-frame0-audio-vs-promise-cap-recut-rank.md#E1 · compatible · sandboxes/2026-10-17__hook-frame0-audio-vs-promise-cap-recut-rank.py · observed RESULT: PASS IPM*D1 picked promise 0.5 in 3/3 scenarios; IPM alone picked [1.0, 1.0, 0.6] · brain train auto loop 1 pass 1; session_01696mc4JbaRUYgcwwnaPSG1
- Cited-by: 2026-10-17 · projects/local__stale-promise-sidecar-picks-wrong-recut-only-when-contender.md#E1 · compatible · sandboxes/2026-10-17__stale-promise-sidecar-picks-wrong-recut-only-when-contender.py · observed RESULT: FAIL derived 0/4096 wrong, hand sidecar 2592/4096 wrong (63.3 percent), one stale entry 112/384 · brain train auto loop 2 pass 1, scheduled run 2026-10-17; session_01696mc4JbaRUYgcwwnaPSG1
- Cited-by: 2026-10-17 · projects/pappydapimp69__brainwork.md#E410 · compatible · sandboxes/2026-10-17__promise-cap-check-needs-derived-from-game-link-not-any-noun.py · observed RESULT: PASS promise cap on any-noun column keeps 0.88/0.88/0.84 of the true-best value vs 1.00/1.00/1.00 for derived-from-game column on decorated sheets; identical with no decoration · scheduled brain train auto pass 5; session_01SfPeSfBRAUqLBZr3G96y7j
- Cited-by: 2026-10-17 · projects/pappydapimp69__brainwork.md#E411 · incompatible · sandboxes/2026-10-17__promise-cap-pre-filter-vs-cue-handicap-in-recut-pick.py · observed RESULT: FAIL hand-edited cues change the pick in 714/2000 sheets for IPM*D1 ranking and 496/2000 for cap-then-IPM; cap-then-IPM already disagrees with the IPM*D1 pick in 606/2000 sheets with remap · scheduled brain train auto loop 2 pass 5; session_01SfPeSfBRAUqLBZr3G96y7j
- Audited: 2026-10-17 · modeled · Read the entry and reran its stored sandbox; the picks are computed over all 15 variants, not built in (IPM alone picks promise 1.0, IPM times D1 picks 0.5 in the linear, steep and cliff cases, flat agrees). But the sandbox fixes the delivered level at 0.5 and only uses penalties of 0.3 or more, so it cannot show the rule's wider statement that the pick equals what the game delivers. I swept delivered 0.25, 0.5, 0.75 with penalties 0.1, 0.3, 0.8 using the same IPM and D1 forms: the pick tracked delivery at penalties 0.3 and 0.8 (0.25, 0.5, 0.75) but jumped to 1.0 at penalty 0.1 for every delivered level, so the rule holds only when the D1 penalty is steep enough to beat the 0.8 IPM gain. All constants are assumed toy values, not ad data, and the stored script ends in a FAIL line from a missed cliff prediction, which the entry discloses. So the numbers hold as a model, with a missing penalty-size condition. · scheduled brain train auto loop 2 pass 3 (audit), Claude Code session_011LtaNZCrPYhhAtwJpZ1y8i
