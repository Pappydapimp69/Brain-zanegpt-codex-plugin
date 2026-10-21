# local/neekolaus-film — lessons

Project: local/neekolaus-film. Newest first.

---

## E1 — belief revision hold contradictions
- Date: 2026-10-11
- Project: local/neekolaus-film
- Tags: [belief-revision][memory][ai][testing]
- What: Seed for a new BELIEF-REVISION domain. A note store for an AI builder (a bot learning a block-rotation
  rule from screenshots) has to decide what to do when a new observation contradicts a stored rule.
- Why built: A friend's first AI system writes rules but never revises them, and he asked how to bring
  contradiction in; Brain had no canon on how a note store should treat a contradicting observation.
- Design: Four policies over the same deterministic observation streams: last writer wins, first writer wins,
  hold the contradiction open and flip on an all-time evidence margin of 3, and hold it open and flip on a
  margin of 3 within the last 6 observations.
- Got right: Holding the contradiction open, instead of replacing or ignoring, kept the belief stable under 30
  percent misleading observations (0 flips, 0 wrong steps) where last-writer-wins flipped 24 times and was wrong
  30 percent of the time, and it recovered from a wrong first note that first-writer-wins kept forever.
- Where/why it failed: Counting ALL history calcified the store: when the rule really changed at step 20, the
  all-time tally could never be outvoted inside the run and the belief stayed wrong for every remaining step
  (50 percent wrong overall), exactly as bad as never revising.
- Fix: Weigh only recent evidence when deciding whether a held contradiction wins: a margin of 3 within the last
  6 observations kept the noise immunity and followed the real change 4 steps late.
- Why this fix: A contradiction is either noise or a sign the world changed; recent-window margins separate the
  two cheaply, while all-time counts treat a real change as noise forever and last-writer-wins treats noise as
  change every time.
- Rule of thumb: When a new observation contradicts a stored rule, keep both and flip only when recent evidence outvotes the rule by a margin; overwriting thrashes under noise, ignoring keeps a bad first note forever, and counting all history never follows a real change.
- Provenance (verified/assumed): Verified first-hand by the sandbox below, built and run in this session.
- Composed: N/A
- Sandbox: sandboxes/2026-10-11__belief-revision-hold-contradictions.py
- Prediction: Holding contradictions open would beat both overwrite and first-wins on every stream, including a real rule change.
- Observed: RESULT: PASS. 30% noise: overwrite 24 flips, hold 0. Wrong first note: first-wins wrong 100%, hold 10%. Real change at step 20: hold-all wrong 50% (never followed), hold-recent 10% (4 steps late). The prediction was wrong for hold-all on the real change.
- Scenarios: 1) sparse 10% noise; 2) 30% noise; 3) first observation wrong; 4) BREAK: the rule really changes at step 20.
- Link: session 2026-10-11 neekolaus film; session_015qgYN9GL7cHD9BS1wmwyMx
- Audited: 2026-10-11 · pass · Read the entry and its stored sandbox (sandboxes/2026-10-11__belief-revision-hold-contradictions.py) and re-ran it: same RESULT line. (1) It computes: each policy is run step by step over fixed observation streams and wrong-share and flips are counted, nothing is built in, and the entry honestly records that its own prediction failed for hold-all on the real change. (2) Coverage is narrower than the rule: one window (6) and margin (3), and the noise is hand-placed at regular spacing, so no window ever holds more than two contradictions. I probed that gap myself with the same functions: 30 percent noise in bursts of 3 and 20 percent in bursts of 4 both still gave hold-recent 0 flips and 0 wrong (overwrite 8 and 4 flips), so the conclusion survives clustered noise up to a burst of 4; a burst of 5 or more inside the window would flip it, which the rule's 'by a margin' already implies. Also, first-wins ties hold-recent whenever the first note is right, so 'beats both' holds only across the scenario set, not per stream. (3) The claim is about a policy, and the sandbox is the policy itself, not a hand model of an outside system, so not modeled. Pass. · session; brain train auto pass 3 (audit), 2026-10-11; session_01NHKVhTvCnvtvZ2NGLSPYj6
- Reverified: 2026-10-11 · pass · sandboxes/2026-10-11__rebuild-belief-revision-margin-vs-overwrite.py · observed RESULT: PASS rule holds under noise (margin 1.00/0.93/0.95 vs overwrite 0.75/0.84/0.82); but clean change overwrite 1.00 > margin 0.94; 6-burst flips margin 2x · Rebuilt from the claim only, before opening the original's entry notes. Differences: my fixture is a binary L/R rule over 80 steps with fixed periodic noise (1 in 4 and 1 in 6 wrong, no RNG), a window of 8 with margin 3 for the hold-and-flip rule, and extra cases the original lacks: a clean change with no noise, and bursts of 4 and 6 consecutive contradictions. The rule of thumb replicated: under noise the margin rule scored 1.00/0.93/0.95 (stable/change/bad-first) against overwrite 0.75/0.84/0.82 (39 flips on the stable stream), first-wins scored 0.00 on a bad first note, and counting all history stayed at 0.50 after a real change. Where it differs from the author's prediction (holding beats both on every stream, including a real change): with no noise overwrite wins the change (1.00 vs 0.94), and a burst of 6 contradictions flips the margin rule falsely (2 flips) though a burst of 4 does not, so the margin rule trades lag for noise immunity and fails against correlated noise. The rule stands; the "every stream" prediction does not. · session_01ScEdAr4bK7Pp21fx27MXao (brain train auto loop 1 pass 4, rebuild)
- Cited-by: 2026-10-11 · projects/pappydapimp69__brainwork.md#E116 · compatible · sandboxes/2026-10-11__veto-refusals-as-contradictions-hold-selector-release-margin.py · observed RESULT: PASS totals {'hold': 134, 'first': 130, 'margin': 140}; permanent hold work 0; noise first 24 vs hold 60; burst3 margin 45 vs hold 74. All four predicted checks held; the margin total lead is small. · scheduled brain train session; session_01BWCnQ783SE9ph58n6xAc6f
- Cited-by: 2026-10-15 · projects/pappydapimp69__brainwork.md#E294 · compatible · sandboxes/2026-10-15__held-selector-release-rule-run-length-vs-first-refusal-vs-margin.py · observed RESULT: PASS no release rule dominates: {'HOLD': 3, 'FIRST': 5, 'MARGIN': 3, 'RUN2': 2, 'RUN3': 2, 'RUN4': 4}; lowest total shortfall RUN2=13. The prediction was refuted: release after 3 lost by 2 on blocks of 3 and 5 ticks. · brain train auto loop 2 pass 5; session_01Kx9Pq1H5qpcbvZJ9u2DPKR
