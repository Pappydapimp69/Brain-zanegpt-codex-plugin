# local/sandbox-mismatch-aliasing-quasiperiodic-fibonacci-lags — lessons

Project: local/sandbox-mismatch-aliasing-quasiperiodic-fibonacci-lags. Newest first.

---

## E1 — sandbox mismatch aliasing quasiperiodic fibonacci lags
- Date: 2026-09-30
- Project: local/sandbox-mismatch-aliasing-quasiperiodic-fibonacci-lags
- Tags: [ui][input][state][gamedev][testing]
- What: Sandbox re-checking the claim that raw hint-versus-state mismatch is only blind (reads 0 at stale lags) on periodic waveforms, using Fibonacci, period-doubling, Rudin-Shapiro and Thue-Morse words next to two periodic waves.
- Why built: The aperiodic-waveform lesson and the new Fibonacci cost lesson were single-source edges; a quasi-periodic word has near-repeats, so it can stress the claim that only exact periodicity lets mismatch alias.
- Design: Deterministic, no RNG, 600 samples. Mismatch counts samples where state at t differs from state at t plus lag, for lags 3,15,20,30,34,40,55,89,144,233,377. Age flag is lag above threshold 2; the age-gated fallback re-resolves when flagged and so is legal by construction.
- Got right: Age flags 11 of 11 lags on every waveform and the gated policy is rule-valid 600/600 throughout. Periodic waves read exactly 0 mismatch at whole cycles (P15W5 lags 15 and 30, P20W8 lags 20 and 40). Thue-Morse and Rudin-Shapiro stay at 200-316 at every lag.
- Where/why it failed: Fibonacci mismatch collapses to 16, 8, 6, 2, 2 and 0 at lags 34, 55, 89, 144, 233 and 377 (Fibonacci numbers), and period-doubling reads 25 at lag 144, so mismatch is near-blind on quasi-periodic state even though it never exactly aliases before the window edge.
- Fix: Treat mismatch as unreliable for staleness on any waveform with near-repeats (periodic or quasi-periodic) and keep the age tag as the detector and the gate.
- Why this fix: Age equals lag by construction and is independent of the waveform, while mismatch measures state autocorrelation, which is high at near-period lags of quasi-periodic sequences.
- Rule of thumb: Mismatch blindness is a property of autocorrelation, not only of exact periodicity: quasi-periodic state fakes freshness at its near-period lags, so never use mismatch as the staleness signal.
- Provenance: Verified first-hand by running the Python sandbox (sb/p5.py) and observing the counts listed above; the lag-377 zero is partly a window-edge effect of 600 samples, and only one lag set was used.
- Composed: local__age-cutoff-roll-up/E1
- Link: session_013efNKK3EZaHZB3Yfzcg6WU
- Cited-by: 2026-10-15 · projects/local__fibonacci-world-older-presses-look-fresher.md#E1 · compatible · sandboxes/2026-10-15__on-a-fibonacci-world-older-presses-look-fresher-to-a-mismatch-gate.py · observed RESULT: FAIL 2/3; lossless cutoff = largest valid lag (34, 30, 60); mismatch at Fibonacci lags 34 0.026, 55 0.016 vs 30 0.764, 60 0.164 · session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto 5-loop run, loop 5 pass 2 (edge), 2026-10-15
