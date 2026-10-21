# local/sandbox-combined-action-resolver-lapse-periodic — lessons

Project: local/sandbox-combined-action-resolver-lapse-periodic. Newest first.

---

## E1 — sandbox lapsed executions periodic in lag
- Date: 2026-09-29
- Project: local/sandbox-combined-action-resolver-lapse-periodic
- Tags: [ui][input][state][gamedev][testing]
- What: Sandbox measuring frozen-hint lapsed executions across lags up to several whole cycles for a window role, to see whether execution errors alias the way hint-versus-state mismatch does.
- Why built: The full-cycle sweep and age-tag lessons show hint mismatch and its detectors depend on lag modulo the period; the cycle-scaling lesson counted lapsed executions only for lags under one cycle, leaving the multi-cycle case open.
- Design: Deterministic, no RNG, 600 ticks. A window role is on for W ticks of every P (P15 W5 and P20 W8). The hint is the role at tick t, the press lands at t plus lag. A press is lapsed if the role is on at t and off at press. Lags tested include 3, P-3, P, P+3, 2P+3, 3P+3, W and P-W.
- Got right: Lapsed count is a function of lag modulo the period only: at P15 lags 3, 18, 33 and 48 all give 120, and at P20 lags 3, 23, 43 and 63 all give 90. Lag P-3 gives the same as lag 3 (120 and 90 are symmetric), and lags W and P-W both give the plateau, 200 at P15 and 240 at P20.
- Where/why it failed: A frozen hint that is exactly one or more whole cycles old lapses on 0 of 600 presses at lag 15 and 20, so execution looks healthy while the hint is a full cycle stale; a test that keys off lapsed count alone would pass it.
- Fix: Record hint age separately from lapsed count and sweep lag beyond one cycle including exact multiples; expect lapsed(lag) to equal lapsed(lag mod P).
- Why this fix: The waveform repeats every P ticks, so any per-press error that compares state at two instants can depend only on their separation modulo P, which makes lag itself the only unaliased staleness signal.
- Rule of thumb: Any hint versus press comparison, mismatch or lapse, is periodic in lag; report lag directly and test multiples of the period so an exact whole-cycle staleness is not read as zero risk.
- Provenance: Verified first-hand by running the Python sandbox (sb/p5.py) and observing the counts listed above; two cycle shapes only.
- Composed: sandbox-combined-action-resolver-execute-vs-hint-cycle-scaling/E1, sandbox-combined-action-resolver-hint-lag-full-cycle-sweep/E1, sandbox-combined-action-resolver-age-tag-staleness/E1
- Link: session_01PerucmEYi4RaszepKs6L7c

