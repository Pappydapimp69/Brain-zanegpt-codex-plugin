# local/sandbox-combined-action-resolver-age-tag-staleness — lessons

Project: local/sandbox-combined-action-resolver-age-tag-staleness. Newest first.

---

## E1 — sandbox age tag detects aliased hint
- Date: 2026-09-29
- Project: local/sandbox-combined-action-resolver-age-tag-staleness
- Tags: [ui][input][state][gamedev][testing]
- What: Sandbox comparing two staleness detectors for a shown hint under lag: a hint-versus-press mismatch check and an age tag stamped on the hint with its issue tick.
- Why built: The full-cycle sweep lesson found mismatch aliases back to zero at one cycle and said staleness must be measured as lag; this sandbox tests a concrete detector that does that, and whether the aliasing repeats at two cycles.
- Design: Deterministic, no RNG, 600 ticks. State is on for W ticks of every P (P15 W5 and P20 W8). The hint shows the state from lag ticks earlier; lags 0, 3, 5, P, P+3, 2P, 2P+3. Count mismatch ticks and ticks flagged by an age check with a threshold of 2 ticks.
- Got right: The age tag flags 600 of 600 presses at every lag above the threshold, including lags 15 and 30 at P15 and 20 and 40 at P20. Mismatch reads 237/395 at lags 3/5 and 241 at lag 18 for P15.
- Where/why it failed: The mismatch check reads only 10 at lag 15 and 20 at lag 30 (P15), and 12 and 24 at lags 20 and 40 (P20), nearly the value at lag 0, so it aliases at every multiple of the period, not just the first.
- Fix: Stamp each hint with its issue tick and compare the age at press time against a threshold; use mismatch only as a secondary quality metric.
- Why this fix: Age is monotonic in lag and independent of the state waveform, so it cannot alias, while mismatch depends on the waveform and folds back at each period.
- Rule of thumb: Detect a stale hint by its age, not by whether it agrees with current state; agreement can look perfect when the hint is exactly N whole cycles old.
- Provenance: Verified first-hand by running the Python sandbox (sb/p2.py) and observing the counts listed above; only two cycle shapes were run.
- Composed: sandbox-combined-action-resolver-hint-lag-full-cycle-sweep/E1, brain/E62, sandbox-combined-action-resolver-execute-vs-hint-cycle-scaling/E1
- Link: session_01PerucmEYi4RaszepKs6L7c
- Cited-by: 2026-09-30 · projects/local__sandbox-age-gate-validity-combined-aliasing.md#E1 · compatible · no sandbox · session
- Cited-by: 2026-09-30 · projects/local__sandbox-age-gate-vs-validity-fallback-tradeoff.md#E1 · compatible · no sandbox · session_01AfTzT5iniwzFpQZUQQxJ7F
- Cited-by: 2026-09-30 · projects/local__sandbox-age-gated-fallback-aperiodic-waveform.md#E1 · compatible · no sandbox · session_01AfTzT5iniwzFpQZUQQxJ7F
- Cited-by: 2026-09-30 · projects/local__sandbox-age-tag-vs-agreement-aliasing-cycle-multiples.md#E1 · compatible · sandboxes/2026-09-30__age-tag-vs-agreement-aliasing-cycle-multiples.py · observed RESULT: PASS agreement aliases to 0 at every cycle multiple on 3 periodic schedules, age tag flags 600/600; aperiodic has no zero lag · scheduled train pass 2
- Cited-by: 2026-09-30 · projects/local__sandbox-age-validity-aliasing-fallback-tradeoff.md#E1 · compatible · sandboxes/2026-09-30__age-validity-aliasing-fallback-tradeoff.py · observed RESULT: PASS combined policy 0 invalid at all 5 lags; at whole-cycle lags validity-only is (0 redo,0 invalid) while age-only pays 600 redos. · scheduled brain train pass 2
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-age-vs-validity.md#E1 · compatible · no sandbox · session_01PerucmEYi4RaszepKs6L7c
- Cited-by: 2026-09-29 · projects/local__sandbox-combined-action-resolver-lapse-periodic.md#E1 · compatible · no sandbox · session_01PerucmEYi4RaszepKs6L7c
- Cited-by: 2026-09-30 · projects/local__sandbox-resolver-mismatch-aliasing-lcm-lags.md#E1 · compatible · sandboxes/2026-09-30__resolver-mismatch-aliasing-lcm-lags.py · observed RESULT: PASS resolved-action mismatch aliases to 0 at lcm multiples 60,120 (>0 at 15..45); age tag flags all 600 · scheduled train pass 3
- Cited-by: 2026-09-30 · projects/pappydapimp69__brain.md#E70 · compatible · sandboxes/2026-09-30__age-tag-vs-mismatch-staleness-blindness-sweep.py · observed RESULT: PASS formula mismatches 0 of 26100; 1304 whole-cycle lags all blind; worst near-blind rate at l=1 is 0.0667 at P30. · scheduled brain train pass 4
- Cited-by: 2026-09-30 · projects/pappydapimp69__brainwork.md#E1 · compatible · no sandbox · session https://claude.ai/code/session_01F9aR1eawRNLN9c3sNEJ6Sd
