# local/sandbox-combined-action-resolver-age-vs-validity — lessons

Project: local/sandbox-combined-action-resolver-age-vs-validity. Newest first.

---

## E1 — sandbox age tag is staleness not validity
- Date: 2026-09-29
- Project: local/sandbox-combined-action-resolver-age-vs-validity
- Tags: [ui][input][state][gamedev][testing]
- What: Sandbox checking whether an age-tag threshold on a hint predicts which presses execute an action that is no longer valid, at three window-cycle shapes.
- Why built: The age-tag lesson shows age cannot alias, and the execute-versus-hint cycle scaling lesson counts lapsed executions; nothing yet related the two, so it was unclear whether age can gate execution.
- Design: Deterministic, no RNG, 600 ticks. A window role is on for W ticks of every P (P15 W5, P20 W8, P9 W3). The hint shows the role at tick t, the press lands at t plus lag, lags 1/2/4 and one full period. A press is truly lapsed if the hinted role is on at t and off at press. The age flag fires when lag exceeds 2 ticks.
- Got right: Lapsed counts match the cycle-scaling lesson: 40/80/160 at P15 for lags 1/2/4 and 67/134/201 at P9, so the models agree.
- Where/why it failed: Age is a poor validity gate. At lag 1 and 2 the flag never fires yet 40 and 80 presses lapse at P15. At lag 4 it flags all 600 but only 160 lapsed, a 73 percent false-positive rate at P15, 80 percent at P20 and 66 percent at P9. At a full period it flags 600 with 0 lapsed.
- Fix: Use the age tag to report staleness to the user or telemetry, and gate execution on a press-time validity check of the hinted action instead.
- Why this fix: Validity depends on the waveform at press time, while age depends only on lag, so age both misses lapses under the threshold and rejects valid presses above it.
- Rule of thumb: Age says how stale a hint is; only a press-time check says whether it is still safe to execute, so never drop or allow input on age alone.
- Provenance: Verified first-hand by running the Python sandbox (sb/p4.py) and observing the counts listed above; the threshold of 2 ticks was a single choice.
- Composed: sandbox-combined-action-resolver-age-tag-staleness/E1, sandbox-combined-action-resolver-execute-vs-hint-cycle-scaling/E1
- Link: session_01PerucmEYi4RaszepKs6L7c
- Cited-by: 2026-09-30 · projects/pappydapimp69__brainwork.md#E1 · compatible · no sandbox · session https://claude.ai/code/session_01F9aR1eawRNLN9c3sNEJ6Sd
- Cited-by: 2026-09-30 · projects/pappydapimp69__brainwork.md#E2 · compatible · no sandbox · session https://claude.ai/code/session_01F9aR1eawRNLN9c3sNEJ6Sd
